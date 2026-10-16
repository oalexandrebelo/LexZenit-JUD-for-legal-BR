# Projetos semelhantes à parte scanner/evidência da LexZenit (frente A)

Data: 16/10/2026. Detalhe de cada projeto, com URLs lidas e o que não foi verificado: `similares-scanners.json` (37 entradas).
Método: WebFetch de páginas do GitHub, PyPI, Packagist, Hugging Face e documentação oficial; commits e releases pela API do GitHub lida via WebFetch. 20 buscas WebSearch. Nada foi baixado, instalado ou executado. Não é parecer jurídico.

Convenções: "sem aviso" = a página lida não mostrava banner de arquivamento. Data de commit = commit mais recente do branch padrão em 16/10/2026. "n/d" = não exibido na fonte. Estrelas vêm do HTML e podem estar arredondadas.

## Conclusão em quatro linhas

1. Nenhum projeto verificado faz o conjunto LexZenit (sinais de privacidade + evidências documentais + cruzamento com catálogo normativo BR/país/mundo). Os mais próximos tecnicamente são GDPRLint (PII por linha, SARIF, baseline) e aibom-scanner (IA, só stdlib, SARIF, códigos de saída).
2. Os scanners de privacidade "grandes" (Privado, Bearer, HoundDog) são úteis como inspiração, mas as licenças (LGPL/GPL, ELv2, proprietária) impedem copiar regras ou listas.
3. Os "scanners de LGPD" brasileiros no GitHub são minúsculos (0 a 2 estrelas, 3 a 56 commits) ou são skills de agente sem detector determinístico (goul4rt/lgpd-skills, lgpd-app/skills). Só privacy-shield-br (PHP, 1 estrela) documenta validação de dígito verificador; os validadores mais usados são bibliotecas à parte (MIT).
4. Achado técnico: o CNPJ alfanumérico já circula desde julho/2026 (título de notícia da Receita nos resultados de busca; página não lida, exigiu login). Algoritmo do DV confirmado no PDF do Serpro. Regex só numérico perde dado.

## Tabela

| # | Projeto | Licença | Situação (16/10/2026) | Saída | Veredito |
|---|---------|---------|-----------------------|-------|----------|
| 1 | Privado (Privado-Inc/privado + privado-core) | LGPL-3.0 / GPL-3.0 (páginas) | commit 14/10/2026; release v1.3.91 (10/11/2025); 651 estrelas | JSON `.privado/privado.json` (sources, processing, dataFlow, collections, violations); RoPA só na nuvem | inspirar (IDs `Data.Sensitive.*`, 3 níveis); não copiar |
| 2 | Bearer CLI | Elastic License 2.0 (LICENSE lido) | commit 12/10/2026; v2.1.1 (24/08/2026); 2,7 mil | json, yaml, sarif, gitlab-sast, rdjson, html; relatório privacy em CSV | inspirar (SARIF, "recipes", titulares); não embutir |
| 3 | HoundDog.ai | Proprietária (Termos de Serviço; binário) | commit 10/10/2026 (repo só distribui); 124 | console, markdown; RoPA/PIA só Enterprise | inspirar (3 níveis de sensibilidade, sinks) |
| 4 | Ethyca Fides | Apache-2.0 | último commit 01/06/2026; v2.86.2 (01/06); 478 | n/d | não (plataforma pesada) |
| 5 | fideslang (IABTechLab) | CC-BY-4.0 | último commit 14/05/2025 (congelado); 95 | taxonomia | adotar como vocabulário (snapshot) |
| 6 | Presidio (agora data-privacy-stack) | MIT (LICENSE lido) | commit 08/10/2026; 11,2 mil; mudou de casa | objetos Python | copiar o modelo de reconhecedor; sem Brasil |
| 7 | Semgrep + semgrep-rules | engine LGPL-2.1; regras: Semgrep Rules License v1.0 | commit 15/10/2026 | SARIF/JSON (não confirmado nas páginas lidas) | não adotar (regras não redistribuíveis) |
| 8 | Tang et al. (artigo, método) | arXiv | 2023 | 10 categorias de dado, 6 classes de sink | adotar o esquema conceitual |
| 9 | GDPRLint | Apache-2.0 | commit 08/10/2026; 0.4.0; 1 estrela | texto, JSON `gdprlint/report/v1`, SARIF 2.1.0, catálogo de regras | adotar ideias (esquema, baseline, `--fail-on`) |
| 10 | Gitleaks | MIT | "feature complete"; 29,9 mil | json, csv, junit, sarif | copiar o conceito de regra (keywords, allowlist, composta) |
| 11 | ScanCode Toolkit | Apache-2.0 (+CC-BY-4.0 dados) | commit 16/10/2026; v32.5.0 Latest | JSON, YAML, HTML, CycloneDX, SPDX | aceitar JSON como entrada opcional |
| 12 | FOSSology | GPL-2.0 | commit 16/10/2026; 4.7.1 (11/06/2026) | SPDX, ReadMe | não (servidor PHP+PostgreSQL) |
| 13 | REUSE (reuse-tool) | GPL-3.0-or-later (código) | commit 13/10/2026 (espelho; dev no Codeberg); spec 3.3 | texto, `--json`, SPDX | adotar a especificação como evidência de licença |
| 14 | ORT | Apache-2.0 | release 94.2.0 (24/09); 2,1 mil | SPDX, CycloneDX, notices | só o conceito de classificação de licenças |
| 15 | Syft | Apache-2.0 | commit 16/10/2026; v1.51.1 (27/08/2026); 9,7 mil | CycloneDX, SPDX, Syft JSON | aceitar a saída como evidência de SBOM |
| 16 | CycloneDX (spec 1.7 + cdxgen) | Apache-2.0 | commit 12/10/2026; ECMA-424 | JSON/XML/protobuf | emitir CycloneDX mínimo; não usar cdxgen |
| 17 | SPDX (3.x model + license-list-data) | licença dos dados não confirmada | lista 3.29.0 em 16/09/2026 | JSON-LD etc. | normalizar ids SPDX |
| 18 | licensee | MIT | commit 15/10/2026; v10.1.0 (07/08/2026); 914 | n/d | reimplementar o algoritmo (normalização + Dice) |
| 19 | Trivy | Apache-2.0 | leitura parcial | não verificado | n/a |
| 20 | goul4rt/lgpd-skills | MIT | commit 31/05/2026; 47 estrelas (74 na listagem do tópico) | Markdown em `.lgpd/` | usar os 18 domínios como checklist de evidências |
| 21 | lgpd-app/skills | Apache-2.0 | 2 estrelas; 5 commits | relatório com nota; `lgpd.md` | detectar `lgpd.md` |
| 22 | mukul975/Privacy-Data-Protection-Skills | Apache-2.0 | 274 estrelas (307 na listagem) | Markdown/YAML/scripts | referência de empacotamento |
| 23 | lvmorales1/privacy-scanner (PHP) | MIT | v0.2.0 (20/06/2026); 0 estrelas | JSON; exit 0/1; nota 0-100 | ideia de `fail_on_score` |
| 24 | Richardmsbr/privacy-shield-br (PHP) | MIT | 3 commits; 1 estrela | contagens, máscara | ideia: PIX como padrão |
| 25 | negraodenio/code-guard-ai | MIT | 56 commits; 1 estrela; camada comercial | lista de violações | não (lição negativa: CPF só por formato) |
| 26 | LordMendes/lgpd-mcp | MIT | 9 commits; 1 estrela | MCP (9 tools) | comparar com o nosso MCP |
| 27 | pydantic-brasil | MIT | 11 estrelas | 22 tipos de documento | lista de cobertura |
| 28 | brutils | MIT | commit 09/10/2026; 525 | funções | vetores de teste |
| 29 | validate-docbr | MIT | commit 01/10/2026; 484 | funções | vetores de teste |
| 30 | hyrule-shield / OpenMed PII-PT | MIT / Apache-2.0 | beta; modelo 66M | entidades | não (pesado) |
| 31 | aibom-scanner (saasvista) | Apache-2.0 | 1.3.0 e commit em 13/10/2026 | table, json, sarif; exit 0/1/2/3 | adotar ideias (cobertura, SDKs de IA, MCP) |
| 32 | Trusera ai-bom | Apache-2.0 | 3.6.0 (15/03/2026); commit 13/04/2026 | CycloneDX 1.6, SARIF, SPDX 3.0 etc. | exportar ML-BOM; telemetria no SDK |
| 33 | ai-act-check | AGPL-3.0 | 2.0.1 (17/01/2026) | JSON + rascunho | não (AGPL, protótipo) |
| 34 | W3C DPV | W3C Document License | commit 06/08/2026; v2.3 | RDF, JSON-LD, Turtle | campo opcional `dpv_iri` |
| 35 | SARIF 2.1.0 (OASIS) | padrão | errata aprovada 28/08/2023 | n/a | emitir |
| 36 | Tracker Radar / Blacklight | CC BY-NC-SA 4.0 (dados) / GPL-3.0 | n/d | JSON/HAR | não |
| 37 | CNPJ alfanumérico (Serpro) | norma técnica | em vigor desde jul/2026 (fonte secundária) | n/a | implementar |

## Top 5 a incorporar (valor/esforço)

1. **Validadores brasileiros com dígito verificador, contexto e score.** Modelo: PatternRecognizer do Presidio (regex + validador + palavras de contexto + score), reescrito em stdlib. Cobrir CPF, CNPJ (incluindo alfanumérico: valor = ASCII - 48, pesos 2 a 9 da direita para a esquerda, módulo 11, DV 0 se resto 0 ou 1, senão 11 - resto, 2º DV sobre 13 caracteres), CNS, PIS/NIS, título de eleitor, CNH, RENAVAM, placa (Mercosul), CEP, chave PIX. Lista de cobertura: pydantic-brasil (22 tipos); vetores de teste: brutils e validate-docbr (MIT; usar só nos testes). Rejeitar sequências repetidas. Esforço baixo; maior ganho em precisão.
2. **SARIF 2.1.0 + esquema JSON versionado + catálogo de regras exportável + baseline + `--fail-on`.** Modelos: GDPRLint, aibom-scanner, Bearer. Um `reportingDescriptor` por sinal, `physicalLocation` = caminho:linha. Esforço baixo a médio. Limites do upload no GitHub code scanning: não verificado (página bloqueada).
3. **Campos de taxonomia no catálogo de sinais.** `fideslang` (CC-BY-4.0: user.health_and_medical, user.biometric, user.government_id, user.payment, user.childrens; usos analytics, marketing, train_ai_system), 10 categorias e 6 classes de sink do estudo de Tang et al., sensibilidade em 3 níveis (Privado/HoundDog), IRI do DPV opcional. Gera um export "RoPA-lite" (dado, titular, finalidade, destino). Esforço baixo (tabela). Guardar como snapshot versionado, porque o fideslang está parado desde mai/2025.
4. **Evidências de licença e SBOM mais fortes.** REUSE (LICENSES/, REUSE.toml, `.reuse/dep5`, `SPDX-License-Identifier`), identificação do texto da LICENSE à la licensee (normalizar + Dice de bigramas contra ~15 licenças), leitura de `bom.json`, `*.cdx.json`, `*.spdx.json` (Syft/cdxgen) e normalização para ids SPDX com tabela própria de classe de copyleft. Esforço médio.
5. **Robustez e IA.** De aibom-scanner e Gitleaks: relatório de cobertura e exit code 3 quando incompleta, separar "observado" de "inferido", pré-filtro por palavras-chave, regras compostas por proximidade (CPF válido a N linhas de "cliente/paciente"), allowlists. Ampliar o sinal de IA generativa com SDKs, servidores MCP e provedores em jurisdição sensível, e arquivos de modelo (.gguf, .safetensors). Complemento: reconhecer `.lgpd/ROPA.md`, `.lgpd/RIPD/` e `lgpd.md` como evidência. Esforço médio.

## O que NÃO adotar

- **Bearer** (ELv2 source-available: proíbe servir como serviço gerenciado; sem copiar regras). **HoundDog** (binário e termos proprietários). **Privado** (LGPL/GPL, licença das regras não confirmada, núcleo separado e telemetria configurável). Só inspiração.
- **Semgrep Rules** (licença permite uso interno e proíbe distribuir as regras; telemetria padrão com configs do Registry).
- **Presidio como dependência**, **hyrule-shield**, **OpenMed**, **Laya do GDPRLint**: NER/ML quebra "só stdlib"; Presidio nem tem Brasil.
- **FOSSology, ORT, ScanCode, cdxgen, Syft, Trivy como dependência**: pesados ou externos. Aceitar a saída deles como entrada opcional.
- **Tracker Radar** (CC BY-NC-SA 4.0, uso comercial exige licença) e **Blacklight** (GPL-3.0, navegador headless).
- **ai-act-check** (AGPL-3.0), **code-guard-ai** (camada comercial, CPF só por formato, tudo CRITICAL, rótulo GDPR para CPF).

## Divergências e lacunas (não verificado)

- Estrelas divergentes: goul4rt/lgpd-skills 47 (repo) vs 74 (listagem do tópico); mukul975 274 vs 307.
- Privado: README diz Java e Python GA; documentação diz Python alpha.
- Presidio: o repositório e a documentação mudaram para data-privacy-stack; a telemetria não foi verificada.
- Não lidos por bloqueio (permissão não respondida, não repetidos): docs.github.com (limites do SARIF), termos da HoundDog, docs e LicenseDB do ScanCode, releases do reuse-tool no Codeberg, relatório de extensões legais do DPV (existência de extensão BR/LGPD: não confirmada), notícia da Receita (exigiu login).
- API do GitHub `/repos/{x}` falhou: licença e estrelas vêm das páginas; última release de ORT, cdxgen e commit de ORT/Trivy: não lidos.
- Resoluções da ANPD citadas por goul4rt (CD/ANPD 2/2022, 4/2023, 15/2024, 18/2024, 19/2024, 30 e 31/2025) e a Lei 15.211/2025: citadas pelo repositório, não conferidas por mim em fonte oficial.
- Itens vistos só na listagem do tópico `lgpd` e não abertos: PrivioSentry, safe-chat-slack-bot, redact-sensitive, br-gpdpl-php.
- Nenhum dado de eficácia (precisão, recall) foi medido; só o artigo de Tang et al. reporta precisão 0,87 para identificação de fluxos em 4 apps.

## Para memória do projeto

- Presidio não tem reconhecedores brasileiros; CPF/CNPJ têm de ser nossos.
- CNPJ alfanumérico em vigor desde jul/2026 (fonte secundária); algoritmo do Serpro.
- fideslang parado desde mai/2025; Fides sem commits desde 01/06/2026; Gitleaks "feature complete".
- Concorrentes diretos no formato skill: goul4rt/lgpd-skills (18 sub-skills, saída em `.lgpd/`), lgpd-app/skills (`lgpd.md`).
