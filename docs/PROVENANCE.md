# Proveniência e atribuição

## Superfícies

**Upstream público:** anthropics/claude-for-legal, commit `4a6c651889c97cc9140580363c73e0eb17379c2b`, árvore `19d28f03edbc916e85ce68733993170952071b0d`, observado em 13/10/2026. Marketplace consultado: 12 plugins de primeira parte e um fornecedor; guia: cinco cookbooks. Não foi integralmente copiado neste ZIP. Fonte: https://github.com/anthropics/claude-for-legal.

**LexGuard V2 da conversa:** pacote `LEXGUARD_ENTERPRISE_BR_V2.zip`, SHA-256 `abf3b069b3ecf6a922ef77f0daf902c54046342929d310b5eae82e86f1b2aa1d`. Reutilizados seletivamente núcleo, testes, exemplos e 53 contratos. Dossiês iniciais simulados não foram incorporados ao motor. Origem individual em catalog/skills.json.

**Camada desta entrega:** 116 workflows adicionais, empacotamento BR, módulo legal_br, testes, documentação, ontologia e ferramentas de montagem. Não é obra oficial ou endossada pela Anthropic.

## Composição

O script clona, fixa o SHA, renomeia origin para upstream, arquiva documentos/marketplace/CI e aplica a camada BR. O CLA original fica no histórico e arquivo, não ativo na raiz. Os plugins originais permanecem mas não são instalados pelo catálogo BR.

Apache-2.0, com LICENSE e NOTICE. Não houve auditoria completa de direitos de todos os arquivos de fornecedor upstream. Antes de distribuição integral, revisar licenças e avisos específicos. Nenhum aviso de terceiro deve ser removido inadvertidamente.

## Exclusões

Não foi publicado o conteúdo bruto dos seis dossiês originais, dados de clientes, credenciais, NBRs integrais ou autos sigilosos. Não foi criado repositório remoto. Proveniência não certifica correção jurídica do material herdado.

## Atualizações

Atualização do upstream requer diff entre SHAs, revisão de permissões/licenças/conectores, testes e novo lock. Não sincronizar branch mutável automaticamente em produção. A camada não usa submódulos nem baixa modelos externos.


## Evolução 0.2.0 — 14/10/2026

Base local: commit `1ce7b53a206177d8453c7e620761d81188241f1f` da camada brasileira entregue anteriormente. Os 169 workflows foram preservados; sete novos foram adicionados em br-legal-engineering. Referências, licenças e conceito adotado estão em research/references.json. Nenhum código, dataset ou checkpoint de eyecite, LexML, LeNER-Br ou CAIL foi copiado. A documentação React Flow usa dependências opcionais, não bibliotecas embarcadas nesta distribuição. Estado de publicação em evidence/publication-attempt.json.

## Evolução 0.3.0 — 16/10/2026

Base: commit `4a1620e` (tag v0.2.0). Adicionados o plugin `br-project-review` (seis workflows), o motor `runtime/lz_revisor` e o catálogo normativo do revisor. As 15 minutas brasileiras foram redigidas para este pacote; nenhum texto de modelo de terceiro foi copiado.

Repositórios públicos auditados em 16/10/2026 como referência de desenho, sem cópia de texto ou código:

| Repositório | Licença observada | Aproveitamento |
|---|---|---|
| georgelinde887-sudo/nda-template-generator | MIT (titularidade inconsistente) | Nenhum texto; só a ideia de gerar minuta por campos |
| ankane/awesome-legal | CC0-1.0 (só a lista) | Taxonomia de documentos de startup; a CC0 não cobre os documentos apontados (Cooley GO proíbe uso para treinar IA; Orrick é proprietária) |
| Ro5s/Startup-Starter-Pack | MIT | Roteiro de fases; conteúdo desatualizado |
| General-Legal/legal-templates | CC0-1.0 | Referência de estrutura; direito dos EUA, não adaptado |
| General-Legal/general-legal-mcp | sem licença, sem código | Só o desenho de ferramentas |
| legalize-kr/legalize-kr e admrule-kr | MIT declarado só no README | Arquitetura de legislação como código (norma por arquivo, metadados de vigência); servidor MCP local somente leitura |
| ethicalml/awesome-artificial-intelligence-regulation | MIT | Lista de partida para N3; entradas conferidas na fonte antes de entrar no catálogo |

Verificação das normas: 106 das 210 foram conferidas em fonte oficial (Planalto, Câmara, assembleias e casas civis estaduais, EUR-Lex, Federal Register, FTC, CPPA, procuradoria do Colorado, CAC, ISO, OCDE, Conselho da Europa). As demais estão marcadas como fonte secundária ou não localizada e nunca geram não conformidade. A pesquisa foi feita por agentes com orçamento de busca limitado; as leituras que sustentam as normas federais centrais foram refeitas pelo integrador no texto oficial.
