/** Optional, real offline React Flow bundle build. Requires installed npm packages. */
import { build } from 'esbuild';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
const here=dirname(fileURLToPath(import.meta.url));
const out=await build({entryPoints:[join(here,'reactflow.mjs')],bundle:true,write:false,
  format:'esm',platform:'browser',target:'es2022',minify:true,legalComments:'inline',
  define:{'process.env.NODE_ENV':'"production"'},metafile:true});
const css=await readFile(join(here,'node_modules/@xyflow/react/dist/style.css'),'utf8');
let html=await readFile(join(here,'index.html'),'utf8');
html=html.replace(/<script type="importmap">[\s\S]*?<\/script>/,'');
html=html.replace(/<script id="reactflow-source" type="text\/plain">[\s\S]*?<\/script>/,
 '<script id="reactflow-bundle" type="text/plain">'+out.outputFiles[0].text.replaceAll('</script','<\\/script')+'</script>');
html=html.replace('</head>','<style id="reactflow-local-css">'+css+'</style></head>');
html=html.replace("script-src 'unsafe-inline' blob: https://esm.sh; style-src 'unsafe-inline' https://cdn.jsdelivr.net; connect-src https://esm.sh https://cdn.jsdelivr.net;", "script-src 'unsafe-inline' blob:; style-src 'unsafe-inline'; connect-src 'none';");
html=html.replaceAll('Carrega React e React Flow via CDN; nenhum dado de caso é enviado','Bibliotecas React Flow embarcadas no build local');
await mkdir(join(here,'dist'),{recursive:true});
await writeFile(join(here,'dist/index.html'),html);
await writeFile(join(here,'dist/build-metafile.json'),JSON.stringify(out.metafile,null,2));
console.log('Built dist/index.html. Network-free rendering after explicit activation. Review npm licenses/lockfile before distribution.');
