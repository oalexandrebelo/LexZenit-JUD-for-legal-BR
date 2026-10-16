---
name: lexml-structure
description: "LexML: estrutura, exceções e alterações: Inventário de unidades, chunks com contexto obrigatório, avisos e limites do subconjunto XML."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
---
# LexML: estrutura, exceções e alterações

Leia a [política embarcada](../../references/POLICY.md). Este workflow é invocado explicitamente; não agenda nem autoriza envio de dados ou protocolo jurídico.

## Entradas mínimas
XML LexML UTF-8 de origem autorizada, hash do original e tamanho máximo da janela.

## Procedimento
Executar o leitor de subconjunto declarado. Conferir namespace, árvore e localizadores. Manter caput, parágrafos, incisos e alterações citadas; se dividir artigo, carregar required_context_ids antes de concluir. Dispositivo excedente permanece íntegro e sinalizado. Rejeitar DTD, entidade e árvore acima do orçamento.

## Saída contratada
Inventário de unidades, chunks com contexto obrigatório, avisos e limites do subconjunto XML.
Preservar fatos e hipóteses separados. Estados: satisfeito_no_escopo, nao_conformidade_evidenciada, inconclusivo, nao_aplicavel_justificado, erro. Fonte, data, localizador e revisão devem acompanhar a entrega. Falha de ferramenta não significa conformidade.

## Ferramenta local disponível
No repositório, a implementação é `runtime/legal_br/lexml.py`. A skill não tem Bash e não a executa implicitamente. O operador pode invocar o comando abaixo na raiz do runtime (exceto comandos com scripts/ ou apps/, executados na raiz do repositório):
```bash
python -m legal_br.engine lexml --file norma.xml --max-chars 12000
```
O operador fornece arquivos reais e autorizados. Não inventar resultados quando o arquivo, dependência ou modelo não estiver disponível.

## Caso adversarial obrigatório
O caput admite exceção no parágrafo seguinte: a divisão não pode transformar o caput isolado em regra absoluta. XSD não validado não recebe rótulo de conformidade plena.

## Proveniência e conceito
- LexML Brasil · Parser de documentos normativos: https://github.com/lexml/lexml-parser-projeto-lei
  Conceito: Estrutura sintática de documentos normativos e identificadores de dispositivos, em vez de janelas arbitrárias.
  Limite: Não copia o código GPL, não executa o parser Scala/Java, não valida XSD completo, não converte PDF ou texto livre em LexML.

## Garantia efetiva
Os testes de engenharia não medem acurácia jurídica da skill. Nenhuma conclusão profissional ou liberação de egress decorre automaticamente deste workflow. Não corrigir silenciosamente o material do usuário; indicar a diferença entre texto fornecido, pesquisa e inferência.
