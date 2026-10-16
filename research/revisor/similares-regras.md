# Projetos semelhantes à LexZenit: catálogo, motor e questionário (frente B)

Data: 2026-10-16. Escopo: regulação como código, catálogos de controles e conformidade de IA. Dados completos, com licença, situação, formato, cobertura, o que incorporar, riscos e URLs lidas, em `similares-regras.json` (61 entradas). Não é parecer jurídico.

## 1. Resposta curta

**Concorrente direto: não encontrado.** Nenhum projeto lido combina leitura de repositório + questionário + catálogo multijurisdição com N1 Brasil e UFs + estados trivalentes + verificação de fonte oficial por norma. O mais próximo é o **Regula** (kuzivaai/getregula), e ele cobre só IA: decisão de aplicabilidade para UE, Coreia do Sul e Colorado; o Brasil entra apenas como referência opcional, "sem decisão de aplicabilidade"; sem UFs; 4 estrelas.

**Top 5 do que incorporar (valor/esforço):**
1. Proveniência por resposta do questionário + regra "desconhecido nunca vira não conforme" + trilha com hash (Regula, que usa hash encadeado segundo o Socket; EuConform verifica integridade de bundles). Valor alto, esforço baixo.
2. URN LEX (LexML) como id canônico e resolvedor de `link_oficial` (federal confirmado). Valor médio-alto, esforço baixo.
3. Saída SARIF + código de saída por severidade + comentário em PR (Regula, aigov, Lula). Valor alto, esforço baixo-médio.
4. Vigência com versões datadas e consulta por data (OpenFisca, Akoma Ntoso Work/Expression, legalize-kr). Valor alto, esforço médio.
5. Exportar OSCAL assessment-results + POA&M, e o conjunto aplicável como profile (OSCAL; precedente: Venturalitica/arXiv 2604.13767). Valor médio (interoperabilidade), esforço médio.

**Não adotar:** SCF como fonte de conteúdo (CC BY-ND 4.0, proíbe derivados, inclusive por IA); código ou bibliotecas AGPL (CISO Assistant, Comp AI, OpenFisca); Catala, Blawx e LegalRuleML como motor ou formato primário; OPA/Rego como motor de gatilhos; eramba, Credo AI Lens (arquivado) e OpenControl (parado); rastreadores "all rights reserved" (OECD.AI, IAPP, PrivacyLawMap) e Digital Policy Alert (BY-NC) como fonte de ingestão.

## 2. Existe algo que faça o que a LexZenit faz junto?

| Projeto | Lê repositório | Questionário | Decisão multijurisdição | LGPD/Brasil | UFs | Fonte oficial por norma | Estados trivalentes | MCP |
|---|---|---|---|---|---|---|---|---|
| Regula (getregula) | sim | sim (`assess`, facts.json) | UE, Coreia, Colorado | só referência opcional | não | não descrito | parcial (`unknown` != `no`, `insufficient_information`) | sim (stdio) |
| EuConform | sim (scan) | quiz art. 5/6 | só UE | não | não | não | não | n/i |
| EU AI Act Compliance Kit | não (descritor YAML) | descritor | só UE | não | não | não | 4 estados (compliant/partial/non_compliant/not_assessed) | não |
| ai-act-check, aigov, ArkForge, AIR Blackbox, EU Act Guard | sim (deps/AST/GitHub) | não | só UE | não | não | não | não | AIR: sim |
| lgpd-audit (skill), lgpd-app/skills | skill: sim; app: n/i | não | não | só LGPD | não | não | lgpd-audit lista o que o código não prova | n/i |
| Privado, Bearer | sim (fluxo de dados) | não | GDPR/CCPA citados | não | não | não | não | não |
| Ansvar EU MCP | não | não | só UE (323 regras de aplicabilidade) | não | não | EUR-Lex sem LLM | n/a | sim |
| regulations.ai | não | não | catálogo mundial (118 jurisdições) | Brasil sim | não confirmado | fonte oficial e data por registro | n/a | sim (remoto) |

Limites da conclusão: 24 buscas e cerca de 100 tentativas de leitura de página (parte bloqueada, ver seção 7). Plataformas comerciais fechadas (OneTrust, Securiti, TrustArc, Credo AI, Holistic AI plataforma) e o mercado privado brasileiro (ex.: Privacy Tools) só apareceram em buscas e não foram avaliados. "Não encontrado" não prova inexistência.

## 3. O que incorporar, campo a campo

| Campo/parte da LexZenit | Adotar | Origem | Esforço |
|---|---|---|---|
| `norma.id` | URN LEX (`urn:lex:br:federal:lei:2018-08-14;13709`, confirmado no LexML) | LexML | baixo |
| `norma.status` / `vigencia` | Norma estável (Work) + lista de redações datadas (Expression); consulta `data_referencia`; números (limiares, prazos, multas) em parâmetros datados com fonte | Akoma Ntoso, OpenFisca, legalize-kr | médio |
| `fonte.verificacao` | Manter oficial/secundária/não localizada; somar `last_checked`, `next_check_due`, `bindingness` e alerta de frescor | Vorp Labs (CC BY 4.0), regulations.ai | baixo |
| `obrigacao.natureza` | Vocabulário deôntico (obrigação, proibição, permissão, direito) e norma constitutiva vs prescritiva; `sanção` ligada à violação | LegalRuleML | baixo |
| Precedência (EC 115 vs lei estadual, lex specialis) | `prevalece_sobre` / `cede_a` explícitos (lógica default) | Catala | médio |
| Gatilho trivalente | Manter. Explicar o porquê do estado (árvore de premissas) | Blawx (conceito) | baixo |
| Respostas do questionário | `{valor, declarado_por, via_pergunta, em}`; hash encadeado do relatório | Regula, EuConform | baixo |
| Questionário de IA | Escopo e papel primeiro; exceções; depois art. 5, art. 6/Anexo III, art. 50, GPAI; saída por papel | FLI Checker | médio |
| Sinais automáticos | Aceitar `privado.json`, SARIF e inventário de IA (aigov) como entrada opcional | Privado, Bearer, aigov | médio |
| Evidências técnicas | Ids OWASP LLM01-10 e MITRE ATLAS; testes (giskard-scan, COMPL-AI) como "evidência esperada" | OWASP, ATLAS, Giskard | baixo |
| Resultado | OSCAL assessment-results + POA&M; SARIF; SoA para "não aplicável" | OSCAL, Probo | médio |
| Crosswalk | Obrigação -> controle com relação tipada; exportar biblioteca CISO Assistant; citar IDs do PPSI | OLIR, CISO Assistant, PPSI | médio |
| Vocabulário de sinais | Mapear a conceitos DPV (IRIs); propor extensão LEGAL-BR (lacuna confirmada) | W3C DPV | médio-alto |
| Radar de PLs | Câmara (arquivos anuais + API), Senado (a verificar), LexML; cruzar com regulations.ai e Vorp | Câmara, LexML | médio |
| Qualidade do catálogo | Usar a lista de ~250 leis do SCF só como checklist de cobertura | SCF | baixo |

## 4. Riscos de licença e complexidade

- **AGPL-3.0**: CISO Assistant, Comp AI, OpenFisca Core. Inspirar-se no desenho; não copiar nem embutir. Gerar arquivo próprio no formato de importação (sem código nem conteúdo deles) tende a não contaminar o nosso catálogo, mas confirmar com a assessoria jurídica e validar o esquema antes.
- **CC BY-ND (SCF 4.0, PPSI 3.0)**: não redistribuir versão modificada; o SCF ainda proíbe derivados feitos por IA e exige licença comercial para produto baseado nele. Citar IDs tende a ser seguro; copiar texto não.
- **GPL/LGPL (LexML, Privado)** e **Elastic License 2.0 (Bearer)**: só consumir saída por processo externo; Bearer não pode virar parte de oferta gerenciada.
- **Sem licença declarada** (FLI Checker, OECD.AI, IAPP, PrivacyLawMap, regulations.ai, ATLAS, OWASP AI Exchange): usar estrutura e links; não ingerir texto.
- **Complexidade**: OSCAL exige extensão própria para dispositivo, sanção e vigência; DPV e LegalRuleML são ontologias pesadas (adotar vocabulário, não formato); Catala, Blawx e s(CASP) não valem como motor.

## 5. Inventário por grupo

### OSCAL e compliance-as-code

| Projeto | Licença | Situação | BR/LGPD | UFs | Sobreposição | Fonte lida |
|---|---|---|---|---|---|---|
| [NIST OSCAL](https://github.com/usnistgov/OSCAL) | CC0 | ativo; v1.2.3 (07/08) | não aplicável | não aplicável | média | sim |
| [compliance-trestle](https://github.com/oscal-compass/compliance-trestle) | Apache-2.0 | ativo; v5.0.0 (07/08/2026); CNCF sandbox | não aplicável | não aplicável | baixa | sim |
| [oscal-cli](https://github.com/metaschema-framework/oscal-cli) | CC0 / domínio público | ativo; v3.2.0 (15/05) | não aplicável | não aplicável | baixa | sim |
| [compliance-to-policy](https://github.com/oscal-compass/compliance-to-policy) | Apache-2.0 | ativo; CNCF sandbox; OPA só no roadmap | não aplicável | não aplicável | baixa | sim |
| [Lula](https://github.com/defenseunicorns/lula) | Apache-2.0 | inicial; 'breaking changes' | não aplicável | não aplicável | baixa | parcial |
| [NIST OLIR](https://csrc.nist.gov/projects/olir) | n/i | ativo; mapeamentos de IA | não aplicável | não aplicável | média | parcial |
| [Control Catalog](https://info.standards.tech.gov.sg/control-catalog) | n/i | publicado | não aplicável | não aplicável | média | parcial |
| [Venturalitica SDK](https://github.com/Venturalitica/venturalitica-sdk) | Apache-2.0 | incerto; 6 estrelas | não informado | não informado | média | parcial |
| [ComplianceAsCode/content](https://github.com/ComplianceAsCode/content) | BSD-3-Clause | ativo; v0.1.82 (01/09) | não aplicável | não aplicável | baixa | sim |
| [OpenControl](https://github.com/opencontrol) | n/c | quase parado (2019-2023; masonry fev/2026) | não aplicável | não aplicável | baixa | parcial |
| [Open Policy Agent](https://github.com/open-policy-agent/opa) | Apache-2.0 | ativo; CNCF graduado | não aplicável | não aplicável | baixa | parcial |
| [Conftest](https://github.com/open-policy-agent/conftest) | n/c | ativo; 3,3 mil estrelas | não aplicável | não aplicável | baixa | parcial |

### GRC e catálogos de controles

| Projeto | Licença | Situação | BR/LGPD | UFs | Sobreposição | Fonte lida |
|---|---|---|---|---|---|---|
| [CISO Assistant Community](https://github.com/intuitem/ciso-assistant-community) | AGPL-3.0 (+ enterprise comercial) | ativo; v4.0.4 (15/09) | LGPD/Brasil NÃO aparecem no README | não | média | parcial |
| [Comp AI](https://github.com/trycompai/comp) | AGPL-3.0 (+ /ee comercial) | ativo; 1,9 mil estrelas | não aparece | não | baixa | sim |
| [Probo](https://github.com/getprobo/probo) | MIT | ativo; 1,3 mil estrelas | LGPD não mencionada | não | média | parcial |
| [eramba](https://www.eramba.org/) | proprietária (Community grátis, não OSS) | ativo; v3.31.0 | LGPD não mencionada | não | baixa | sim |
| [Secure Controls Framework](https://securecontrolsframework.com/) | CC BY-ND 4.0 (derivados proibidos) | ativo; trimestral | SIM | não | média | sim |
| [PPSI 2.0 - Programa de Privacidade e Segurança da Informação](https://www.gov.br/governodigital/pt-br/privacidade-e-seguranca/ppsi-2.0) | CC BY-ND 3.0 | em vigor desde 01/01/2026 | SIM | não | média | parcial |

### Rules as code e legislação estruturada

| Projeto | Licença | Situação | BR/LGPD | UFs | Sobreposição | Fonte lida |
|---|---|---|---|---|---|---|
| [OpenFisca Core](https://github.com/openfisca/openfisca-core) | AGPL-3.0 | ativo; 5.260 commits | Nenhum pacote para o Brasil encontrado nas fontes lidas | não | média | parcial |
| [Catala](https://github.com/CatalaLang/catala) | Apache-2.0 | pesquisa Inria; compilador 'instável' | não informado | não | baixa-média | sim |
| [Blawx](https://github.com/Lexpedite/blawx) | MIT | alfa; 'educacional e experimental' | não informado | não | baixa | sim |
| [OASIS LegalRuleML Core Specification v1.0](https://docs.oasis-open.org/legalruleml/legalruleml-core-spec/v1.0/legalruleml-core-spec-v1.0.html) | OASIS (RF on Limited Terms) | padrão 30/08/2021 | não aplicável | não aplicável | média | sim |
| [OASIS Akoma Ntoso 1.0](https://docs.oasis-open.org/legaldocml/akn-core/v1.0/akn-core-v1.0-part1-vocabulary.html) | OASIS | padrão 29/08/2018 | não verificado | não aplicável | média | parcial |
| [LexML Brasil](https://www.lexml.gov.br/) | repos GPL-2.0/3.0 | ativo; lexml-eta 13/10/2026 | SIM | Padrão de URN para UFs não verificado | média | parcial |
| [W3C Data Privacy Vocabulary](https://github.com/w3c/dpv) | W3C FSA | v2.3 (25/02/2026) | NÃO | não | média | sim |
| [legalize-kr](https://github.com/legalize-kr/legalize-kr) | MIT só estrutura | ativo (frente A) | não | não | média | sim |
| [RegBR](https://www.repositorio.unb.br/handle/10482/45107?locale=fr) | n/i | artigo 2022 | SIM | não | baixa | parcial |

### Conformidade e segurança de IA (checkers, benchmarks, catálogos)

| Projeto | Licença | Situação | BR/LGPD | UFs | Sobreposição | Fonte lida |
|---|---|---|---|---|---|---|
| [EU AI Act Compliance Checker](https://artificialintelligenceact.eu/assessment/eu-ai-act-compliance-checker/) | n/i (fechado) | ativo; changelog 03/07/2025 | não | não | média | sim |
| [COMPL-AI](https://github.com/compl-ai/compl-ai) | Apache-2.0 | ativo; v2 em construção | não | não | baixa | sim |
| [AI Verify](https://github.com/aiverify-foundation/aiverify) | Apache-2.0 | ativo; v2.0 'upcoming' | não | não | baixa | sim |
| [Credo AI Lens](https://github.com/credo-ai/credoai_lens) | Apache-2.0 | ARQUIVADO 12/07/2024 | não | não | baixa | sim |
| [Giskard](https://github.com/Giskard-AI/giskard-oss) | Apache-2.0 | ativo; v3 | não | não | baixa | sim |
| [NIST Dioptra](https://github.com/usnistgov/dioptra) | CC BY 4.0 | ativo; v1.1.0 | não | não | baixa | sim |
| [Holistic AI](https://github.com/holistic-ai/holisticai) | Apache-2.0 | público; 113 estrelas | não | não | baixa | sim |
| [MITRE ATLAS](https://github.com/mitre-atlas/atlas-data) | n/c (Public Release) | ativo; conteúdo 2026.05 | não | não | baixa | parcial |
| [OWASP AI Exchange](https://github.com/OWASP/www-project-ai-security-and-privacy-guide) | n/c | ativo; Flagship | não | não | baixa | parcial |
| [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/) | CC BY-SA 4.0 | edição 2025 | tradução em português disponível | não | baixa | sim |

### Scanners de repositório e concorrentes parciais

| Projeto | Licença | Situação | BR/LGPD | UFs | Sobreposição | Fonte lida |
|---|---|---|---|---|---|---|
| [Regula](https://github.com/kuzivaai/getregula) | Apache-2.0 OU EUPL-1.2 (PyPI diz MIT) | 4 estrelas; 20 commits | só referência opcional (sem decisão) | NÃO | ALTA parcial | parcial |
| [EuConform](https://github.com/hiepler/euconform) | MIT + EUPL-1.2 | público; 125 estrelas | não | não | média | sim |
| [EU AI Act Compliance Kit](https://github.com/ogulcanaydogan/eu-ai-act-compliance-kit) | Apache-2.0 | mantido; 0 estrelas | não | não | média | sim |
| [ai-act-check](https://github.com/svel26/ai-act-check) | Apache-2.0 | protótipo; 0.3.1 (03/12/2025) | não | não | baixa-média | parcial |
| [aigov](https://pypi.org/project/aigov/) | Apache-2.0 | alfa; 0.5.2 (28/04/2026) | LGPD não mencionada | não | média-baixa | parcial |
| [EU Act Guard](https://hunted.space/product/eu-act-guard) | n/i | early access | não | não | média | parcial |
| [ArkForge EU AI Act API / MCP](https://arkforge.tech/en/eu-ai-act-api.html) | n/i (comercial) | ativo; freemium | não | não | média-baixa | parcial |
| [AIR Blackbox MCP Server](https://mcpservers.org/servers/airblackbox/air-blackbox-mcp) | n/i | PyPI | não | não | média | parcial |
| [lgpd-app/skills](https://github.com/lgpd-app/skills) | Apache-2.0 | 5 commits; 2 estrelas | SIM | NÃO | média na parte LGPD; nenhuma em multi-jurisdição | parcial |
| [Skill lgpd-audit](https://claudskills.com/skills/lgpd-audit/SKILL.md) | n/i | origem desconhecida | SIM | NÃO | média na parte LGPD-código | parcial |
| [Complyr](https://www.tabnews.com.br/marivaaldo/pitch-complyr-lgpd-sem-dor-de-cabeca-mvp-aberto-e-gratuito) | n/i | MVP 23/10/2025 | SIM | NÃO | baixa | parcial |
| [Privado](https://github.com/Privado-Inc/privado) | LGPL-3.0 / GPL-3.0 | v1.3.91 (10/11/2025) | LGPD não mencionada | não | média | sim |
| [Bearer CLI](https://github.com/Bearer/bearer) | Elastic License 2.0 | ativo; 2,7 mil estrelas | não | não | baixa-média | sim |
| [Fides](https://github.com/ethyca/fides) | Apache-2.0; fideslang CC BY 4.0 | ativo | LGPD não mencionada | não | baixa-média | parcial |

### Catálogos jurídicos via MCP e rastreadores de regulação

| Projeto | Licença | Situação | BR/LGPD | UFs | Sobreposição | Fonte lida |
|---|---|---|---|---|---|---|
| [Ansvar EU Regulations MCP](https://github.com/Ansvar-Systems/EU_compliance_MCP) | Apache-2.0 | 1.1.2 (17/02/2026); repo arquivado | NÃO | NÃO | média | parcial |
| [regulations.ai](https://regulations.ai/) | sem licença formal (atribuição) | ativo; verificado 16/10/2026 | SIM | não confirmado | média | sim |
| [Vorp Labs - AI regulatory updates tracker](https://vorplabs.com/ai-regulatory-updates) | CC BY 4.0 | ativo; 10/10/2026 | Brasil NÃO confirmado | não confirmado | média | sim |
| [Digital Policy Alert](https://digitalpolicyalert.org/) | CC BY-NC 4.0 / licença paga | ativo | Brasil não citado na página | não | baixa-média | parcial |
| [OECD.AI Policy Navigator](https://oecd.ai/en/dashboards/overview) | all rights reserved | ativo | O Brasil não apareceu na página de visão geral | não | baixa | parcial |
| [IAPP US State Privacy Legislation Tracker](https://www.iapp.org/resources/article/us-state-privacy-legislation-tracker/) | n/i (membros) | atualizado 08/09/2026 | não | não | baixa | parcial |
| [PrivacyLawMap](https://privacylawmap.com/) | all rights reserved | dados 12/10/2026 | não | não | média no desenho do gatilho de aplicabilidade | parcial |
| [Dados Abertos da Câmara dos Deputados](https://dadosabertos.camara.leg.br/) | n/i | ativo; diário | SIM | não | alta para o radar de PLs federais | parcial |
| [Dados Abertos do Senado Federal](https://legis.senado.leg.br/dadosabertos/docs/index.html) | não verificado | não verificado | não verificado | não verificado | alta para o radar | não |
| [LegisWeb](https://www.legisweb.com.br/) | comercial | ativo | Tributário | SIM para legislação tributária estadual | baixa | parcial |

Legenda: n/i = não informado na fonte lida; n/c = não confirmado; "Fonte lida" = sim (página primária lida), parcial (faltam campos), não (não lido). A coluna Sobreposição resume a avaliação (alta/média/baixa).

## 6. Premissas do briefing que a fonte não confirmou ou corrigiu

- CISO Assistant: EU AI Act e GDPR constam; LGPD/Brasil não aparecem no README. A listagem completa das bibliotecas não pôde ser lida.
- compliance-to-policy (C2P): OPA/Gatekeeper não é suportado hoje (só Kyverno, OCM e Auditree; OPA no roadmap).
- Lula: o README lido não menciona Rego, Kyverno nem component-definition.
- NIST Dioptra: não é testbed só de segurança de ML (é avaliação de confiabilidade; apoia a função Measure do AI RMF).
- Credo AI Lens: arquivado em 12/07/2024.
- eramba: a própria empresa diz que a Community não é open source.
- OpenFisca: não achei pacote para o Brasil; o formato YAML dos parâmetros com datas não apareceu nas páginas lidas.
- Catala: as releases lidas citam backends Java e Python.
- W3C DPV: não há extensão para o Brasil.
- OSCAL: não confirmei os valores de `objective-status` nem como representar "inconclusivo" (páginas de referência bloqueadas).
- Regula: o resumo do PyPI/Socket afirma LGPD e Marco Legal da IA; o README no GitHub diz que `brazil` só é referência opcional. Fontes em conflito; prevalece o GitHub.

## 7. Não verificado e bloqueios

- Páginas bloqueadas por permissão (PROVENANCE_REQUIRED): `pages.nist.gov/OSCAL-Reference/.../json-outline` e `json-reference`; `legis.senado.leg.br/dadosabertos/docs/index.html`; `securecontrolsframework.com/start-here/set-theory-relationship-mapping-strm`.
- Bloqueadas por robots ou erro: listagens de `ciso-assistant-community/.../libraries`, `github.com/kuzivaai/getregula/tree/main/data`, api.github.com e jsdelivr.
- API autenticada do GitHub indisponível (token inválido; não anexei repositórios). Releases e licenças vieram das páginas públicas; onde a página não mostrava, está "não visível".
- Anos de várias releases não aparecem nas páginas (ex.: CISO Assistant 15/09; ComplianceAsCode 01/09; oscal-cli 15/05).
- Não verificados: formato de URN LEX para UFs; API/SRU do LexML; esquema das bibliotecas do CISO Assistant; STRM/OLIR (tipos de relação); licença do ATLAS e do OWASP AI Exchange; termos de reuso do regulations.ai.
- Nada foi instalado, clonado ou executado; nenhum código de terceiros foi copiado.

## 8. Método

WebFetch em GitHub e sites oficiais (README, releases, LICENSE quando acessível) (cerca de 100 tentativas, algumas bloqueadas) e 24 WebSearch para descoberta. Cada entrada do JSON traz `verificado_em_fonte`, `url_fonte_lida` e `nao_verificado`. A entrada legalize-kr vem da frente A (`repos.md`).
