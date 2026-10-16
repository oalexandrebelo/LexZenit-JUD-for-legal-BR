---
name: architecture-explorer
description: "Arquitetura navegável: contratos e confiança: Mapa navegável e lista acessível dos mesmos nós; visão explícita de capacidades presentes e dependências pendentes."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
---
# Arquitetura navegável: contratos e confiança

Leia a [política embarcada](../../references/POLICY.md). Este workflow é invocado explicitamente; não agenda nem autoriza envio de dados ou protocolo jurídico.

## Entradas mínimas
Catálogo de arquitetura da versão, dados de implementação e referências verificadas.

## Procedimento
Abrir as vistas pipeline, referências, privacidade e avaliação. Para cada nó, conferir status, arquivo, entradas, saídas, falhas e evidências. Arestas de origem conceitual não são integrações de execução. Nó de revisão humana não representa autenticação implementada. O viewer não recebe dados de casos nem executa comandos.

## Saída contratada
Mapa navegável e lista acessível dos mesmos nós; visão explícita de capacidades presentes e dependências pendentes.
Preservar fatos e hipóteses separados. Estados: satisfeito_no_escopo, nao_conformidade_evidenciada, inconclusivo, nao_aplicavel_justificado, erro. Fonte, data, localizador e revisão devem acompanhar a entrega. Falha de ferramenta não significa conformidade.

## Ferramenta local disponível
No repositório, a implementação é `runtime/legal_br/privacy.py`. A skill não tem Bash e não a executa implicitamente. O operador pode invocar o comando abaixo na raiz do runtime (exceto comandos com scripts/ ou apps/, executados na raiz do repositório):
```bash
python -m http.server 8080 --bind 127.0.0.1 --directory apps/architecture
```
O operador fornece arquivos reais e autorizados. Não inventar resultados quando o arquivo, dependência ou modelo não estiver disponível.

## Caso adversarial obrigatório
Um nó planejado de modelo NER não pode aparecer como serviço ativo por estar desenhado junto ao módulo testado.

## Proveniência e conceito
- xyflow · React Flow: https://reactflow.dev/learn
  Conceito: Visualização de nós e arestas, navegação espacial e inspeção de contratos.
  Limite: A interface não executa skills, não autentica revisores e não representa observabilidade ao vivo.

## Garantia efetiva
Os testes de engenharia não medem acurácia jurídica da skill. Nenhuma conclusão profissional ou liberação de egress decorre automaticamente deste workflow. Não corrigir silenciosamente o material do usuário; indicar a diferença entre texto fornecido, pesquisa e inferência.
