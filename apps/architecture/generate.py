"""Generate the portable, offline-first documentation page from canonical sources."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def generate() -> Path:
    graph=json.loads((ROOT/'architecture.json').read_text(encoding='utf8'))
    text=(ROOT/'template.html').read_text(encoding='utf8')
    text=text.replace('__STYLES__',(ROOT/'styles.css').read_text(encoding='utf8'))
    text=text.replace('__GRAPH_JSON__',json.dumps(graph,ensure_ascii=False).replace('<','\\u003c'))
    text=text.replace('__REACTFLOW_SOURCE__',(ROOT/'reactflow.mjs').read_text(encoding='utf8').replace('</script','<\\/script'))
    text=text.replace('__LOCAL_UI__',(ROOT/'ui.js').read_text(encoding='utf8'))
    result=ROOT/'index.html';result.write_text(text,encoding='utf8');return result
if __name__=='__main__':print(generate())
