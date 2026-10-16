"""Explicit local engineering CLI. No network, model download or external act."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import stat
import sys
import xml.etree.ElementTree as ET
from typing import Any
from .citations import extract_citations, extract_us_citations, parse_ecli, IntegrationUnavailable
from .lexml import read_lexml, article_chunks
from .privacy import EntitySpan, pseudonymize
from .evaluation import evaluate_multilabel, validate_split, selective_triage


def read_bytes(path: Path, limit: int = 10*1024*1024, *, secret: bool = False) -> bytes:
    # Validate the opened descriptor, not a pathname that can change after stat.
    # Ancestor directories remain a host boundary; this CLI is not a sandbox.
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    if not hasattr(os, 'O_NOFOLLOW') and path.is_symlink():
        raise ValueError('Symbolic input paths are not accepted.')
    fd = os.open(path, flags)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise ValueError('Expected a regular file.')
        if secret and os.name == 'posix' and info.st_mode & 0o077:
            raise ValueError('Key permissions allow other users.')
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Input size exceeded.')
    return data


def read_json(path: Path) -> Any:
    def invalid_constant(value: str) -> None:
        raise ValueError('Non-finite JSON value.')
    return json.loads(read_bytes(path).decode('utf8'),parse_constant=invalid_constant)


def main(argv: list[str] | None = None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,help='Create a private new file; existing files are never overwritten.')
    sub=p.add_subparsers(dest='command',required=True)
    c=sub.add_parser('citations');c.add_argument('--file',type=Path,required=True);c.add_argument('--jurisdiction',choices=['BR','US'],default='BR')
    x=sub.add_parser('lexml');x.add_argument('--file',type=Path,required=True);x.add_argument('--max-chars',type=int,default=12000)
    e=sub.add_parser('ecli');e.add_argument('identifier')
    r=sub.add_parser('privacy');r.add_argument('--file',type=Path,required=True);r.add_argument('--entities',type=Path);r.add_argument('--key-file',type=Path,required=True);r.add_argument('--tenant',required=True);r.add_argument('--matter',required=True)
    v=sub.add_parser('evaluate');v.add_argument('--file',type=Path,required=True)
    s=sub.add_parser('validate-split');s.add_argument('--file',type=Path,required=True);s.add_argument('--cutoff',required=True)
    t=sub.add_parser('triage');t.add_argument('--file',type=Path,required=True)
    args=p.parse_args(argv)
    try:
        if args.command=='citations':
            text=read_bytes(args.file).decode('utf8')
            result=(extract_citations if args.jurisdiction=='BR' else extract_us_citations)(text)
        elif args.command=='lexml':
            result=read_lexml(read_bytes(args.file));result['chunks']=article_chunks(result,max_chars=args.max_chars)
        elif args.command=='ecli':result=parse_ecli(args.identifier)
        elif args.command=='privacy':
            key=read_bytes(args.key_file,4096,secret=True)
            entities=[]
            if args.entities:
                supplied=read_json(args.entities)
                if not isinstance(supplied,list):raise ValueError('Entities must be a JSON array.')
                entities=[EntitySpan(**item) for item in supplied]
            result=pseudonymize(read_bytes(args.file).decode('utf8'),key=key,tenant=args.tenant,matter=args.matter,entities=entities)
        elif args.command=='evaluate':
            payload=read_json(args.file)
            if set(payload)!={'rows','labels'}:raise ValueError('Unexpected evaluation fields.')
            result=evaluate_multilabel(payload['rows'],labels=payload['labels'])
        elif args.command=='validate-split':result=validate_split(read_json(args.file),cutoff=args.cutoff)
        else:
            payload=read_json(args.file)
            if set(payload)!={'scores','threshold','minimum_margin','in_distribution'}:raise ValueError('Unexpected triage fields.')
            result=selective_triage(**payload)
        output=json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
        if args.output:
            fd=os.open(args.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'w',encoding='utf8') as stream:stream.write(output)
        else:print(output,end='')
        return 0
    except (ValueError,TypeError,KeyError,OSError,UnicodeError,ET.ParseError,IntegrationUnavailable):
        # Never echo input text, paths, raw identifiers or secret material.
        print(json.dumps({'status':'blocked','error':'invalid_input_or_unavailable_optional_dependency',
                          'legal_conclusion':None}),file=sys.stderr)
        return 2


if __name__=='__main__':raise SystemExit(main())
