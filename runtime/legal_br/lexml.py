"""Original bounded reader for a declared subset of LexML XML.

Not the GPL LexML Parser, not an XSD validator, not a plain-text-to-LexML
converter. Hierarchical XML, source hashes and per-article context are retained.
"""
from __future__ import annotations
import hashlib
import io
import re
import xml.etree.ElementTree as ET
from typing import Any

NS = 'http://www.lexml.gov.br/1.0'
STRUCTURE = {'Articulacao','Livro','Parte','Titulo','Capitulo','Secao','Subsecao',
             'Artigo','Caput','Paragrafo','Inciso','Alinea','Item','Pena','Alteracao'}
AGGREGATES = {'Articulacao','Livro','Parte','Titulo','Capitulo','Secao','Subsecao'}
MAX_BYTES = 10 * 1024 * 1024
ID = re.compile(r'[A-Za-z_][A-Za-z0-9_.:-]{0,255}\Z')


def _name(tag: str) -> str:
    return tag.split('}',1)[-1]


def read_lexml(raw: bytes, *, max_depth: int = 96, max_nodes: int = 100000) -> dict[str, Any]:
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_BYTES:
        raise ValueError('Invalid XML size or input type.')
    if type(max_depth) is not int or not 1 <= max_depth <= 128:
        raise ValueError('Invalid depth budget.')
    if type(max_nodes) is not int or not 1 <= max_nodes <= 200000:
        raise ValueError('Invalid node budget.')
    text = raw.decode('utf-8-sig', errors='strict')
    if '\x00' in text or re.search(r'<!\s*(DOCTYPE|ENTITY)', text, re.I):
        raise ValueError('DTD, entity declarations and NUL are forbidden.')
    declaration = re.match(r'\s*<\?xml\s+[^?]*encoding=["\']([^"\']+)', text, re.I)
    if declaration and declaration[1].lower().replace('-','') != 'utf8':
        raise ValueError('Only UTF-8 XML is supported.')
    seen_ids: set[str] = set()
    path_stack: list[str] = []
    sibling_stack: list[dict[str,int]] = []
    meta: dict[int,dict[str,Any]] = {}
    depth = nodes = 0
    root = None
    # iterparse permits stopping at the start event before deeply nested input
    # is assembled. The input byte budget bounds oversized text node memory.
    for event, el in ET.iterparse(io.StringIO(text), events=('start','end')):
        if event == 'start':
            depth += 1; nodes += 1
            if depth > max_depth or nodes > max_nodes:
                raise ValueError('XML resource budget exceeded.')
            if not isinstance(el.tag,str) or not el.tag.startswith('{'+NS+'}'):
                raise ValueError('Foreign or missing XML namespace.')
            name = _name(el.tag)
            if name.lower() in {'include','script','iframe'}:
                raise ValueError('Unsupported active XML element.')
            if root is None:
                root = el
                if name != 'LexML':
                    raise ValueError('Expected LexML root.')
            if sibling_stack:
                sibling_stack[-1][name] = sibling_stack[-1].get(name,0)+1
                ordinal = sibling_stack[-1][name]
            else:
                ordinal = 1
            path_stack.append(f'{name}[{ordinal}]'); sibling_stack.append({})
            element_id = el.get('id')
            if element_id:
                if not ID.fullmatch(element_id) or element_id in seen_ids:
                    raise ValueError('Invalid or duplicate XML id.')
                seen_ids.add(element_id)
            meta[id(el)] = {'path':'/'+('/'.join(path_stack)), 'source_id':element_id, 'order':nodes}
        else:
            depth -= 1; path_stack.pop(); sibling_stack.pop()
    if root is None:
        raise ValueError('Missing XML root.')
    out: list[dict[str,Any]] = []
    warnings: list[str] = []
    source_hash = hashlib.sha256(raw).hexdigest()

    def walk(el: ET.Element, parents: tuple[str,...], in_amendment: bool) -> None:
        name = _name(el.tag)
        local = meta[id(el)]
        amendment = in_amendment or name == 'Alteracao'
        if name in STRUCTURE:
            key = local['source_id'] or 'path-'+hashlib.sha256(local['path'].encode()).hexdigest()[:24]
            # Own text excludes structural children: caput and provisos stay
            # individually addressable instead of being duplicated at every level.
            parts: list[str] = []
            if el.text and el.text.strip():
                parts.append(el.text.strip())
            for child in el:
                if _name(child.tag) not in STRUCTURE:
                    val = ''.join(child.itertext()).strip()
                    if val: parts.append(val)
                if child.tail and child.tail.strip(): parts.append(child.tail.strip())
            label = next((''.join(c.itertext()).strip() for c in el if _name(c.tag)=='Rotulo'), '')
            own = '\n'.join(parts)
            record = {'id':key, 'type':name, 'label':label, 'parent_id':parents[-1] if parents else None,
                      'ancestor_ids':list(parents), 'own_text':own,
                      'xpath':local['path'], 'source_xml_id':local['source_id'],
                      'quoted_amendment':amendment, 'order':local['order'],
                      'source_sha256':source_hash,
                      'unit_sha256':hashlib.sha256(own.encode()).hexdigest(),
                      'legal_effect_verified':False}
            out.append(record); parents = (*parents,key)
            if not local['source_id']: warnings.append('generated_locator:'+local['path'])
        for child in el:
            walk(child, parents, amendment)
    walk(root, (), False)
    if not any(n['type']=='Artigo' for n in out):
        raise ValueError('No article in supported LexML structure.')
    return {'schema_version':'1.0', 'parser':'legal-br-lexml-subset', 'source_sha256':source_hash,
            'namespace':NS, 'nodes':out, 'warnings':warnings,
            'xsd_validated':False, 'source_authenticity_verified':False,
            'external_resource_fetches':0}


def article_chunks(document: dict[str,Any], *, max_chars: int = 12000) -> list[dict[str,Any]]:
    """Group whole article families; split only between provisions, never truncate.

An individual oversized provision is retained intact and flagged. Capacity
policies must reject/route it; they must not silently delete an exception.
"""
    if type(max_chars) is not int or not 64 <= max_chars <= 1000000:
        raise ValueError('Invalid chunk budget.')
    records = document['nodes']
    index = {item['id']:item for item in records}
    if len(index) != len(records): raise ValueError('Duplicate unit identifiers.')
    articles = [n for n in records if n['type']=='Artigo']
    by_article: dict[str,list[dict[str,Any]]] = {n['id']:[] for n in articles}
    for item in records:
        ancestry = [*item['ancestor_ids'],item['id']]
        nearest = next((key for key in reversed(ancestry) if key in by_article),None)
        if nearest and item['own_text']:
            by_article[nearest].append(item)
    chunks: list[dict[str,Any]] = []
    for article in articles:
        family = by_article[article['id']]
        groups: list[list[dict[str,Any]]] = []
        group: list[dict[str,Any]] = []; size = 0
        for item in family:
            extra = len(item['own_text']) + (2 if group else 0)
            if group and size + extra > max_chars:
                groups.append(group); group=[]; size=0
            group.append(item); size += len(item['own_text']) + (2 if len(group)>1 else 0)
        if group: groups.append(group)
        family_ids = [i['id'] for i in family]
        for number, members in enumerate(groups,1):
            chunk_text='\n\n'.join(i['own_text'] for i in members)
            member_ids=[i['id'] for i in members]
            chunks.append({'chunk_id':f"{article['id']}:part:{number}", 'article_id':article['id'],
                           'text':chunk_text, 'unit_ids':member_ids,
                           'required_context_ids':[i for i in family_ids if i not in member_ids],
                           'ancestor_ids':article['ancestor_ids'],
                           'quoted_amendment':article['quoted_amendment'],
                           'oversized':len(chunk_text)>max_chars,
                           'source_sha256':document['source_sha256'],
                           'text_sha256':hashlib.sha256(chunk_text.encode()).hexdigest(),
                           'part':number, 'parts':len(groups)})
    return chunks
