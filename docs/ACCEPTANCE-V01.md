# Aceitação da versão 0.1.0

## Resultados executados nesta entrega

**132 testes aprovados:** 119 do runtime (65 herdados e 54 adicionais) e 13 do repositório/montagem. Logs: `evidence/runtime-tests.txt`, `evidence/repository-tests.txt`; relatório estruturado: `evidence/test-report-v0.1.0.json`.

Ambiente: Python 3.13.5, SQLite 3.46.1, Linux, Pydantic 2.13.5. Durações desta execução: runtime 2.243 s; repositório 0.277 s. Esses números **não são latência de análise jurídica ou benchmark GPU**.

O validador próprio confirmou 38 plugins, 169 skills, 182 fontes e 169 especificações semânticas, além das referências da ontologia. JSON e frontmatter produzidos seguem as convenções definidas; não houve execução do CLI oficial do Claude Code.

## Cobertura dos testes de software

Ingestão idempotente, tamanho/formato/UTF-8, preservação de bytes e BOM, inputs inválidos, caso divergente, banco estrangeiro recusado sem adição de tabelas, symlink, citações falsas, offsets, timestamps com fuso, eficácia desconhecida, períodos semiabertos, conhecimento histórico, rejeição posterior, busca literal, relações propostas/revistas/rejeitadas, prova inelegível, ciclos, limites de nós/arestas, rollback, adulteração simples, comparação de âncora, CLI real, manifesto, catálogo e montagem em repositório Git sintético real.

O conjunto herdado cobre contratos, gate, cálculos Decimal, intervalos de disponibilidade, fronteiras de preço/garantia e DAG local. Atestação jurídica não é determinada por esses testes.

## Não executado

Clone integral do upstream nesta sessão; criação/push no GitHub; CI remoto; matriz Python 3.11; instalação/validação em Claude Code; 169 avaliações semânticas; revisão profissional de todos os workflows; conectores reais; OCR/PDF/tabelas; GPU/LLM; PostgreSQL/pgvector/Neo4j; autenticação corporativa; assinatura/KMS/WORM; protocolo judicial ou administrativo.

A configuração de CI está incluída com actions fixadas em SHAs consultados, permissão de leitura, sem secrets/deploy e matriz Python 3.11/3.13. Seu resultado remoto não é presumido. A dependência Python e suas dependências diretas estão pinadas nas versões testadas; não foram produzidos hashes de wheels nem auditada toda a cadeia de distribuição.

## Casos semânticos

`evals/semantic-cases.jsonl` contém 169 especificações. São insumos para avaliação posterior com corpus autorizado, modelo identificado e revisão humana. Não representam acurácia, recall ou taxa de aprovação já medida.

Critérios de homologação proposta: citação existente com localizador; suporte material; norma temporalmente aplicável; exceções consideradas; abstenção quando insuficiente; ausência de fatos inventados; dado privado não enviado em consulta pública; nenhum ato externo sem autorização da versão exata. Especificar denominador e estratificação por domínio antes de calcular percentual.

## Publicação

Destino previsto: `oalexandrebelo/claude-for-legal-br`. **Nenhum repositório remoto foi criado por esta entrega.** A montagem real requer rede; a publicação requer GitHub CLI autenticado. O script padrão cria privado e recusa sobrescrita. Não existe badge de CI verde ou release remota alegada.
