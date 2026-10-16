# Contratos de engenharia — 0.3.0 · revisor jurídico de projetos

O plugin `ab-lexzenit-project-review` e o motor `runtime/lz_revisor` mapeiam o que um projeto de IA, SaaS ou startup precisa cumprir, e o que já tem, em três níveis. Agora são 40 plugins e 182 workflows. O motor é código executável, só com a biblioteca padrão do Python. As seis skills são instruções somente leitura.

Nome: o plugin se chama `ab-lexzenit-project-review` (marca AB LexZenit Project Review). O prefixo `ab-lexzenit-` fica reservado a produtos LexZenit da AB ED&IA; o validador aceita `br-` (áreas do Direito) e `ab-lexzenit-`.

## Níveis

| Nível | Escopo | Quando é aplicável |
|---|---|---|
| N1 · Brasil | União (`BR`) e 27 UFs (`BR-XX`) | União sempre; UF quando é sede ou está em `ufs_atuacao` |
| N2 · país | EUA por padrão (federal `US` e estados `US-XX`) ou outro país soberano | País em `paises_alvo`; estado americano só com `us_estados`; sem usuários declarados, **prontidão** |
| N3 · mundo | UE extraterritorial, tratados (`INT`) e padrões (`ISO`); leis nacionais de outros países (`CN`, `KR`) | UE/INT/ISO como prontidão; país nacional só quando está no alcance |

Escolha do N2, na ordem: `pais_n2` fixado → `mercado_principal` (país estrangeiro com maior receita ou usuários) → EUA entre os alvos → primeiro país estrangeiro (membro da UE leva o regime europeu) → sinal de público na UE ou no Reino Unido → EUA. A ponderação da exposição real é decisão profissional: o questionário a recebe por `mercado_principal` ou `pais_n2`.

## Legislação como código

`ab-lexzenit-project-review/references/catalog/`:

| Arquivo | Conteúdo |
|---|---|
| `sinais.json` | 50 características do projeto. Detectores: dependências, caminhos e regex por linha. Algumas só vêm do questionário. `confianca_dependencias` rebaixa indícios fracos (SDK de nuvem pode estar em região brasileira). |
| `evidencias.json` | 38 evidências esperadas: documentos (globs; sem extensão explícita, só casam .md, .pdf, .html, .txt, .docx), menções (termos com fronteira de palavra) e minuta que fecha a lacuna |
| `questionario.json` | Campos (UF, países, mercado principal, estados, estágio) e perguntas por sinal |
| `regra-n2.json` | Regra N2 e jurisdições com pacote |
| `normas/*.json` | 210 normas: `n1-federal` (19), `n1-uf` (152), `n2-eua` (19), `n2-alternativos` (7), `n3-global` (13) |
| `ufs.json` | Cobertura por UF e dúvidas de pesquisa |

Cada norma tem nível, jurisdição, status (`vigente`, `parcialmente_vigente`, `vigencia_futura` com `vigencia.inicio`, `em_tramitacao`, `suspensa`, `revogada`), fonte com estado de verificação (`oficial_conferido` exige URL e data; `fonte_secundaria`; `nao_localizado`), relevância (`obrigacao` ou `oportunidade`), gatilho e obrigações. Cada obrigação tem dispositivo, natureza (`obrigacao_legal`, `boa_pratica`, `exigencia_mercado`, `vedacao`), severidade, evidências e minuta. A norma pode trazer `alerta_competencia` (por exemplo, lei estadual que impõe dever de dados pessoais a particular, EC 115/2022), que aparece no relatório. O motor recusa catálogo com sinal ou evidência desconhecidos, ID duplicado, jurisdição N1 inválida, fonte oficial sem data ou vigência futura sem início.

## Avaliação

Gatilhos usam lógica de três valores (Kleene): `todos`, `algum`, `nao`. Sinal não detectado é `falso` com ressalva; sinal sem detector e sem resposta é `desconhecido` e vira pergunta. Estados das obrigações seguem `docs/POLICY.md`:

- **`nao_conformidade_evidenciada`** só quando todas valem: jurisdição aplicável (não prontidão), norma vigente na data, fonte `oficial_conferido`, natureza `obrigacao_legal`, dispositivo identificado, sem alerta de competência, gatilho com confiança alta ou média e nenhuma evidência no escopo.
- **Vedação** (o que o produto não pode fazer) nunca é firme: falta de documento não prova a prática.
- País só **detectado** no código (moeda, idioma) fica em prontidão; aplicável exige `paises_alvo`. Com EUA no alcance e sem `us_estados`, a norma estadual fica desconhecida e gera pergunta.
- Com varredura truncada ou exclusões do `.lzrevisorignore`, sinal não detectado vira desconhecido.
- Respostas com tipo errado (`"false"` em texto, UF em texto em vez de lista, sinal inexistente) são recusadas.
- **`inconclusivo`** para lacuna sem esses requisitos, para evidência localizada (documento existir não prova conformidade) e para resposta pendente.
- **`nao_aplicavel_justificado`** com o motivo (gatilho ausente, UF ou país fora do alcance).
- **`satisfeito_no_escopo`** nunca é declarado pelo motor.

Projeto de lei e norma suspensa vão para o radar regulatório; sandbox, fomento e compras de inovação vão para oportunidades.

## Superfícies

| Superfície | Uso |
|---|---|
| CLI | `python -m lz_revisor revisar <projeto> --respostas r.json --saida dir/` (não sobrescreve), `perguntas`, `normas`, `minutas`, `minuta`, `validar-catalogo` |
| CI | `revisar --sarif revisao.sarif --falhar-em alta`: SARIF 2.1.0 com o local do gatilho (`arquivo:linha`) e código de saída 3 quando há não conformidade da severidade pedida ou maior. `--data AAAA-MM-DD` avalia a vigência na data dos fatos. |
| Radar | `python -m lz_revisor radar`: status de cada projeto de lei do catálogo na API de dados abertos da Câmara, com a marca do que mudou desde a conferência. Único comando com rede; nunca altera o catálogo. |
| MCP stdio | `claude mcp add lz-revisor -e PYTHONPATH=<repo>/runtime -- python3 -m lz_revisor mcp --raiz <pasta>`. Sete ferramentas. Lê só dentro de `--raiz`, não escreve, não executa código do projeto, não acessa rede. |
| Skills | `/ab-lexzenit-project-review:revisar-projeto`, `mapa-uf`, `escolher-n2`, `classificar-risco-ia`, `kit-documentos`, `atualizar-catalogo` |

O MCP é habilitado pelo operador. O plugin não traz `.mcp.json` nem hooks, conforme a política do repositório. O relatório registra caminho e linha de cada indício, nunca o texto casado.

## Rastreabilidade e verificação

- **Proveniência:** cada resultado traz a versão do motor, a data de referência, o SHA-256 do catálogo e o das respostas, e quais sinais foram declarados ou detectados.
- **Respostas que o código contradiz:** quando o questionário diz "não" e o scanner encontra indício, o relatório lista arquivo e linha (`divergencias`); a resposta declarada continua valendo.
- **Identificadores:** leis federais têm `urn` no padrão URN LEX do LexML.
- **CPF e CNPJ (inclusive alfanumérico):** só contam com dígito verificador válido (`lz_revisor/validadores.py`). O valor nunca entra no relatório.

## Não faz

O motor não emite parecer, não interpreta conteúdo de documento, não confere a vigência na data dos fatos, não acessa fontes online e não substitui a pesquisa de normas municipais e setoriais. A cobertura estadual depende da pesquisa de 16/10/2026: ausência de norma no catálogo não prova ausência de norma.

## Revisão independente

Antes da entrega, um revisor separado, somente leitura, testou o motor com projetos sintéticos. Corrigido o seguinte, cada item com caso de regressão em `runtime/tests/test_lz_revisor.py`:

- "EUR" no código tornava a UE aplicável.
- Resposta `"false"` em texto virava verdadeiro.
- Vedação era firme por falta de documento.
- Sete normas estaduais estavam como oficiais sem leitura integral e foram rebaixadas.
- Decretos estaduais de LGPD figuravam como obrigação do fornecedor e passaram a boa prática.
- SDK de e-mail acionava o cadastro de telemarketing.
- O alerta de competência não chegava ao relatório.
- Globs de evidência casavam `CLAUDE.md` e `calendar.ts`.
- FIFO travava a varredura.
- Regex quadrática em `go.mod` e `Gemfile`.
- Estado americano sumia quando os EUA não eram o N2.
- O art. 24 do ECA Digital não estava restrito a redes sociais.

Ficaram como limitação conhecida:

- Vigência por obrigação, como a carência do AI Act art. 50(2), não é modelada.
- O AI Act aceita apenas `paises_alvo`, sem distinção de província ou subdivisão.
- `.env.example` não é lido.

