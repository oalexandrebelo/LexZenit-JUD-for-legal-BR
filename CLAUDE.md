# Regras do repositório brasileiro

Este repositório contém um marketplace de instruções e um runtime local, não uma autoridade jurídica. O estado efetivo de implementação é descrito no README e em docs/ACCEPTANCE.md. Não promover catálogos a conectores, casos de teste semânticos a resultados, nem cálculos a decisões jurídicas.

Antes de editar, ler docs/POLICY.md, SECURITY.md e docs/PROVENANCE.md. Conservar `upstream.lock.json`, LICENSE e NOTICE. Não modificar silenciosamente conteúdo de fornecedor quando este repositório tiver sido montado com o upstream.

As alterações brasileiras devem manter `.claude-plugin/marketplace.json`, cada `br-*/.claude-plugin/plugin.json`, `catalog/skills.json`, fontes locais e casos de avaliação em sincronia. Os plugins são independentes: nenhum SKILL.md deve depender de arquivo fora do diretório do plugin instalado.

Executar `python3 scripts/validate_br.py`, `python3 -m unittest discover -s tests -v` e, em runtime, `python3 -m unittest discover -s tests -v`. Relatar separadamente verificações não executadas no CLI oficial ou em sistemas externos. Nunca adicionar arquivos de clientes, tokens, CPF, prontuários ou autos reais a exemplos ou testes. Não ativar ferramentas de escrita em uma skill de análise.

`br-*/CLAUDE.md` é modelo de perfil de prática, não contexto automaticamente carregado pela instalação. O perfil operacional precisa ser selecionado e autorizado fora do cache do plugin. Mudanças legais exigem fonte, versão, escopo temporal, revisão profissional e caso de regressão. O usuário pode pedir implementação; isso não autoriza envio de petição, pagamento ou comunicação externa em nome de terceiros.
