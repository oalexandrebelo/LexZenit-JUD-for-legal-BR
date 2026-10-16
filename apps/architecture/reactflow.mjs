/** Actual React Flow renderer. This module has no access to case files or runtime CLI. */
import React from 'react';
import { createRoot } from 'react-dom/client';
import { ReactFlow, Background, Controls, MiniMap, MarkerType } from '@xyflow/react';

const h = React.createElement;
let root;
const colors = {implemented:'#46d7b0',pending:'#e8b26d',human:'#c2b0ff',reference:'#81b9f5',unverified:'#f28f95',optional:'#a1bed3'};
export function mountReactFlow(host, model, onSelect) {
  if (!root) root = createRoot(host);
  const nodes = model.nodes.map(n => ({id:n.id,position:n.position,
    className:`legal-node status-${n.status}`,
    data:{label:h('div',null,
      h('small',{className:'rf-status'},model.statuses[n.status]),
      h('strong',null,n.title),h('span',null,n.subtitle))},
    style:{width:245,minHeight:110,borderTop:`3px solid ${colors[n.status]}`,borderRadius:12},
    ariaLabel:`${n.title}. ${model.statuses[n.status]}. Selecionar para ver contrato.`}));
  const edges = model.edges.map(e=>({id:e.id,source:e.source,target:e.target,label:e.label,
    type:'smoothstep',animated:false,
    style:{stroke:e.kind==='planned'?'#b89970':'#66839b',strokeWidth:1.5,strokeDasharray:e.kind==='planned'?'6 6':undefined},
    labelStyle:{fill:'#bacadd',fontSize:11},labelBgStyle:{fill:'#0a1424',fillOpacity:0.95},
    markerEnd:{type:MarkerType.ArrowClosed,color:'#66839b'}}));
  root.render(h(ReactFlow,{key:model.viewId,nodes,edges,fitView:true,fitViewOptions:{padding:0.17},
      minZoom:0.2,maxZoom:2.5,nodesDraggable:false,nodesConnectable:false,
      elementsSelectable:true,deleteKeyCode:null,colorMode:'dark',
      onNodeClick:(_event,node)=>onSelect(node.id),
      ariaLabelConfig:{'controls.zoomIn.ariaLabel':'Ampliar','controls.zoomOut.ariaLabel':'Reduzir','controls.fitView.ariaLabel':'Enquadrar'},
      attributionPosition:'bottom-right'},
    h(Background,{gap:24,size:1,color:'#21364c'}),h(Controls,{showInteractive:false}),
    h(MiniMap,{nodeColor:n=>colors[model.nodes.find(x=>x.id===n.id)?.status]||'#66839b',maskColor:'rgba(3,9,18,.55)',pannable:true,zoomable:true})));
}
export function unmountReactFlow() { if (root) {root.unmount();root=undefined;} }
