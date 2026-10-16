# Similares ao LexZenit: Brasil, legaltech, geradores e MCP jurídicos (frente C)

Data: 16/10/2026. Pesquisa de mercado e de licenças; não é parecer jurídico. Método: 41 buscas na web, dezenas de leituras de página, 8 repositórios clonados só para leitura (`--depth 1`), nada instalado nem executado, nenhum texto de modelo copiado. Marcação: **confirmado** (visto na fonte primária), **parcial** (vitrine, terceiro ou só em parte), **não verificado**. Dados completos em `similares-brasil.json`.

## 1. Há concorrente direto?

**Não.** Não encontrei produto, aberto ou comercial, que reúna os cinco traços do nosso: (1) leitura do repositório do projeto, (2) questionário, (3) catálogo de normas por Brasil/UF com alerta de competência constitucional, (4) camadas N2 (EUA) e N3 (mundo) e (5) pacote de minutas brasileiras (política, termos, NDA, cessão de PI, acordo de fundadores, term sheet, RIPD, avaliação de impacto de IA, DPA, plano de incidentes). Nos itens lidos não encontrei menção a leis estaduais brasileiras nem a competência constitucional (nos repositórios clonados confirmei por grep).

Mais próximos, cada um cobrindo só uma fatia:

| Produto | Cobre | Não cobre |
|---|---|---|
| goul4rt/lgpd-skills (MIT) (D3) | repositório -> inventário de dados -> ROPA, RIPD, política, DPA e runbook de incidente, só LGPD/ANPD/ECA Digital, em português, para Claude Code e outros agentes | UF, EUA, mundo, PL 2338/EU AI Act, avaliação de impacto de IA, minutas societárias e de PI |
| ArkForge mcp-eu-ai-act (MIT, SaaS Pro) (E1) | repositório -> lacunas EU AI Act + GDPR -> modelos (política, DPIA, ROPA, violação, documentação técnica de IA) como servidor MCP | Brasil, UF, questionário, minutas societárias |
| EU ACT Guard (comercial, acesso antecipado) (E3) | repositório + cruzamento de respostas do questionário com o código | qualquer jurisdição fora da UE |
| WeScan (comercial) (E2) | repositório -> nota e achados -> pacote de políticas (GDPR, CCPA, SOC 2) | LGPD e AI Act não confirmados, UF, minutas societárias |
| Confidata (comercial) (B1) | questionário LGPD gratuito de 24 perguntas e plataforma com ROPA, RIPD, LIA | leitura de repositório, UF, EUA, mundo, minutas societárias |
| anthropics/claude-for-legal (Apache-2.0) (D1) | estrutura de plugins (privacy, product, ai-governance) com reg-gap-analysis e launch-review | Brasil (0 ocorrências de Brazil/Brasil/LGPD/ANPD no clone), leitura de repositório, minutas |

- A busca foi limitada (41 consultas) e não vê ferramentas internas de escritórios, produtos em beta fechado nem repositórios privados.
- Os projetos abertos de LGPD em agentes (lgpd-skills, lgpd-mcp, lgpd-app/skills, dpo2u) são novos (2026) e evoluem rápido; reavaliar em 2-3 meses.
- O diferencial real do LexZenit está na combinação (UF + competência constitucional + N2/N3 + minutas), não em qualquer peça isolada.

## 2. Top 5 para incorporar (valor sobre esforço)

**1. Radar de PLs automático pela API de Dados Abertos da Câmara (e Senado /processo)** (valor alto; esforço baixo (dias); fontes F1, F2)

Rotina semanal lê uma lista de proposições-alvo (PL 2338/2023 = id 2487262 na Câmara, mais os PLs do radar), consulta statusProposicao e a coleção 'Atualizações', compara com o valor salvo e gera um diff para revisão humana antes de alterar o catálogo. Começar só com a Câmara; adicionar o Senado após testar o endpoint novo. Pendências: Testar busca por palavra-chave/tema; descobrir limites; confirmar a API nova da Câmara citada no FAQ; ler o endpoint /processo do Senado.

**2. Ramo 'agente de tratamento de pequeno porte' no questionário, alinhado à Res. CD/ANPD 2/2022 e aos guias da ANPD** (valor alto; esforço baixo a médio; fontes A1, A2)

Quatro perguntas (porte/receita, tratamento de alto risco, grupo econômico, enquadramento como startup na LC 182/2021) que ativam ou desativam obrigações no relatório, cada resposta citando a norma. Ligar legítimo interesse a um gatilho de LIA; cookies e encarregado aos guias e à Res. 18/2024. Pendências: Conferir no texto da Res. 2/2022 (já no N1) quais obrigações são flexibilizadas; não li o texto da resolução nesta rodada.

**3. Gate de coerência 'declarado x encontrado' e artefatos vivos versionados** (valor alto; esforço médio; fontes E3, D3, E1)

Depois do questionário, comparar cada resposta com evidências do repositório (dependências de LLM, campos de data de nascimento, SDKs de analytics, transferências para fora do país) e listar divergências no relatório. Gravar tudo numa pasta própria do projeto (STATUS, gaps, minutas versionadas) com aprovação humana antes de cada minuta final. Pendências: Definir lista de sinais de código por tema; reescrever, sem copiar texto dos repositórios.

**4. Auditoria de cobertura do N1 contra a lista oficial de resoluções da ANPD, e conferência de citações** (valor médio a alto; esforço muito baixo (horas); fontes A2, D7, E9, F3, F4)

Script que compara a lista da página de regulamentos da ANPD com o catálogo. Achado imediato: falta a Res. CD/ANPD 32/2026 (UE reconhecida como adequada, 26/01/2026). Acrescentar etapa final que confere que cada artigo/norma citado no relatório existe e está vigente (ideia de 'check_currency/validate_citation' do brazil-law-mcp e 'Analisar Referências' do Jus IA), usando Planalto e LexML. Pendências: Decidir se 23/2024, 30 e 31/2025 (planejamento) entram só no radar.

**5. Campo 'fonte_atualizacao' por UF e adaptadores para as assembleias com dados abertos (SP, PE) + LexML SRU** (valor médio; esforço médio a alto; fontes F3, F5)

Cada UF do catálogo ganha o tipo de fonte (api, xml, manual) e a URL. Primeiros adaptadores: ALESP (arquivos XML de normas e proposituras) e ALEPE (API). As demais ficam em revisão manual trimestral com URN do LexML. O mapa completo vem do estudo SciELO Preprints (2025), cujo PDF ainda precisa ser lido. Pendências: Ler o PDF do estudo; confirmar termos de ALESP/ALEPE; ALMG foi bloqueada por robots.txt.

Outras ideias de menor prioridade:

- Emitir um arquivo 'lgpd.md' (padrão aberto do lgpd-app) como saída extra do relatório (D5). Baixo custo; adoção do padrão desconhecida.
- Term sheet/instrumento de investimento: reconhecer mútuo conversível, MAIS (OAB/RJ) e, se aprovado, o CICC (PLP 252/2023); pedir a licença do MAIS antes de aproveitar texto (B8).
- N3 União Europeia: consultar o endpoint SPARQL Cellar do Publications Office para atos por CELEX (D14).
- Lista de PLs estaduais de IA do dossiê IDMJR (RJ, SP, ES, PR, SC) como ponto de partida do radar estadual (F9).
- Pacote 'para due diligence de cliente ou investidor' (política, RIPD, mapa de fluxo, operadores), no estilo do 'policy pack' do WeScan (E2).
- Ferramentas pequenas e determinísticas dentro do MCP (validar base legal, verificar consentimento) ao estilo do lgpd-mcp (D4).

## 3. Fontes de dados abertos para atualização automática

| Fonte | Uso | Frequência | Autenticação | Termos | Estado |
|---|---|---|---|---|---|
| [API Dados Abertos da Câmara](https://dadosabertos.camara.leg.br/) (F1) | Status e tramitação de PLs (PL 2338/2023 etc.) | semanal; diária em semanas de votação | nenhuma (testado) | livre, sem licença declarada | testado em 16/10/2026 |
| [API Dados Abertos do Senado (endpoint /processo)](https://legis.senado.leg.br/dadosabertos/) (F2) | PLs que tramitam no Senado | semanal | nenhuma aparente | não verificado | endpoint antigo depreciado; novo não lido |
| [LexML Brasil (SRU, URN LEX)](https://www.lexml.gov.br/busca/SRU) (F3) | Conferir existência/URN de normas federais e estaduais | mensal | nenhuma aparente | licença não declarada; texto de lei sem proteção autoral | parcial |
| [Portal da Legislação do Planalto](https://www.planalto.gov.br/ccivil_03/) (F4) | Texto federal compilado e alterações (comparar hash) | mensal | n/a | art. 8º, IV, Lei 9.610/98 | parcial |
| [ANPD - regulamentos](https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/regulamentacoes_anpd) (A2) | Lista-mestra de resoluções para auditar o N1 | mensal | n/a | CC BY-ND 3.0 (citar, não adaptar) | confirmado |
| [ALESP (XML) e ALEPE (API)](https://www.al.sp.gov.br/dados-abertos/) (F5) | Normas e proposições de SP e PE | trimestral para normas; mensal para PLs de IA | não verificado | não verificado | parcial; demais UFs a mapear |
| [Cellar/EUR-Lex (SPARQL)](https://glama.ai/mcp/servers/matematicsolutions/mcp-eu-sparql) (F10) | Atualização de atos da UE no N3 | trimestral | nenhuma (endpoint público do Publications Office, segundo o MCP) | não verificado na fonte oficial | parcial |

## 4. O que NÃO adotar

- **Texto de iubenda, Termly, TermsFeed, Cooley GO e Orrick**: iubenda proíbe reprodução e scraping e limita uso a assinatura ativa; Cooley GO proíbe copiar e usar para treinar IA; Orrick all rights reserved. Termly e TermsFeed: termos não lidos.
- **Skills da coleção lawvable (lgpd-sentinel, privacy-policy, founder-agreement-drafting etc.)**: AGPL-3.0 (copyleft de rede) e a lista é CC BY-NC-ND. Só referenciar.
- **Texto dos guias da ANPD e do guia/modelo de RIPD da SGD/MGI**: CC BY-ND 3.0 e CC BY-NC-ND 4.0 (sem derivados). Citar e linkar; escrever perguntas e minutas próprias.
- **Conteúdo do Data Privacy Brasil**: CC BY-SA 4.0: ingerir texto obrigaria a mesma licença.
- **LeXML-mcp (GPL-3.0) como dependência**: GPL-3.0; chamar o SRU do LexML diretamente.
- **senado-br-mcp e datajud-mcp**: Primeiro arquivado e preso a endpoints depreciados; segundo cobre só o TJMA e tem 'predição' sem metodologia.
- **brazil-law-mcp (Ansvar) como dependência ou fonte de corpus**: Licença do código e do corpus não verificadas; só federal.
- **court-listener-mcp de Travis-Prall**: PolyForm Noncommercial.
- **Conteúdo do GDPRhub via mcp-eu-sparql**: CC BY-NC-SA 4.0.
- **Conteúdo do OECD.AI e do tracker da IAPP**: Todos os direitos reservados; só linkar. O da IAPP está defasado (out/2024).
- **docassemble como base técnica**: Exige servidor Python; excesso para um MCP stdio local. Aproveitar apenas o padrão entrevista x modelo.
- **Selos de 'certificação' de relatório (ArkForge Certified) e notas sem metodologia (predição de julgamento, score 0-100)**: Marketing sem lastro jurídico; nosso relatório deve citar norma e marcar o que não foi verificado.

## 5. Achados incidentais

- Falta no N1 a Res. CD/ANPD 32/2026 (26/01/2026), que reconhece a União Europeia como nível adequado para transferências internacionais (A2). O N1 já tem 15.352/2026.
- O repo goul4rt/lgpd-skills descreve as Res. 30 e 31/2025 como 'agendas regulatória e de fiscalização'; a página da ANPD diz que a 30 é o mapa de temas prioritários 2026-2027 e a 31 altera a agenda regulatória. Não herdar a normativa dele sem conferir.
- O endpoint antigo de matérias do Senado ainda responde, mas a própria resposta o marca como depreciado (18/03/2025) e desativado (01/02/2026); trocar para /dadosabertos/processo (F2).
- Lumiun não é plataforma de LGPD (é segurança de internet). Adequa, Vitreo e Datasafe não foram confirmados como produtos.
- O PL 2338/2023 já está cadastrado na API da Câmara (id 2487262, apresentado ali em 17/03/2025); último status lido: tramitação de 02/09/2026, órgão MESA, 'Aguardando Parecer'.
- O ECA Digital: o lgpd-skills afirma vigência desde 17/03/2026 e a Lei 15.352/2026 altera o início da vigência da Lei 15.211/2025. Conferir a data no nosso N1 (não verificado nesta rodada).

## 6. Inventário (nome, URL, tipo, licença, situação, o que faz, sobreposição, incorporar, riscos)

### Brasil - oficial

#### A1. ANPD - guias orientativos e materiais

- **URL:** https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes
- **Tipo:** oficial
- **Licença e termos (cópia e treino de IA):** Conteúdo do site sob CC BY-ND 3.0 (atribuição, sem derivações), conforme a própria página. Sem menção a treino de IA.
- **Situação:** Ativo. Lista lida em 16/10/2026: Encarregado; Legítimo Interesse; Estudos e pesquisas; Poder Público; Cookies; Definições dos agentes (v2.0/2022 e v1.0/2021); Segurança da informação para agentes de pequeno porte; contexto eleitoral. A página não mostra datas.
- **O que faz:** Orientação não vinculante sobre a LGPD. A página NÃO lista guia de RIPD, de IA ou de transferência internacional, nem checklists, modelos ou formulários (essas matérias estão em resoluções: ver A2). Um artigo de terceiro (Projuris, atualizado 21/09/2026) descreve um checklist ligado ao guia de segurança para pequeno porte; o checklist oficial não foi localizado.
- **Sobreposição (baixa):** Fornece a base normativa do questionário; não é ferramenta.
- **Vale incorporar:** Alinhar o questionário a quatro guias: pequeno porte (ramo 'sou ATPP?'), cookies, legítimo interesse (gatilho para LIA) e encarregado. Citar título e URL no relatório; escrever perguntas e minutas próprias.
- **Riscos:** ND: não republicar nem adaptar o texto dos guias. Datas e versões vigentes não aparecem na página; conferir no PDF antes de citar.
- **Verificação:** confirmado (página); checklist oficial: não verificado. Fonte: WebFetch da página em 16/10/2026; WebSearch + WebFetch Projuris.

#### A2. ANPD - regulamentos (Resoluções CD/ANPD)

- **URL:** https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/regulamentacoes_anpd
- **Tipo:** oficial
- **Licença e termos (cópia e treino de IA):** CC BY-ND 3.0 (declarado na página). Texto de atos oficiais não tem proteção autoral (art. 8º, IV, Lei 9.610/98, confirmado no Planalto).
- **Situação:** Lista lida em 16/10/2026, todas 'em vigor': nº 32/2026 (26/01/2026, União Europeia reconhecida como nível adequado), 31/2025 e 30/2025 (agenda e mapa de temas prioritários 2026-2027), 23/2024, 19/2024 (transferência internacional e cláusulas-padrão), 18/2024 (encarregado), 15/2024 (incidentes), 11/2023, 10/2023, 5/2023, 4/2023 (dosimetria), 2/2022 (pequeno porte, alterada pela 15/2024), 1/2021. Não há resolução de IA nem de RIPD na página.
- **O que faz:** Fonte primária do N1 para o regulador. Serve de lista-mestra para auditar a cobertura do catálogo.
- **Sobreposição (nenhuma):** Insumo, não concorrente.
- **Vale incorporar:** Comparação automática mensal 'lista oficial x catálogo N1'. Hoje o N1 tem Res. 1/2021, 2/2022, 4/2023, 15/2024, 18/2024 e 19/2024; falta a Res. CD/ANPD 32/2026 (relevante para transferência de dados Brasil-UE). As de agenda/temas (23/2024, 30 e 31/2025) entram só no radar.
- **Riscos:** A página pode mudar sem aviso; o repo goul4rt/lgpd-skills descreve as Res. 30 e 31/2025 como 'agendas regulatória e de fiscalização', o que diverge da página oficial (30 = mapa de temas; 31 = alteração da agenda). Não copiar de terceiros.
- **Verificação:** confirmado. Fonte: WebFetch da página; grep no n1-federal.json local.

#### A3. SGD/MGI - Guia para elaboração de RIPDs e Modelo de RIPD (PPSI 2.0)

- **URL:** https://www.gov.br/governodigital/pt-br/privacidade-e-seguranca/ppsi-2.0/arquivos/guia-para-elaboracao-de-ripds-v0-1-31072026.pdf
- **Tipo:** oficial
- **Licença e termos (cópia e treino de IA):** CC BY-NC-ND 4.0 (copiar e redistribuir só sem fins comerciais, com crédito; sem obra derivada).
- **Situação:** Publicado em 31/07/2026. O nome do arquivo indica guia v0.1 e modelo v1.0; o texto do guia diz versão 1.0 (inconsistência não resolvida). Escopo: órgãos do SISP (administração federal).
- **O que faz:** Ensina a decidir se um produto/serviço precisa de RIPD e como preencher o modelo: contexto e tratamento, princípios da LGPD, direitos dos titulares, gestão de riscos, versionamento e aprovação.
- **Sobreposição (baixa):** Referência para a minuta de RIPD (uma das 15).
- **Vale incorporar:** Conferir se a nossa minuta de RIPD cobre as mesmas seções (contexto, princípios, direitos, riscos, versionamento, aprovação) e incluir 'quando é exigido' como pergunta do questionário.
- **Riscos:** NC+ND: não derivar o modelo. Escopo setor público federal; não é padrão para o setor privado.
- **Verificação:** confirmado. Fonte: WebFetch do PDF.

### Brasil - comercial (diagnóstico e privacy management)

#### B1. Confidata (diagnóstico LGPD gratuito + plataforma)

- **URL:** https://confidata.com.br/diagnostico-lgpd
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Termos de Uso existem, mas não foram lidos: cláusulas de cópia/IA não verificadas. Página declara que respostas são guardadas 12 meses e não são compartilhadas.
- **Situação:** Ativo em 16/10/2026. Diagnóstico gratuito: 24 perguntas em 8 domínios (3 por domínio), 7 a 9 minutos, nota 0-100 em 5 níveis (Inicial a Otimizado), relatório completo por e-mail, sem cadastro prévio.
- **O que faz:** Plataforma GRC/LGPD: inventário de dados, ROPA, RIPD e LIA gerados automaticamente, cookies e consentimento, portal do titular, incidentes ligados ao prazo da ANPD, transferência internacional, checklist com pontuação, políticas com IA e assistente de IA ('55 skills'). Declara não usar dados de clientes para treinar modelos.
- **Sobreposição (média):** É o que mais se parece com o nosso questionário (questionário -> lacunas LGPD). Não lê repositório, não cobre UF, EUA nem mundo, não gera minutas societárias (NDA, cessão de PI, acordo de fundadores, term sheet).
- **Vale incorporar:** Escala de maturidade por domínio e relatório 'o que fazer em cada domínio' como formato de saída. Mapear os 8 domínios deles contra os nossos blocos do questionário para achar buracos (sem copiar perguntas).
- **Riscos:** Termos de uso não lidos; possível proibição de cópia das perguntas. A página não menciona startups/PMEs como público.
- **Verificação:** confirmado (páginas); termos: não verificado. Fonte: WebFetch de confidata.com.br e /diagnostico-lgpd.

#### B2. Privacy Tools (Porto Alegre/RS)

- **URL:** https://www.privacytools.com.br/
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Termos de uso linkados no rodapé, não lidos: não verificado. Preços não públicos ('Solicite Demonstração').
- **Situação:** Ativo em 16/10/2026. Módulos listados: Cookies e Políticas, Consentimentos, Data Mapping (gera ROPA e RIPD), Data Discovery, Pedidos de Titulares, Incidentes, GRC, Governança de IA, Diagnósticos e Avaliações, Canal de Denúncias, ESG, Open Finance, Riscos de Terceiros, entre outros; implantação guiada de até 60 dias.
- **O que faz:** Suíte enterprise de privacidade e GRC (setores: enterprise, governo, saúde, financeiro, energia, varejo, educação).
- **Sobreposição (baixa):** Mesmo tema (LGPD, ROPA, RIPD, IA), mas é plataforma operacional pós-adequação. A página não descreve questionários nem leitura de código ('Governança de IA' e 'Diagnósticos' sem detalhe).
- **Vale incorporar:** Usar a lista de módulos como checklist de cobertura: inventário, terceiros, incidentes, titulares, cookies, IA. Nada de conteúdo.
- **Riscos:** Termos não lidos; produto fechado.
- **Verificação:** parcial. Fonte: WebFetch da home.

#### B3. DPOnet

- **URL:** https://exame.com/negocios/startup-que-automatiza-implementacao-e-gestao-da-lgpd-capta-r-6-milhoes/
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Não verificado.
- **Situação:** Notícia de 29/09/2022: rodada seed de R$ 6 milhões; mais de 1.500 empresas e 7.000 pessoas treinadas (dados da época). Situação atual: não verificado.
- **O que faz:** SaaS de automação e gestão de conformidade LGPD, cursos e marketplace de serviços.
- **Sobreposição (baixa):** Mesmo mercado (adequação LGPD para PMEs), sem evidência de leitura de repositório.
- **Vale incorporar:** Nada concreto; indicador de que há demanda por adequação automatizada para PMEs.
- **Riscos:** Dados de 2022; empresa pode ter mudado.
- **Verificação:** parcial (notícia de 2022). Fonte: WebFetch Exame.

#### B4. OneTrust

- **URL:** https://www.onetrust.com/
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Não verificado.
- **Situação:** Ativo. A navegação do site lista AI Governance, Consent & Preferences, Data Use Governance, Privacy Automation, Tech Risk & Compliance e Third-Party Management. A página em português retornou 404; presença no Brasil, módulo LGPD e preços: não verificado.
- **O que faz:** Plataforma global de privacidade, risco e governança de IA para grandes empresas.
- **Sobreposição (baixa):** Enterprise; não é revisor de projeto a partir de repositório (não verificado).
- **Vale incorporar:** Nada; referência de taxonomia (inventário de IA, avaliações, terceiros).
- **Riscos:** Fechado e caro (preço não verificado).
- **Verificação:** parcial. Fonte: WebFetch (home em inglês via 404).

#### B5. Lumiun, Adequa, Vitreo, Datasafe (nomes citados no briefing)

- **URL:** https://www.lumiun.com/
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Não verificado.
- **Situação:** Lumiun CONFIRMADO como fornecedor de segurança de internet (Lumiun Box: firewall/VPN; Lumiun DNS: filtro), sem LGPD na página: não é plataforma de privacy management. Adequa, Vitreo e Datasafe: apareceram só como termos de busca; nenhuma página própria confirmou produto LGPD. Não verificado.
- **O que faz:** Lumiun: controle de acesso à internet para PMEs e provedores.
- **Sobreposição (nenhuma):** Nenhuma.
- **Vale incorporar:** Nada. Retirar Lumiun da lista de concorrentes de LGPD.
- **Riscos:** Não citar Adequa/Vitreo/Datasafe como existentes sem confirmar.
- **Verificação:** Lumiun: confirmado; demais: não verificado. Fonte: WebFetch lumiun.com; WebSearch.

### Brasil - comercial (documentos e contratos)

#### B6. Contraktor, Juridoc, Netlex

- **URL:** https://www.b2bstack.com.br/compare/juridoc-vs-contraktor
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Não verificado (nenhum termo lido).
- **Situação:** Comparativo B2BStack (terceiro): Contraktor (fundada 2016) organiza, gerencia e assina contratos, a partir de R$ 0 com teste de 7 dias; Juridoc (2017) automação e gestão de contratos e documentos, a partir de R$ 457/mês, com versão gratuita. Netlex (MobileTime, 04/05/2026) prepara agentes de IA: gestão de cláusulas/alertas e aprovação com nota de confiabilidade; a plataforma já usa IA para criar modelos de contrato. Clientes citados: Localiza, Samsung, Ambev, Andrade Gutierrez.
- **O que faz:** CLM, automação de documentos e assinatura eletrônica para áreas jurídicas e RH.
- **Sobreposição (baixa):** Produzem/gerenciam contratos, mas não revisam produto de IA/startup contra normas (nenhuma página menciona LGPD ou revisão regulatória; 'Monitoramento de Compliance Legal' aparece só como item de tabela).
- **Vale incorporar:** Exportar minutas em .docx com campos de mesclagem para o fluxo de assinatura (Clicksign/Contraktor/Autentique) como etapa seguinte; sem integração agora.
- **Riscos:** Preços vêm de comparador de terceiros; podem estar desatualizados.
- **Verificação:** parcial. Fonte: WebFetch B2BStack e MobileTime.

### Brasil - geradores de política em português

#### B7. Legal Forge; geradores Nuvemshop e blog Remessa Online

- **URL:** https://www.tabnews.com.br/mrbispo/legal-forge
- **Tipo:** comercial/independente
- **Licença e termos (cópia e treino de IA):** Legal Forge: licença e repositório não informados. Nuvemshop e Remessa Online: só apareceram em busca; não abertos: não verificado.
- **Situação:** Legal Forge: SaaS anunciado no TabNews em 20/04/2025 por 'mrbispo' (política de privacidade, termos de uso e aviso de cookies com IA; Next.js e OpenAI pelas hashtags; plano gratuito; cita LGPD e GDPR). URL do produto: legalforge.nidussolutions.com. Status atual: não verificado.
- **O que faz:** Gera política/termos/cookies adaptados ao idioma e à legislação, por IA, sem descrever validação jurídica.
- **Sobreposição (baixa):** Cobre 2 das 15 minutas (política e termos) sem revisão de lacunas, UF ou contexto do projeto.
- **Vale incorporar:** Nada de texto. Confirma que o mercado aceita 'geração por IA' para políticas simples; nosso diferencial é cruzar com o repositório e o catálogo.
- **Riscos:** Sem rastreio de validação jurídica; risco de políticas genéricas.
- **Verificação:** parcial. Fonte: WebFetch TabNews.

### Brasil - kits para startups

#### B8. MAIS (OAB/RJ e parceiros), ABStartups, CICC (PLP 252/2023), cartilha OAB-PE/Sebrae

- **URL:** https://startup-mais.com.br/
- **Tipo:** open source declarado / associação / proposta legislativa
- **Licença e termos (cópia e treino de IA):** MAIS: página diz 'minuta padrão open source' mas NÃO nomeia licença nem diz se pode adaptar/uso comercial. ABStartups: guia sem aviso de copyright nem licença. Sebrae (índice de conteúdos): 'todos os direitos reservados'. Cartilha OAB-PE: só o título apareceu na busca; conteúdo e licença não verificados.
- **Situação:** MAIS: modelo de acordo de investimento early-stage inspirado no SAFE, adaptado ao direito brasileiro, apoiado por Comissão de Startups da OAB/RJ, Anjos do Brasil, BizHub, Equity Rio, Fator3, Grey Matter, Invest.Rio, Norte Ventures, Vieira Rezende e outros; downloads em Word e PDF; data e versão não informadas. Artigo do Startups.com.br descreve cláusulas próprias (conversão forçada ou devolução após 5 anos sem rodada). CICC (Contrato de Investimento Conversível em Capital Social, PLP 252/2023, inspirado no SAFE): artigo de 08/05/2024 só fala em projeto aprovado na CAE do Senado; situação atual: não verificado. ABStartups: guia do Marco Legal (LC 182/2021) sem modelos e sem menção à LGPD.
- **O que faz:** MAIS é o único kit brasileiro aberto de instrumento de investimento encontrado. Não localizei kit aberto de NDA, cessão de PI, acordo de fundadores ou RIPD para startups brasileiras (busca limitada; não prova ausência). Cubo: não verificado (não pesquisado em fonte própria).
- **Sobreposição (baixa):** Toca em 1 das 15 minutas (term sheet/instrumento de investimento).
- **Vale incorporar:** Fazer a minuta de term sheet/instrumento de investimento reconhecer os veículos brasileiros (mútuo conversível, MAIS, CICC se virar lei) e apontar o MAIS como referência externa. Antes de reutilizar qualquer texto, pedir a licença ao contato da OAB/RJ.
- **Riscos:** Licença do MAIS indefinida: não copiar cláusulas. Status do CICC não verificado.
- **Verificação:** parcial. Fonte: WebFetch startup-mais.com.br, luma.com/MAIS, Startups.com.br, ABStartups.

### Geradores internacionais

#### C1. iubenda

- **URL:** https://www.iubenda.com/pt-br/help/146046-free-privacy-policy-generator-5/
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** ToS (https://www.iubenda.com/en/user/tos/legal, lido): reprodução dos documentos sem autorização escrita é infração; documentos gerados só podem ser usados com assinatura ativa; copiar e colar só via código de integração; scraping e coleta automatizada proibidos sem autorização. Nenhuma cláusula específica sobre treino de IA no trecho lido. Diz expressamente que não é aconselhamento jurídico.
- **Situação:** Ativo. Gerador de política gratuito (mais de 1.700 serviços, 14 idiomas, site em português BR), versão Pro paga, atualização remota quando a lei muda. Cita a LGPD num link, sem detalhar como o gerador a trata.
- **O que faz:** Gera e hospeda política de privacidade, cookies e termos para sites e apps.
- **Sobreposição (baixa):** Só política/cookies; não lê projeto, não faz análise de lacunas por UF/EUA/mundo.
- **Vale incorporar:** Ideia de 'atualização remota': nossa minuta de política poderia ter um marcador de versão do catálogo e avisar quando uma norma citada mudar (já coberto pelo radar). Nenhum texto.
- **Riscos:** Não ingerir nem raspar o site ou os documentos; ToS proíbe.
- **Verificação:** confirmado. Fonte: WebFetch (generator + ToS).

#### C2. Termly

- **URL:** https://termly.io/
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Não verificado: a página do gerador e os Terms of Use não carregaram. O rodapé de uma página lida cita 'Our AI Terms Of Use', não lida.
- **Situação:** Ativo (hospeda termos gratuitamente, segundo página lida). Suporte a LGPD, idiomas e preços: não verificado.
- **O que faz:** Gerador de política, termos e cookies com banner de consentimento.
- **Sobreposição (baixa):** Mesma categoria do iubenda.
- **Vale incorporar:** Nada até ler o ToU e o AI Terms.
- **Riscos:** Pode ter cláusula de IA/cópia; ler antes de qualquer uso.
- **Verificação:** nao_verificado. Fonte: WebFetch parcial.

#### C3. TermsFeed

- **URL:** https://www.termsfeed.com/
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Não verificado (página de termos não carregou).
- **Situação:** Ativo. Geradores: política de privacidade, termos e condições/de serviço/de uso, consentimento, cookies, aviso legal, EULA, reembolso. 14 idiomas incluindo português. A home cita CCPA/CPRA, CalOPPA, GDPR, ePrivacy, PIPEDA, Reino Unido e Austrália; LGPD e Brasil NÃO aparecem.
- **O que faz:** Gerador e biblioteca de modelos de documentos de site/app.
- **Sobreposição (baixa):** Só documentos de site; sem Brasil.
- **Vale incorporar:** Lista de tipos de documento de produto (EULA, reembolso, SLA) para checar se faltam minutas de produto no nosso conjunto de 15.
- **Riscos:** ToU não lido.
- **Verificação:** parcial. Fonte: WebFetch home.

#### C4. docassemble

- **URL:** https://docassemble.org/
- **Tipo:** open source
- **Licença e termos (cópia e treino de IA):** Código MIT; documentação CC BY 3.0 (página oficial). GitHub: jhpyle/docassemble, MIT, 985 estrelas, 312 forks, 4.647 commits (página).
- **Situação:** Ativo pelos sinais da página do GitHub (13 issues e 8 PRs abertos), mas última release e data do último commit: não verificado (aba Releases vazia).
- **O que faz:** Plataforma de entrevistas guiadas (YAML + Markdown + Python) que gera PDF, DOCX ou RTF, com API e armazenamento.
- **Sobreposição (baixa):** Resolve 'questionário -> documento', mas sem catálogo de normas nem leitura de repositório.
- **Vale incorporar:** Padrão de separar 'entrevista' (perguntas e condições) de 'modelo' (DOCX com variáveis). Já usamos algo equivalente; não migrar.
- **Riscos:** Exige servidor Python/Docker e manutenção; excesso para um servidor MCP stdio local.
- **Verificação:** confirmado (página). Fonte: WebFetch docassemble.org e GitHub.

#### C5. Clerky

- **URL:** https://www.clerky.com/
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Não verificado. Declara não ser escritório de advocacia; formulários podem ser personalizados e revisados por advogado convidado.
- **Situação:** Ativo. US$ 427 por uso ou US$ 819 pacote vitalício (preços da página). Delaware (e qualificação na Califórnia/Nova York).
- **O que faz:** Incorporação Delaware C-corp, ações de fundadores, estatuto, 83(b), SAFEs e notas conversíveis, consentimentos do conselho, ofertas de emprego, consultoria/advisor, acordos de confidencialidade e cessão de invenções, NDAs, concessão de opções.
- **Sobreposição (baixa):** Cobre a mesma família de documentos de startup, mas só EUA/Delaware.
- **Vale incorporar:** Checklist de 'o que um fundador precisa' para ver o que falta no conjunto de 15 minutas (carta-oferta/contrato de trabalho, termo de advisor, atas societárias). Não usar texto.
- **Riscos:** Termos não lidos; direito americano.
- **Verificação:** confirmado (página). Fonte: WebFetch.

#### C6. Stripe Atlas

- **URL:** https://stripe.com/atlas
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Página não trata de propriedade ou licença dos documentos gerados.
- **Situação:** Ativo. US$ 500 de abertura, US$ 100/ano de agente registrado a partir do segundo ano. Delaware C-corp ou LLC, ações dos fundadores, 83(b), SAFE post-money de template da YC. Diz que templates foram criados com a Cooley LLP (sem afiliação). Lista de países elegíveis não confirmada; o seletor de país inclui Brasil.
- **O que faz:** Constituição de empresa nos EUA e documentos básicos de captação.
- **Sobreposição (nenhuma):** Outra jurisdição e outro objetivo.
- **Vale incorporar:** Quando o projeto declarar entidade nos EUA, o questionário deve apontar que o catálogo N2 cobre os EUA por padrão e perguntar se há holding Delaware.
- **Riscos:** Nenhum para nós além de não copiar documentos.
- **Verificação:** confirmado (página). Fonte: WebFetch.

#### C7. Y Combinator - SAFE e documentos

- **URL:** https://www.ycombinator.com/documents
- **Tipo:** aberto de fato (sem licença declarada)
- **Licença e termos (cópia e treino de IA):** A página não declara licença, não diz se pode reutilizar ou modificar e não menciona IA. Diz que é 'ponto de partida' e que a YC não assume responsabilidade pelo conteúdo.
- **Situação:** Post-money SAFE em três versões para empresas dos EUA e uma versão (valuation cap) para empresas do Canadá, Ilhas Cayman e Singapura, com side letters. Não há versão brasileira. Sem data de atualização na página.
- **O que faz:** Instrumento de captação early-stage.
- **Sobreposição (nenhuma):** Insumo conceitual para o term sheet.
- **Vale incorporar:** Mesmo ponto do B8: tratar o SAFE como análogo; o instrumento brasileiro é mútuo conversível/MAIS.
- **Riscos:** Sem licença: não copiar cláusulas.
- **Verificação:** confirmado (página). Fonte: WebFetch.

#### C8. Cooley GO e Orrick (formulários)

- **URL:** https://www.cooleygo.com/
- **Tipo:** comercial/gratuito proprietário
- **Licença e termos (cópia e treino de IA):** Verificado na rodada anterior (repos.md, não repetido agora): Cooley GO, ToU de 20/09/2024, seção 5: uso interno, sem copiar, modificar ou redistribuir, e PROÍBE uso para treinar ou melhorar IA/ML/LLM. Orrick: all rights reserved, uso pessoal e não comercial, sem obras derivadas (ToU jul/2018).
- **Situação:** Ativos na rodada anterior; não revisitados.
- **O que faz:** Formulários jurídicos de startups (EUA).
- **Sobreposição (nenhuma):** Outra jurisdição.
- **Vale incorporar:** Nenhum texto. Series Seed (CC0) é o único material da Cooley aproveitável, conforme repos.md.
- **Riscos:** Cláusula expressa contra treino de IA: bloqueio total de ingestão.
- **Verificação:** confirmado na rodada anterior. Fonte: research/repos.md.

### MCP e plugins jurídicos

#### D1. anthropics/claude-for-legal (upstream)

- **URL:** https://github.com/anthropics/claude-for-legal
- **Tipo:** open source
- **Licença e termos (cópia e treino de IA):** Apache-2.0 (LICENSE lido no clone). Exige manter aviso de licença e marcar alterações nos arquivos modificados. Cada saída é rascunho para revisão de advogado, não parecer.
- **Situação:** Ativo. Página em 16/10/2026: 9,6 mil estrelas, 1,9 mil forks, 24 issues, 56 PRs. Último commit do clone: 22/07/2026. 12 plugins (ai-governance, commercial, corporate, employment, ip, law-student, legal-builder-hub, legal-clinic, litigation, privacy, product, regulatory) + external_plugins/cocounsel-legal (Thomson Reuters).
- **O que faz:** Fluxos para advogados e jurídico interno: perfil da prática via 'cold-start interview'; privacy-legal (dpa-review, dsar-response, pia-generation, policy-monitor, reg-gap-analysis, use-case-triage); product-legal (launch-review lê PRD ou ticket e devolve memorando por categoria; marketing-claims-review; feature-risk-assessment); ai-governance-legal (ai-inventory do EU AI Act, aia-generation, vendor-ai-review, policy-starter); ip-legal/oss-review (lê manifestos de dependências, não o produto inteiro). Conectores: CourtListener, Descrybe, Ironclad, DocuSign, iManage, Linear, Jira, Asana, Drive etc. Cookbooks de agentes gerenciados (reg-monitor, launch-radar, docket-watcher).
- **Sobreposição (média):** É a base do nosso marketplace. Mesma ideia de 'reg-gap-analysis' e 'launch-review', mas orientada a advogado, parte de PRD (não de repositório) e não tem Brasil: busca por Brazil/Brasil/LGPD/ANPD no clone deu 0 ocorrências. Não gera as 15 minutas.
- **Vale incorporar:** (1) Manter o padrão cold-start + CLAUDE.md de perfil, já herdado. (2) Estudar o cookbook reg-monitor/launch-radar como desenho para o radar de PLs e normas. (3) Marcar citações como '[verify]' quando não houver conector de pesquisa, como eles fazem. (4) Repassar à Anthropic a lacuna Brasil se quisermos upstream.
- **Riscos:** Apache-2.0: manter NOTICE/atribuição e indicar alterações nos arquivos copiados para o claude-for-legal-br. Forks: lista não acessível (API do GitHub bloqueada); nenhum fork brasileiro apareceu nas buscas, o que não prova ausência.
- **Verificação:** confirmado (clone + página). Fonte: git clone --depth 1 (somente leitura), grep, WebFetch da página do repositório.

#### D2. lawvable/agent-skills (coleção curada de 264 skills jurídicas)

- **URL:** https://github.com/lawvable/agent-skills
- **Tipo:** open source (licenças mistas)
- **Licença e termos (cópia e treino de IA):** A LISTA é CC BY-NC-ND 4.0 (proíbe uso comercial e versões modificadas). Cada skill tem licença própria; as lidas são AGPL-3.0 (lgpd-sentinel, bacen-compliance-sentinel, privacy-policy, founder-agreement-drafting, dpia-sentinel, eu-ai-act-high-risk-classifier, privacy-policy-generator). A skill 'lgpd' de Tanaji Hemant Naik não tem campo de licença.
- **Situação:** Último commit 02/10/2026. Inclui skills em português para o Brasil: lgpd-sentinel (Rafael Mastronardi, 2026-05-20: bases legais, RIPD, incidentes, direitos, transferência) e bacen-compliance-sentinel; mais cobertura ampla de EU AI Act, GDPR, CCPA, NIST AI RMF, DPIA, cookie policy, política de privacidade, acordo de fundadores.
- **O que faz:** Conhecimento de domínio empacotado como SKILL.md. Instruções, não código executável.
- **Sobreposição (média):** Cobre sozinhas muitas das áreas (LGPD, EU AI Act, política, acordo de fundadores), mas cada skill atua isolada, sem repositório, sem catálogo por UF e sem pacote de minutas.
- **Vale incorporar:** Usar como MAPA de cobertura para N3 (quais regimes alguém já considerou relevantes: EU AI Act em papéis/classificação/transparência, NIST AI RMF, DPDPA da Índia, Data Act, CRA). Não ler para copiar.
- **Riscos:** AGPL-3.0 é copyleft de rede: incorporar texto ou código contaminaria nosso plugin. A coleção em si é ND. Regra: referenciar, nunca copiar.
- **Verificação:** confirmado (clone). Fonte: git clone --depth 1; leitura de README e cabeçalhos de SKILL.md.

#### D3. goul4rt/lgpd-skills

- **URL:** https://github.com/goul4rt/lgpd-skills
- **Tipo:** open source
- **Licença e termos (cópia e treino de IA):** MIT (LICENSE, 2026, goul4rt).
- **Situação:** Último commit 31/05/2026, v1.2.0. 19 skills (1 maestro 'lgpd-audit' + 18): data-mapping, legal-basis, consent-schema, dsar, incident-response, ropa, ripd, retention-erasure, vendor-audit, dpa, international-transfer, dpo-encarregado, anonymization, audit-logging, encryption-keys, privacy-policy, legacy-retrofit, eca-digital-minors. Funciona em Claude Code, Codex, Gemini CLI, Cursor e OpenCode.
- **O que faz:** Audita um projeto de software contra a LGPD: reconstrói o inventário de dados a partir do código (schemas Prisma, endpoints, SDKs de terceiros, logs), classifica bases legais e grava 'artefatos vivos' versionados em Git sob .lgpd/ (STATUS, data-map, ROPA, RIPD, política de privacidade, DPA, runbook de incidente, gaps). Quatro pipelines: greenfield, legado, híbrido, incidente. Pausa obrigatória para aprovação humana antes de gerar RIPD, ROPA final, política e comunicação à ANPD. Cita artigo da LGPD ou resolução ANPD em cada recomendação. Cobertura declarada: LGPD (com Lei 15.352/2026), Res. 2/2022, 4/2023, 15/2024, 18/2024, 19/2024 e ECA Digital.
- **Sobreposição (alta (no eixo LGPD)):** É o produto mais próximo do nosso fluxo 'repositório -> lacunas -> documentos' e o único em português. Falta o que nos diferencia: nenhuma menção a leis estaduais ou competência (grep: 0 'estadual'), nada de PL 2338/2023 nem EU AI Act (0 ocorrências), nada de EUA/mundo (N2/N3), sem avaliação de impacto de IA, sem NDA, cessão de PI, acordo de fundadores, term sheet; stack assumida Next.js/Prisma/Postgres.
- **Vale incorporar:** (1) Artefatos vivos versionados em pasta própria do projeto (por ex. .lexzenit/) com STATUS e gaps. (2) Pipelines por cenário, especialmente 'incidente em andamento' com prazo de 3 dias úteis (Res. 15/2024). (3) Checkpoint humano antes de cada minuta. (4) Regra 'sem citação, sem recomendação'. Licença MIT permite reuso com atribuição, mas escreva o nosso.
- **Riscos:** Erro encontrado na descrição das Res. 30 e 31/2025 (ver A2): não herdar a normativa deles sem conferir. Projeto de um autor; adoção (estrelas, uso): não verificada. Pode evoluir e passar a cobrir UF/IA.
- **Verificação:** confirmado (clone). Fonte: git clone --depth 1; README, lgpd-audit/SKILL.md, grep.

#### D4. LordMendes/lgpd-mcp

- **URL:** https://github.com/LordMendes/lgpd-mcp
- **Tipo:** open source
- **Licença e termos (cópia e treino de IA):** MIT (package.json).
- **Situação:** v0.1.0, commit único de 12/02/2026 no clone; sem sinais de manutenção ativa.
- **O que faz:** Servidor MCP (stdio e HTTP, TypeScript) com 9 ferramentas: validar_base_legal (art. 7 e 11), verificar_consentimento (art. 8), gerar_modelo_consentimento, PIA, checklist, políticas, direitos do titular, mapeamento de dados sensíveis e avaliação de risco; 5 resources (fundamentos, artigos, bases legais, glossário, ANPD) e 4 prompts. Não lê código.
- **Sobreposição (média):** Mesmo formato (MCP stdio local, LGPD, modelos), muito menor: sem repositório, sem UF/EUA/mundo, 1 modelo de documento por ferramenta.
- **Vale incorporar:** Desenho de ferramentas pequenas e determinísticas (validar_base_legal, verificar_consentimento) que o relatório pode chamar para checagens objetivas, em vez de deixar tudo ao modelo.
- **Riscos:** Projeto inicial; docs/DISCLAIMER.md. Não depender.
- **Verificação:** confirmado (clone). Fonte: git clone --depth 1; README e docs/TOOLS.md.

#### D5. lgpd-app/skills (lgpd-check e lgpd-md)

- **URL:** https://github.com/lgpd-app/skills
- **Tipo:** open source
- **Licença e termos (cópia e treino de IA):** Apache-2.0.
- **Situação:** 5 commits, último em 03/06/2026; 2 estrelas e 1 fork (página). Spec e schema do padrão ficam em github.com/lgpd-app/lgpd-md e lgpd.md (o site lgpd.md foi bloqueado para leitura: não verificado).
- **O que faz:** lgpd-check audita SITES em 6 módulos (política, cookies, minimização, transferência internacional, direitos, scripts de terceiros) com nota e correções priorizadas. lgpd-md gera/valida o arquivo 'lgpd.md', uma declaração de conformidade LGPD em Markdown com frontmatter validável por JSON Schema, publicada em https://{domínio}/lgpd.md.
- **Sobreposição (baixa):** Audita site, não repositório; só LGPD.
- **Vale incorporar:** Gerar, como saída extra do relatório, um 'lgpd.md' (declaração máquina-legível do controlador, encarregado, bases, direitos, transferências). Custo baixo; valor depende de adoção do padrão (desconhecida).
- **Riscos:** Padrão novo e sem adoção comprovada; schema não lido na fonte oficial.
- **Verificação:** confirmado (clone); padrão lgpd.md: parcial. Fonte: git clone --depth 1; SKILL.md e LGPD-MD-SPEC.md.

#### D6. dpo2u/dpo2u-mcp

- **URL:** https://lobehub.com/nl/mcp/dpo2u-dpo2u-mcp
- **Tipo:** open source (informação de vitrine)
- **Licença e termos (cópia e treino de IA):** MIT, segundo a página da LobeHub. Repositório github.com/dpo2u/dpo2u-mcp não pôde ser clonado na nossa sessão: não verificado.
- **Situação:** v1.0.0 segundo a vitrine; data não mostrada. LLM local via Ollama e busca vetorial LEANN sobre cerca de 2.856 documentos LGPD/GDPR.
- **O que faz:** 10 ferramentas: auditoria de infraestrutura, verificação de conformidade, avaliação de risco (RIPD), mapa de fluxo de dados, auditoria de consentimento, simulação de violação, análise de contrato/DPA, nota de privacidade; gera política de privacidade e relatório executivo de DPO. Não consta leitura de código-fonte.
- **Sobreposição (média):** LGPD + GDPR em MCP local. Sem UF, sem EUA/mundo além de GDPR, sem minutas societárias.
- **Vale incorporar:** Nada para copiar; confirma que MCP local + modelo local é desejado por usuários sensíveis a privacidade. Considerar modo 'sem envio de dados a terceiros' na documentação do nosso servidor stdio.
- **Riscos:** Alegação '100% dos artigos LGPD/GDPR' não verificável.
- **Verificação:** parcial. Fonte: WebFetch LobeHub.

#### D7. Ansvar-Systems/brazil-law-mcp (@ansvar/brazil-law-mcp)

- **URL:** https://github.com/ansvar-systems/brazil-law-mcp
- **Tipo:** open source? (não verificado)
- **Licença e termos (cópia e treino de IA):** NÃO verificado: nenhuma vitrine declara licença e o repositório não pôde ser clonado na nossa sessão. Licença do corpus de leis também não verificada (leis em si não têm proteção autoral, art. 8º, IV, Lei 9.610/98).
- **Situação:** Vitrines: MCP Market (corpus declarado: 2.471 leis federais e 28.585 dispositivos) e claudemarketplaces (última atualização 22/02/2026, STDIO e HTTP). Data do último commit: não verificado.
- **O que faz:** Busca em texto integral em leis federais (LGPD, Marco Civil, CDC, Código Civil, telecom), recuperação de dispositivos, validação de citações, verificação de vigência, ferramentas de comparação com a legislação da UE (ex.: LGPD x GDPR), checagem automática de atualização com base em LexML e Planalto.
- **Sobreposição (baixa (no revisor); média (no catálogo)):** Compete com a nossa fonte de textos federais e com 'verificar vigência'. Só federal: sem UF e sem revisão de projeto.
- **Vale incorporar:** Duas ideias de ferramenta: 'validate_citation' (conferir que artigo citado existe) e 'check_currency' (alertar norma alterada/revogada). Reproduzir sobre as nossas fontes (Planalto/LexML), sem depender do pacote.
- **Riscos:** Alegações de marketing; sem licença confirmada: não adotar como dependência nem raspar.
- **Verificação:** parcial. Fonte: WebFetch MCP Market, claudemarketplaces, skillsplayground.

#### D8. prof-ramos/LeXML-mcp

- **URL:** https://github.com/prof-ramos/LeXML-mcp
- **Tipo:** open source
- **Licença e termos (cópia e treino de IA):** GPL-3.0-or-later (página; repositório não clonável na nossa sessão).
- **Situação:** 8 commits, 1 estrela, 0 forks; v0.2.0 observada em 28/07/2026; Glama marca manutenção como 'Stale'.
- **O que faz:** 3 ferramentas: lexml_search (consulta CQL no SRU do LexML), lexml_resolve_urn (URN para URL pública com proteção SSRF) e lexml_explain (metadados do serviço). Python/FastMCP. Endpoint SRU: https://www.lexml.gov.br/busca/SRU.
- **Sobreposição (baixa):** É só uma casca fina sobre a API pública do LexML.
- **Vale incorporar:** Chamar o SRU do LexML diretamente a partir do nosso servidor (ver F3) e copiar apenas a ideia de proteger a resolução de URN contra SSRF.
- **Riscos:** GPL-3.0 impede embutir o código no nosso plugin sem adotar a mesma licença.
- **Verificação:** confirmado (vitrines e página do repo). Fonte: WebFetch Glama e GitHub.

#### D9. SidneyBissoli/senado-br-mcp

- **URL:** https://github.com/SidneyBissoli/senado-br-mcp
- **Tipo:** open source
- **Licença e termos (cópia e treino de IA):** MIT.
- **Situação:** Repositório marcado como DEPRECATED/arquivado no próprio README (migrou para senado-br-mcp-cloudflare, 66 ferramentas, v3.2.1+). Último commit do clone: 24/06/2026.
- **O que faz:** 33 ferramentas sobre dados abertos do Senado (matérias, tramitação, textos, votos, senadores) e raspagem do e-Cidadania.
- **Sobreposição (baixa):** Fonte potencial para o radar de PLs.
- **Vale incorporar:** Nada a instalar. Ler a lista de endpoints como referência. O código usa /materia/pesquisa/lista, que a própria API do Senado devolve marcado como depreciado (ver F2).
- **Riscos:** Arquivado; depende de endpoints depreciados; raspagem do e-Cidadania.
- **Verificação:** confirmado (clone). Fonte: git clone --depth 1; grep em src/api/endpoints.ts.

#### D10. ranielbnunes/datajud-mcp

- **URL:** https://github.com/ranielbnunes/datajud-mcp
- **Tipo:** open source
- **Licença e termos (cópia e treino de IA):** MIT (README).
- **Situação:** Uma versão, 1.0.0 de 18/06/2025; README com placeholders não substituídos; Glama marca 'cannot be deployed'.
- **O que faz:** 6 ferramentas sobre a API DataJud do TJMA (Maranhão) apenas: consultar processo, buscar, movimentações, estatísticas por comarca, produtividade e 'predição de julgamento' (metodologia não explicada).
- **Sobreposição (nenhuma):** Irrelevante para revisão de projeto.
- **Vale incorporar:** Nada.
- **Riscos:** Predição sem metodologia; cobre um tribunal.
- **Verificação:** confirmado (vitrine). Fonte: WebFetch Glama.

#### D11. Legalis MCP (edsonsousa) e skills de advocacia em PT (flowgrammers-skills)

- **URL:** https://github.com/edsonsousa/legalis-mcp
- **Tipo:** open source (cliente) de plataforma comercial
- **Licença e termos (cópia e treino de IA):** legalis-mcp: MIT (pyproject.toml); depende de conta na plataforma Legalis (legalis-ia.com), cujos termos não foram lidos. flowgrammers-skills/juridico-advocacia: MIT segundo a vitrine.
- **Situação:** legalis-mcp: último commit 09/04/2026; 13 ferramentas (casos, documentos, generate_section, run_interview, search_legislation via LexML, get_my_usage). juridico-advocacia: skill de petições, contratos, captação e precificação para advogados; não menciona LGPD.
- **O que faz:** Assistência a advogados brasileiros (peças, casos).
- **Sobreposição (baixa):** Público e objetivo diferentes (advogado litigante), não revisão de projeto.
- **Vale incorporar:** Ferramenta 'run_interview' mostra o padrão de entrevista guiada via MCP; já temos o questionário.
- **Riscos:** Servidor remoto da plataforma recebe dados do caso; não aplicável a nós.
- **Verificação:** confirmado (clone/vitrine). Fonte: git clone --depth 1 (legalis-mcp); WebFetch (skill).

#### D12. legalize-kr/legalize-kr e admrule-kr (arquitetura de referência)

- **URL:** https://github.com/legalize-kr/legalize-kr
- **Tipo:** open source (código) / dados sem licença
- **Licença e termos (cópia e treino de IA):** Verificado na rodada anterior (repos.md): código MIT OR Apache-2.0; repositório de dados sem LICENSE e com aviso de force-push.
- **Situação:** Rodada anterior: 5.770 leis coreanas em Markdown, revisão = commit com data de promulgação, MCP local com 11 ferramentas somente leitura (laws_get, laws_article, laws_diff, search), consulta por data.
- **O que faz:** Mostra como versionar legislação em Git.
- **Sobreposição (nenhuma):** Outro país; mesma arquitetura que serve de modelo.
- **Vale incorporar:** Já registrado em repos.md: lei = arquivo, revisão = commit, frontmatter de vigência, consulta por data. Aplicar ao catálogo N1/UF.
- **Riscos:** Ver repos.md.
- **Verificação:** confirmado na rodada anterior. Fonte: research/repos.md.

#### D13. MCPs do CourtListener (Free Law Project) e eCFR

- **URL:** https://glama.ai/mcp/servers/Travis-Prall/court-listener-mcp
- **Tipo:** open source / uso restrito
- **Licença e termos (cópia e treino de IA):** Travis-Prall/court-listener-mcp: PolyForm Noncommercial (uso comercial ou hospedado exige permissão). DefendTheDisabled/courtlistener-mcp: MIT, marcado inativo. O upstream claude-for-legal usa o conector CourtListener (público, chave opcional).
- **Situação:** Travis-Prall: 30 ferramentas (CourtListener API v4, GovInfo para estatutos, Regulations.gov), v0.2.2, manutenção 'slow'. eCFR: nenhum servidor MCP encontrado nas buscas: não verificado.
- **O que faz:** Pesquisa de jurisprudência e norma federal dos EUA.
- **Sobreposição (baixa):** Útil para o N2 (EUA) só se quisermos citar precedentes; nosso foco é lei e regulação.
- **Vale incorporar:** Para o N2, usar GovInfo e eCFR/Regulations.gov direto como fonte de atualização de regras federais dos EUA, em vez de jurisprudência. Se algum dia usarmos CourtListener, usar o conector oficial do upstream.
- **Riscos:** PolyForm Noncommercial bloqueia produto comercial.
- **Verificação:** confirmado (vitrines). Fonte: WebFetch Glama.

#### D14. MCPs de EUR-Lex (lexsocket/mcp-eurlex; matematicsolutions/mcp-eu-sparql)

- **URL:** https://glama.ai/mcp/servers/matematicsolutions/mcp-eu-sparql
- **Tipo:** open source / remoto
- **Licença e termos (cópia e treino de IA):** mcp-eu-sparql: MIT; conteúdo do GDPRhub que ele consulta é CC BY-NC-SA 4.0. lexsocket/mcp-eurlex: licença não declarada, servidor remoto com autenticação.
- **Situação:** mcp-eu-sparql v1.1.0 (24/06/2026): EUR-Lex/Cellar via SPARQL (por CELEX, por data, CJUE, ECLI, GDPRhub). mcp-eurlex: atualizado em 23/01/2026, remoto (streamable HTTP).
- **O que faz:** Consulta direito da UE.
- **Sobreposição (baixa):** Fonte para N3 (UE).
- **Vale incorporar:** Usar o endpoint SPARQL Cellar do Publications Office como fonte de atualização dos atos da UE no N3 (por CELEX). Não ingerir GDPRhub (NC-SA).
- **Riscos:** Remoto com autenticação envia consultas a terceiros.
- **Verificação:** parcial (vitrines). Fonte: WebFetch Glama e claudemarketplaces.

### Scanners de projeto e produtos de IA

#### E1. ArkForge mcp-eu-ai-act

- **URL:** https://github.com/ark-forge/mcp-eu-ai-act
- **Tipo:** open source + SaaS pago
- **Licença e termos (cópia e treino de IA):** MIT (LICENSE e docs/TERMS_OF_USE.md lidos no clone). Free: 10 scans/dia; Pro: 29 EUR/mês (vitrine).
- **Situação:** Ativo: último commit do clone 25/09/2026; ferramentas atualizadas em 01/09/2026 e testado em 15/10/2026 (Glama). Inconsistência: Glama diz 22 frameworks de IA, README diz 16.
- **O que faz:** Varre um projeto, detecta frameworks de IA (OpenAI, Anthropic, LangChain, PyTorch etc.) e fluxos de dados pessoais (campos PII, cookies, pixels, SDKs de analytics), mapeia para artigos do EU AI Act e do GDPR com aprovado/reprovado e correção, e gera modelos: política de privacidade, DPIA, ROPA, procedimento de violação (GDPR) e gestão de risco, documentação técnica, transparência, supervisão humana (AI Act); roadmap semanal e pacote Anexo IV (Pro); relatório certificado com prova pública. 16 ferramentas.
- **Sobreposição (média):** Mesma forma (repositório -> lacunas -> modelos, como MCP), só UE (AI Act + GDPR). Brasil/LGPD: 0 ocorrências no README. Sem questionário, sem UF, sem minutas societárias.
- **Vale incorporar:** (1) Relatório de 'aprovado/reprovado por artigo' com correção objetiva. (2) Roadmap semana a semana como seção do relatório. (3) Dados de artigos em JSON (data/eu_ai_act_articles.json) como referência de formato do nosso catálogo.
- **Riscos:** Selo 'certificado' é produto de marketing; não adotar. Aviso de isenção de responsabilidade em docs.
- **Verificação:** confirmado (clone). Fonte: git clone --depth 1; README e docs; WebFetch Glama.

#### E2. WeScan (Glade Tech)

- **URL:** https://wescan.it.com/
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Não verificado (termos não lidos). Página: o código é clonado, varrido em memória e apagado; só os achados ficam por 90 dias.
- **Situação:** Ativo em 16/10/2026. Free (1 scan/mês, 3 achados), Starter £29/mês, Pro £99/mês.
- **O que faz:** Envia URL de GitHub, repo privado com token ou ZIP de até 4 MB; detecta OpenAI, Anthropic, Bedrock, Azure OpenAI, Gemini e Hugging Face; nota de 0 a 100 e achados Crítico/Alto/Médio com regulação e correção; gera 'policy pack' (política de uso de IA, checklist de DPA, mapa de fluxo de dados). Cita GDPR (art. 28), CCPA e SOC 2.
- **Sobreposição (média):** Mesmo fluxo para startups que vendem a empresas; sem LGPD nem AI Act confirmados, sem UF, sem minutas societárias.
- **Vale incorporar:** O argumento comercial 'documentos para revisão de segurança/compliance exigida por clientes enterprise'. Para o público brasileiro: gerar um 'pacote para due diligence de cliente/investidor' (política, RIPD, mapa de fluxo, lista de operadores).
- **Riscos:** Alegações próprias da página, não verificadas.
- **Verificação:** parcial. Fonte: WebFetch.

#### E3. EU ACT Guard

- **URL:** https://www.producthunt.com/products/eu-act-guard
- **Tipo:** comercial (acesso antecipado)
- **Licença e termos (cópia e treino de IA):** Não verificado.
- **Situação:** Lançado no Product Hunt em 2026 (cerca de 5 meses antes da leitura); gratuito/acesso antecipado.
- **O que faz:** Lê repositório GitHub e aponta violações com arquivo e linha; verifica rotulagem do art. 50 no site, política de privacidade, rascunho de ficha técnica do Anexo IV e mapeamento ISO 42001; três relatórios (técnico, jurídico, negócio). Sinaliza CONTRADIÇÕES entre as respostas do questionário e o que o código faz.
- **Sobreposição (média):** É o único que declara combinar questionário e código. Só UE.
- **Vale incorporar:** Gate de coerência: depois do questionário, comparar cada resposta com evidências do repositório (ex.: 'não coletamos dados de crianças' x campos de data de nascimento; 'não usamos IA' x dependências de LLM) e listar divergências no relatório. Alto valor, esforço médio.
- **Riscos:** Alegação de 6 em 10 repositórios é do próprio criador.
- **Verificação:** parcial. Fonte: WebFetch Product Hunt.

#### E4. Privado.ai (privacy code scanning)

- **URL:** https://privado.ai/products/privacy-code-scanning
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Não verificado.
- **Situação:** Ativo; SOC 2; preços não públicos, demonstração sob pedido.
- **O que faz:** Varre código de sites, apps e backends para mapear fluxos de dados pessoais, classificar dados sensíveis, apontar riscos e orientar correção; 'preenche automaticamente' RoPA, PIA e DPIA após cada varredura; integra GitHub, GitLab, Jira, Slack, OneTrust e TrustArc.
- **Sobreposição (média):** Repositório -> mapa de dados -> RoPA/DPIA. Páginas de lei listadas: GDPR e CCPA; LGPD não mencionada.
- **Vale incorporar:** Gerar o mapa de dados a partir do código como entrada do RIPD e do questionário (já é parte do nosso 'ler repositório'). Sincronizar com ROPA existente é futuro.
- **Riscos:** Produto enterprise; sem LGPD.
- **Verificação:** parcial. Fonte: WebFetch.

#### E5. Scanners só de GDPR: GDPR Shift-Left MCP, gdpr-compliance-scanner, GDPRScout, Legiscope

- **URL:** https://glama.ai/mcp/servers/x8d7cccw1z
- **Tipo:** open source e comerciais
- **Licença e termos (cópia e treino de IA):** GDPR Shift-Left MCP (KevinRabun): MIT. gdpr-compliance-scanner (jeremylongshore): MIT. GDPRScout (varredura de URL, PeerPush, 28/03/2026) e Legiscope (plataforma GDPR, sem varredura de código): termos não lidos.
- **Situação:** Shift-Left: 34 ferramentas, AST em Python/JS/TS/Java/C#/Go, IaC (Bicep/Terraform/ARM), ROPA e DPIA, só GDPR. Os demais: só GDPR, CCPA e AI Act em site.
- **O que faz:** Varreduras de GDPR em código/infra ou site.
- **Sobreposição (baixa):** Só UE/EUA em escopo estreito.
- **Vale incorporar:** Lista de verificações de código do Shift-Left (log de PII, segredos no código, consentimento ausente, transferências transfronteiriças) como inspiração para a lista de 'sinais no repositório' do revisor. Reescrever para a LGPD.
- **Riscos:** Nenhum relevante.
- **Verificação:** parcial. Fonte: WebFetch Glama, agentskill.sh, PeerPush, Legiscope.

#### E6. Harvey

- **URL:** https://www.harvey.ai/
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Não verificado. Preço sob demonstração.
- **Situação:** Ativo. Página: uso em 85+ países (lista não divulgada); logos incluem América Móvil e Creel García; certificações SOC 2 II e ISO 27001 (da Harvey, não do cliente).
- **O que faz:** Knowledge (pesquisa jurídica, regulatória e tributária), Vault (análise de documentos em lote), agentes, orquestração de trabalho jurídico, Intake e Horizon Scanning (monitoramento regulatório).
- **Sobreposição (baixa):** Suporta equipe jurídica; a página não menciona revisão de código/produto, nem Brasil.
- **Vale incorporar:** Horizon Scanning como categoria de funcionalidade: nosso radar de PLs e normas é o equivalente leve e aberto.
- **Riscos:** Fechado.
- **Verificação:** parcial. Fonte: WebFetch home.

#### E7. Legora

- **URL:** https://legora.com/solutions/in-house
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Não verificado.
- **Situação:** Ativo. Página de jurídico interno: verificação de documentos contra GTC/DPA e padrões internos, monitoramento regulatório com sumários, prazos e fontes oficiais e conversão de norma nova em checklist, playbooks no Word.
- **O que faz:** Revisão e monitoramento para jurídico interno.
- **Sobreposição (baixa):** Não menciona Brasil, LGPD, revisão de produto nem leitura de código.
- **Vale incorporar:** 'Nova norma vira checklist' no radar: ao detectar mudança, gerar a lista de perguntas do questionário afetadas.
- **Riscos:** Fechado.
- **Verificação:** parcial. Fonte: WebFetch.

#### E8. Luminance e Spellbook

- **URL:** https://www.luminance.com/
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Não verificado.
- **Situação:** Luminance: revisão e negociação de contratos com playbooks; a página não menciona português/Brasil nem revisão de conformidade de produto. Spellbook: aparece só em resultados de busca e artigos próprios; produto não verificado nesta rodada.
- **O que faz:** Revisão e redação de contratos.
- **Sobreposição (baixa):** Contratos, não projeto de IA.
- **Vale incorporar:** Nada.
- **Riscos:** Fechado.
- **Verificação:** Luminance: parcial; Spellbook: não verificado. Fonte: WebFetch luminance.com.

#### E9. Jusbrasil - Jus IA (e 'Jurimetria')

- **URL:** https://lexlegal.com.br/?p=17322
- **Tipo:** comercial
- **Licença e termos (cópia e treino de IA):** Termos de uso e política de dados não lidos: proibição de cópia/treino de IA não verificada.
- **Situação:** Anunciado em 20/03/2025 (artigo): assistente jurídico generativo sobre base de mais de 1,2 bilhão de documentos, modelo próprio treinado com a Maritaca AI e revisão humana. Funções: Fazer Pergunta Jurídica, Criar Documento (petições e contestações) e Analisar Referências (confere se jurisprudência e dispositivos citados existem). 'Jurimetria' como produto: não verificado.
- **O que faz:** Pesquisa e peças para advogados.
- **Sobreposição (baixa):** Público advogado; não revisa projeto/startup.
- **Vale incorporar:** Função 'Analisar Referências' (verificar que cada citação existe) como etapa final do relatório: toda citação normativa passa por conferência no catálogo.
- **Riscos:** Base proprietária; não raspar.
- **Verificação:** parcial (artigo de terceiro). Fonte: WebFetch lexlegal.com.br.

### Rastreadores e fontes de atualização

#### F1. API de Dados Abertos da Câmara dos Deputados

- **URL:** https://dadosabertos.camara.leg.br/
- **Tipo:** oficial
- **Licença e termos (cópia e treino de IA):** FAQ: acesso aberto a 'qualquer cidadão ou entidade', sem cadastro nem identificação; permite cobrar por aplicativo feito com os dados; não declara licença nem limite de requisições; sem cláusula sobre robôs ou IA.
- **Situação:** Teste em 16/10/2026 (via WebFetch; o proxy da sessão bloqueou curl): GET /api/v2/proposicoes?siglaTipo=PL&numero=2338&ano=2023 respondeu sem autenticação e devolveu id 2487262 para o PL 2338/2023. /api/v2/proposicoes/2487262 devolveu statusProposicao: dataHora 2026-09-02T15:06, órgão MESA, tramitação 'Notificação de Apensação', situação 'Aguardando Parecer' (o despacho citado trata de outra apensação; interpretar com cautela), apresentação no Câmara em 2025-03-17. O FAQ avisa que há uma API nova e que a anterior só receberá correções; qual é a nova: não verificado.
- **O que faz:** Coleções: proposições (PL, PEC, MPV, pareceres, requerimentos), votações, órgãos, eventos, referências e 'Atualizações' (lista de mudanças registradas num intervalo de tempo).
- **Sobreposição (nenhuma):** Insumo.
- **Vale incorporar:** Radar de PLs automático: rotina semanal que consulta uma lista de proposições-alvo (PL 2338/2023 e os PLs do radar) e a coleção 'Atualizações', compara statusProposicao/situação com o último valor salvo e abre um diff para revisão humana antes de mudar o catálogo. Não gravar nada no catálogo sem revisão.
- **Riscos:** Sem SLA nem limites documentados; esquema pode mudar (a Câmara já avisou quebra em 2021). Busca por palavra-chave/tema não testada.
- **Verificação:** confirmado (testes). Fonte: WebFetch dos endpoints e do FAQ.

#### F2. API de Dados Abertos do Senado Federal

- **URL:** https://legis.senado.leg.br/dadosabertos/
- **Tipo:** oficial
- **Licença e termos (cópia e treino de IA):** Não verificado (termos não lidos).
- **Situação:** Teste em 16/10/2026: /materia/pesquisa/lista?sigla=PL&numero=2338&ano=2023 devolveu XML (PesquisaBasicaMateria v7; código 157233; ementa 'Dispõe sobre o uso da Inteligência Artificial'), mas o metadado do serviço o marca como depreciado em 18/03/2025 e desativado em 01/02/2026, com substituto /dadosabertos/processo. O substituto não pôde ser lido (permissão negada pela ferramenta): não verificado.
- **O que faz:** Matérias, tramitação, textos, votos, senadores.
- **Sobreposição (nenhuma):** Insumo.
- **Vale incorporar:** Usar só o endpoint novo (/processo) após testar; o PL 2338/2023 nasceu no Senado (matéria 157233) e consta na Câmara desde 17/03/2025, então a Câmara é a fonte do status atual; o Senado serve para PLs que ainda estão lá.
- **Riscos:** Endpoints antigos depreciados (o MCP senado-br-mcp ainda os usa). Formato XML.
- **Verificação:** parcial. Fonte: WebFetch.

#### F3. LexML Brasil (Rede de Informação Legislativa e Jurídica)

- **URL:** https://www.lexml.gov.br/
- **Tipo:** oficial
- **Licença e termos (cópia e treino de IA):** Licença/termos de uso não declarados nas páginas lidas: não verificado. Texto de lei não tem proteção autoral (art. 8º, IV, Lei 9.610/98).
- **Situação:** Ativo. Abas: Legislação, Jurisprudência, Proposições Legislativas, Doutrina. Serviço SRU documentado pelo Senado (resultados em XML), endpoint https://www.lexml.gov.br/busca/SRU. Cobertura segundo a Wikipédia (data da contagem não informada): federal 148.577, estadual 956.695, municipal 2.522.741 normas. Padrões: URN LEX e OAI-PMH.
- **O que faz:** Índice nacional de normas, proposições e jurisprudência com identificador URN estável.
- **Sobreposição (nenhuma):** Insumo.
- **Vale incorporar:** Fonte para verificar que cada norma citada no catálogo (federal e estadual) existe e para obter o URN/URL estável; checar vigência de normas estaduais quando o portal da assembleia não tem API. Chamar o SRU direto (o MCP LeXML-mcp é GPL).
- **Riscos:** Completude por UF desconhecida; atraso de indexação desconhecido; sem licença declarada.
- **Verificação:** parcial. Fonte: WebFetch Senado dados abertos, Wikipedia, vitrine do LeXML-mcp.

#### F4. Portal da Legislação do Planalto

- **URL:** https://www.planalto.gov.br/ccivil_03/
- **Tipo:** oficial
- **Licença e termos (cópia e treino de IA):** Art. 8º, IV, da Lei 9.610/98 (confirmado em planalto.gov.br/ccivil_03/leis/l9610.htm): não são objeto de proteção autoral os textos de tratados, leis, decretos, regulamentos, decisões judiciais e demais atos oficiais.
- **Situação:** Fonte canônica do texto federal compilado. API: não verificado (nenhuma API documentada foi encontrada nas leituras).
- **O que faz:** Texto compilado e histórico de alterações das normas federais.
- **Sobreposição (nenhuma):** Insumo.
- **Vale incorporar:** Texto-base do N1 federal e verificação de redação vigente (link por norma já no catálogo). Para alerta de alteração, comparar hash do HTML compilado mensalmente (esforço baixo).
- **Riscos:** HTML sem API; mudanças de layout quebram o comparador.
- **Verificação:** parcial. Fonte: WebFetch (Lei 9.610).

#### F5. Assembleias Legislativas (27 UFs): portais e dados abertos

- **URL:** https://www2.camara.leg.br/a-camara/estruturaadm/mesa/segundavice/interacao-legislativa/links-relacionados-1/legislativos-estaduais
- **Tipo:** oficial
- **Licença e termos (cópia e treino de IA):** ALESP e ALEPE: licença/termos não declarados nas páginas lidas. ALMG: leitura bloqueada por robots.txt (não verificado).
- **Situação:** A Câmara lista os 27 portais (al.ac.leg.br, al.al.leg.br, al.ap.leg.br, aleam.gov.br, al.ba.gov.br, al.ce.gov.br, cl.df.gov.br, al.es.gov.br, al.go.leg.br, al.ma.leg.br, al.mt.gov.br, al.ms.gov.br, almg.gov.br, alepa.pa.gov.br, al.pb.leg.br, alep.pr.gov.br, alepe.pe.gov.br, al.pi.leg.br, alerj.rj.gov.br, al.rn.gov.br, al.rs.gov.br, al.ro.leg.br, al.rr.leg.br, alesc.sc.gov.br, al.se.leg.br, al.sp.gov.br, al.to.leg.br). ALESP: arquivos XML (proposituras.xml, documento_andamento.xml, legislacao_normas.xml); portal CKAN 'em breve'. ALEPE: API de dados abertos, com pacote R 'alepe' v0.1.1 (30/09/2026, MIT) que inclui proposições legislativas. Estudo da SciELO Preprints (Vinicius Santos, Senado, 2025) compara as APIs das 26 assembleias e da CLDF e conclui 'forte assimetria e fragmentação técnica', mas o mapa por assembleia está no PDF, que não li.
- **O que faz:** Fonte primária da legislação e dos PLs estaduais.
- **Sobreposição (nenhuma):** Insumo.
- **Vale incorporar:** Adaptadores por UF em ordem de custo: SP (XML), PE (API), depois as demais conforme o PDF do estudo; as sem API ficam em revisão manual trimestral com URN do LexML. O catálogo UF guarda 'fonte_atualizacao' (api/xml/manual) por UF para o alerta de competência constitucional saber o que é checável automaticamente.
- **Riscos:** Fragmentação: 27 formatos. Raspagem pode violar termos; preferir API/arquivos abertos e respeitar robots.txt.
- **Verificação:** parcial. Fonte: WebFetch Câmara (lista), ALESP, CRAN alepe, SciELO Preprints.

#### F6. DataJud (CNJ) - API pública

- **URL:** https://datajud-wiki.cnj.jus.br/
- **Tipo:** oficial
- **Licença e termos (cópia e treino de IA):** Página oficial bloqueada para leitura na sessão (permissão): não verificado. Segundo comparativo da JUDIT (empresa concorrente, 'ponto de vista comercial'), há termo de uso que responsabiliza o usuário pelo uso e pela interpretação.
- **Situação:** Segundo a JUDIT: dá acesso a metadados de processos públicos (número CNJ, tribunal, grau, classe, assuntos, movimentos) e NÃO documenta texto integral; chave pública publicada e rotacionada pelo DPJ/CNJ, enviada no cabeçalho 'Authorization: APIKey ...'; limites e atraso de atualização não informados.
- **O que faz:** Metadados processuais.
- **Sobreposição (nenhuma):** Insumo marginal.
- **Vale incorporar:** Nada agora: o revisor trabalha com norma e regulação, não com processos. Reavaliar se quisermos 'litígio recente sobre o tema' no relatório.
- **Riscos:** Sem texto integral; metodologia de cobertura desconhecida.
- **Verificação:** parcial (fonte secundária). Fonte: WebFetch JUDIT.

#### F7. STJ - Portal de Dados Abertos (termo de uso)

- **URL:** https://bdjur.stj.jus.br/jspui/bitstream/2011/179190/Termo%20de%20Uso%20-%20Dados%20Abertos.pdf
- **Tipo:** oficial
- **Licença e termos (cópia e treino de IA):** Termo v1.0 (03/10/2023), contrato de adesão sem licença padrão nomeada: uso, reuso e redistribuição livres, inclusive comerciais; obrigatório indicar a fonte; não trata de robôs/raspagem; dados 'como estão', STJ pode alterar ou retirar dados sem aviso.
- **Situação:** Termo lido; o portal em si (dadosabertos.web.stj.jus.br) foi bloqueado: quais conjuntos de jurisprudência existem, formatos e frequência: não verificado.
- **O que faz:** Dados abertos do tribunal.
- **Sobreposição (nenhuma):** Insumo marginal.
- **Vale incorporar:** Modelo de termo permissivo: se usarmos dados do STJ (decisões sobre dados pessoais), basta indicar a fonte.
- **Riscos:** Dados podem ser retirados sem aviso.
- **Verificação:** parcial. Fonte: WebFetch do PDF do termo.

#### F8. Data Privacy Brasil e Observatório da Privacidade

- **URL:** https://www.dataprivacybr.org/
- **Tipo:** sociedade civil
- **Licença e termos (cópia e treino de IA):** Rodapé: conteúdo sob CC BY-SA 4.0 (copyleft: obras derivadas precisam da mesma licença).
- **Situação:** Newsletter, blog, podcast, Escola de Governança de Dados; área de governança 'monitora, analisa e incide em processos de governança digital'. O Observatório da Privacidade (observatorioprivacidade.com.br) tem seção 'Legislativo' que mapeia propostas no Congresso Nacional como 'página viva'; a captura lida parece de cerca de 2022; sem dataset, API nem cobertura estadual mencionados.
- **O que faz:** Análise e monitoramento de privacidade e regulação de IA no Brasil.
- **Sobreposição (nenhuma):** Fonte editorial.
- **Vale incorporar:** Assinar o boletim como gatilho de revisão manual do radar; linkar, não copiar.
- **Riscos:** SA: não ingerir texto no catálogo.
- **Verificação:** parcial. Fonte: WebFetch.

#### F9. IDMJR (dossiê de 183 proposições de IA), Lapin e LeisEstaduais.com.br

- **URL:** https://jornaldebrasilia.com.br/noticias/brasil/dossie-aponta-priorizacao-de-vigilancia-sobre-educacao-em-proposicoes-de-ia/
- **Tipo:** sociedade civil / comercial (não verificado)
- **Licença e termos (cópia e treino de IA):** Não verificado.
- **Situação:** Dossiê da Iniciativa Direito à Memória e Justiça Racial (IDMJR), divulgado em 08/04/2026: 183 proposições de IA, incluindo assembleias de RJ, SP, ES, PR e SC (2023-2025). A matéria não menciona conjunto de dados público. Lapin: nenhuma página encontrada: não verificado. LeisEstaduais.com.br: leitura falhou e a busca não retornou o site: não verificado.
- **O que faz:** Mapeia PLs de IA estaduais (dossiê).
- **Sobreposição (nenhuma):** Insumo.
- **Vale incorporar:** Usar o dossiê como lista de partida de PLs estaduais de IA para o radar (RJ, SP, ES, PR, SC) e ir buscar o status na fonte de cada assembleia.
- **Riscos:** Sem dados abertos; metodologia não vista.
- **Verificação:** parcial. Fonte: WebFetch Jornal de Brasília.

#### F10. OECD.AI Policy Navigator e IAPP Global AI Law and Policy Tracker

- **URL:** https://oecd.ai/en/dashboards/policy-initiatives/bill-no-2338-of-2023
- **Tipo:** organismo internacional / associação
- **Licença e termos (cópia e treino de IA):** OECD.AI: '© 2026 OECD. All rights reserved', remete aos Terms & conditions (não lidos); sem API ou download na página. IAPP: © 2024 IAPP, sem licença de reuso.
- **Situação:** OECD.AI tem entrada do PL 2338/2023 criada em 27/04/2026 e atualizada em 28/04/2026, status 'proposto/em desenvolvimento'. IAPP tracker (via aigl.blog): 28 páginas, 'last updated October 2024', inclui o Brasil (estratégia de IA, PL 2338/2023, parecer da ANPD).
- **O que faz:** Índices internacionais de políticas de IA.
- **Sobreposição (nenhuma):** Insumo para N3.
- **Vale incorporar:** Usar como lista de 'o que existe no mundo' para conferir lacunas do N3, citando por link. IAPP está defasado (out/2024).
- **Riscos:** Todos os direitos reservados: não ingerir.
- **Verificação:** parcial. Fonte: WebFetch.

## 7. Não verificado

- Termos de uso de Termly, TermsFeed, Privacy Tools, Confidata, Netlex, Juridoc, Contraktor, Harvey, Legora, Luminance, Spellbook, Jusbrasil: cláusulas de cópia e de treino de IA não lidas.
- Adequa, Vitreo, Datasafe, Lapin, LeisEstaduais.com.br, Nuvemshop e Remessa Online (geradores), cartilha OAB-PE/Sebrae-PE, eCFR MCP, Spellbook e 'Jurimetria' como produto.
- Repositórios que não pude clonar: ansvar-systems/brazil-law-mcp (licença e corpus), prof-ramos/LeXML-mcp (só página), dpo2u/dpo2u-mcp (só vitrine).
- URLs bloqueadas: lgpd.md, datajud-wiki.cnj.jus.br, dadosabertos.web.stj.jus.br, legis.senado.leg.br/dadosabertos/processo (permissão não respondida); dadosabertos.almg.gov.br e github.com/anthropics/claude-for-legal/tree/... (robots.txt); glama.ai brlaw_mcp_server (robots.txt); termly.io e termsfeed.com (termos) e npmjs.com (erro).
- Forks do claude-for-legal (API do GitHub inacessível), status atual do CICC (PLP 252/2023), checklist oficial da ANPD para pequeno porte, versão nova da API da Câmara, limites de requisição de qualquer API, data da contagem do LexML.
- Estudo SciELO Preprints sobre APIs das assembleias: li só o resumo, não o PDF.
