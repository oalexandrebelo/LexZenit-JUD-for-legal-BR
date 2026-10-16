"""Read/write local workspace CLI. No network requests or automatic legal acts."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sqlite3
import sys
from .store import Workspace


def main(argv: list[str] | None = None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',required=True,type=Path)
    p.add_argument('--matter',required=True)
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('init')
    i=sub.add_parser('ingest');i.add_argument('--file',type=Path,required=True);i.add_argument('--title',required=True);i.add_argument('--source-id',required=True);i.add_argument('--kind',choices=['case','normative'],required=True)
    a=sub.add_parser('attest');a.add_argument('--document-id',required=True);a.add_argument('--reviewer',required=True);a.add_argument('--reason',required=True);a.add_argument('--status',choices=['reviewed','rejected'],required=True);a.add_argument('--valid-from');a.add_argument('--valid-until')
    s=sub.add_parser('search');s.add_argument('--query',required=True);s.add_argument('--effective-on',required=True);s.add_argument('--known-at');s.add_argument('--include-unverified',action='store_true');s.add_argument('--limit',type=int,default=10);s.add_argument('--hops',type=int,default=1)
    q=sub.add_parser('quote');q.add_argument('--chunk-id',required=True);q.add_argument('--text',required=True)
    l=sub.add_parser('link');l.add_argument('--source',required=True);l.add_argument('--target',required=True);l.add_argument('--relation',required=True);l.add_argument('--evidence',required=True);l.add_argument('--quotation',required=True)
    r=sub.add_parser('review-link');r.add_argument('--edge',required=True);r.add_argument('--status',choices=['reviewed','rejected'],required=True);r.add_argument('--reviewer',required=True);r.add_argument('--reason',required=True)
    v=sub.add_parser('verify');v.add_argument('--expected-head')
    args=p.parse_args(argv)
    try:
        if args.command != 'init' and not args.db.is_file():
            raise ValueError('Initialize the workspace explicitly first.')
        with Workspace(args.db,args.matter) as ws:
            if args.command=='init':result={'matter':ws.matter,'created_or_opened':True}
            elif args.command=='ingest':result=ws.ingest_file(args.file,source_id=args.source_id,title=args.title,kind=args.kind)
            elif args.command=='attest':result={'attestation':ws.attest(args.document_id,reviewer=args.reviewer,reason=args.reason,status=args.status,valid_from=args.valid_from,valid_until=args.valid_until),'identity_authenticated':False}
            elif args.command=='search':result=ws.search(args.query,effective_on=args.effective_on,known_at=args.known_at,verified_only=not args.include_unverified,limit=args.limit,hops=args.hops)
            elif args.command=='quote':result=ws.quote(args.chunk_id,args.text)
            elif args.command=='link':result={'edge':ws.link(args.source,args.target,args.relation,args.evidence,args.quotation),'status':'proposed'}
            elif args.command=='review-link':result={'review':ws.review_link(args.edge,status=args.status,reviewer=args.reviewer,reason=args.reason),'identity_authenticated':False}
            else:result=ws.integrity(args.expected_head)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (ValueError,UnicodeError,OSError,sqlite3.Error) as exc:
        # No tracebacks/document text, tokens or secret values in normal CLI errors.
        print(json.dumps({'error_type':type(exc).__name__,'error':'Operation failed; validate inputs and local workspace integrity.'}),file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
