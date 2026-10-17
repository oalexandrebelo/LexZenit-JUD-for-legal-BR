"""Regressão do revisor jurídico de projetos (lz_revisor). Projetos sintéticos; não mede acurácia jurídica."""
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from lz_revisor.catalog import CatalogError, Catalog, load_catalog, validate
from lz_revisor.engine import EstadoSinal, avaliar, escolher_n2, revisar
from lz_revisor.mcp_server import Server, serve
from lz_revisor.scanner import scan
from lz_revisor.service import Revisor
from lz_revisor import templates

AQUI = Path(__file__).resolve().parent
RUNTIME = AQUI.parent
FIXTURES = RUNTIME / "examples" / "revisor"
HOJE = date(2026, 10, 16)
GO = {"sede_uf": "GO", "ufs_atuacao": ["GO"], "paises_alvo": [], "estagio": "mvp",
      "sinais": {"b2c_consumidor": True, "empresa_constituida": True, "agente_pequeno_porte": True}}

CAT = load_catalog()


def achado(res, norma_id, obrigacao_id):
    for a in res["achados"] + res["nao_aplicaveis"]:
        if a["norma_id"] == norma_id and a.get("obrigacao_id") == obrigacao_id:
            return a
    raise AssertionError(f"{norma_id}/{obrigacao_id} ausente")


class CatalogoTests(unittest.TestCase):
    def test_catalogo_valido_com_tres_niveis(self):
        niveis = {n["nivel"] for n in CAT.normas}
        self.assertEqual(niveis, {"N1", "N2", "N3"})
        self.assertTrue(any(n["jurisdicao"] == "BR" for n in CAT.normas))
        self.assertGreaterEqual(len({n["jurisdicao"] for n in CAT.normas if n["jurisdicao"].startswith("BR-")}), 20)

    def test_oficial_exige_url_e_data(self):
        for n in CAT.normas:
            if n["fonte"]["verificacao"] == "oficial_conferido":
                self.assertTrue(n["fonte"]["url"].startswith("https://"), n["id"])
                self.assertRegex(n["fonte"]["verificado_em"], r"^\d{4}-\d{2}-\d{2}$")

    def test_projeto_de_lei_nao_tem_obrigacao(self):
        for n in CAT.normas:
            if n["status"] == "em_tramitacao":
                self.assertEqual(n["obrigacoes"], [], n["id"])

    def test_sinal_desconhecido_quebra_catalogo(self):
        ruim = dict(CAT.normas[0], id="X-1", gatilho="sinal_que_nao_existe")
        cat = Catalog(CAT.root, CAT.versao, CAT.sinais, CAT.evidencias, CAT.questionario, CAT.regra_n2, [ruim])
        with self.assertRaises(CatalogError):
            validate(cat)

    def test_vigencia_futura_exige_inicio(self):
        ruim = dict(CAT.normas[0], id="X-2", status="vigencia_futura")
        ruim.pop("vigencia", None)
        cat = Catalog(CAT.root, CAT.versao, CAT.sinais, CAT.evidencias, CAT.questionario, CAT.regra_n2, [ruim])
        with self.assertRaises(CatalogError):
            validate(cat)

    def test_n1_so_aceita_uf_valida(self):
        ruim = dict(CAT.normas[0], id="X-3", nivel="N1", jurisdicao="BR-XX")
        cat = Catalog(CAT.root, CAT.versao, CAT.sinais, CAT.evidencias, CAT.questionario, CAT.regra_n2, [ruim])
        with self.assertRaises(CatalogError):
            validate(cat)


class LogicaTests(unittest.TestCase):
    def s(self, **kw):
        return {k: EstadoSinal(v, "declarado") for k, v in kw.items()}

    def test_kleene(self):
        sin = self.s(a=True, b=False, c=None)
        self.assertEqual(avaliar({"todos": ["a", "b"]}, sin)[0], False)
        self.assertIsNone(avaliar({"todos": ["a", "c"]}, sin)[0])
        self.assertEqual(avaliar({"algum": ["b", "a"]}, sin)[0], True)
        self.assertIsNone(avaliar({"algum": ["b", "c"]}, sin)[0])
        self.assertIsNone(avaliar({"nao": "c"}, sin)[0])
        self.assertEqual(avaliar(True, sin)[0], True)


class N2Tests(unittest.TestCase):
    def n2(self, respostas, **sinais):
        sin = {k: EstadoSinal(None, "desconhecido") for k in CAT.sinais}
        sin.update({k: EstadoSinal(v, "detectado", "media") for k, v in sinais.items()})
        return escolher_n2(CAT, sin, respostas)

    def test_padrao_eua(self):
        self.assertEqual(self.n2({})["pais"], "US")

    def test_membro_ue_vira_bloco_ue(self):
        r = self.n2({"paises_alvo": ["PT"]})
        self.assertEqual((r["pais"], r["bloco"]), ("PT", "EU"))

    def test_eua_no_alvo_vence_ordem(self):
        self.assertEqual(self.n2({"paises_alvo": ["MX", "US"]})["pais"], "US")

    def test_mercado_principal_vence_eua(self):
        r = self.n2({"paises_alvo": ["US", "PT"], "mercado_principal": "PT"})
        self.assertEqual((r["bloco"], r["regra"]), ("EU", "mercado_principal"))

    def test_fixado_vence_tudo(self):
        self.assertEqual(self.n2({"paises_alvo": ["US"], "mercado_principal": "PT", "pais_n2": "GB"})["pais"], "GB")

    def test_sinal_ue_sem_pais_declarado(self):
        self.assertEqual(self.n2({}, publico_ue=True)["regra"], "sinal_ue")


class ScannerTests(unittest.TestCase):
    def test_app_b2c_sinais(self):
        v = scan(FIXTURES / "app-ia-b2c", CAT)
        for sid in ("ia_generativa", "pagamentos", "cpf_br", "rastreamento_cookies", "web_publico"):
            self.assertIn(sid, v.sinais, sid)

    def test_sdk_de_nuvem_e_indicio_fraco(self):
        v = scan(FIXTURES / "app-ia-b2c", CAT)
        self.assertEqual({i.confianca for i in v.sinais["hospedagem_exterior"]}, {"baixa"})

    def test_saas_documentado_evidencias(self):
        v = scan(FIXTURES / "saas-documentado", CAT)
        for eid in ("politica_privacidade", "termos_uso", "ripd", "aviso_ia", "licenca"):
            self.assertTrue(v.evidencias.get(eid, {}).get("documentos"), eid)

    def test_indicio_guarda_local_nunca_texto(self):
        v = scan(FIXTURES / "app-ia-b2c", CAT)
        locais = [l for ind in v.sinais["cpf_br"] for l in ind.locais]
        self.assertTrue(all(re.match(r"^[\w./-]+:\d+$", l) for l in locais), locais)


class MotorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = revisar(CAT, scan(FIXTURES / "app-ia-b2c", CAT), GO, HOJE)
        cls.saas = revisar(CAT, scan(FIXTURES / "saas-documentado", CAT), GO, HOJE)

    def test_marca_minuta(self):
        self.assertEqual(self.app["marca"], "MINUTA — REVISÃO PROFISSIONAL OBRIGATÓRIA")

    def test_lgpd_sem_politica_e_nao_conformidade(self):
        a = achado(self.app, "BR-LGPD", "transparencia")
        self.assertEqual(a["estado"], "nao_conformidade_evidenciada")
        self.assertEqual(a["modelo"], "politica-privacidade")

    def test_documento_localizado_nunca_vira_satisfeito(self):
        a = achado(self.saas, "BR-LGPD", "transparencia")
        self.assertEqual(a["estado"], "inconclusivo")
        self.assertFalse(a["lacuna"])
        self.assertNotIn("satisfeito_no_escopo", {x["estado"] for x in self.saas["achados"]})

    def test_fonte_secundaria_nunca_e_firme(self):
        for a in self.app["achados"]:
            if a["fonte"]["verificacao"] != "oficial_conferido":
                self.assertNotEqual(a["estado"], "nao_conformidade_evidenciada", a["norma_id"])

    def test_indicio_fraco_nao_e_firme(self):
        a = achado(self.app, "BR-LGPD", "transferencia-internacional")
        self.assertEqual(a["estado"], "inconclusivo")
        self.assertIn("baixa confiança", a["motivo"])

    def test_pequeno_porte_afasta_encarregado(self):
        self.assertEqual(achado(self.app, "BR-LGPD", "encarregado")["estado"], "nao_aplicavel_justificado")

    def test_sinal_desconhecido_vira_pergunta(self):
        self.assertTrue(any("investimento" in p for p in self.app["perguntas_pendentes"]))
        self.assertIsNone(achado(self.app, "BR-LC182-APORTE", "instrumento")["lacuna"])

    def test_uf_fora_da_atuacao_nao_aplica(self):
        sp = [a for a in self.app["nao_aplicaveis"] if a["jurisdicao"] == "BR-SP"]
        self.assertTrue(sp)
        self.assertFalse([a for a in self.app["achados"] if a["jurisdicao"] == "BR-SP"])

    def test_uf_desconhecida_e_inconclusiva(self):
        res = revisar(CAT, None, {"sinais": {"b2c_consumidor": True}}, HOJE)
        uf = [a for a in res["achados"] if a["jurisdicao"].startswith("BR-")]
        self.assertTrue(uf)
        self.assertTrue(all(a["estado"] == "inconclusivo" for a in uf))

    def test_projeto_de_lei_so_no_radar(self):
        self.assertIn("BR-PL-2338-2023", {r["norma_id"] for r in self.app["radar_regulatorio"]})
        self.assertFalse([a for a in self.app["achados"] if a["status_norma"] == "em_tramitacao"])

    def test_oportunidades_nao_sao_achados(self):
        self.assertIn("BR-LC182", {o["norma_id"] for o in self.app["oportunidades"]})
        self.assertFalse([a for a in self.app["achados"] if a["norma_id"] == "BR-LC182"])

    def test_n2_sem_usuarios_declarados_e_prontidao(self):
        n2 = [a for a in self.app["achados"] if a["nivel"] == "N2"]
        self.assertTrue(n2)
        self.assertTrue(all(a["modo"] == "prontidao" and a["estado"] != "nao_conformidade_evidenciada" for a in n2))

    def test_eua_declarado_aplica_federal_e_estado(self):
        r = dict(GO, paises_alvo=["US"], us_estados=["CA"],
                 sinais=dict(GO["sinais"], limiar_privacidade_eua=True, ia_decisao_automatizada=True))
        res = revisar(CAT, scan(FIXTURES / "app-ia-b2c", CAT), r, HOJE)
        self.assertEqual(achado(res, "US-CA-CPPA-RISCO", "avaliacao-risco")["modo"], "aplicavel")
        self.assertEqual(achado(res, "US-FTC-S5", "promessas-privacidade")["modo"], "aplicavel")
        co = achado(res, "US-CO-SB26-189", "aviso-previo")
        self.assertEqual(co["modo"], "prontidao")   # outro estado: prontidão, nunca firme
        self.assertNotEqual(co["estado"], "nao_conformidade_evidenciada")

    def test_eua_no_alcance_sem_estados_e_pergunta(self):
        r = dict(GO, paises_alvo=["US", "GB"], mercado_principal="GB", sinais=dict(GO["sinais"], limiar_privacidade_eua=True))
        a = achado(revisar(CAT, scan(FIXTURES / "app-ia-b2c", CAT), r, HOJE), "US-CA-CCPA", "aviso-coleta")
        self.assertEqual((a["modo"], a["estado"]), ("desconhecido", "inconclusivo"))

    def test_pais_nacional_n3_fora_sem_alcance(self):
        self.assertFalse([a for a in self.app["achados"] if a["jurisdicao"] in ("CN", "KR")])
        res = revisar(CAT, scan(FIXTURES / "app-ia-b2c", CAT), dict(GO, paises_alvo=["CN"]), HOJE)
        self.assertEqual(achado(res, "CN-IA-GENERATIVA", "dados-treino")["modo"], "aplicavel")

    def test_vigencia_futura_vira_vigente_na_data(self):
        r = dict(GO, paises_alvo=["US"], us_estados=["CO"], sinais=dict(GO["sinais"], ia_decisao_automatizada=True))
        antes = achado(revisar(CAT, None, r, HOJE), "US-CO-SB26-189", "aviso-previo")
        depois = achado(revisar(CAT, None, r, date(2027, 1, 2)), "US-CO-SB26-189", "aviso-previo")
        self.assertIn("vigência futura", antes["motivo"])
        self.assertEqual(depois["estado"], "nao_conformidade_evidenciada")


class RelatorioTests(unittest.TestCase):
    def test_markdown_tem_marca_e_assinatura(self):
        rev = Revisor()
        md = rev.markdown(rev.revisar(str(FIXTURES / "app-ia-b2c"), GO))
        self.assertIn("MINUTA — REVISÃO PROFISSIONAL OBRIGATÓRIA", md)
        self.assertIn("OAB/UF", md)
        self.assertIn("## Radar regulatório", md)
        self.assertNotRegex(md, r"\d{3}\.\d{3}\.\d{3}-\d{2}")

    def test_relatorio_nao_copia_texto_casado(self):
        cpf = "123" + ".456.789-" + "09"   # valor sintético montado no teste, nunca gravado no repositório
        with tempfile.TemporaryDirectory() as d:
            Path(d, "cadastro.ts").write_text(f'const cpf = "{cpf}"; const email = "x"\n')
            rev = Revisor()
            res = rev.revisar(d, GO)
            texto = rev.markdown(res) + json.dumps(res, ensure_ascii=False)
            self.assertIn("cpf_br", {k for k, v in res["sinais"].items() if v["valor"]})
            self.assertNotIn(cpf, texto)
            self.assertIn("cadastro.ts:1", texto)


class MinutaTests(unittest.TestCase):
    def test_lista_e_preenche(self):
        ids = {m["id"] for m in templates.listar(CAT.root)}
        self.assertIn("politica-privacidade", ids)
        r = templates.gerar(CAT.root, "nda-mutuo", {"parte_a_nome": "Empresa Sintética Ltda."})
        self.assertIn("Empresa Sintética Ltda.", r["texto"])
        self.assertIn("parte_b_nome", r["campos_pendentes"])

    def test_modelo_com_caminho_e_recusado(self):
        with self.assertRaises(ValueError):
            templates.gerar(CAT.root, "../POLICY", {})


class McpTests(unittest.TestCase):
    def roundtrip(self, msgs, raiz=FIXTURES):
        out = io.StringIO()
        serve([raiz], None, io.StringIO("\n".join(json.dumps(m) for m in msgs) + "\n"), out)
        return [json.loads(l) for l in out.getvalue().splitlines()]

    def test_initialize_list_call(self):
        r = self.roundtrip([
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "revisar_projeto", "arguments": {"caminho": "app-ia-b2c", "respostas": GO, "formato": "json"}}},
        ])
        self.assertEqual([x["id"] for x in r], [1, 2, 3])
        self.assertEqual(r[0]["result"]["protocolVersion"], "2025-06-18")
        self.assertIn("revisar_projeto", {t["name"] for t in r[1]["result"]["tools"]})
        res = json.loads(r[2]["result"]["content"][0]["text"])
        self.assertEqual(res["n2"]["pais"], "US")

    def test_caminho_fora_da_raiz_e_recusado(self):
        r = self.roundtrip([{"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                             "params": {"name": "escanear_sinais", "arguments": {"caminho": "/etc"}}}])
        self.assertTrue(r[0]["result"]["isError"])
        self.assertIn("fora das raízes", r[0]["result"]["content"][0]["text"])

    def test_metodo_e_ferramenta_desconhecidos(self):
        r = self.roundtrip([{"jsonrpc": "2.0", "id": 1, "method": "resources/list"},
                            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "apagar"}}])
        self.assertEqual(r[0]["error"]["code"], -32601)
        self.assertEqual(r[1]["error"]["code"], -32602)

    def test_json_invalido(self):
        out = io.StringIO()
        serve([FIXTURES], None, io.StringIO("{nao json\n"), out)
        self.assertEqual(json.loads(out.getvalue())["error"]["code"], -32700)


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "lz_revisor", *args], cwd=RUNTIME, capture_output=True, text=True)

    def test_validar_catalogo(self):
        p = self.run_cli("validar-catalogo")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["catalogo"], "valido")

    def test_saida_nao_sobrescreve(self):
        with tempfile.TemporaryDirectory() as d:
            resp = Path(d) / "r.json"
            resp.write_text(json.dumps(GO))
            out = Path(d) / "saida"
            p1 = self.run_cli("revisar", str(FIXTURES / "vazio"), "--respostas", str(resp), "--saida", str(out))
            self.assertEqual(p1.returncode, 0, p1.stderr)
            antes = (out / "revisao.md").read_text()
            p2 = self.run_cli("revisar", str(FIXTURES / "vazio"), "--respostas", str(resp), "--saida", str(out))
            self.assertNotEqual(p2.returncode, 0)
            self.assertEqual((out / "revisao.md").read_text(), antes)


class RevisaoIndependenteTests(unittest.TestCase):
    """Casos de regressão dos achados da revisão independente de 2026-10-16."""

    def projeto(self, d, arquivos):
        for nome, txt in arquivos.items():
            Path(d, nome).parent.mkdir(parents=True, exist_ok=True)
            Path(d, nome).write_text(txt)
        return revisar(CAT, scan(d, CAT), GO, HOJE)

    def test_moeda_detectada_nao_torna_ue_aplicavel(self):
        with tempfile.TemporaryDirectory() as d:
            res = self.projeto(d, {"package.json": '{"dependencies": {"openai": "1"}}', "precos.ts": 'const m = ["BRL", "EUR"]\n'})
            ue = [a for a in res["achados"] if a["jurisdicao"] == "EU"]
            self.assertTrue(ue)
            self.assertTrue(all(a["modo"] == "prontidao" for a in ue))
            self.assertFalse([a for a in ue if a["estado"] == "nao_conformidade_evidenciada"])

    def test_resposta_com_tipo_errado_e_recusada(self):
        for ruim in ({"sinais": {"dados_pessoais": "false"}}, {"ufs_atuacao": "SP"}, {"sinais": {"nao_existe": True}},
                     {"estagio": "unicornio"}):
            with self.assertRaises(ValueError, msg=ruim):
                revisar(CAT, None, ruim, HOJE)

    def test_vedacao_nunca_e_firme(self):
        r = dict(GO, paises_alvo=["DE"], sinais=dict(GO["sinais"], chatbot_publico=True))
        a = achado(revisar(CAT, None, r, HOJE), "EU-AI-ACT", "praticas-proibidas")
        self.assertEqual((a["modo"], a["estado"]), ("aplicavel", "inconclusivo"))
        self.assertIn("Vedação", a["motivo"])

    def test_alerta_de_competencia_impede_firme_e_aparece(self):
        r = dict(GO, sinais=dict(GO["sinais"], ia_decisao_automatizada=True))
        res = revisar(CAT, None, r, HOJE)
        a = achado(res, "BR-GO-IA-001", "decisao-automatizada")
        self.assertEqual(a["estado"], "inconclusivo")
        self.assertIn("competência", a["motivo"])
        linha = next(l for l in Revisor().markdown(res).splitlines() if "decisões automatizadas, informar o uso" in l)
        self.assertIn("competência constitucional", linha)

    def test_nome_de_arquivo_parecido_nao_e_evidencia(self):
        with tempfile.TemporaryDirectory() as d:
            v = scan(self.projeto_dir(d, {"CLAUDE.md": "x", "src/calendar.ts": "x", "src/searchTerms.ts": "x",
                                          "src/PrivacyToggle.tsx": "x", "src/main-impact.ts": "x",
                                          "src/tx.ts": "const transaction = 1\n"}), CAT)
            for eid in ("cessao_pi", "nda", "termos_uso", "politica_privacidade", "avaliacao_impacto_ia", "atendimento_consumidor"):
                self.assertFalse(v.evidencias.get(eid), eid)

    def projeto_dir(self, d, arquivos):
        for nome, txt in arquivos.items():
            Path(d, nome).parent.mkdir(parents=True, exist_ok=True)
            Path(d, nome).write_text(txt)
        return d

    def test_fifo_nao_trava_varredura(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            os.mkfifo(Path(d, "notas.txt"))
            Path(d, "README.md").write_text("Política de Privacidade\n")
            v = scan(d, CAT)
            self.assertTrue(v.evidencias["politica_privacidade"]["mencoes"])

    def test_gomod_patologico_e_rapido(self):
        import time
        with tempfile.TemporaryDirectory() as d:
            Path(d, "go.mod").write_text("\n" * 200_000 + "x")
            t = time.monotonic()
            scan(d, CAT)
            self.assertLess(time.monotonic() - t, 5)

    def test_exclusao_torna_nao_detectado_desconhecido(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, ".lzrevisorignore").write_text("src/\n")
            Path(d, "README.md").write_text("x\n")
            res = revisar(CAT, scan(d, CAT), GO, HOJE)
            self.assertIsNone(res["sinais"]["dados_pessoais"]["valor"])
            self.assertIn("src/", Revisor().markdown(res))

    def test_sdk_de_email_nao_aciona_cadastro_de_telemarketing(self):
        with tempfile.TemporaryDirectory() as d:
            r = dict(GO, ufs_atuacao=["GO", "SP", "RO"])
            res = revisar(CAT, scan(self.projeto_dir(d, {"package.json": '{"dependencies": {"nodemailer": "1", "stripe": "1"}}'}), CAT), r, HOJE)
            firmes = [a for a in res["achados"] if a["estado"] == "nao_conformidade_evidenciada" and a["jurisdicao"] != "BR"]
            self.assertFalse([a for a in firmes if "telemarketing_cobranca" in a["sinais_gatilho"] or "sac_telefonico" in a["sinais_gatilho"]])


class RadarTests(unittest.TestCase):
    def test_radar_usa_ficha_da_camara_e_marca_mudanca(self):
        from lz_revisor import radar
        chamadas = []
        def fake(url):
            chamadas.append(url)
            return {"dados": {"siglaTipo": "PL", "numero": 2338, "ano": 2023,
                              "statusProposicao": {"dataHora": "2026-11-20T10:00", "descricaoSituacao": "Aguardando Parecer",
                                                   "descricaoTramitacao": "Notificação", "siglaOrgao": "PL233823", "despacho": "x"}}}
        itens = radar.consultar(CAT, fetch=fake)
        self.assertTrue(itens)
        self.assertTrue(all(u.startswith("https://dadosabertos.camara.leg.br/api/v2/proposicoes/") for u in chamadas))
        pl = next(i for i in itens if i["norma_id"] == "BR-PL-2338-2023")
        self.assertEqual((pl["proposicao"], pl["mudou"]), ("PL 2338/2023", True))
        self.assertIn("PL 2338/2023", radar.to_markdown(itens))

    def test_radar_registra_erro_sem_parar(self):
        from lz_revisor import radar
        def falha(url):
            raise OSError("sem rede")
        itens = radar.consultar(CAT, fetch=falha)
        self.assertTrue(all("erro" in i for i in itens))

    def test_radar_recusa_outro_host(self):
        from lz_revisor import radar
        with self.assertRaises(ValueError):
            radar._fetch("https://example.com/api")


class DivergenciaTests(unittest.TestCase):
    def test_resposta_nao_contradita_pelo_codigo(self):
        r = dict(GO, sinais=dict(GO["sinais"], ia_generativa=False))
        res = revisar(CAT, scan(FIXTURES / "app-ia-b2c", CAT), r, HOJE)
        d = [x for x in res["divergencias"] if x["sinal"] == "ia_generativa"]
        self.assertTrue(d and d[0]["indicios"])
        self.assertIn("Respostas que o código contradiz", Revisor().markdown(res))


class CiTests(unittest.TestCase):
    def test_sarif_com_local_do_gatilho(self):
        from lz_revisor.sarif import to_sarif
        res = revisar(CAT, scan(FIXTURES / "app-ia-b2c", CAT), GO, HOJE)
        sar = to_sarif(res)
        self.assertEqual(sar["version"], "2.1.0")
        rs = sar["runs"][0]["results"]
        self.assertTrue(any(r["level"] == "error" for r in rs))
        cdc = next(r for r in rs if r["ruleId"] == "BR-CDC/arrependimento")
        self.assertEqual(cdc["locations"][0]["physicalLocation"]["artifactLocation"]["uri"], "src/lib/checkout.ts")
        ids = {r["id"] for r in sar["runs"][0]["tool"]["driver"]["rules"]}
        self.assertTrue({r["ruleId"] for r in rs} <= ids)

    def test_cli_falhar_em_e_data(self):
        with tempfile.TemporaryDirectory() as d:
            resp = Path(d) / "r.json"
            resp.write_text(json.dumps(GO))
            base = [sys.executable, "-m", "lz_revisor", "revisar", str(FIXTURES / "app-ia-b2c"), "--respostas", str(resp)]
            p = subprocess.run(base + ["--falhar-em", "alta", "--sarif", str(Path(d) / "r.sarif")], cwd=RUNTIME, capture_output=True, text=True)
            self.assertEqual(p.returncode, 3, p.stderr)
            self.assertTrue((Path(d) / "r.sarif").is_file())
            p2 = subprocess.run(base + ["--falhar-em", "critica"], cwd=RUNTIME, capture_output=True, text=True)
            self.assertEqual(p2.returncode, 0, p2.stderr)
            p3 = subprocess.run(base + ["--data", "2027-01-02"], cwd=RUNTIME, capture_output=True, text=True)
            self.assertIn("data de referência 2027-01-02", p3.stdout)

    def test_proveniencia_e_urn(self):
        res = revisar(CAT, None, GO, HOJE)
        pv = res["proveniencia"]
        self.assertEqual(len(pv["catalogo_sha256"]), 64)
        self.assertEqual(pv["data_de_referencia"], "2026-10-16")
        self.assertEqual(CAT.norma("BR-LGPD")["urn"], "urn:lex:br:federal:lei:2018-08-14;13709")


class ValidadoresTests(unittest.TestCase):
    @staticmethod
    def cpf_sintetico(base9):
        n = [int(c) for c in base9]
        for k in (9, 10):
            n.append((sum(v * w for v, w in zip(n, range(k + 1, 1, -1))) * 10 % 11) % 10)
        s = "".join(map(str, n))
        return f"{s[:3]}.{s[3:6]}.{s[6:9]}-{s[9:]}"

    def test_cpf_e_cnpj(self):
        from lz_revisor.validadores import cpf, cnpj
        bom = self.cpf_sintetico("123456789")
        self.assertTrue(cpf(bom))
        self.assertFalse(cpf(bom[:-1] + str((int(bom[-1]) + 1) % 10)))
        self.assertFalse(cpf("111.111.111-11"))
        self.assertTrue(cnpj("12.ABC.345/01DE-35"))      # exemplo oficial do CNPJ alfanumérico
        self.assertTrue(cnpj("11.222.333/0001-81"))
        self.assertFalse(cnpj("11.222.333/0001-82"))

    def test_scanner_so_conta_dv_valido_e_nao_guarda_valor(self):
        bom = self.cpf_sintetico("987654321")
        with tempfile.TemporaryDirectory() as d:
            Path(d, "a.ts").write_text('const x = "' + "123" + '.456.789-00"\n')     # formato sem DV válido
            Path(d, "b.ts").write_text(f'const y = "{bom}"\n')
            Path(d, "rodape.html").write_text("<p>CNPJ 12.ABC.345/01DE-35</p>\n")
            v = scan(d, CAT)
            ind = [i for i in v.sinais["cpf_br"] if "dígito" in i.rotulo]
            self.assertEqual([l for i in ind for l in i.locais], ["b.ts:1"])
            self.assertIn("rodape.html:1", v.evidencias["identificacao_fornecedor"]["mencoes"])
            self.assertNotIn(bom, json.dumps(v.to_dict(), ensure_ascii=False))

    def test_reuse_e_sbom_como_evidencia(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "LICENSES").mkdir()
            Path(d, "LICENSES", "Apache-2.0.txt").write_text("x")
            Path(d, "bom.cdx.json").write_text("{}")
            Path(d, ".lgpd").mkdir()
            Path(d, ".lgpd", "ROPA.md").write_text("x")
            v = scan(d, CAT)
            self.assertTrue(v.evidencias["licenca"]["documentos"])
            self.assertTrue(v.evidencias["auditoria_licencas"]["documentos"])
            self.assertTrue(v.evidencias["registro_operacoes"]["documentos"])


class FixtureHygieneTests(unittest.TestCase):
    def test_fixtures_sem_cpf_nem_chave(self):
        cpf = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
        chave = re.compile(r"(sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|-----BEGIN)")
        for f in FIXTURES.rglob("*"):
            if f.is_file():
                t = f.read_text(encoding="utf8", errors="replace")
                self.assertIsNone(cpf.search(t), f)
                self.assertIsNone(chave.search(t), f)


if __name__ == "__main__":
    unittest.main()
