# Contratos de engenharia — 0.2.0

Este adendo especifica funções adicionadas à arquitetura [ARCHITECTURE.md](ARCHITECTURE.md), cuja tabela 0.1.0 permanece histórica. Agora são 39 plugins e 176 workflows. Quatro novos módulos locais e um CLI são código executável; sete novos workflows são instruções para revisão, não modelos treinados.

## Contratos de entrada e saída

| Módulo | Entrada | Saída | Não faz |
|---|---|---|---|
| citations.py | Texto UTF-8 e jurisdição explícita | Candidatos com spans, checksum e estado | Consultar tribunal, verificar vigência ou suporte |
| lexml.py | Bytes XML LexML de subconjunto declarado | Árvore de dispositivos e chunks por artigo | OCR, conversão texto/XML ou XSD integral |
| privacy.py | Texto, chave, escopo e spans opcionais | Pseudônimos e mapa de offsets | Inferência LeNER, anonimato ou liberação de egress |
| evaluation.py | Dados/labels/scores fornecidos | Métricas e abstenção | Treinamento, calibração ou julgamento |

O CLI é `python -m legal_br.engine`, a partir de `runtime/`. `--output` deve anteceder o subcomando. Saída já existente é recusada. A omissão desse parâmetro envia o JSON ao stdout, que pode conter texto pseudonimizado e dados identificadores: o operador deve proteger terminal e logs.

## Coordenação e fluxo

As funções são independentes e composáveis em processo, sem broker. Não existe um novo daemon nem integração transacional automática com a Workspace SQLite. XML exporta uma representação; sua integração persistente futura precisa conservar o vínculo de transformação com os bytes. Não reutilizar offsets do texto extraído como se fossem offsets do XML original.

Uma integração futura deve carregar `required_context_ids` antes de produzir conclusão. Conclusão sem a exceção referenciada é incompleta, mesmo que o próprio chunk caiba na janela do modelo. Unidades oversized não podem ser truncadas silenciosamente pelo consumidor.

A identidade de citação é de ocorrência no documento. A normalização de número ou caixa não muda sua superfície original. Existem referências que este parser não reconhece; ausência de resultado nunca equivale a texto sem citações. Remissões curtas são candidatos, não links jurídicos comprovados.

## Limites e micro-otimizações

Texto/XML até 10 MiB. XML: 96 níveis por padrão, máximo configurável 128; 100.000 elementos por padrão. DTD/entidades não são resolvidas. IDs duplicados são erro. Artigos são agrupados deterministicamente e mantêm proveniência.

Citações: até 50.000 ocorrências. Remissões curtas usam índices de início e de parágrafo, janela de candidatos limitada a 128 com indicador de truncamento. O parser não cria chamadas concorrentes a APIs.

Privacidade: até 100.000 spans por origem/entrada; detecção e união precedem HMAC. A biblioteca verifica o orçamento antes de materializar indefinidamente um iterável. Chave: 32–4.096 bytes. O comprimento não comprova entropia; o operador deve gerar segredo aleatório com fonte criptográfica e gerir rotação fora da biblioteca.

Avaliação: até um milhão de registros e dez mil rótulos por lista; o CLI também limita bytes. O tally percorre conjuntos efetivamente anotados, em vez de todos os rótulos do universo por exemplo. Essa contenção não substitui quotas de CPU/memória em serviço compartilhado.

## Fronteiras de segurança

A abertura de arquivo usa O_NOFOLLOW quando disponível e valida o descritor. Diretórios ancestrais e controle do host continuam responsabilidade do ambiente. Não chamar o CLI de sandbox. Nenhum comando possui capacidade de rede embutida ou autenticação corporativa.

A máscara não cobre toda PII; a revisão de privacidade é uma etapa externa. O campo `egress_authorized` não é um firewall: é uma declaração conservadora da saída. Um host com ferramentas livres pode enviar dados; a política deve ser imposta fora do modelo.

A prova de existência de uma citação, a validade da tese e sua aplicação são verificações separadas. Nem `syntax_valid`, nem revisão declarada, nem score liberam um ato externo. Mensagens de erro do CLI não ecoam dados secretos, identificadores ou caminhos recebidos.

## Documentação interativa

`apps/architecture/architecture.json` é o registro canônico: 31 nós e quatro vistas. Cada nó identifica entrada, saída, falha, limite, status, código e referências. Os 35 vínculos distribuídos pelas vistas podem representar dados, conceito, etapa humana ou dependência futura. Não representam uma DAG completamente executada.

`reactflow.mjs` usa a biblioteca React Flow real. `ui.js` implementa navegação local independente. O modo local é inicial e não carrega rede. Em telas pequenas, a lista acessível é selecionada automaticamente. As duas superfícies usam os mesmos contratos. O JSON exportado reproduz o registro, sem dados de processos.

O build local das bibliotecas é opcional e não foi executado nesta sessão. O viewer fornecido permite ativação de CDN após ação do usuário; sem conexão mantém o modo local. O pacote não afirma bundle vendorizado ou instalação npm testada.
