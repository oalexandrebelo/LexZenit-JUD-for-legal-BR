---
name: citations-provenance
description: "Citações: extrair, resolver, autenticar: Tabela de candidatos, pendências de identidade, verificação de existência e suporte separadas."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
---
# Citações: extrair, resolver, autenticar

Leia a [política embarcada](../../references/POLICY.md). Este workflow é invocado explicitamente; não agenda nem autoriza envio de dados ou protocolo jurídico.

## Entradas mínimas
Texto autorizado, país, data relevante e identificadores oficiais disponíveis.

## Procedimento
Obter o resultado do parser local; conferir cada superfície nos offsets originais. Distinguir processo, decisão, súmula, diploma e dispositivo. Manter autoridade/ano ambíguos sem completar por palpite. Referências curtas exigem resolução; autenticar existência em fonte primária separada e conferir suporte da afirmação.

## Saída contratada
Tabela de candidatos, pendências de identidade, verificação de existência e suporte separadas.
Preservar fatos e hipóteses separados. Estados: satisfeito_no_escopo, nao_conformidade_evidenciada, inconclusivo, nao_aplicavel_justificado, erro. Fonte, data, localizador e revisão devem acompanhar a entrega. Falha de ferramenta não significa conformidade.

## Ferramenta local disponível
No repositório, a implementação é `runtime/legal_br/citations.py`. A skill não tem Bash e não a executa implicitamente. O operador pode invocar o comando abaixo na raiz do runtime (exceto comandos com scripts/ ou apps/, executados na raiz do repositório):
```bash
python -m legal_br.engine citations --file documento.txt
```
O operador fornece arquivos reais e autorizados. Não inventar resultados quando o arquivo, dependência ou modelo não estiver disponível.

## Caso adversarial obrigatório
Uma menção a Lei 14.133/21 não identifica automaticamente autoridade federal e data completa; um CNJ com checksum válido não confirma processo existente.

## Proveniência e conceito
- Free Law Project · eyecite: https://github.com/freelawproject/eyecite
  Conceito: Separação de extração, agregação de referências e anotação de citações.
  Limite: Não transplantar gramática americana nem afirmar autenticação de precedente por parsing.
- CNJ · Resolução 65/2008: https://atos.cnj.jus.br/atos/detalhar/119
  Conceito: Numeração processual unificada e dígito verificador módulo 97.
  Limite: Dígito válido não comprova processo existente, decisão específica, competência ou tese.

## Garantia efetiva
Os testes de engenharia não medem acurácia jurídica da skill. Nenhuma conclusão profissional ou liberação de egress decorre automaticamente deste workflow. Não corrigir silenciosamente o material do usuário; indicar a diferença entre texto fornecido, pesquisa e inferência.
