# Auditoria de repositórios de referência (revisor jurídico LexZenit)

Data: 2026-10-16. Método: `git clone --depth 1`, leitura de arquivos e WebFetch de páginas oficiais. Nenhum script dos repositórios foi executado. Detalhes, trechos e caminhos em `repos.json`. Não é parecer jurídico.

## Quadro geral

| # | Repo | Último commit (HEAD) | Licença | Conteúdo real | Uso pela LexZenit |
|---|------|---------------------|---------|---------------|-------------------|
| 1 | georgelinde887-sudo/nda-template-generator | 2026-10-16 (commit único) | MIT (SendNow) | JS + HTML, 1 template de NDA | Só ideia de arquitetura; texto não |
| 2 | ankane/awesome-legal | 2026-07-04 | CC0-1.0 (só a lista) | 3 arquivos, apenas links | Mapa de documentos; checar licença de cada link |
| 3 | Ro5s/Startup-Starter-Pack | 2020-09-30 | MIT (não cobre terceiros) | 13 modelos .md + links | Roteiro conceitual; desatualizado |
| 4 | General-Legal/legal-templates | 2026-09-22 | CC0-1.0 | 12 modelos .md/.docx | Copiável/adaptável, mas direito dos EUA |
| 5 | General-Legal/general-legal-mcp | 2026-10-14 | nenhuma | manifestos + 2 skills, sem código | Só referência de desenho de tools |
| 6 | legalize-kr/legalize-kr | 2026-10-16 (data sintética) | MIT só no README | 5.770 leis coreanas em .md | Arquitetura sim; texto não |
| 7 | legalize-kr/admrule-kr | 2026-10-11 (data sintética) | MIT só no README | 22.647 normas administrativas | Idem |
| 8 | ethicalml/awesome-artificial-intelligence-regulation | 2026-10-13 | MIT | 140 links, 47 de regulação | Insumo do catálogo global |

Todos os 8 existem com os nomes exatos informados. API do GitHub bloqueada (403): estrelas, "arquivado" e linguagem oficial do GitHub = não verificado; tamanho e linguagem foram medidos nos clones.

## O que vale ouro em cada um

1. **nda-template-generator.** Pouco. Motor de template puro (7 cláusulas) com testes de unidade. Defeitos: a "jurisdição" só troca uma string; modo unilateral mantém corpo mútuo ("to each other"); "Party A/B" vs "Disclosing/Receiving Party" não definidos. Repo criado hoje, titularidade inconsistente (conta pessoal, copyright SendNow, CI apontando para `sendnow-ecosystem`), `REPO_METADATA.json` com `sendnow_anchor_text`: veículo de backlinks.
2. **awesome-legal.** Taxonomia de documentos para startups. Nada além de links. A CC0 não se estende aos documentos apontados.
3. **Startup-Starter-Pack.** Roteiro de 8 fases; Series Seed da Cooley em .md (fonte original CC0, melhor usar a atualizada). `.DOC` e `.PDF` vazios. "LLC Package (Delaware)" aponta para template de Nova York.
4. **legal-templates.** O mais reaproveitável juridicamente: CC0 "sem atribuição" (rodapé de crédito é pedido, não obrigação). Pipeline: `fetch_templates.py` (raspa general.legal) e `convert_docx.py` (python-docx, `<mark>` nos campos). NDAs com lei de Delaware; offer letter da Califórnia; BAA/HIPAA. Adaptar ao Brasil (LGPD, CDC, Código Civil), não copiar às cegas.
5. **general-legal-mcp.** É plugin de cliente para servidores remotos fechados. Tools: `start_deal`, `upload_document`, `confirm_upload`, `list_deals`, `list_contracts`, `list_thread_messages`, `reply_to_thread`, `download_contract` (+6 de cadastro/recuperação no endpoint de agentes). SDK do servidor: não verificado. Sem licença: não copiar. Padrões úteis: upload por link com idempotência, disclaimers antes do pagamento, revisão IA + advogado humano.
6. **legalize-kr.** Arquitetura: lei = arquivo, revisão = commit com data de promulgação, frontmatter (`법령MST`, `공포일자`, `시행일자`, `상태`), mensagem padronizada com links. Cadeia: `legalize-pipeline` (Python, OpenAPI oficial, Actions diário) -> `compiler` (Rust, repo Git bare) -> dados. `cli-tools`: servidor MCP local, SDK Python `mcp>=2.2,<3`, 11 tools somente leitura (`laws_get`, `laws_article`, `laws_diff`, `search` etc.), consulta por data. Código em MIT OR Apache-2.0; repo de dados sem LICENSE e com aviso de force-push.
7. **admrule-kr.** Mesma cadeia para atos infralegais, organizados por órgão; HEAD só com "vigentes" (`현행여부: Y`); 708 documentos só com anexo. Útil como modelo para normas de reguladores brasileiros (ANPD, BCB, CVM).
8. **ethicalml.** 47 entradas de regulação em 15 jurisdições; 1 do Brasil (PL 2338/2023), sem LGPD. Erros: Taiwan sob China, link "Legal Text" do GDPR.EU aponta para o Privacy Act dos EUA, CCPA aponta para bill de 2017-2018, Privacy Shield provavelmente obsoleto, várias entradas são autopromoção comercial. Catálogo extraído: 125 entradas (7 cursos e 8 newsletters excluídos) em `repos.json` > `catalogo_global`.

## Licenças dos itens do awesome-legal (amostragem)

| Item | Licença / termos | Verificado |
|------|------------------|-----------|
| Series Seed e fork Cooley (GitHub) | CC0-1.0 | sim (README local) |
| GitHub Balanced Employee IP; GitHub site-policy | CC0-1.0 | sim (clone) |
| Common Paper (CSA v2.1) | CC BY 4.0 | sim (página); NDA mútuo bloqueado, inferido |
| Basecamp policies | CC BY 4.0 | sim (clone) |
| Bloomberg Beta | CC BY 3.0 | sim (clone) |
| Automattic legalmattic; Medium policy | CC BY-SA 4.0 (copyleft) | sim (clone) |
| **Cooley GO (formulários)** | Proprietária: uso interno, sem copiar/modificar/redistribuir; **proíbe uso para treinar ou melhorar IA/ML/LLM** (ToU 9/20/24, seção 5) | sim (página) |
| **Orrick** | All rights reserved; uso pessoal, único, não comercial; sem obras derivadas (ToU jul/2018) | sim (página) |
| Founder Institute FAST | "free and can be modified" (FAQ), sem licença formal; copyright FI; ToU bloqueado | parcial |
| YC SAFE | Sem aviso de licença na página; .docx bloqueado | não verificado |
| NVCA | página bloqueada | não verificado |

## Afirmações de terceiros

- **a) parcial.** Não há modelos no repo, só links. Confirmados como links: Common Paper CSA, NDA mútuo (Cooley, Common Paper), Series Seed. "IP assignment": só como "Employee IP agreements" (inclui Invention Assignment). "SAFE post-money": README diz só "SAFE"; a YC oferece apenas post-money.
- **b) parcial.** 8 fases confirmadas na mesma ordem; pacotes Delaware (LLC e Corp.) confirmados (link do LLC é de NY). **Vesting com cliff: não confirmado** (zero ocorrências de "cliff"). Markdown só em 13 arquivos.
- **c) parcial.** Só o CC0 é confirmado (legal-templates). **Servidor MCP Python/Flask com RAG, prompts de validação e taxonomia de risco: não confirmado**; `general-legal-mcp` não tem código nem licença. O único Flask da organização é `findthefuckup-open` (chama a API Anthropic, severidade high/medium/low, não é MCP, sem RAG, MIT só no README).
- **d) parcial.** Git + Markdown confirmados. JSON não existe no repo de dados. Vigência: `상태`/`시행일자` no frontmatter, mas commit = promulgação, e todos os 5.770 arquivos do HEAD estão "시행"; em 2 commits "(폐지)" inspecionados o arquivo permaneceu (como revogação definitiva é representada: não verificado). Testes são do pipeline/compilador, não do texto legal.

## Limitações

WebSearch indisponível (orçamento esgotado). Bloqueadas e não repetidas: Common Paper Mutual NDA, `fi.co/terms`, NVCA, docx do YC SAFE e art. 7 da Lei de Direitos Autorais coreana (o argumento de "obra pública" é só do README). Links do catálogo não foram checados; status legislativos de 2026 não foram confirmados em fontes oficiais.
