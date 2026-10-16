"""Validadores de identificadores brasileiros por dígito verificador (só biblioteca padrão).

Usados pelo scanner para separar um número com cara de CPF/CNPJ de um identificador válido.
O valor encontrado nunca é guardado nem impresso: só o local (arquivo:linha).
CNPJ alfanumérico: cada caractere vale ord(c) - 48, pesos 5..2,9..2 e 6..2,9..2, módulo 11
(algoritmo publicado pelo Serpro/Receita Federal; exemplo oficial 12.ABC.345/01DE-35).
"""
from __future__ import annotations

import re


def _so(s: str, chars: str) -> str:
    return re.sub(f"[^{chars}]", "", s.upper())


def cpf(valor: str) -> bool:
    d = _so(valor, "0-9")
    if len(d) != 11 or d == d[0] * 11:
        return False
    nums = [int(c) for c in d]
    for n in (9, 10):
        s = sum(v * w for v, w in zip(nums[:n], range(n + 1, 1, -1)))
        if (s * 10 % 11) % 10 != nums[n]:
            return False
    return True


def cnpj(valor: str) -> bool:
    d = _so(valor, "0-9A-Z")
    if len(d) != 14 or not d[12:].isdigit() or d == d[0] * 14:
        return False
    vals = [ord(c) - 48 for c in d[:12]]

    def dv(v, pesos):
        r = sum(a * b for a, b in zip(v, pesos)) % 11
        return 0 if r < 2 else 11 - r

    d1 = dv(vals, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    d2 = dv(vals + [d1], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return d[12:] == f"{d1}{d2}"


VALIDADORES = {"cpf": cpf, "cnpj": cnpj}
