---
name: privacy-local
description: "Privacidade: pseudonimização local por caso: Cópia pseudonimizada restrita, offsets de transformação e checklist de revisão; egress permanece bloqueado."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
---
# Privacidade: pseudonimização local por caso

Leia a [política embarcada](../../references/POLICY.md). Este workflow é invocado explicitamente; não agenda nem autoriza envio de dados ou protocolo jurídico.

## Entradas mínimas
Documento autorizado, política de minimização, chave privada local, tenant/caso e spans humanos ou BIO previamente alinhados.

## Procedimento
Executar exclusivamente no ambiente autorizado. Unir spans sobrepostos antes de mascarar. Usar pseudônimos HMAC escopados; nunca publicar chave ou mapa reverso. Conferir CPF, e-mail e telefone, inclusive valores inválidos. Examinar nomes, endereços, saúde e identificadores indiretos que detectores não cobrem. Não autorizar egress por ausência de achado.

## Saída contratada
Cópia pseudonimizada restrita, offsets de transformação e checklist de revisão; egress permanece bloqueado.
Preservar fatos e hipóteses separados. Estados: satisfeito_no_escopo, nao_conformidade_evidenciada, inconclusivo, nao_aplicavel_justificado, erro. Fonte, data, localizador e revisão devem acompanhar a entrega. Falha de ferramenta não significa conformidade.

## Ferramenta local disponível
No repositório, a implementação é `runtime/legal_br/privacy.py`. A skill não tem Bash e não a executa implicitamente. O operador pode invocar o comando abaixo na raiz do runtime (exceto comandos com scripts/ ou apps/, executados na raiz do repositório):
```bash
python -m legal_br.engine privacy --file documento.txt --key-file chave.bin --tenant organizacao --matter caso
```
O operador fornece arquivos reais e autorizados. Não inventar resultados quando o arquivo, dependência ou modelo não estiver disponível.

## Caso adversarial obrigatório
NER marca uma lei como entidade jurídica e omite um CPF inválido: preservar a referência jurídica e mascarar o identificador candidato sem declarar anonimização.

## Proveniência e conceito
- LeNER-Br · Pedro H. Luz de Araujo e colaboradores: https://github.com/peluz/lener-br
  Conceito: NER jurídico em português e anotação BIO de entidades.
  Limite: Corpus NER não é detector completo de PII; nenhum modelo, corpus ou checkpoint foi embarcado; não há garantia de anonimização ou conformidade LGPD.

## Garantia efetiva
Os testes de engenharia não medem acurácia jurídica da skill. Nenhuma conclusão profissional ou liberação de egress decorre automaticamente deste workflow. Não corrigir silenciosamente o material do usuário; indicar a diferença entre texto fornecido, pesquisa e inferência.
