# Referências e projetos semelhantes · revisor jurídico (0.3.0)

Pesquisa feita em 16/10/2026, antes da publicação, em três frentes:

- scanners de privacidade e licença no código;
- regulação como código e conformidade de IA;
- Brasil, legaltech e servidores MCP jurídicos.

Foram 150 itens avaliados na fonte (página do projeto, LICENSE ou termos de uso). Nada foi instalado ou executado, e nenhum código, texto de modelo ou regra de terceiros foi copiado. O que não pôde ser confirmado na fonte está marcado como não verificado nos registros de pesquisa.

## Concorrente direto

Não foi encontrado. Nenhum produto aberto ou comercial avaliado junta, num só fluxo:

- leitura do repositório e questionário;
- catálogo do Brasil por UF, com alerta de competência constitucional;
- um segundo país escolhido pelo mercado e normas globais;
- estados de três valores com verificação da fonte de cada norma;
- minutas brasileiras.

Plataformas comerciais fechadas e ferramentas internas de escritórios ficaram fora do alcance da pesquisa.

Fatias parciais mais próximas:

| Projeto | O que cobre | Licença | Diferença |
|---|---|---|---|
| [Regula](https://github.com/kuzivaai/getregula) | Código → aplicabilidade de IA na UE, Coreia e Colorado; MCP stdio; "desconhecido nunca vira não" | Apache-2.0 ou EUPL-1.2 | Só IA; Brasil como referência opcional, sem UFs |
| [goul4rt/lgpd-skills](https://github.com/goul4rt/lgpd-skills) | Skills que leem o código e geram ROPA, RIPD, política, DPA | MIT | Só LGPD/ANPD; sem UF, EUA, mundo ou IA; descreve errado as Res. 30 e 31/2025 |
| [GDPRLint](https://github.com/pablorivast/GDPRLint) | Dado pessoal por linha, SARIF, baseline | Apache-2.0 | Só GDPR; sem catálogo normativo |
| [aibom-scanner](https://github.com/saasvista/aibom-scanner) | Inventário de IA, só biblioteca padrão, SARIF, códigos de saída | Apache-2.0 | Sem camada jurídica |
| [ArkForge mcp-eu-ai-act](https://github.com/ark-forge/mcp-eu-ai-act) | Repositório → lacunas do AI Act | MIT | Só UE |
| [EuConform](https://github.com/hiepler/euconform) | Conformidade com o AI Act | MIT e EUPL-1.2 | Só UE |
| [anthropics/claude-for-legal](https://github.com/anthropics/claude-for-legal) | Upstream dos plugins jurídicos | Apache-2.0 | Sem Brasil, LGPD ou ANPD |

## Incorporado nesta versão

| Ideia | Inspiração | Onde |
|---|---|---|
| Radar de projetos de lei pela API aberta da Câmara | Pesquisa Brasil | `python -m lz_revisor radar` (único comando com rede; não altera o catálogo) |
| Respostas que o código contradiz | EU ACT Guard | Seção do relatório e campo `divergencias` |
| Proveniência com hash do catálogo e das respostas | Regula, EuConform | Campo `proveniencia` e linha no relatório |
| URN LEX nas leis federais | [LexML](https://www.lexml.gov.br/) | Campo `urn` em `normas/n1-federal.json` |
| SARIF 2.1.0 e código de saída por severidade | GDPRLint, aibom-scanner, [OASIS SARIF](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html) | `--sarif` e `--falhar-em`; formato `sarif` no MCP |
| Revisão na data dos fatos | OpenFisca, Akoma Ntoso, legalize-kr | `--data AAAA-MM-DD` e parâmetro `data` no MCP |
| CPF e CNPJ, inclusive alfanumérico, por dígito verificador | [Presidio](https://github.com/data-privacy-stack/presidio) (modelo de reconhecedor), [algoritmo do Serpro](https://www.serpro.gov.br/menu/noticias/videos/calculodvcnpjalfanaumerico.pdf) | `lz_revisor/validadores.py`; o valor nunca é guardado |
| Sinais REUSE e SBOM como evidência | [REUSE](https://github.com/fsfe/reuse-tool), [CycloneDX](https://github.com/CycloneDX/specification), [Syft](https://github.com/anchore/syft) | `LICENSES/`, `REUSE.toml`, `SPDX-License-Identifier`, `bom.json`, `*.cdx.json`, `*.spdx.json` |
| Res. CD/ANPD 32/2026 (UE adequada) e lista oficial de resoluções | Lista de regulamentos da ANPD | Notas de `BR-ANPD-REGULAMENTOS` |

## Próximos passos avaliados

- Exportar resultados em [OSCAL](https://github.com/usnistgov/OSCAL) (assessment-results e POA&M), depois de definir como representar "inconclusivo".
- Mapear sinais para a taxonomia [fideslang](https://github.com/IABTechLab/fideslang) (CC BY 4.0) e para o [W3C DPV](https://github.com/w3c/dpv), que ainda não tem extensão para o Brasil.
- Adaptadores de atualização por UF: ALESP (XML), ALEPE (API) e SRU do LexML; API nova do Senado (`/dadosabertos/processo`).
- Baseline de achados aceitos e ampliação dos validadores: CNS, PIS, título de eleitor, CNH, RENAVAM, placa Mercosul e PIX.
- Fluxo "papel primeiro" do [EU AI Act Compliance Checker](https://artificialintelligenceact.eu/assessment/eu-ai-act-compliance-checker/) na skill de classificação de risco.

## Não adotado, e por quê

| Item | Motivo |
|---|---|
| Secure Controls Framework | CC BY-ND 4.0: proíbe derivados, inclusive por IA |
| CISO Assistant, Comp AI, OpenFisca, ai-act-check | AGPL-3.0 |
| Bearer CLI | Elastic License 2.0 |
| HoundDog | Proprietário |
| Privado | LGPL/GPL; só como programa externo |
| semgrep-rules | Licença proíbe redistribuir as regras |
| Presidio, spaCy e modelos de NER | Quebram a regra "só biblioteca padrão"; o Presidio não cobre o Brasil |
| Catala, Blawx, LegalRuleML como motor | Instáveis ou experimentais; LegalRuleML só como vocabulário |
| OECD.AI, IAPP, Digital Policy Alert, Tracker Radar | Direitos reservados ou CC BY-NC |
| Data Privacy Brasil | CC BY-SA: obrigaria a mesma licença |
| Guias da ANPD e da SGD/MGI | Sem derivados (ND); citar, não adaptar |
| iubenda, Cooley GO, Orrick, coleção lawvable | Proíbem cópia, uso comercial ou treino de IA |
| LeXML-mcp, senado-br-mcp, datajud-mcp, court-listener-mcp | GPL-3.0, arquivado, cobertura parcial ou licença não comercial |

Registros completos da pesquisa, com fonte lida, licença e estado de verificação de cada item, estão em [`research/revisor/`](../research/revisor/): `similares-scanners`, `similares-regras`, `similares-brasil` e a auditoria dos repositórios indicados (`repos`).
