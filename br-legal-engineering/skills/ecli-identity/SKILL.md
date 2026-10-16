---
name: ecli-identity
description: "ECLI: identidade sem inferir força jurídica: Registro de sintaxe, existência pendente e diferenças entre processo, decisão e tese."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
---
# ECLI: identidade sem inferir força jurídica

Leia a [política embarcada](../../references/POLICY.md). Este workflow é invocado explicitamente; não agenda nem autoriza envio de dados ou protocolo jurídico.

## Entradas mínimas
Identificador ECLI integral, país de origem e fonte declarada.

## Procedimento
Conferir os cinco componentes sintáticos e possíveis pontos finais ambíguos. Consultar cadastro nacional e decisão apenas quando ferramenta autorizada existir. Não criar equivalência com CNJ, URN Lex ou número de recurso. Relações de suporte/contradição exigem trecho, revisão e contexto jurisdicional.

## Saída contratada
Registro de sintaxe, existência pendente e diferenças entre processo, decisão e tese.
Preservar fatos e hipóteses separados. Estados: satisfeito_no_escopo, nao_conformidade_evidenciada, inconclusivo, nao_aplicavel_justificado, erro. Fonte, data, localizador e revisão devem acompanhar a entrega. Falha de ferramenta não significa conformidade.

## Ferramenta local disponível
No repositório, a implementação é `runtime/legal_br/citations.py`. A skill não tem Bash e não a executa implicitamente. O operador pode invocar o comando abaixo na raiz do runtime (exceto comandos com scripts/ ou apps/, executados na raiz do repositório):
```bash
python -m legal_br.engine ecli ECLI:NL:HR:2020:1
```
O operador fornece arquivos reais e autorizados. Não inventar resultados quando o arquivo, dependência ou modelo não estiver disponível.

## Caso adversarial obrigatório
Um ECLI sintaticamente válido contém tribunal não registrado; a saída deve manter registry_verified e existence_verified como false.

## Proveniência e conceito
- European Case Law Identifier · Portal Europeu da Justiça: https://eur-lex.europa.eu/content/help/eurlex-content/ecli.html
  Conceito: Identificador de decisão com cinco componentes e metadados harmonizados.
  Limite: ECLI não é uma ontologia completa, não cria força vinculante e não comprova adoção de ECLI pelo Brasil.

## Garantia efetiva
Os testes de engenharia não medem acurácia jurídica da skill. Nenhuma conclusão profissional ou liberação de egress decorre automaticamente deste workflow. Não corrigir silenciosamente o material do usuário; indicar a diferença entre texto fornecido, pesquisa e inferência.
