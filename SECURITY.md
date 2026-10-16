# Segurança e fronteiras

## Limites efetivos

Não há autenticação de revisores, isolamento SaaS, criptografia de banco local, KMS, assinatura, WORM, sandbox ou egress proxy. O runtime é ferramenta local de operador autorizado. Não expô-lo como serviço multiusuário.

`allowed-tools` não é denylist universal ou sandbox. `disable-model-invocation` controla acionamento automático em cliente compatível; o host deve impor rede, ferramentas e acesso a arquivos. Um documento não pode ampliar autorizações.

| Ameaça | Controle presente | Limite residual |
|---|---|---|
| Aprovação de dado não verificado | Busca exclui não atestado e norma sem período; skill usa inconclusão | Atestação não autentica competência do revisor |
| Citação inventada | Substring exata, hash e offsets | Não comprova suporte semântico |
| Caso trocado | Banco por matter e recusa de identificador divergente | Acesso ao arquivo permite leitura por outro software |
| Contaminação temporal | Snapshot conhecido e intervalo jurídico | Datas jurídicas são declaradas |
| Aresta inventada | Proposta separada de revisão; prova e endpoints elegíveis | Revisor pode errar |
| Explosão do grafo | Candidatos, seeds, saltos, nós e arestas limitados | Limites reduzem recall e são reportados |
| Binário/memória | UTF-8 estrito, máximo 10 MiB, tipos admitidos | Não é antivírus nem parser PDF |
| Adulteração simples | Hashes, fingerprint, cadeia e âncora opcional | Não resiste a reescrita administrativa de base e âncora |
| Protocolo indevido | Não existe ferramenta de protocolo/envio/assinatura | Outras ferramentas do host exigem controle próprio |
| Sobrescrita de repo | Destino existente recusado; sem force push | Create/push pode falhar parcialmente; reconciliar |

## Dados e supply chain

Casos reais ficam fora do Git. Não versionar tokens, CPF, prontuários, documentos de crianças ou dumps. Fixtures são sintéticas. Pseudonimização não é anonimização nem conformidade integral. Referência: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm.

Plugins BR não contêm MCP ou hooks. A montagem preserva os plugins upstream, mas não os ativa no marketplace BR. Permissões e conectores originais requerem revisão própria. Workflows upstream são arquivados e substituídos pelo CI BR, sem deploy ou segredo.

Apache-2.0 não transfere marcas nem dispensa atribuição. Revisar avisos de subdiretórios e política de contribuições antes de distribuição pública.

## Incidentes

Erro técnico, fonte incompleta, citação inexistente e incoerência temporal nunca significam conformidade. APIs futuras precisam de orçamento e estados explícitos. Resultado desconhecido de protocolo exige reconciliação, não repetição cega.

Não abrir issue pública com dados reais. Esta distribuição não declara canal privado ou SLA de resposta inexistente. O mantenedor deve estabelecê-los antes de uso institucional.


## Adições 0.2.0

A pseudonimização não autoriza egress; não há modelo NER embarcado ou anonimização completa. Arquivos de chaves devem permanecer fora do repositório. Originais, hashes, offsets e pseudônimos são tratados como dados potencialmente protegidos. O viewer recebe somente arquitetura pública estática: sem documentos de casos, uploads, telemetria ou execução de comandos. A carga CDN é explícita e não é equivalente a um build com lockfile e integridade revisada. O script de publicação independente só atua sobre repositório novo e recusa origin preexistente, sem force push.
