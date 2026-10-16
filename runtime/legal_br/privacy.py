"""Local span redaction and case-scoped pseudonymization, not anonymization.

LeNER-Br supplies an NER task/dataset concept. No checkpoint is bundled or
silently downloaded. PERSON spans can be produced by an authorized local model
or a reviewer. Pattern recognition complements NER; neither proves completeness.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import hmac
import json
import re
import unicodedata
from typing import Any, Iterable
from .citations import checked_text

CPF = re.compile(r'(?<![0-9])(?:[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}|[0-9]{11})(?![0-9])')
EMAIL = re.compile(r'(?<![\w.+-])[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]{1,64}@[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?\.[A-Za-z]{2,63}(?![\w-])')
PHONE = re.compile(r'(?<![0-9])(?:\+55\s*)?\([1-9][0-9]\)\s*[0-9]{4,5}[-\s]?[0-9]{4}(?![0-9])')
TAG_MAP = {'PESSOA':'PERSON','PERSON':'PERSON','LOCAL':'LOCATION','LOCATION':'LOCATION',
           'ORGANIZACAO':'ORGANIZATION','ORGANIZAÇÃO':'ORGANIZATION','ORGANIZATION':'ORGANIZATION',
           'TEMPO':'TIME','TIME':'TIME','LEGISLACAO':'LEGISLATION','LEGISLAÇÃO':'LEGISLATION',
           'LEGISLATION':'LEGISLATION','JURISPRUDENCIA':'JURISPRUDENCE',
           'JURISPRUDÊNCIA':'JURISPRUDENCE','JURISPRUDENCE':'JURISPRUDENCE'}
MASKABLE = {'PERSON','LOCATION','TIME','ORGANIZATION','CPF','EMAIL','PHONE','ID','SENSITIVE'}
DEFAULT_MASK = frozenset({'PERSON','LOCATION','CPF','EMAIL','PHONE','ID','SENSITIVE'})


@dataclass(frozen=True)
class EntitySpan:
    start: int
    end: int
    label: str
    source: str = 'reviewer_or_local_ner'

    def validate(self, text: str) -> None:
        if type(self.start) is not int or type(self.end) is not int or not 0 <= self.start < self.end <= len(text):
            raise ValueError('Invalid entity offsets.')
        if self.label not in MASKABLE | {'LEGISLATION','JURISPRUDENCE'}:
            raise ValueError('Unsupported entity label.')
        if not isinstance(self.source,str) or not self.source.strip() or len(self.source)>80:
            raise ValueError('Invalid entity provenance.')


def bio_spans(text: str, tokens: list[str], tags: list[str]) -> list[EntitySpan]:
    """Strict full-document CoNLL BIO alignment; rejects dropped text/invalid I-."""
    text=checked_text(text)
    if not isinstance(tokens,list) or not isinstance(tags,list) or not tokens or len(tokens)!=len(tags):
        raise ValueError('Token/tag length mismatch.')
    if len(tokens)>1000000: raise ValueError('Token budget exceeded.')
    offsets=[]; cursor=0
    for token in tokens:
        if not isinstance(token,str) or not token or token.isspace(): raise ValueError('Invalid token.')
        start=text.find(token,cursor)
        if start < 0 or text[cursor:start].strip(): raise ValueError('Tokens do not preserve original text.')
        offsets.append((start,start+len(token))); cursor=start+len(token)
    if text[cursor:].strip(): raise ValueError('Unaligned document tail.')
    spans=[]; active: tuple[int,int,str] | None=None
    def close() -> None:
        nonlocal active
        if active:
            spans.append(EntitySpan(*active,source='conll_bio_adapter')); active=None
    for (start,end),tag in zip(offsets,tags,strict=True):
        if tag=='O': close(); continue
        if not isinstance(tag,str) or len(tag)<3 or tag[:2] not in {'B-','I-'} or tag[2:] not in TAG_MAP:
            raise ValueError('Unsupported BIO tag.')
        label=TAG_MAP[tag[2:]]
        if tag[:2]=='B-': close(); active=(start,end,label)
        elif active is None or active[2]!=label:
            raise ValueError('Invalid BIO continuation.')
        else: active=(active[0],end,label)
    close()
    return spans


def cpf_checksum_valid(value: str) -> bool:
    digits=re.sub(r'[^0-9]','',value)
    if len(digits)!=11 or len(set(digits))==1:return False
    numbers=[int(i) for i in digits]
    for k in (9,10):
        digit=(sum(numbers[i]*(k+1-i) for i in range(k))*10)%11
        if digit==10:digit=0
        if numbers[k]!=digit:return False
    return True


def detect_patterns(text: str) -> list[EntitySpan]:
    text=checked_text(text)
    found=[]
    for pattern,label in ((CPF,'CPF'),(EMAIL,'EMAIL'),(PHONE,'PHONE')):
        for match in pattern.finditer(text):
            if len(found)>=100000:raise ValueError('Pattern entity budget exceeded.')
            found.append(EntitySpan(match.start(),match.end(),label,'local_pattern'))
    return found


def pseudonymize(text: str, *, key: bytes, tenant: str, matter: str,
                 entities: Iterable[EntitySpan] = (), labels: frozenset[str] = DEFAULT_MASK) -> dict[str,Any]:
    text=checked_text(text)
    if not isinstance(key,bytes) or not 32<=len(key)<=4096:raise ValueError('Key must be 32 to 4096 bytes.')
    for scope in (tenant,matter):
        if not isinstance(scope,str) or not scope.strip() or len(scope)>128 or any(ord(c)<32 for c in scope):
            raise ValueError('Invalid trust scope.')
    if not isinstance(labels,frozenset) or not labels <= MASKABLE or not {'CPF','EMAIL','PHONE'} <= labels:
        raise ValueError('Direct-identifier masking cannot be disabled.')
    supplied=[]
    for entity in entities:
        if len(supplied)>=100000:raise ValueError('Entity budget exceeded.')
        supplied.append(entity)
    for span in supplied:
        if not isinstance(span,EntitySpan):raise ValueError('Expected typed entity span.')
        span.validate(text)
    candidates=[s for s in [*supplied,*detect_patterns(text)] if s.label in labels]
    candidates.sort(key=lambda s:(s.start,s.end,s.label))
    # Union overlapping spans, never let a lower-priority entity expose a suffix.
    groups: list[list[EntitySpan]]=[]
    group_end=-1
    for span in candidates:
        if groups and span.start<group_end:
            groups[-1].append(span); group_end=max(group_end,span.end)
        else:
            groups.append([span]); group_end=span.end
    output=[]; metadata=[]; cursor=0; output_length=0
    for group in groups:
        start=min(s.start for s in group);end=max(s.end for s in group)
        label_set=sorted({s.label for s in group})
        label=label_set[0] if len(label_set)==1 else 'SENSITIVE'
        raw=text[start:end]
        normalized=unicodedata.normalize('NFC',raw)
        if label=='CPF':normalized=re.sub(r'[^0-9]','',raw)
        # Length-delimited JSON avoids tenant/matter separator collisions.
        message=json.dumps(['legal-br-pseudo-v1',tenant,matter,label,normalized],
                           ensure_ascii=False,separators=(',',':')).encode()
        token=f'[{label}_{hmac.new(key,message,hashlib.sha256).hexdigest()[:32]}]'
        prefix=text[cursor:start]; output.append(prefix);output_length+=len(prefix)
        output_start=output_length;output.append(token);output_length+=len(token)
        metadata.append({'original_start':start,'original_end':end,'output_start':output_start,
                         'output_end':output_length,'labels':label_set,'pseudonym':token,
                         'provenance':sorted({s.source for s in group}),
                         'checksum_valid':cpf_checksum_valid(raw) if label=='CPF' else None})
        cursor=end
    output.append(text[cursor:]);redacted=''.join(output)
    return {'schema_version':'1.0','text':redacted,'redactions':metadata,
            'source_sha256':hashlib.sha256(text.encode()).hexdigest(),
            'redacted_sha256':hashlib.sha256(redacted.encode()).hexdigest(),
            'coordinate_system':'unicode_codepoints','mapping_persisted':False,
            'ner_model_executed':False,'supplied_entities':len(supplied),
            'anonymity_guaranteed':False,'pii_coverage':'partial_requires_review',
            'egress_authorized':False,
            'warnings':['unrecognized_identifiers_and_names_may_remain',
                        'pseudonyms_and_offsets_remain_sensitive',
                        'authenticated_review_and_egress_policy_required']}
