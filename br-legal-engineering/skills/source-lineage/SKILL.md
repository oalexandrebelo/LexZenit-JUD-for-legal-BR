---
name: source-lineage
description: "Referências, licenças e capacidade demonstrada: Registro de adoção com conceito, licença, implementação, teste, limitações e decisão."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
---
# Referências, licenças e capacidade demonstrada

Leia a [política embarcada](../../references/POLICY.md). Este workflow é invocado explicitamente; não agenda nem autoriza envio de dados ou protocolo jurídico.

## Entradas mínimas
Referência proposta, autor, URL, licença, arquivo/módulo alvo e demonstração executável.

## Procedimento
Separar conceito, dependência opcional, código copiado, dados e pesos. Conferir licença de cada ativo e registrar evidência sem prometer autorização de dados pessoais. Fonte não localizada permanece não verificada. Não acrescentar import obrigatório por benefício hipotético; comparar alternativa própria com teste de equivalência no escopo.

## Saída contratada
Registro de adoção com conceito, licença, implementação, teste, limitações e decisão.
Preservar fatos e hipóteses separados. Estados: satisfeito_no_escopo, nao_conformidade_evidenciada, inconclusivo, nao_aplicavel_justificado, erro. Fonte, data, localizador e revisão devem acompanhar a entrega. Falha de ferramenta não significa conformidade.

## Ferramenta local disponível
No repositório, a implementação é `runtime/legal_br/citations.py`. A skill não tem Bash e não a executa implicitamente. O operador pode invocar o comando abaixo na raiz do runtime (exceto comandos com scripts/ ou apps/, executados na raiz do repositório):
```bash
python scripts/validate_br.py
```
O operador fornece arquivos reais e autorizados. Não inventar resultados quando o arquivo, dependência ou modelo não estiver disponível.

## Caso adversarial obrigatório
Open-ECLI-Utils não foi localizado por nome exato: não inventar URL ou licença nem tratar a ausência de resultado como prova de inexistência.

## Proveniência e conceito
- Free Law Project · eyecite: https://github.com/freelawproject/eyecite
  Conceito: Separação de extração, agregação de referências e anotação de citações.
  Limite: Não transplantar gramática americana nem afirmar autenticação de precedente por parsing.
- LexML Brasil · Parser de documentos normativos: https://github.com/lexml/lexml-parser-projeto-lei
  Conceito: Estrutura sintática de documentos normativos e identificadores de dispositivos, em vez de janelas arbitrárias.
  Limite: Não copia o código GPL, não executa o parser Scala/Java, não valida XSD completo, não converte PDF ou texto livre em LexML.
- LeNER-Br · Pedro H. Luz de Araujo e colaboradores: https://github.com/peluz/lener-br
  Conceito: NER jurídico em português e anotação BIO de entidades.
  Limite: Corpus NER não é detector completo de PII; nenhum modelo, corpus ou checkpoint foi embarcado; não há garantia de anonimização ou conformidade LGPD.
- European Case Law Identifier · Portal Europeu da Justiça: https://eur-lex.europa.eu/content/help/eurlex-content/ecli.html
  Conceito: Identificador de decisão com cinco componentes e metadados harmonizados.
  Limite: ECLI não é uma ontologia completa, não cria força vinculante e não comprova adoção de ECLI pelo Brasil.
- THUNLP / CAIL2018 · Xiao et al.: https://github.com/china-ai-law-challenge/CAIL2018
  Conceito: Definição explícita de tarefas de classificação jurídica e avaliação por tarefa.
  Limite: Não transferir tipos penais, teses, penas, rótulos ou pesos chineses. Split temporal e gate de abstenção são decisões adicionais desta engenharia, não alegação sobre todo CAIL.

## Garantia efetiva
Os testes de engenharia não medem acurácia jurídica da skill. Nenhuma conclusão profissional ou liberação de egress decorre automaticamente deste workflow. Não corrigir silenciosamente o material do usuário; indicar a diferença entre texto fornecido, pesquisa e inferência.
