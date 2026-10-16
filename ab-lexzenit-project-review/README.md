<p align="center">
  <a href="https://oalexandrebelo.github.io/LexZenit-JUD-for-legal-BR/"><img alt="LexZenit" src="assets/lexzenit-logo.svg" width="300"></a>
  &nbsp;&nbsp;&nbsp;
  <a href="https://www.alexandrebelo.com.br"><img alt="AB — Alexandre Belo" src="assets/ab-logo.svg" height="72"></a>
</p>

# AB LexZenit · Project Review — revisor jurídico de projetos (N1 · N2 · N3)

Mapeia o que um projeto de IA, SaaS ou startup precisa cumprir, e o que já tem, em três níveis:

- **N1 Brasil:** União e as 27 UFs (sede e atuação), com alerta de competência constitucional.
- **N2 país:** EUA por padrão, ou o país soberano mais coerente com o mercado real (regra em `references/catalog/regra-n2.json`).
- **N3 mundo:** normas extraterritoriais (UE), tratados e padrões globais.

Cada achado traz estado (`nao_conformidade_evidenciada`, `inconclusivo`, `nao_aplicavel_justificado`), severidade, norma com fonte e estado de verificação, evidência localizada no código e a minuta brasileira que fecha a lacuna. Projetos de lei ficam no radar; sandbox, compras de inovação e fomento ficam em oportunidades.

## Uso

Instalação: `/plugin install ab-lexzenit-project-review@legal-br`.

- `/ab-lexzenit-project-review:revisar-projeto` — revisão completa N1/N2/N3.
- `/ab-lexzenit-project-review:mapa-uf` — normas de uma ou mais UFs.
- `/ab-lexzenit-project-review:escolher-n2` — escolha do país N2.
- `/ab-lexzenit-project-review:classificar-risco-ia` — classificação do sistema de IA por regime.
- `/ab-lexzenit-project-review:kit-documentos` — minutas a partir das lacunas.
- `/ab-lexzenit-project-review:atualizar-catalogo` — inclusão ou atualização de norma (legislação como código).

As skills são somente leitura e não instalam conectores. O motor determinístico e o servidor MCP ficam em `runtime/lz_revisor` do repositório e são habilitados explicitamente pelo operador:

```bash
cd runtime
python3 -m lz_revisor revisar /caminho/do/projeto --respostas respostas.json --saida revisao/
claude mcp add lz-revisor -e PYTHONPATH="$PWD" -- python3 -m lz_revisor mcp --raiz /caminho/dos/projetos
```

## Conteúdo empacotado

- `references/catalog/`: sinais, evidências, questionário, regra N2, cobertura por UF e 210 normas (`normas/*.json`: 19 federais, 152 estaduais, 26 do N2 e 13 do N3), cada uma com fonte, status, vigência e verificação. 106 conferidas em fonte oficial.
- `references/templates/`: 15 minutas brasileiras com base legal e campos `{{campo}}`.
- `references/POLICY.md` e `references/sources.json`.

O catálogo tem data de corte. Fonte secundária nunca gera não conformidade; ausência de achado não prova ausência de norma. Não é parecer jurídico: toda saída é minuta para revisão profissional.

---

LexZenit é uma solução da **AB ED&IA Soluções em Tecnologia Ltda.** (CNPJ 57.531.384/0001-96). [alexandrebelo.com.br](https://www.alexandrebelo.com.br) · [LexZenit](https://oalexandrebelo.github.io/LexZenit-JUD-for-legal-BR/) · Apache-2.0.
