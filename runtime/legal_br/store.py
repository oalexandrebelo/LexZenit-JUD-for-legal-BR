"""Local evidence workspace. No network, LLM, authentication, or legal decision.

One SQLite database per matter. The caller owns filesystem permissions and reviewer
identity. Local attestations are recorded assertions, not certified legal opinions.
"""
from __future__ import annotations

from contextlib import contextmanager
from bisect import bisect_left
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Iterator
from uuid import uuid4

MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
RELATIONS = frozenset({'references', 'supports', 'contradicts', 'amends', 'revokes', 'interprets'})
ID = re.compile(r'^[a-z0-9][a-z0-9._:-]{0,127}$')


def timestamp(value: str | None = None) -> str:
    if value is not None and not isinstance(value, str):
        raise ValueError('Timestamp must be text.')
    dt = datetime.now(timezone.utc) if value is None else datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError('Timestamp must include timezone.')
    return dt.astimezone(timezone.utc).isoformat(timespec='microseconds')


def day(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError('Date must be text.')
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError('Use YYYY-MM-DD.')
    return value


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(data: object) -> str:
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def nonempty(value: str, name: str, maximum: int = 8192) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum or '\x00' in value:
        raise ValueError(f'Invalid {name}.')
    return value


def segments(text: str, size: int = 4000, overlap: int = 400) -> Iterator[tuple[int, int]]:
    """Character-offset windows with newline preference; NOT semantic/token chunking."""
    if type(size) is not int or type(overlap) is not int or not 64 <= size <= 16000 or not 0 <= overlap < size // 2:
        raise ValueError('Invalid window parameters.')
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        if end < len(text):
            boundary = text.rfind('\n', start + size // 2, end)
            if boundary > start:
                end = boundary + 1
        yield start, end
        if end == len(text):
            break
        start = end - overlap


SCHEMA = '''
CREATE TABLE IF NOT EXISTS workspace(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS documents(
 id TEXT PRIMARY KEY, fingerprint TEXT UNIQUE NOT NULL, source_id TEXT NOT NULL,
 title TEXT NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('case','normative')),
 original BLOB NOT NULL, sha256 TEXT NOT NULL, content TEXT NOT NULL,
 observed_at TEXT NOT NULL, recorded_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS chunks(
 id TEXT PRIMARY KEY, doc_id TEXT NOT NULL REFERENCES documents(id), ordinal INTEGER NOT NULL,
 start_offset INTEGER NOT NULL, end_offset INTEGER NOT NULL,
 start_line INTEGER NOT NULL, end_line INTEGER NOT NULL,
 content TEXT NOT NULL, sha256 TEXT NOT NULL, UNIQUE(doc_id,ordinal));
CREATE VIRTUAL TABLE IF NOT EXISTS chunk_fts USING fts5(chunk_id UNINDEXED, content, tokenize='unicode61 remove_diacritics 2');
CREATE TABLE IF NOT EXISTS attestations(
 seq INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT NOT NULL REFERENCES documents(id),
 status TEXT NOT NULL CHECK(status IN ('reviewed','rejected')),
 reviewer TEXT NOT NULL, reason TEXT NOT NULL, valid_from TEXT, valid_until TEXT,
 recorded_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS attestations_lookup ON attestations(doc_id,recorded_at,seq);
CREATE TABLE IF NOT EXISTS edges(
 id TEXT PRIMARY KEY, source_chunk TEXT NOT NULL REFERENCES chunks(id),
 target_chunk TEXT NOT NULL REFERENCES chunks(id), relation TEXT NOT NULL,
 evidence_chunk TEXT NOT NULL REFERENCES chunks(id), quotation TEXT NOT NULL,
 recorded_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS edges_source ON edges(source_chunk);
CREATE TABLE IF NOT EXISTS edge_reviews(
 seq INTEGER PRIMARY KEY AUTOINCREMENT, edge_id TEXT NOT NULL REFERENCES edges(id),
 status TEXT NOT NULL CHECK(status IN ('reviewed','rejected')),
 reviewer TEXT NOT NULL, reason TEXT NOT NULL, recorded_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS edge_review_lookup ON edge_reviews(edge_id,recorded_at,seq);
CREATE TABLE IF NOT EXISTS audit(
 seq INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL, previous TEXT NOT NULL, sha256 TEXT NOT NULL UNIQUE);
'''


class Workspace:
    def __init__(self, path: Path | str, matter: str) -> None:
        if not isinstance(matter, str) or not ID.fullmatch(matter):
            raise ValueError('Invalid matter identifier.')
        path = Path(path)
        if path.is_symlink():
            raise ValueError('Database must not be a symbolic link.')
        existing_file = path.is_file() and path.stat().st_size > 0
        self.db = sqlite3.connect(str(path), timeout=5, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        try:
            if existing_file:
                table = self.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='workspace'").fetchone()
                if not table:
                    raise ValueError('Existing database is not a legal-br workspace.')
                identity = dict(self.db.execute('SELECT key,value FROM workspace').fetchall())
                if identity.get('matter') != matter or identity.get('schema') != '1':
                    raise ValueError('Wrong matter or unsupported workspace schema.')
            self.db.execute('PRAGMA foreign_keys=ON')
            self.db.execute('PRAGMA journal_mode=WAL')
            self.db.execute('PRAGMA synchronous=FULL')
            self.db.executescript(SCHEMA)
            with self.transaction():
                existing = dict(self.db.execute('SELECT key,value FROM workspace').fetchall())
                if existing and (existing.get('matter') != matter or existing.get('schema') != '1'):
                    raise ValueError('Wrong matter or unsupported workspace schema.')
                if not existing:
                    self.db.executemany('INSERT INTO workspace VALUES(?,?)', [('matter', matter), ('schema', '1')])
            self.matter = matter
        except BaseException:
            self.db.close()
            raise

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> Workspace:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @contextmanager
    def transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def _audit(self, action: str, payload: dict) -> None:
        last = self.db.execute('SELECT sha256 FROM audit ORDER BY seq DESC LIMIT 1').fetchone()
        previous = last[0] if last else '0' * 64
        event = canonical({'action': action, 'matter': self.matter, 'payload': payload, 'at': timestamp()})
        value = digest((previous + '\n' + event).encode())
        self.db.execute('INSERT INTO audit(event,previous,sha256) VALUES(?,?,?)', (event, previous, value))

    def ingest(self, raw: bytes, *, source_id: str, title: str, kind: str,
               observed_at: str | None = None) -> dict:
        if not isinstance(raw, bytes) or not raw or len(raw) > MAX_DOCUMENT_BYTES:
            raise ValueError('Document must be nonempty bytes within the 10 MiB limit.')
        nonempty(source_id, 'source_id', 2048)
        nonempty(title, 'title', 1024)
        if kind not in {'case', 'normative'}:
            raise ValueError('Invalid document kind.')
        text = raw.decode('utf-8-sig', errors='strict')
        nonempty(text, 'text', MAX_DOCUMENT_BYTES)
        if text.startswith('%PDF-') or '\x00' in text:
            raise ValueError('Only UTF-8 text is supported; extract PDFs separately with provenance.')
        observed = timestamp(observed_at)
        recorded = timestamp()
        if observed > recorded:
            raise ValueError('Observation cannot be in the future.')
        sha = digest(raw)
        fingerprint = digest(canonical([source_id, title, kind, sha]).encode())
        with self.transaction():
            row = self.db.execute('SELECT id FROM documents WHERE fingerprint=?', (fingerprint,)).fetchone()
            if row:
                return {'document_id': row['id'], 'sha256': sha, 'deduplicated': True}
            doc = str(uuid4())
            self.db.execute('INSERT INTO documents VALUES(?,?,?,?,?,?,?,?,?,?)',
                            (doc, fingerprint, source_id, title, kind, raw, sha, text, observed, recorded))
            count = 0
            newline_offsets = [i for i, character in enumerate(text) if character == '\n']
            for ordinal, (start, end) in enumerate(segments(text)):
                value = text[start:end]
                cid = digest(f'{doc}:{start}:{end}'.encode())
                self.db.execute('INSERT INTO chunks VALUES(?,?,?,?,?,?,?,?,?)',
                                (cid, doc, ordinal, start, end, bisect_left(newline_offsets, start)+1,
                                 bisect_left(newline_offsets, end-1)+1, value, digest(value.encode())))
                self.db.execute('INSERT INTO chunk_fts(chunk_id,content) VALUES(?,?)', (cid, value))
                count += 1
            self._audit('ingest', {'document_id': doc, 'sha256': sha, 'fingerprint': fingerprint, 'chunks': count})
            return {'document_id': doc, 'sha256': sha, 'deduplicated': False, 'chunks': count,
                    'source_status': 'unverified', 'legal_validity': 'unknown'}

    def ingest_file(self, path: Path, **metadata) -> dict:
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in {'.md', '.txt'}:
            raise ValueError('Provide a regular .md or .txt file; symlinks are not accepted.')
        with path.open('rb') as stream:
            raw = stream.read(MAX_DOCUMENT_BYTES + 1)
        return self.ingest(raw, **metadata)

    def attest(self, doc_id: str, *, reviewer: str, reason: str, status: str,
               valid_from: str | None = None, valid_until: str | None = None) -> int:
        nonempty(reviewer, 'reviewer', 256)
        nonempty(reason, 'reason')
        if status not in {'reviewed', 'rejected'}:
            raise ValueError('Invalid attestation status.')
        if valid_from is not None:
            day(valid_from)
        if valid_until is not None:
            day(valid_until)
            if valid_from is None or valid_until <= valid_from:
                raise ValueError('Validity is [from,until); an end requires an earlier start.')
        with self.transaction():
            if not self.db.execute('SELECT 1 FROM documents WHERE id=?', (doc_id,)).fetchone():
                raise ValueError('Unknown document.')
            now = timestamp()
            cur = self.db.execute('INSERT INTO attestations(doc_id,status,reviewer,reason,valid_from,valid_until,recorded_at) VALUES(?,?,?,?,?,?,?)',
                                  (doc_id,status,reviewer,reason,valid_from,valid_until,now))
            seq = cur.lastrowid
            self._audit('attest', {'sequence': seq, 'document_id': doc_id, 'status': status,
                                  'reviewer': reviewer, 'reason': reason, 'valid_from': valid_from, 'valid_until': valid_until})
            return seq

    def _eligibility(self, doc_id: str, effective_on: str, known_at: str) -> tuple[bool, str]:
        doc = self.db.execute('SELECT kind,observed_at,recorded_at FROM documents WHERE id=?', (doc_id,)).fetchone()
        if not doc or doc['recorded_at'] > known_at or doc['observed_at'] > known_at:
            return False, 'not_known_at_snapshot'
        review = self.db.execute('SELECT * FROM attestations WHERE doc_id=? AND recorded_at<=? ORDER BY recorded_at DESC,seq DESC LIMIT 1',
                                 (doc_id, known_at)).fetchone()
        if not review:
            return False, 'unverified'
        if review['status'] != 'reviewed':
            return False, 'rejected'
        if doc['kind'] == 'normative':
            if review['valid_from'] is None:
                return False, 'unknown_legal_time'
            if effective_on < review['valid_from'] or (review['valid_until'] is not None and effective_on >= review['valid_until']):
                return False, 'outside_legal_time'
        return True, 'locally_attested_not_independently_certified'

    def quote(self, chunk_id: str, quotation: str) -> dict:
        nonempty(quotation, 'quotation', 16000)
        row = self.db.execute('SELECT c.*, d.original, d.sha256 AS document_sha256 FROM chunks c JOIN documents d ON d.id=c.doc_id WHERE c.id=?', (chunk_id,)).fetchone()
        if not row:
            raise ValueError('Unknown chunk.')
        if digest(row['original']) != row['document_sha256'] or digest(row['content'].encode()) != row['sha256']:
            raise ValueError('Content integrity failure.')
        parent = row['original'].decode('utf-8-sig')
        if row['content'] != parent[row['start_offset']:row['end_offset']]:
            raise ValueError('Chunk does not match original offsets.')
        if quotation not in row['content']:
            raise ValueError('Quotation is not an exact substring of the referenced chunk.')
        start = row['start_offset'] + row['content'].index(quotation)
        end = start + len(quotation)
        return {'chunk_id': chunk_id, 'quote_start_offset': start, 'quote_end_offset': end, 'document_id': row['doc_id'], 'document_sha256': row['document_sha256'],
                'start_line': parent.count('\n', 0, start)+1, 'end_line': parent.count('\n', 0, end-1)+1, 'quotation': quotation,
                'semantic_support_verified': False}

    def link(self, source: str, target: str, relation: str, evidence: str, quotation: str) -> str:
        if relation not in RELATIONS or source == target:
            raise ValueError('Unsupported relation or reflexive link.')
        with self.transaction():
            for cid in (source, target):
                if not self.db.execute('SELECT 1 FROM chunks WHERE id=?', (cid,)).fetchone():
                    raise ValueError('Unknown edge endpoint.')
            self.quote(evidence, quotation)
            edge = str(uuid4())
            self.db.execute('INSERT INTO edges VALUES(?,?,?,?,?,?,?)', (edge, source, target, relation, evidence, quotation, timestamp()))
            self._audit('propose_edge', {'edge': edge, 'source': source, 'target': target, 'relation': relation,
                                         'evidence': evidence, 'quotation': quotation})
            return edge

    def review_link(self, edge: str, *, status: str, reviewer: str, reason: str) -> int:
        if status not in {'reviewed', 'rejected'}:
            raise ValueError('Invalid edge review status.')
        nonempty(reviewer,'reviewer',256); nonempty(reason,'reason')
        with self.transaction():
            if not self.db.execute('SELECT 1 FROM edges WHERE id=?',(edge,)).fetchone():
                raise ValueError('Unknown edge.')
            cur = self.db.execute('INSERT INTO edge_reviews(edge_id,status,reviewer,reason,recorded_at) VALUES(?,?,?,?,?)',
                                  (edge,status,reviewer,reason,timestamp()))
            self._audit('review_edge', {'edge':edge,'sequence':cur.lastrowid,'status':status,'reviewer':reviewer,'reason':reason})
            return cur.lastrowid

    def search(self, query: str, *, effective_on: str, known_at: str | None = None,
               verified_only: bool = True, limit: int = 10, hops: int = 1, max_nodes: int = 100, max_edges: int = 2000) -> dict:
        nonempty(query, 'query', 2048); day(effective_on); known=timestamp(known_at)
        if type(verified_only) is not bool or type(limit) is not int or not 1 <= limit <= 100 or type(hops) is not int or not 0 <= hops <= 3 or type(max_nodes) is not int or not limit <= max_nodes <= 1000 or type(max_edges) is not int or not 1 <= max_edges <= 10000:
            raise ValueError('Invalid bounded retrieval parameters.')
        terms=re.findall(r'[^\W_]+',query,flags=re.UNICODE)[:32]
        if not terms:
            raise ValueError('Query has no searchable terms.')
        expression=' OR '.join('"'+t.replace('"','""')+'"' for t in terms)
        # Read transaction pins an SQLite snapshot across eligibility and graph queries.
        self.db.execute('BEGIN')
        try:
            rows=self.db.execute('SELECT c.*, d.title, d.source_id, d.kind, bm25(chunk_fts) AS rank FROM chunk_fts JOIN chunks c ON c.id=chunk_fts.chunk_id JOIN documents d ON d.id=c.doc_id WHERE chunk_fts MATCH ? ORDER BY rank,c.id LIMIT 1001',(expression,)).fetchall()
            selected=[]; seen=set(); paths=[]; excluded={}; candidate_truncated=len(rows)>1000
            eligible_ids=set()
            for r in rows[:1000]:
                ok,why=self._eligibility(r['doc_id'],effective_on,known)
                if why in {'not_known_at_snapshot','rejected','outside_legal_time'} or (verified_only and not ok):
                    excluded[why]=excluded.get(why,0)+1;continue
                self.quote(r['id'], r['content'])
                if ok: eligible_ids.add(r['id'])
                item=dict(r);item['eligibility']=why;item['via']='lexical';selected.append(item);seen.add(r['id'])
                if len(selected)>=limit: break
            frontier=[x['id'] for x in selected if x['id'] in eligible_ids]
            graph_truncated=False
            inspected_edges=0
            for _ in range(hops):
                following=[]
                for current in frontier:
                    if inspected_edges >= max_edges:
                        graph_truncated=True;break
                    edges=self.db.execute('SELECT e.* FROM edges e WHERE e.source_chunk=? AND e.recorded_at<=? AND (SELECT r.status FROM edge_reviews r WHERE r.edge_id=e.id AND r.recorded_at<=? ORDER BY r.recorded_at DESC,r.seq DESC LIMIT 1)=? ORDER BY e.id LIMIT 1001', (current,known,known,'reviewed')).fetchall()
                    if len(edges)>1000:graph_truncated=True
                    for e in edges[:1000]:
                        if inspected_edges >= max_edges:
                            graph_truncated=True;break
                        inspected_edges += 1
                        evidence_doc=self.db.execute('SELECT doc_id FROM chunks WHERE id=?',(e['evidence_chunk'],)).fetchone()[0]
                        evidence_ok,_=self._eligibility(evidence_doc,effective_on,known)
                        if not evidence_ok:continue
                        self.quote(e['evidence_chunk'],e['quotation'])
                        target=self.db.execute('SELECT c.*,d.title,d.source_id,d.kind FROM chunks c JOIN documents d ON d.id=c.doc_id WHERE c.id=?',(e['target_chunk'],)).fetchone()
                        ok,why=self._eligibility(target['doc_id'],effective_on,known)
                        if not ok:continue
                        self.quote(target['id'],target['content'])
                        if target['id'] not in seen:
                            if len(seen)>=max_nodes:graph_truncated=True;continue
                            seen.add(target['id']);following.append(target['id'])
                            item=dict(target);item['eligibility']=why;item['via']='reviewed_graph';selected.append(item)
                        paths.append({'edge_id':e['id'],'source':current,'target':target['id'],'relation':e['relation'],'evidence_chunk':e['evidence_chunk']})
                frontier=following
                if not frontier:break
            return {'matter':self.matter,'effective_on':effective_on,'known_at':known,'results':selected,'paths':paths,
                    'excluded_candidates':excluded,'candidate_window_truncated':candidate_truncated,
                    'graph_truncated':graph_truncated,'inspected_edges':inspected_edges,'generation_performed':False,'semantic_support_verified':False,
                    'notice':'Local attestations only; retrieval is not a legal conclusion.'}
        finally:
            self.db.execute('ROLLBACK')

    def integrity(self, expected_head: str | None = None) -> dict:
        previous='0'*64;count=0
        for r in self.db.execute('SELECT * FROM audit ORDER BY seq'):
            if r['previous']!=previous or r['sha256']!=digest((previous+'\n'+r['event']).encode()):
                raise ValueError('Audit chain failure.')
            previous=r['sha256'];count+=1
        if expected_head is not None and previous!=expected_head:
            raise ValueError('External anchor mismatch.')
        docs=0;chunks=0
        for d in self.db.execute('SELECT * FROM documents'):
            if digest(d['original'])!=d['sha256'] or d['original'].decode('utf-8-sig')!=d['content']:
                raise ValueError('Document integrity failure.')
            if d['fingerprint']!=digest(canonical([d['source_id'],d['title'],d['kind'],d['sha256']]).encode()):
                raise ValueError('Metadata fingerprint failure.')
            docs+=1
        for c in self.db.execute('SELECT c.*,d.content AS parent_text FROM chunks c JOIN documents d ON d.id=c.doc_id'):
            if c['content']!=c['parent_text'][c['start_offset']:c['end_offset']] or digest(c['content'].encode())!=c['sha256']:
                raise ValueError('Chunk integrity failure.')
            chunks+=1
        return {'events':count,'documents':docs,'chunks':chunks,'head':previous,'externally_anchored':expected_head is not None,
                'signature_verified':False,'limitation':'Not WORM, not authenticated reviewers, not a full database tamper proof.'}
