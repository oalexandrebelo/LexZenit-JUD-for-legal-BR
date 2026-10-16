# Documentação interativa — React Flow e consulta offline

Abra `index.html` em um navegador. Para um host que restringe arquivos locais:

```bash
python -m http.server 8080 --bind 127.0.0.1 --directory apps/architecture
```

Acesse `http://127.0.0.1:8080`. Não sirva diretórios de dados de clientes. O servidor é somente para documentação, não produção.

Quatro vistas, pesquisa, filtro por estado, zoom, seleção por teclado, painel de contrato, lista acessível, referências e exportação JSON. Nenhum dado de caso é recebido e nenhum comando é executado.

## React Flow real

`reactflow.mjs` importa React, createRoot e `@xyflow/react`. A ativação explícita carrega versões fixadas de React 18.3.1 e React Flow 12.8.5 por esm.sh/jsDelivr. O modo inicial não faz essas requisições. Falha de rede mantém o grafo nativo, sem apresentá-lo como React Flow.

Essa escolha torna a documentação imediatamente consultável offline e evita um falso bundle de dependências. Versões fixadas na URL não equivalem a integridade criptográfica de todo conteúdo de CDN. A variante de distribuição institucional deve usar o build local, lockfile revisado e SBOM.

## Build com bibliotecas locais

Com Node e acesso autorizado ao registro npm:

```bash
cd apps/architecture
npm install
npm test
npm run build
```

O build gera `dist/index.html` com React Flow embarcado e CSP `connect-src 'none'`. Guardar/revisar `package-lock.json`, validar licenças transitivas, executar navegador e examinar `dist/build-metafile.json` antes de distribuir. O build não foi executado neste ambiente: a resolução de dependências npm estava indisponível. Nenhum lockfile transiente foi inventado.

## Verificação executada

```bash
python apps/architecture/generate.py
node --test apps/architecture/graph.test.mjs
node --check apps/architecture/ui.js
node --check apps/architecture/reactflow.mjs
python apps/architecture/browser_tests.py
```

O último comando requer Playwright e Chromium, podendo receber `CHROMIUM_PATH`. Os testes carregam HTML próprio em memória e bloqueiam rede para testar consulta offline e falha de CDN. Não são testes E2E do React Flow. O resultado observado está em `evidence/test-report-v0.2.0.json`.

Fonte técnica: https://reactflow.dev/learn. Licença da biblioteca: MIT. O código do viewer é original. Manter atribuição da xyflow.
