"""Executor local de DAG validado, concorrência limitada e falha explícita.

Não é scheduler distribuído/durável. Nós devem ser funções async cooperativas;
CPU pesada pertence a workers isolados, não ao event loop.
"""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from pydantic import TypeAdapter

from .models import CheckResult, CheckState, Identifier


@dataclass(frozen=True)
class Node:
    name: str
    dependencies: tuple[str, ...]
    timeout_seconds: float
    run: Callable[[Mapping[str, CheckResult]], Awaitable[CheckResult]]


class DAGRunner:
    def __init__(self, nodes: tuple[Node, ...], *, concurrency: int = 4) -> None:
        if type(concurrency) is not int or concurrency < 1:
            raise ValueError("Concorrência deve ser inteiro positivo.")
        self._nodes = {node.name: node for node in nodes}
        if not nodes or len(self._nodes) != len(nodes):
            raise ValueError("DAG vazia ou IDs de nós duplicados.")
        for node in nodes:
            TypeAdapter(Identifier).validate_python(node.name, strict=True)
            if not node.name or node.timeout_seconds <= 0 or not node.timeout_seconds < float("inf"):
                raise ValueError("Nó sem nome ou prazo inválido.")
            if len(set(node.dependencies)) != len(node.dependencies):
                raise ValueError("Dependências duplicadas.")
            if set(node.dependencies) - set(self._nodes):
                raise ValueError("Dependência desconhecida.")
        remaining = set(self._nodes)
        visited: set[str] = set()
        while remaining:
            ready = {name for name in remaining if set(self._nodes[name].dependencies) <= visited}
            if not ready:
                raise ValueError("Ciclo no grafo de dependências.")
            visited |= ready
            remaining -= ready
        self._concurrency = concurrency

    async def execute(self, *, total_timeout_seconds: float = 60.0) -> tuple[CheckResult, ...]:
        if total_timeout_seconds <= 0 or not total_timeout_seconds < float("inf"):
            raise ValueError("Prazo total inválido.")
        pending = set(self._nodes)
        completed: dict[str, CheckResult] = {}
        running: dict[asyncio.Task[CheckResult], str] = {}

        async def evaluate(node: Node) -> CheckResult:
            deps = MappingProxyType({key: completed[key] for key in node.dependencies})
            if any(value.state in (CheckState.ERROR, CheckState.INCONCLUSIVE) for value in deps.values()):
                return CheckResult(skill_id=node.name, state=CheckState.INCONCLUSIVE,
                                   justification="Dependência não produziu evidência utilizável.")
            try:
                async with asyncio.timeout(node.timeout_seconds):
                    result = await node.run(deps)
                if not isinstance(result, CheckResult) or result.skill_id != node.name:
                    raise ValueError("Resultado não corresponde ao contrato do nó.")
                # Revalidação impede aceitar instância construída sem validação em um plugin.
                return CheckResult.model_validate_json(result.model_dump_json())
            except asyncio.CancelledError:
                raise
            except TimeoutError:
                return CheckResult(skill_id=node.name, state=CheckState.ERROR,
                                   justification="Prazo do nó excedido.")
            except Exception as exc:
                # Não registrar str(exc): exceções podem conter texto confidencial do documento.
                return CheckResult(skill_id=node.name, state=CheckState.ERROR,
                                   justification=f"Execução falhou ({type(exc).__name__}).")

        try:
            async with asyncio.timeout(total_timeout_seconds):
                while pending or running:
                    ready = sorted(name for name in pending
                                   if set(self._nodes[name].dependencies) <= set(completed))
                    for name in ready[:self._concurrency - len(running)]:
                        task = asyncio.create_task(evaluate(self._nodes[name]), name=f"lexguard:{name}")
                        running[task] = name
                        pending.remove(name)
                    if not running:
                        raise RuntimeError("DAG validada sem nó executável.")
                    done, _ = await asyncio.wait(running, return_when=asyncio.FIRST_COMPLETED)
                    for task in done:
                        name = running.pop(task)
                        completed[name] = task.result()
        except TimeoutError:
            for name in self._nodes:
                if name not in completed:
                    completed[name] = CheckResult(skill_id=name, state=CheckState.ERROR,
                                                  justification="Prazo total do pipeline excedido.")
        finally:
            for task in running:
                task.cancel()
            if running:
                await asyncio.gather(*running, return_exceptions=True)
        return tuple(completed[name] for name in sorted(completed))
