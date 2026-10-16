"""CAIL-inspired task separation and leakage-resistant evaluation utilities.

Consumes human labels and external score predictions, not a Chinese pretrained
judge. Scores are not called calibrated probabilities. No auto legal decisions.
"""
from __future__ import annotations
from datetime import date
import math
from typing import Any


def _finite(value: Any) -> float:
    if isinstance(value,bool) or not isinstance(value,(float,int)):
        raise ValueError('Expected finite numeric score.')
    try:
        numeric = float(value)
    except OverflowError as exc:
        raise ValueError('Numeric score exceeds finite range.') from exc
    if not math.isfinite(numeric):
        raise ValueError('Expected finite numeric score.')
    return numeric


def _label_set(values: Any) -> set[str]:
    if not isinstance(values,list) or len(values)>10000 or any(not isinstance(v,str) or not v or len(v)>128 for v in values):
        raise ValueError('Expected a list of nonempty labels.')
    if len(values)!=len(set(values)):raise ValueError('Duplicate labels.')
    return set(values)


def validate_split(rows: list[dict[str,Any]], *, cutoff: str) -> dict[str,Any]:
    """No matter/document-content family may cross train/dev/test boundaries."""
    if not isinstance(rows,list) or not rows or len(rows)>1000000:raise ValueError('Invalid dataset.')
    cut=date.fromisoformat(cutoff)
    ids=set();matters:dict[str,str]={};contents:dict[str,str]={}; counts={'train':0,'dev':0,'test':0}
    labels:dict[str,set[str]]={k:set() for k in counts}
    for row in rows:
        if set(row)!={'id','matter_id','content_sha256','split','available_on','labels'}:
            raise ValueError('Unexpected dataset fields.')
        for field in ('id','matter_id'):
            if not isinstance(row[field],str) or not row[field].strip() or len(row[field])>128:
                raise ValueError('Invalid dataset identifier.')
        if row['id'] in ids:raise ValueError('Duplicate example identifier.')
        ids.add(row['id']);partition=row['split'];digest=row['content_sha256']
        if partition not in counts:raise ValueError('Unknown split.')
        if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Expected SHA-256 digest.')
        for index,key in ((matters,row['matter_id']),(contents,digest)):
            if key in index and index[key]!=partition:raise ValueError('Cross-split leakage.')
            index[key]=partition
        observed=date.fromisoformat(row['available_on'])
        if (partition=='train' and observed>cut) or (partition!='train' and observed<=cut):
            raise ValueError('Temporal leakage or invalid holdout boundary.')
        labels[partition].update(_label_set(row['labels'])); counts[partition]+=1
    if not all(counts.values()):raise ValueError('Train, dev and test are required.')
    unseen=sorted((labels['dev']|labels['test'])-labels['train'])
    return {'split_valid':True,'counts':counts,'training_cutoff':cutoff,
            'unseen_holdout_labels':unseen,'labels_adjudicated':False,
            'legal_corpus_quality_verified':False}


def selective_triage(scores: dict[str,float], *, threshold: float,
                     minimum_margin: float, in_distribution: bool) -> dict[str,Any]:
    """Single-route proposal with abstention; scores are caller-supplied."""
    threshold=_finite(threshold); minimum_margin=_finite(minimum_margin)
    if not 0<=threshold<=1 or not 0<=minimum_margin<=1 or type(in_distribution) is not bool:
        raise ValueError('Invalid triage policy.')
    if not isinstance(scores,dict) or len(scores)<2 or len(scores)>10000:
        raise ValueError('At least two candidate routes are required.')
    normalized=[]
    for label,value in scores.items():
        if not isinstance(label,str) or not label or len(label)>128:raise ValueError('Invalid label.')
        score=_finite(value)
        if not 0<=score<=1:raise ValueError('Score must be within unit interval.')
        normalized.append((label,score))
    normalized.sort(key=lambda v:(-v[1],v[0]));top=normalized[0];margin=top[1]-normalized[1][1]
    reason=None
    if not in_distribution:reason='out_of_distribution'
    elif top[1]<threshold:reason='insufficient_score'
    elif margin<=0 or margin<minimum_margin:reason='ambiguous_routes'
    return {'proposed_route':None if reason else top[0],'abstained':reason is not None,
            'reason':reason,'top_score':top[1],'margin':margin,
            'calibration_verified':False,'distribution_assertion_verified':False,
            'automatic_legal_decision':False}


def evaluate_multilabel(rows: list[dict[str,Any]], *, labels: list[str]) -> dict[str,Any]:
    universe=_label_set(labels)
    if not universe or not isinstance(rows,list) or not rows or len(rows)>1000000:raise ValueError('Empty evaluation.')
    tally={k:{'tp':0,'fp':0,'fn':0} for k in sorted(universe)}
    ids=set(); abstentions=0;exact=0;accepted=0
    for row in rows:
        if set(row)!={'id','gold','predicted','abstained'} or not isinstance(row['id'],str) or not row['id']:
            raise ValueError('Unexpected prediction row.')
        if row['id'] in ids:raise ValueError('Duplicate prediction ID.')
        ids.add(row['id']);gold=_label_set(row['gold']);pred=_label_set(row['predicted'])
        if not (gold|pred)<=universe or type(row['abstained']) is not bool:raise ValueError('Invalid prediction.')
        if row['abstained']:
            if pred:raise ValueError('Abstention must not conceal a prediction.')
            abstentions+=1
        else:
            accepted+=1;exact+=int(gold==pred)
        # Abstention retains false negatives in end-to-end recall.
        for label in gold & pred:tally[label]['tp']+=1
        for label in pred-gold:tally[label]['fp']+=1
        for label in gold-pred:tally[label]['fn']+=1
    details={}
    for label,t in tally.items():
        precision=t['tp']/(t['tp']+t['fp']) if t['tp']+t['fp'] else 0.0
        recall=t['tp']/(t['tp']+t['fn']) if t['tp']+t['fn'] else 0.0
        f1=2*t['tp']/(2*t['tp']+t['fp']+t['fn']) if 2*t['tp']+t['fp']+t['fn'] else 0.0
        details[label]={**t,'precision':precision,'recall':recall,'f1':f1}
    tp=sum(v['tp'] for v in tally.values());fp=sum(v['fp'] for v in tally.values());fn=sum(v['fn'] for v in tally.values())
    return {'examples':len(rows),'abstentions':abstentions,'coverage':accepted/len(rows),
            'selective_exact_match':exact/accepted if accepted else None,
            'micro_f1':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.0,
            'macro_f1':sum(v['f1'] for v in details.values())/len(details),
            'per_label':details,'abstention_counts_as_false_negative':True,
            'source_labels_verified':False,'legal_accuracy_established':False}
