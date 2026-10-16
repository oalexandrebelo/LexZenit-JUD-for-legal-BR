---
name: triage-evaluation
description: "Triagem: avaliar com abstenção e sem vazamento: Relatório reproduzível de métricas, leakage e política de abstenção; não entrega classificador treinado."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
---
# Triagem: avaliar com abstenção e sem vazamento

Leia a [política embarcada](../../references/POLICY.md). Este workflow é invocado explicitamente; não agenda nem autoriza envio de dados ou protocolo jurídico.

## Entradas mínimas
Taxonomia BR adjudicada, dados autorizados com matter_id/hash/available_on, partições e scores do modelo realmente executado.

## Procedimento
Auditar grupos e hashes entre train/dev/test e corte temporal. Calcular precisão, recall e F1 por rótulo, micro/macro, cobertura e acerto seletivo. Registrar denominadores; abstenção não remove falso negativo da métrica completa. Recusar pontuações não finitas, fora de faixa e empate. Sem calibração demonstrada, score não é probabilidade de êxito judicial.

## Saída contratada
Relatório reproduzível de métricas, leakage e política de abstenção; não entrega classificador treinado.
Preservar fatos e hipóteses separados. Estados: satisfeito_no_escopo, nao_conformidade_evidenciada, inconclusivo, nao_aplicavel_justificado, erro. Fonte, data, localizador e revisão devem acompanhar a entrega. Falha de ferramenta não significa conformidade.

## Ferramenta local disponível
No repositório, a implementação é `runtime/legal_br/evaluation.py`. A skill não tem Bash e não a executa implicitamente. O operador pode invocar o comando abaixo na raiz do runtime (exceto comandos com scripts/ ou apps/, executados na raiz do repositório):
```bash
python -m legal_br.engine evaluate --file avaliacao.json
```
O operador fornece arquivos reais e autorizados. Não inventar resultados quando o arquivo, dependência ou modelo não estiver disponível.

## Caso adversarial obrigatório
O mesmo processo aparece com dois nomes em treino e teste: a partição deve falhar mesmo que os rótulos tenham boa acurácia aparente.

## Proveniência e conceito
- THUNLP / CAIL2018 · Xiao et al.: https://github.com/china-ai-law-challenge/CAIL2018
  Conceito: Definição explícita de tarefas de classificação jurídica e avaliação por tarefa.
  Limite: Não transferir tipos penais, teses, penas, rótulos ou pesos chineses. Split temporal e gate de abstenção são decisões adicionais desta engenharia, não alegação sobre todo CAIL.

## Garantia efetiva
Os testes de engenharia não medem acurácia jurídica da skill. Nenhuma conclusão profissional ou liberação de egress decorre automaticamente deste workflow. Não corrigir silenciosamente o material do usuário; indicar a diferença entre texto fornecido, pesquisa e inferência.
