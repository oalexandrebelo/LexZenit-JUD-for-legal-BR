# Aceitação da release 0.3.0

**288 testes aprovados:** 263 do runtime Python (63 novos do revisor `lz_revisor`), 13 de catálogo/montagem Git e 12 do grafo/JavaScript. Os 10 testes de navegador da 0.2.0 não foram reexecutados, porque a documentação visual não mudou.

Relatório: `evidence/test-report-v0.3.0.json`. Agora são 40 plugins, 182 workflows e 192 registros de fontes (inventário, não conectores). O catálogo normativo do revisor tem 210 normas; 106 foram conferidas em fonte oficial.

Verificações no CLI oficial, nesta sessão:
- `claude plugin validate`: passou para o marketplace e para `ab-lexzenit-project-review`. O aviso sobre `CLAUDE.md` é esperado: o arquivo é o modelo de perfil de prática.
- `claude mcp list`: o servidor `lz-revisor` aparece como conectado, com HOME isolado e `PYTHONPATH` apontando para `runtime/`.

Um revisor independente, somente leitura, testou o motor com projetos sintéticos. Os achados foram corrigidos e cada um ganhou caso de regressão. A lista está em [ENGINEERING-V03](ENGINEERING-V03.md#revisão-independente).

Ambiente: Python 3.13.16, SQLite 3.45.1, Node v22.22.0, Linux. A duração dos testes não é latência de inferência nem benchmark jurídico.

Não foi feito nesta release:
- Avaliação de LLM das 182 especificações semânticas.
- Instalação pelo marketplace no cliente Claude.
- Pesquisa de normas municipais e setoriais.
- Conferência oficial de 104 normas (fonte secundária ou não localizada; nunca geram não conformidade).
- Publicação da branch no GitHub.

Evidências anteriores são históricas: [ACCEPTANCE-V02.md](ACCEPTANCE-V02.md), [ACCEPTANCE-V01.md](ACCEPTANCE-V01.md).
