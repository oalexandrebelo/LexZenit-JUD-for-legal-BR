# Projetos sintéticos do revisor

Projetos falsos, só com nomes de campos e chamadas de biblioteca, para testar o `lz_revisor`. Não contêm dados pessoais, CPF, chaves ou segredos.

- `app-ia-b2c`: app web de consumo com cadastro, IA generativa, pagamento e analytics, sem documentos jurídicos.
- `saas-documentado`: SaaS B2B com IA e RAG que já tem licença, política de privacidade, termos, RIPD e aviso de IA.
- `vazio`: diretório só com README, para testar o comportamento sem sinais.

`respostas-go.json` é um questionário sintético (sede em Goiás, atuação em GO e SP, MVP B2C). Exemplo: `python -m lz_revisor revisar examples/revisor/app-ia-b2c --respostas examples/revisor/respostas-go.json`.
