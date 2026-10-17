"""Servidor MCP por stdio (JSON-RPC 2.0, uma mensagem por linha), só biblioteca padrão.

Ativação explícita pelo operador, nunca pelo plugin:
    claude mcp add lz-revisor -e PYTHONPATH=<repositório>/runtime -- python3 -m lz_revisor mcp --raiz /caminho/dos/projetos

Segurança:
- lê apenas dentro das raízes passadas em --raiz (padrão: diretório atual);
- não escreve arquivos, não executa código do projeto, não acessa rede;
- o relatório guarda caminho e linha dos indícios, nunca o texto casado.
"""
from __future__ import annotations

import json
import sys
import traceback
from datetime import date
from pathlib import Path

from . import __version__
from .service import Revisor

PROTOCOLOS = ["2025-06-18", "2025-03-26", "2024-11-05"]

RESPOSTAS_SCHEMA = {
    "type": "object",
    "description": "Respostas do questionário: {sinais:{id:bool}, sede_uf, ufs_atuacao[], paises_alvo[], us_estados[], estagio, mercado_principal, pais_n2, evidencias:{id:local}}",
    "properties": {
        "sinais": {"type": "object", "additionalProperties": {"type": ["boolean", "null"]}},
        "sede_uf": {"type": "string"},
        "ufs_atuacao": {"type": "array", "items": {"type": "string"}},
        "paises_alvo": {"type": "array", "items": {"type": "string"}},
        "us_estados": {"type": "array", "items": {"type": "string"}},
        "estagio": {"type": "string", "enum": ["ideia", "mvp", "tracao", "escala"]},
        "mercado_principal": {"type": "string", "description": "País estrangeiro com maior receita ou usuários (ISO)"},
        "pais_n2": {"type": "string"},
        "evidencias": {"type": "object", "additionalProperties": {"type": "string"}},
    },
}

TOOLS = [
    {"name": "revisar_projeto",
     "description": "Revisa um projeto e mapeia lacunas jurídicas em N1 (Brasil: União e UFs), N2 (EUA ou país mais coerente) e N3 (mundo). Lê o código em modo somente leitura, cruza com o catálogo normativo e devolve relatório. Minuta para revisão profissional, não parecer.",
     "inputSchema": {"type": "object", "properties": {
         "caminho": {"type": "string", "description": "Diretório do projeto (dentro das raízes autorizadas). Omitir para revisar só pelas respostas."},
         "respostas": RESPOSTAS_SCHEMA,
         "formato": {"type": "string", "enum": ["markdown", "json", "sarif"], "default": "markdown"},
         "data": {"type": "string", "description": "Data de referência AAAA-MM-DD para a vigência (padrão: hoje)"}}}},
    {"name": "perguntas_pendentes",
     "description": "Lista as perguntas do questionário que ainda faltam para fechar a revisão (UF, países, investimento, menores, decisões automatizadas...).",
     "inputSchema": {"type": "object", "properties": {"caminho": {"type": "string"}, "respostas": RESPOSTAS_SCHEMA}}},
    {"name": "escanear_sinais",
     "description": "Mostra o que o código indica sobre o projeto (dados pessoais, IA generativa, pagamentos, público-alvo...), com arquivo e linha de cada indício.",
     "inputSchema": {"type": "object", "required": ["caminho"], "properties": {"caminho": {"type": "string"}, "respostas": RESPOSTAS_SCHEMA}}},
    {"name": "escolher_n2",
     "description": "Decide o país N2 do projeto (EUA por padrão; outro país soberano quando o mercado real indicar) e explica a regra aplicada.",
     "inputSchema": {"type": "object", "properties": {"caminho": {"type": "string"}, "respostas": RESPOSTAS_SCHEMA}}},
    {"name": "consultar_normas",
     "description": "Consulta o catálogo normativo por nível (N1, N2, N3), jurisdição (BR, BR-GO, US, US-CA, EU...), UF ou texto. Cada norma traz status, vigência, fonte e estado de verificação.",
     "inputSchema": {"type": "object", "properties": {
         "nivel": {"type": "string", "enum": ["N1", "N2", "N3"]}, "jurisdicao": {"type": "string"},
         "uf": {"type": "string"}, "busca": {"type": "string"}}}},
    {"name": "listar_minutas",
     "description": "Lista as minutas brasileiras disponíveis (política de privacidade, termos de uso, NDA, cessão de PI, acordo de fundadores, RIPD, avaliação de impacto de IA...) e os campos de cada uma.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "gerar_minuta",
     "description": "Preenche uma minuta com os campos informados e devolve o texto. Não grava arquivo. A saída continua sendo minuta para revisão profissional.",
     "inputSchema": {"type": "object", "required": ["modelo"], "properties": {
         "modelo": {"type": "string"}, "campos": {"type": "object", "additionalProperties": {"type": "string"}}}}},
]


class Server:
    def __init__(self, raizes: list[Path], catalog_dir: Path | None = None):
        self.raizes = [r.resolve() for r in raizes]
        self.revisor = Revisor(catalog_dir)

    def _caminho(self, valor: str | None) -> str | None:
        if not valor:
            return None
        p = Path(valor).expanduser()
        if not p.is_absolute():
            p = self.raizes[0] / p
        p = p.resolve()
        if not any(p == r or r in p.parents for r in self.raizes):
            raise PermissionError(f"Caminho fora das raízes autorizadas: {p}")
        if not p.is_dir():
            raise FileNotFoundError(f"Diretório não encontrado: {p}")
        return str(p)

    def call(self, name: str, args: dict) -> str:
        args = args or {}
        resp = args.get("respostas") or {}
        if name == "revisar_projeto":
            hoje = date.fromisoformat(args["data"]) if args.get("data") else None
            res = self.revisor.revisar(self._caminho(args.get("caminho")), resp, hoje)
            if args.get("formato") == "json":
                return json.dumps(res, ensure_ascii=False, indent=2)
            if args.get("formato") == "sarif":
                from .sarif import to_sarif
                return json.dumps(to_sarif(res), ensure_ascii=False, indent=2)
            return self.revisor.markdown(res)
        if name == "perguntas_pendentes":
            return json.dumps(self.revisor.perguntas(self._caminho(args.get("caminho")), resp), ensure_ascii=False, indent=2)
        if name == "escanear_sinais":
            caminho = self._caminho(args.get("caminho"))
            if not caminho:
                raise ValueError("Informe 'caminho'.")
            return json.dumps(self.revisor.sinais(caminho, resp), ensure_ascii=False, indent=2)
        if name == "escolher_n2":
            return json.dumps(self.revisor.n2(self._caminho(args.get("caminho")), resp), ensure_ascii=False, indent=2)
        if name == "consultar_normas":
            return json.dumps(self.revisor.normas(args.get("nivel"), args.get("jurisdicao"), args.get("uf"), args.get("busca")),
                              ensure_ascii=False, indent=2)
        if name == "listar_minutas":
            return json.dumps(self.revisor.modelos(), ensure_ascii=False, indent=2)
        if name == "gerar_minuta":
            r = self.revisor.minuta(args.get("modelo", ""), args.get("campos"))
            return f"{r['aviso']}\nCampos pendentes: {', '.join(r['campos_pendentes']) or 'nenhum'}\n\n{r['texto']}"
        raise KeyError(name)

    def handle(self, msg: dict) -> dict | None:
        mid = msg.get("id")
        method = msg.get("method")
        if mid is None:          # notificação: nunca responde
            return None
        try:
            if method == "initialize":
                pedido = (msg.get("params") or {}).get("protocolVersion")
                versao = pedido if pedido in PROTOCOLOS else PROTOCOLOS[0]
                result = {"protocolVersion": versao, "capabilities": {"tools": {"listChanged": False}},
                          "serverInfo": {"name": "lz-revisor", "title": "LexZenit · revisor jurídico de projetos", "version": __version__},
                          "instructions": "Revisor jurídico local. Use perguntas_pendentes antes de revisar_projeto para reduzir achados inconclusivos. Toda saída é minuta para revisão profissional."}
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                params = msg.get("params") or {}
                name = params.get("name")
                if name not in {t["name"] for t in TOOLS}:
                    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": f"Ferramenta desconhecida: {name}"}}
                try:
                    text = self.call(name, params.get("arguments") or {})
                    result = {"content": [{"type": "text", "text": text}], "isError": False}
                except (ValueError, PermissionError, FileNotFoundError, KeyError) as exc:
                    result = {"content": [{"type": "text", "text": f"Erro: {exc}"}], "isError": True}
            else:
                return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Método não suportado: {method}"}}
            return {"jsonrpc": "2.0", "id": mid, "result": result}
        except Exception as exc:  # erro interno nunca vira conformidade
            traceback.print_exc(file=sys.stderr)
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32603, "message": f"Erro interno: {exc}"}}


def serve(raizes: list[Path], catalog_dir: Path | None = None, stdin=None, stdout=None) -> None:
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    server = Server(raizes or [Path.cwd()], catalog_dir)
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON inválido"}}) + "\n")
            stdout.flush()
            continue
        msgs = msg if isinstance(msg, list) else [msg]
        replies = [r for r in (server.handle(m) for m in msgs if isinstance(m, dict)) if r is not None]
        if replies:
            out = replies if isinstance(msg, list) else replies[0]
            stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
            stdout.flush()
