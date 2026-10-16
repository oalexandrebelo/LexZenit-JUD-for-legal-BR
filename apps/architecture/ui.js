/* Local documentation renderer. No third-party requests before explicit activation. */
(() => {
'use strict';
const data=JSON.parse(document.getElementById('architecture-data').textContent);
const byId=new Map(data.nodes.map(n=>[n.id,n]));
const refs=new Map(data.references.map(r=>[r.id,r]));
const $=id=>document.getElementById(id);
let view=data.views[0], selected=null, query='', status='all', zoom=1, activeRenderer=null, busy=false, listMode=window.matchMedia('(max-width:650px)').matches;
const colors={implemented:'#46d7b0',pending:'#e8b26d',human:'#c2b0ff',reference:'#81b9f5',unverified:'#f28f95',optional:'#a1bed3'};
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function externalLink(url,title){if(!url||!url.startsWith('https://'))return el('span',title+' · referência não localizada');const a=el('a',title);a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a;}
function exportJSON(){const b=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});const u=URL.createObjectURL(b);const a=el('a');a.href=u;a.download='claude-para-juridico-arquitetura.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
function getModel(){
 const nodes=view.nodes.map(p=>({...byId.get(p.id),position:{x:p.x,y:p.y}})).filter(n=>(status==='all'||status===n.status)&&(!query||[n.title,n.subtitle,n.note,n.file,...n.reference_ids].join(' ').toLowerCase().includes(query)));
 const ids=new Set(nodes.map(n=>n.id));return {viewId:view.id,nodes,edges:view.edges.filter(e=>ids.has(e.source)&&ids.has(e.target)),statuses:data.statuses};
}
function select(id){
 const n=byId.get(id);if(!n)return;selected=id;
 $('inspector').replaceChildren();const head=el('div',undefined,'inspector-head');
 const badge=el('span',data.statuses[n.status],'badge');badge.style.setProperty('--badge-color',colors[n.status]);head.append(badge,el('h2',n.title),el('p',n.subtitle));$('inspector').append(head);
 for(const [name,value] of [['Entradas',n.inputs],['Saídas',n.outputs],['Falha e bloqueio',n.failure],['Limite da capacidade',n.note]]){
  const section=el('section');section.append(el('h3',name),el('p',value));$('inspector').append(section);
 }
 if(n.file){const section=el('section');section.append(el('h3','Arquivo de implementação'),el('code',n.file));$('inspector').append(section);}
 if(n.reference_ids.length){const section=el('section');section.append(el('h3','Referência e conceito'));for(const rId of n.reference_ids){const r=refs.get(rId);section.append(externalLink(r.url,r.name),el('p',r.concept),el('small',r.license));}$('inspector').append(section);}
 $('inspector').append(el('p','Documentação da release, não execução ao vivo.','footnote'));
 document.querySelectorAll('[data-node-id]').forEach(item=>item.classList.toggle('is-selected',item.dataset.nodeId===id));
 $('selected-title').textContent=n.title;
}
function svgEl(tag,attrs={},text){const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;return n;}
function wrap(text,max){const words=text.split(' '), lines=[];let current='';for(const word of words){if(current&&(current+' '+word).length>max){lines.push(current);current=word;}else current+=(current?' ':'')+word;}if(current)lines.push(current);return lines;}
function renderNative(model){
 const host=$('native-canvas');host.replaceChildren();host.hidden=listMode;$('list-panel').hidden=!listMode;$('flow-canvas').hidden=true;
 if(listMode){const list=$('list-panel');list.replaceChildren();for(const n of model.nodes){const button=el('button',undefined,'list-node');button.dataset.nodeId=n.id;button.append(el('span',data.statuses[n.status],'eyebrow'),el('strong',n.title),el('p',n.subtitle));button.onclick=()=>select(n.id);list.append(button);}return;}
 const width=Math.max(800,...model.nodes.map(n=>n.position.x+290)),height=Math.max(420,...model.nodes.map(n=>n.position.y+170));
 const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`,role:'group','aria-label':'Diagrama de arquitetura local. Use Tab e Enter para selecionar nós.'});
 svg.style.width=`${Math.max(100,100*zoom)}%`;svg.style.minHeight=`${Math.max(380,height*0.65*zoom)}px`;
 const defs=svgEl('defs');const marker=svgEl('marker',{id:'arrow',viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:6,markerHeight:6,orient:'auto-start-reverse'});marker.append(svgEl('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:'#66839b'}));defs.append(marker);svg.append(defs);
 for(const edge of model.edges){const a=model.nodes.find(n=>n.id===edge.source),b=model.nodes.find(n=>n.id===edge.target);const x1=a.position.x+245,y1=a.position.y+60,x2=b.position.x,y2=b.position.y+60;let d;
  if(b.position.x>a.position.x)d=`M ${x1} ${y1} C ${x1+65} ${y1},${x2-65} ${y2},${x2} ${y2}`;
  else d=`M ${a.position.x+122} ${a.position.y+122} C ${a.position.x+122} ${a.position.y+170},${b.position.x+122} ${b.position.y-55},${b.position.x+122} ${b.position.y}`;
  svg.append(svgEl('path',{d,fill:'none',stroke:edge.kind==='planned'?'#b89970':'#57758c','stroke-width':1.8,'stroke-dasharray':edge.kind==='planned'?'6 6':'none','marker-end':'url(#arrow)'}));
 }
 for(const n of model.nodes){const g=svgEl('g',{transform:`translate(${n.position.x},${n.position.y})`,tabindex:0,role:'button','aria-label':`${n.title}. ${data.statuses[n.status]}`,'data-node-id':n.id,class:'diagram-node'});
  g.append(svgEl('rect',{width:245,height:125,rx:13,fill:'#111f31',stroke:'#294257','stroke-width':1.5}));
  g.append(svgEl('rect',{x:0,y:12,width:3,height:98,rx:2,fill:colors[n.status]}));
  g.append(svgEl('circle',{cx:18,cy:23,r:3,fill:colors[n.status]}),svgEl('text',{x:29,y:28,fill:colors[n.status],'font-size':10,'font-family':'system-ui'},data.statuses[n.status].toUpperCase()));
  wrap(n.title,26).slice(0,2).forEach((line,i)=>g.append(svgEl('text',{x:18,y:52+i*20,fill:'#f0f6fc','font-weight':650,'font-size':16,'font-family':'system-ui'},line)));
  wrap(n.subtitle,31).slice(0,2).forEach((line,i)=>g.append(svgEl('text',{x:18,y:96+i*14,fill:'#9bafc4','font-size':11,'font-family':'system-ui'},line)));
  g.onclick=()=>select(n.id);g.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select(n.id);}};svg.append(g);
 }
 host.append(svg);
}
function render(){
 $('list-toggle').textContent=listMode?'Ver grafo':'Ver lista acessível';
 const model=getModel();$('view-title').textContent=view.title;$('view-description').textContent=view.description;$('node-count').textContent=`${model.nodes.length} nós · ${model.edges.length} relações`;
 document.querySelectorAll('[data-view]').forEach(b=>{b.classList.toggle('active',b.dataset.view===view.id);b.setAttribute('aria-pressed',String(b.dataset.view===view.id));});
 $('empty').hidden=!!model.nodes.length;
 if(activeRenderer&&!listMode){$('native-canvas').hidden=true;$('list-panel').hidden=true;$('flow-canvas').hidden=false;activeRenderer.mountReactFlow($('flow-canvas'),model,select);}
 else renderNative(model);
 if(!model.nodes.some(n=>n.id===selected)&&model.nodes.length)selected=model.nodes[0].id;
 if(selected)select(selected);
}
for(const v of data.views){const b=el('button',v.title);b.dataset.view=v.id;b.onclick=()=>{view=v;zoom=1;render();};$('views').append(b);}
for(const [key,label] of Object.entries(data.statuses)){if(key==='optional')continue;const opt=el('option',label);opt.value=key;$('status-filter').append(opt);const item=el('span',label);item.style.setProperty('--dot',colors[key]);$('legend').append(item);}
$('search').oninput=e=>{query=e.target.value.trim().toLowerCase();render();};$('status-filter').onchange=e=>{status=e.target.value;render();};
$('list-toggle').onclick=()=>{listMode=!listMode;$('list-toggle').textContent=listMode?'Ver grafo':'Ver lista acessível';render();};
$('zoom-in').onclick=()=>{zoom=Math.min(3,zoom+0.25);render();};$('zoom-out').onclick=()=>{zoom=Math.max(1,zoom-0.25);render();};$('fit').onclick=()=>{zoom=1;render();};$('export').onclick=exportJSON;
$('activate-flow').onclick=async()=>{
 if(busy)return;
 if(activeRenderer){activeRenderer.unmountReactFlow();activeRenderer=null;$('mode-label').textContent='Grafo local · sem bibliotecas externas';$('activate-flow').textContent='Ativar React Flow';render();return;}
 busy=true;$('activate-flow').disabled=true;$('mode-label').textContent='Carregando biblioteca de visualização…';
 try{
  const bundled=document.getElementById('reactflow-bundle');let code=bundled?bundled.textContent:document.getElementById('reactflow-source').textContent;
  const css=document.getElementById('reactflow-local-css');
  if(!css&&!document.getElementById('flow-css')){const link=el('link');link.id='flow-css';link.rel='stylesheet';link.href='https://cdn.jsdelivr.net/npm/@xyflow/react@12.8.5/dist/style.css';document.head.append(link);}
  const url=URL.createObjectURL(new Blob([code],{type:'text/javascript'}));
  try{activeRenderer=await Promise.race([import(url),new Promise((_,reject)=>setTimeout(()=>reject(new Error('timeout')),20000))]);}finally{URL.revokeObjectURL(url);}
  $('mode-label').textContent=bundled?'React Flow · bibliotecas locais':'React Flow 12.8.5 · CDN explícita';$('activate-flow').textContent='Voltar ao grafo local';listMode=false;render();
 }catch(_e){window.__LEGAL_FLOW_ERROR__={name:_e.name,message:_e.message};activeRenderer=null;$('mode-label').textContent='React Flow indisponível; grafo local preservado.';$('flow-notice').textContent='A biblioteca não pôde ser carregada. Todos os contratos permanecem acessíveis no grafo local. O build com dependências locais elimina a CDN.';render();}
 finally{busy=false;$('activate-flow').disabled=false;}
};
$('references').replaceChildren();for(const r of data.references){const article=el('article',undefined,'reference-card');article.append(el('span',`${r.region} / ${r.priority}`,'eyebrow'),externalLink(r.url,r.name),el('p',r.concept),el('p',r.adoption),el('small',r.license));$('references').append(article);}
window.matchMedia('(max-width:650px)').addEventListener('change',e=>{if(e.matches){listMode=true;render();}});
render();window.__LEGAL_DOCS__={version:data.version,nodeCount:data.nodes.length,views:data.views.length,isLive:false};
})();
