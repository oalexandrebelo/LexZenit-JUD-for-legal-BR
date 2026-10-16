# Aceitação da release 0.2.0

**235 testes aprovados:** 200 do runtime Python, 13 de catálogo/montagem Git, 12 do grafo/JavaScript e 10 de navegador para a documentação local e falha de CDN.

Relatório: `evidence/test-report-v0.2.0.json`. Os 169 workflows anteriores foram comparados byte a byte com o ZIP anexado e permanecem idênticos. Agora são 39 plugins, 176 workflows e 189 registros de fontes (inventário, não conectores).

O navegador foi Chromium real. A documentação foi carregada de HTML próprio em memória. Os testes de indisponibilidade bloqueiam rede explicitamente; não substituem React Flow por mocks. O teste de ativação real da CDN também não completou: timeout e erro de resolução de nome. A visualização React Flow, o bundle npm e o CI remoto não foram homologados.

O build opcional foi tentado e bloqueou por ausência do pacote esbuild. Nenhum lockfile ou bundle externo foi fabricado. O renderizador local é imediatamente utilizável sem rede; o código React Flow é entregue para ativação online ou build local em ambiente conectado.

Python 3.13.5, SQLite 3.46.1, v22.16.0 e Chromium 144.0.7559.96 built on Debian GNU/Linux 13 (trixie). Duração dos testes não é latência de inferência nem benchmark jurídico.

As 176 especificações semânticas não foram executadas como avaliação de LLM. Nenhum treinamento, corpus nacional completo, pipeline NER integral, conector oficial, autenticação institucional, protocolo jurídico ou publicação no GitHub foi realizado. Evidências anteriores em [ACCEPTANCE-V01.md](ACCEPTANCE-V01.md) e `test-report-v0.1.0.json` são históricas.
