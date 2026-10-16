# Novidades 0.2.0 — engenharia local

Execute os exemplos da seção CLI do README. Abra `apps/architecture/index.html` para explorar os quatro mapas. Os dados em `runtime/examples/engineering/` são sintéticos, não documentos de clientes.

Pseudonimização requer chave privada criada pelo operador, fora do repositório. Em ambiente POSIX, um exemplo de geração é:

```bash
(umask 077; set -C; openssl rand 32 > "$HOME/.legal-br-case-key.bin")
cd runtime
python -m legal_br.engine --output saida-privada.json privacy \
  --file examples/engineering/privacy.txt \
  --key-file "$HOME/.legal-br-case-key.bin" --tenant laboratorio --matter sintetico
```

Não execute o comando de geração sobre uma chave existente em uso. A rotação altera pseudônimos e requer plano de migração. `saida-privada.json` não pode existir antes da execução; permaneça fora do controle de versão. O exemplo contém um nome que o detector de padrões não reconhece: esse resíduo é intencional e demonstra a necessidade de NER/revisão, não uma garantia de proteção completa.

A publicação independente agora possui `scripts/publish_independent.sh`; o roteiro histórico abaixo continua exigindo montagem do upstream. A instalação Claude, autenticação de revisores e integração com serviços oficiais não foram executadas.

---

# Execução local e revisão verificável

## Ambiente

O runtime local de evidências usa Python e SQLite FTS5, sem dependência de GitHub, LLM ou API externa. Trabalhe em pasta privada fora do repositório para casos reais. O exemplo abaixo usa apenas **texto sintético** e não representa lei, contrato ou decisão real.

Execute a partir da pasta `runtime`:

```bash
mkdir -p _workspace
printf 'DOCUMENTO SINTÉTICO DE TESTE.
A garantia contratual deste exemplo será revisada pelo responsável.
' > _workspace/exemplo.txt
python3 -m legal_br --db _workspace/caso.sqlite --matter caso-demo init
python3 -m legal_br --db _workspace/caso.sqlite --matter caso-demo ingest \
  --file _workspace/exemplo.txt --source-id fixture-local \
  --title 'Exemplo sintético' --kind case
python3 -m legal_br --db _workspace/caso.sqlite --matter caso-demo search \
  --query garantia --effective-on 2026-10-13
```

A primeira busca padrão retorna zero documentos elegíveis: o original foi armazenado, mas não foi revisto. Esse resultado é correto. Para inspecionar conteúdo ainda não atestado:

```bash
python3 -m legal_br --db _workspace/caso.sqlite --matter caso-demo search \
  --query garantia --effective-on 2026-10-13 --include-unverified
```

A saída informa `document_id`, `id` do chunk, conteúdo, linhas, offsets e status. Para eliminar edição manual de identificadores neste tutorial, use a API Python; ela realiza exatamente a mesma operação:

```bash
python3 - <<'PY'
from pathlib import Path
from legal_br import Workspace
with Workspace('_workspace/caso.sqlite', 'caso-demo') as ws:
    document = ws.ingest_file(Path('_workspace/exemplo.txt'), source_id='fixture-local',
                             title='Exemplo sintético', kind='case')
    ws.attest(document['document_id'], reviewer='revisor-local-de-teste',
              reason='Texto sintético conferido para demonstrar o fluxo.', status='reviewed')
    report = ws.search('garantia', effective_on='2026-10-13')
    print(report)
    print(ws.integrity())
PY
```

O revisor é uma **identidade declarada**, não autenticada. Não registrar a demonstração como parecer.

## Normas e tempo

Documentos `kind=normative` exigem atestação com `valid_from` para ingressar na busca padrão. `valid_until` é exclusivo: `[início,fim)`. Revisão sem início permanece `unknown_legal_time`. `effective_on` é a data de aplicação; `known_at` é a data-limite de conhecimento, com fuso obrigatório.

Data de observação, registro local e intervalo jurídico não são intercambiáveis. Uma norma ingerida hoje não pode aparecer como conhecida pelo workspace ontem. Atestações são acrescentadas; a última conhecida no snapshot determina a elegibilidade. Rejeição posterior não apaga a atestação histórica.

O runtime não descobre vigência, revogação, modulação ou alcance territorial. Esses dados precisam ser informados e revistos. Um diploma com períodos diferentes por dispositivo deve ser representado por unidades distintas; não atribuir a ele uma vigência única por conveniência.

## Grafo

`link` registra uma proposta entre chunks com citação exata de evidência. Existência da citação não prova suporte semântico. `review-link` registra revisão da proposta. A expansão exige relação revista, endpoints e prova elegíveis. `supports` não certifica interpretação.

A busca usa BM25/FTS5, até 1.000 candidatos lexicais, no máximo 100 seeds, até três saltos, até 1.000 nós e orçamento global configurável de arestas. Os padrões são menores; truncamentos aparecem na saída. Não há embeddings, reranking neural, resumos de comunidades, extração automática de entidades ou geração textual.

## Integridade e backup

`verify` confere cadeia local, hashes, fingerprints e correspondência de chunks com originais. A cabeça pode ser guardada externamente e passada como `--expected-head` para detectar remoção de cauda contra essa âncora. Isso não é assinatura nem WORM; administrador capaz de reescrever base e âncora continua fora da garantia.

SQLite usa WAL. Não copiar somente o arquivo principal durante escrita ativa. Para backup consistente, usar API de backup do SQLite e manter âncora em fronteira administrativa distinta quando exigido. Esse armazenamento externo não está implementado.

PDF, binário, texto vazio, UTF-8 inválido, symlink, documento maior que 10 MiB, timestamp sem fuso, identificador desconhecido, citação inexistente e parâmetros fora dos limites são rejeitados. Caminho incorreto em consulta não cria base silenciosamente: inicializar explicitamente.

A ferramenta é local e não multiusuário. Permissões de filesystem continuam indispensáveis.
