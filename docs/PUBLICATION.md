# Publicação — camada independente ou composição upstream

Atualização em 16/10/2026: publicado como repositório público `oalexandrebelo/LexZenit-JUD-for-legal-BR`. O texto abaixo registra o estado de 14/10/2026 e o fluxo de scripts, que ainda aponta para `oalexandrebelo/claude-for-legal-br`.

Estado em 14/10/2026: **não publicado**. `evidence/publication-attempt.json` registra o 404 do destino no conector e a ausência de rota disponível de criação. Nenhum outro repositório foi alterado.

## Usando o bundle Git desta release

No ambiente do proprietário, com GitHub CLI autenticado como `oalexandrebelo`:

```bash
git clone claude-for-legal-br-v0.2.0.bundle claude-for-legal-br
cd claude-for-legal-br
git remote remove origin
bash scripts/publish_independent.sh
```

O origin removido acima é somente o caminho do bundle local recém-clonado. Não execute essa remoção em uma cópia que já esteja vinculada a um repositório remoto sem revisar a configuração. O script só publica uma camada independente sobre um destino novo e tem visibilidade privada por padrão. A opção `--public` é uma decisão explícita de exposição.

## Usando somente o ZIP

Depois de revisar os arquivos, testar e confirmar que o diretório não é um repositório existente:

```bash
git init -b main
git add .
git commit -m "feat: Brazilian legal engineering and architecture documentation"
bash scripts/publish_independent.sh
```

A criação recusa destino existente; o script recusa origin já configurado e alterações não commitadas. Não faz force push, não altera proteção de branches e não registra tokens. Ele não resolve conflitos com trabalho remoto existente; esse caso exige leitura e reconciliação em branch própria.

## Derivado com o upstream completo

O fluxo original `scripts/assemble_fork.py` continua disponível para clonar a revisão fixada e aplicar esta camada. Nessa variante, usar `scripts/publish_github.sh` após revisar, testar e commitar a composição. Não chamar a camada independente de fork integral concluído.

## Build visual

A documentação nativa funciona sem rede. Para React Flow integralmente local, instalar dependências npm em `apps/architecture`, gerar/revisar lockfile e executar `npm run build`. A construção não foi concluída nesta sessão por ausência de dependências e conectividade; não existe bundle npm homologado escondido neste pacote.
