"""CLI: python -m lz_revisor <comando>.

revisar <projeto> [--respostas f.json] [--saida dir]   relatório Markdown + JSON
        [--data AAAA-MM-DD] [--sarif f.sarif] [--falhar-em alta]   vigência na data, SARIF para CI, código 3
perguntas [<projeto>] [--respostas f.json]              o que falta responder
normas [--nivel N1] [--uf GO] [--jurisdicao US] [--busca texto]
minutas                                                  lista as minutas
minuta <id> [--campos f.json] [--saida arquivo.md]       preenche uma minuta
validar-catalogo                                         confere o catálogo
mcp [--raiz dir ...]                                     servidor MCP por stdio
radar [--json]                                           status dos PLs na API da Câmara (único comando com rede)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from datetime import date

from .catalog import SEVERIDADE, CatalogError, load_catalog
from .service import Revisor


def _json(path: str | None) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf8"))


def _write_new(path: Path, text: str) -> None:
    if path.exists():
        raise SystemExit(f"{path} já existe; escolha outro destino (nada foi sobrescrito).")
    path.write_text(text, encoding="utf8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="lz_revisor", description="LexZenit · revisor jurídico de projetos")
    ap.add_argument("--catalogo", help="Diretório do catálogo (padrão: plugin ab-lexzenit-project-review)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("revisar")
    r.add_argument("projeto", nargs="?")
    r.add_argument("--respostas")
    r.add_argument("--saida", help="Diretório novo ou vazio para revisao.md e revisao.json")
    r.add_argument("--titulo")
    r.add_argument("--data", help="Data de referência AAAA-MM-DD (vigência na data dos fatos)")
    r.add_argument("--sarif", help="Arquivo novo para a saída SARIF 2.1.0 (CI e GitHub code scanning)")
    r.add_argument("--falhar-em", choices=["critica", "alta", "media", "baixa"],
                   help="Sai com código 3 se houver não conformidade com essa severidade ou maior")
    p = sub.add_parser("perguntas")
    p.add_argument("projeto", nargs="?")
    p.add_argument("--respostas")
    n = sub.add_parser("normas")
    n.add_argument("--nivel")
    n.add_argument("--uf")
    n.add_argument("--jurisdicao")
    n.add_argument("--busca")
    sub.add_parser("minutas")
    m = sub.add_parser("minuta")
    m.add_argument("modelo")
    m.add_argument("--campos")
    m.add_argument("--saida")
    sub.add_parser("validar-catalogo")
    s = sub.add_parser("mcp")
    s.add_argument("--raiz", action="append", default=[])
    rd = sub.add_parser("radar", help="Consulta a API da Câmara (acessa a rede)")
    rd.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    cat_dir = Path(a.catalogo) if a.catalogo else None

    try:
        if a.cmd == "validar-catalogo":
            cat = load_catalog(cat_dir)
            por = {}
            for nrm in cat.normas:
                por.setdefault(nrm["nivel"], 0)
                por[nrm["nivel"]] += 1
            ver = {}
            for nrm in cat.normas:
                ver[nrm["fonte"]["verificacao"]] = ver.get(nrm["fonte"]["verificacao"], 0) + 1
            print(json.dumps({"catalogo": "valido", "versao": cat.versao, "normas": len(cat.normas), "por_nivel": por,
                              "verificacao": ver, "sinais": len(cat.sinais), "evidencias": len(cat.evidencias),
                              "ufs_com_normas": sorted({x["jurisdicao"][3:] for x in cat.normas if x["jurisdicao"].startswith("BR-")})},
                             ensure_ascii=False, indent=2))
            return 0
        if a.cmd == "radar":
            from . import radar
            itens = radar.consultar(load_catalog(cat_dir))
            print(json.dumps(itens, ensure_ascii=False, indent=2) if a.json else radar.to_markdown(itens))
            return 0
        if a.cmd == "mcp":
            from .mcp_server import serve
            serve([Path(x) for x in a.raiz] or [Path.cwd()], cat_dir)
            return 0
        rev = Revisor(cat_dir)
        if a.cmd == "revisar":
            hoje = date.fromisoformat(a.data) if a.data else None
            res = rev.revisar(a.projeto, _json(a.respostas), hoje)
            md = rev.markdown(res, a.titulo)
            if a.saida:
                out = Path(a.saida)
                out.mkdir(parents=True, exist_ok=True)
                _write_new(out / "revisao.md", md)
                _write_new(out / "revisao.json", json.dumps(res, ensure_ascii=False, indent=2))
                print(f"Relatório em {out/'revisao.md'} e {out/'revisao.json'}")
            else:
                print(md)
            if a.sarif:
                from .sarif import to_sarif
                _write_new(Path(a.sarif), json.dumps(to_sarif(res), ensure_ascii=False, indent=2))
                print(f"SARIF em {a.sarif}", file=sys.stderr)
            if a.falhar_em:
                limite = SEVERIDADE.index(a.falhar_em)
                if any(x["estado"] == "nao_conformidade_evidenciada" and SEVERIDADE.index(x["severidade"]) <= limite
                       for x in res["achados"]):
                    return 3
            return 0
        if a.cmd == "perguntas":
            print(json.dumps(rev.perguntas(a.projeto, _json(a.respostas)), ensure_ascii=False, indent=2))
            return 0
        if a.cmd == "normas":
            print(json.dumps(rev.normas(a.nivel, a.jurisdicao, a.uf, a.busca), ensure_ascii=False, indent=2))
            return 0
        if a.cmd == "minutas":
            print(json.dumps(rev.modelos(), ensure_ascii=False, indent=2))
            return 0
        if a.cmd == "minuta":
            r = rev.minuta(a.modelo, _json(a.campos))
            text = f"<!-- {r['aviso']} -->\n\n{r['texto']}"
            if a.saida:
                _write_new(Path(a.saida), text)
                print(f"Minuta em {a.saida}. Campos pendentes: {', '.join(r['campos_pendentes']) or 'nenhum'}")
            else:
                print(text)
            return 0
    except (CatalogError, ValueError, FileNotFoundError, PermissionError, json.JSONDecodeError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    return 1
