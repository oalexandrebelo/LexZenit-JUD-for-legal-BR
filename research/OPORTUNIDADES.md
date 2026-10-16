# Claude para Jurídico — oportunidades incorporadas na versão 0.2.0

**Base:** camada brasileira 0.1.0 anexada nesta conversa. **Pesquisa:** projetos e fontes primárias conferidos em 14/10/2026. **Entrega:** evolução independente; não é fork completo do upstream, corpus nacional integral ou classificador jurídico treinado. A autorização de publicação foi recebida, mas a sessão não conseguiu criar o repositório remoto.

A matriz estruturada completa, inclusive licenças observadas e caminhos de implementação, está em [references.json](references.json). Não existe download de repositório, dados ou pesos durante o uso dos módulos brasileiros. A referência internacional informa o desenho; não define o Direito aplicável.

## 1. O que as referências efetivamente sustentam

| Referência | O que o projeto ou padrão oferece | Aproveitamento nesta release | O que não foi incorporado |
|---|---|---|---|
| Free Law Project / eyecite | Extração, anotação e agregação de citações jurídicas, predominantemente americanas | Parser BR original com spans e estados de resolução; adaptador opcional get_citations para material dos EUA | Gramática americana como regra brasileira; validação automática de existência ou força do precedente |
| LexML Parser | Parser de documentos normativos no ecossistema LexML, não mero divisor por tokens | Leitor XML original de subconjunto LexML, árvore e divisão por família de artigo | Implementação GPL, conversão de texto livre/PDF, validação XSD integral ou compilação do parser Scala/Java |
| LeNER-Br | Dataset/tarefa de NER jurídico em português e recursos de anotação | Adaptador BIO estrito e camada própria de pseudonimização local | Checkpoint neural, corpus redistribuído, detector universal de PII ou certificado de conformidade LGPD |
| ECLI oficial | Identificador uniforme de decisão com cinco componentes e metadados harmonizados | Parser sintático e separação entre identificador, processo, decisão e relação de evidência | Ontologia pronta de Direito brasileiro ou atribuição automática de força vinculante |
| Open-ECLI-Utils | Nome informado na solicitação, não confirmado por busca exata confiável | Registro explícito da lacuna; nenhuma dependência adicionada | URL, autor, licença, API ou implementação inventados |
| THUNLP / CAIL2018 | Tarefas e benchmarks chineses de predição de artigos aplicáveis, acusações e penas | Separação de tarefas; harness BR de métricas, partições e triagem seletiva | Rótulos penais, teses, pesos chineses ou modelo de previsão de resultado judicial no Brasil |

A construção de partições por caso/hash/tempo, a política de abstenção e a pseudonimização HMAC são **decisões adicionais desta engenharia**. Não são atribuídas indevidamente como características implementadas por todos os projetos citados.

## 2. eyecite: o ganho está no contrato da citação

Fonte primária: https://github.com/freelawproject/eyecite. Artigo: Cushman, Dahl e Lissner, *eyecite: A Tool for Parsing Legal Citations*, JOSS 6(66), 3617, 2021: https://joss.theoj.org/papers/10.21105/joss.03617.

Uma extração útil mantém superfície original, offsets, categoria, componentes e identidade da ocorrência. Número de processo, acórdão específico e tese são entidades diferentes. A numeração CNJ identifica um processo; vários atos podem existir sob o mesmo número. Uma extração lexical não prova existência do processo, vigência da norma, aderência fática ou suporte semântico.

Implementação: `runtime/legal_br/citations.py`. Reconhece um conjunto explícito de referências normativas, dispositivos, súmulas, classes processuais, CNJ, ECLI e remissões curtas. Os offsets contam codepoints Unicode no texto original, não bytes UTF-8 nem páginas de PDF. A assinatura da ocorrência inclui hash do documento, tipo e intervalo. Autoridade não informada e ano com dois dígitos permanecem ambíguos. O checksum CNJ, quando válido, recebe status matemático, não confirmação do tribunal.

A remissão Id./supra não é ligada automaticamente à referência mais próxima. Candidatos no parágrafo são apresentados; o conjunto é limitado e o truncamento é explícito. Índices de início e de parágrafo evitam revarrer o documento inteiro para cada remissão. Existe orçamento de 50.000 ocorrências; excedê-lo gera bloqueio, nunca resultado incompleto sem aviso.

A adaptação US chama a API real do eyecite somente na rota explicitamente escolhida. Dependência ausente é erro. Ela não foi instalada nem executada nesta sessão. O parser nacional funciona sem eyecite.

**Prioridade P0:** impedir que uma citação produzida por modelo ganhe status de autenticada apenas por ter formato convincente. **Critério de promoção:** corpus BR adjudicado, precisão/recall por tipo, corpus adversarial de negação/abreviação, consulta oficial separada e verificação de suporte. Os testes atuais verificam engenharia, não esse benchmark jurídico.

## 3. LexML: preservar exceções antes de aumentar contexto

Fontes primárias: https://github.com/lexml/lexml-parser-projeto-lei e https://www.lexml.gov.br/. O parser consultado é identificado como GPL-2.0. Sua implementação não foi copiada. Não basta colocar um processo separado para presumir eliminadas obrigações de licença; uma futura integração deve analisar o modo concreto de distribuição, modificação e ligação.

Implementação própria: `runtime/legal_br/lexml.py`. O leitor recebe XML UTF-8 no namespace declarado, rejeita entidades/DTD e impõe limites de bytes, profundidade e elementos. Conserva hash dos bytes, IDs fornecidos, XPath, ordem e ascendência. Unidade sem ID recebe localizador gerado explicitamente, sem fingir identificador oficial.

Caput, parágrafo, inciso, alínea e item permanecem identificáveis. Os chunks agrupam famílias de artigo. Quando a família precisa ser dividida, `required_context_ids` informa as demais unidades da família; o consumidor deve recuperá-las antes de analisar regra e exceção. Um dispositivo individual maior que a janela não é cortado: permanece inteiro e recebe `oversized=true`, permitindo outra rota ou rejeição consciente.

A presença de alteração citada não modifica automaticamente a norma alvo. Texto de projeto, transcrição de redação anterior e dispositivo em vigor precisam de proveniência e tempo próprios. O leitor marca a estrutura citada; não decide sua eficácia jurídica.

O resultado declara `xsd_validated=false` e `source_authenticity_verified=false`. Não existe importação de PDF, OCR ou parser de texto livre neste módulo. A rota de evidências herdada continua recebendo TXT/MD. A integração transacional entre XML e o armazenamento de documentos não foi implementada; o CLI exporta um artefato estruturado para revisão, sem alegar pipeline completo.

**Prioridade P0:** reduzir a perda de exceções, hierarquia e remissões por divisão arbitrária. **Critério de promoção:** XMLs oficiais de diferentes órgãos, tabela de recursos suportados/rejeitados, validação XSD versionada e medição de cobertura estrutural, com ligação verificável ao original.

## 4. LeNER-Br: NER não encerra a proteção de dados

Fontes primárias: https://github.com/peluz/lener-br e https://teodecampos.github.io/LeNER-Br/. O repositório consultado apresenta licença MIT; datasets, checkpoints e cada forma de distribuição ainda precisam de exame próprio. Nenhum deles foi redistribuído aqui.

Implementação: `runtime/legal_br/privacy.py`. O adaptador recebe o texto e tokens/rótulos BIO alinhados, rejeitando continuação I- inválida, texto omitido e cauda desalinhada. Pode receber spans de revisão humana ou modelo local autorizado. Não executa inferência NER nem usa nomes fictícios como substituto de um modelo real.

Detectores adicionais identificam CPF, e-mail e telefone formatado. CPF com checksum inválido também pode representar informação pessoal ou tentativa de identificação e é mascarado. Essa decisão favorece proteção, mas pode gerar falsos positivos; referências numéricas precisam ser revistas. Dados indiretos, endereço, RG, nome, biometria, saúde e combinações identificadoras não são cobertos integralmente.

As sobreposições são unidas antes da substituição, evitando que a prioridade de uma entidade exponha o sufixo de outra. A pseudonimização usa HMAC-SHA-256 sobre representação estruturada que inclui tenant, caso, categoria e valor. O mesmo valor recebe pseudônimo estável no mesmo escopo; em outro caso ou chave, muda. A representação estruturada evita colisões triviais de delimitadores. O identificador é truncado a 128 bits; não é prova matemática de unicidade universal.

A chave permanece como entrada local. O módulo não a serializa, não publica mapa reverso e não cria um cofre autenticado. O CLI cria saídas novas com permissão restrita; na leitura da chave verifica o descritor aberto e rejeita permissões de grupo/outros em POSIX. Permissões no sistema de arquivos não substituem criptografia em repouso ou controle de acesso institucional.

A cópia pseudonimizada, offsets e hashes ainda merecem proteção. Dados podem permanecer reidentificáveis por correlação. Toda saída conserva `anonymity_guaranteed=false`, `pii_coverage=partial_requires_review` e `egress_authorized=false`. A decisão de compartilhar é externa a esta biblioteca.

**Prioridade P0:** fronteira local antes de uma futura chamada a LLM externo. **Critério de promoção:** avaliação por entidade e span, recall de classes críticas, testes de reidentificação, política de retenção, controle autenticado e teste de egress. Não usar apenas F1 de tokens para declarar documento seguro.

## 5. ECLI: identidade uniforme não é ontologia de precedentes

Fonte primária acessível: https://eur-lex.europa.eu/content/help/eurlex-content/ecli.html. A documentação descreve prefixo, país, corte, ano e ordinal. A corte tem de um a sete caracteres; o parser preserva a diferença entre validade sintática e confirmação no registro nacional. A capitalização é normalizada sem mudar o texto original da ocorrência.

A busca pelo nome exato `Open-ECLI-Utils` não identificou correspondência confiável. Essa conclusão é limitada à pesquisa realizada; não prova que o projeto inexista. O nome não virou pacote instalável, licença presumida ou URL inventada.

O benefício para o grafo brasileiro é de modelagem: manter identidades e proveniência explícitas. Arestas como cita, interpreta, distingue, modifica ou revoga não podem ser inferidas pelo simples compartilhamento de um identificador. O grafo herdado aceita relações propostas e revisadas com prova; não autentica o revisor nem confere automaticamente a correção jurídica da aresta.

A estrutura ECLI não deve ser artificialmente aplicada a julgados brasileiros. Um identificador `ECLI:BR:...` sintaticamente aceitável continua com registro e existência não verificados. CNJ, URN Lex e ECLI possuem escopos diferentes, sem conversão automática.

**Prioridade P1:** interoperabilidade de fontes estrangeiras e saneamento de identidade. **Critério de promoção:** resolvedores autorizados por jurisdição, reconciliação de documentos duplicados, versões de decisões e relações com prova/tempo/revisor.

## 6. CAIL: aproveitar avaliação, não importar o julgador

Fontes: Xiao et al., *CAIL2018: A Large-Scale Legal Dataset for Judgment Prediction*: https://arxiv.org/abs/1807.02478; Zhong et al., *Overview of CAIL2018*: https://arxiv.org/abs/1810.05851; código e submissões: https://github.com/china-ai-law-challenge/CAIL2018.

Os trabalhos definem tarefas específicas sobre fatos de casos chineses, incluindo artigos aplicáveis, acusações e penas. A oportunidade não é converter automaticamente esse conhecimento em Direito brasileiro. A adaptação feita aqui é avaliar tarefas delimitadas e não esconder desempenho ruim sob uma métrica agregada.

`runtime/legal_br/evaluation.py` valida partições train/dev/test. Impede compartilhamento de caso ou digest entre partições e exige treinamento até o corte temporal e holdout posterior. A data deve representar disponibilidade efetiva da informação, não uma data retrospectiva conveniente. IDs verdadeiros e equivalências semânticas ainda precisam de curadoria: o código não descobre que dois IDs diferentes são o mesmo processo.

As métricas incluem micro/macro F1, TP/FP/FN por classe, cobertura e acerto exato seletivo. Abstenções sem predição contribuem para falso negativo de rótulo presente no denominador completo; não são retiradas da amostra para inflar desempenho. Classes sem suporte recebem zero segundo a política explícita do código; interpretações precisam considerar esse denominador.

A triagem aceita scores fornecidos por um modelo realmente executado, limiar, margem mínima e declaração de domínio. Empate, margem baixa ou OOD declarado resultam em abstenção. Score não é probabilidade calibrada. O módulo não detecta OOD autonomamente, não treina, não carrega checkpoint e não toma decisão jurídica.

**Prioridade P1:** criar uma avaliação BR antes de comparar fornecedores de modelo. **P2 de pesquisa:** similar-case matching, como CAIL2019-SCM, pode inspirar pares positivos/negativos para avaliar recuperação de casos; ainda não incorporado ou benchmarkado. Semelhança textual nunca substitui análise de tese e força do precedente. Referência adicional: https://arxiv.org/html/1911.08962v3.

## 7. Decisões de arquitetura que evitam dependência

O core brasileiro usa biblioteca padrão Python para os quatro novos módulos. A calculadora herdada mantém Pydantic/Decimal. eyecite é um adaptador opt-in, não biblioteca necessária para analisar documentos BR. LexML, LeNER e CAIL são referências conceituais, sem clone em runtime, download de pesos ou código vendorizado. Trocar um LLM futuro não altera os identificadores das evidências.

O viewer usa um registro único de nós/arestas. React Flow é biblioteca real de visualização, não desenho apresentado como sistema rodando. A primeira carga local não faz requisição. A ativação explícita pode carregar React/React Flow por CDN; a alternativa de build incorpora as dependências e remove esse acesso em runtime. Sem rede, grafo nativo e lista permanecem utilizáveis. Não há fontes externas, telemetria ou upload de processos.

Orçamentos de bytes, elementos, entidades, ocorrências e candidatos impõem contenção local. Não há promessa de TTFT, custo por documento ou desempenho jurídico. O mesmo rigor se aplica ao roadmap: conector oficial, modelo NER, classificador treinado, autenticação e atos externos têm status pendente.

## 8. Licença, distribuição e publicação

O código original desta camada permanece Apache-2.0. eyecite é BSD-2-Clause; o parser LexML é identificado como GPL-2.0; os repositórios LeNER-Br e CAIL2018 consultados têm MIT. A licença de cada recurso não autoriza uso irrestrito de dados pessoais nem de todos os arquivos ligados. Não foram distribuídos datasets ou checkpoints.

A versão anterior continua identificada por sua revisão local. O pacote atual é uma camada independente preparada para composição com o upstream, sem afirmar clonagem integral concluída. Os scripts recusam sobrescrita e force push; publicação independente e montagem de derivação do upstream são operações separadas. O relatório em `evidence/publication-attempt.json` registra as limitações observadas nesta sessão.
