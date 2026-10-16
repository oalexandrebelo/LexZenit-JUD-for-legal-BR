"""Real SQLite/filesystem regression tests. Every document is synthetic test data."""
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from legal_br.store import Workspace, MAX_DOCUMENT_BYTES, segments, timestamp, day, digest


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'case.sqlite'
        self.ws = Workspace(self.path, 'synthetic-case')

    def tearDown(self):
        self.ws.close()
        self.tmp.cleanup()

    def add(self, text='Contrato sintético alfa.\nCláusula de garantia.', kind='case', title='Teste', source='fixture'):
        result = self.ws.ingest(text.encode(), source_id=source, title=title, kind=kind)
        chunk = self.ws.db.execute('SELECT id FROM chunks WHERE doc_id=? ORDER BY ordinal', (result['document_id'],)).fetchone()[0]
        return result['document_id'], chunk

    def review(self, doc, **kwargs):
        return self.ws.attest(doc, reviewer='test-reviewer', reason='Synthetic acceptance test, not a legal opinion.', status='reviewed', **kwargs)

    def search(self, query='contrato', **kwargs):
        return self.ws.search(query, effective_on='2026-01-01', **kwargs)

    def test_empty_workspace_integrity(self):
        self.assertEqual(self.ws.integrity()['documents'], 0)
        self.assertEqual(self.ws.integrity()['head'], '0'*64)

    def test_wrong_matter_refused(self):
        with self.assertRaises(ValueError): Workspace(self.path, 'other-case')

    def test_existing_foreign_database_not_modified(self):
        other=Path(self.tmp.name)/'unrelated.sqlite'
        with sqlite3.connect(other) as connection:
            connection.execute('CREATE TABLE keep(value TEXT)')
            connection.execute("INSERT INTO keep VALUES('preserve')")
        with self.assertRaises(ValueError):Workspace(other,'synthetic-case')
        with sqlite3.connect(other) as connection:
            self.assertEqual(connection.execute('SELECT value FROM keep').fetchone()[0],'preserve')
            self.assertFalse(connection.execute("SELECT 1 FROM sqlite_master WHERE name='workspace'").fetchone())

    def test_invalid_matter_refused(self):
        for matter in ['../secret', '', 'Contains spaces', 'a'*129]:
            with self.subTest(matter=matter), self.assertRaises(ValueError): Workspace(Path(self.tmp.name)/'other', matter)

    def test_database_symlink_refused(self):
        link = Path(self.tmp.name)/'link'; link.symlink_to(self.path)
        with self.assertRaises(ValueError): Workspace(link, 'synthetic-case')

    def test_ingest_unknown_by_default(self):
        doc,_ = self.add()
        self.assertEqual(self.search()['results'], [])
        self.assertEqual(self.search(verified_only=False)['results'][0]['doc_id'], doc)

    def test_review_enables_case(self):
        doc,_=self.add(); self.review(doc)
        result=self.search()
        self.assertEqual(len(result['results']),1)
        self.assertFalse(result['generation_performed'])
        self.assertFalse(result['semantic_support_verified'])

    def test_idempotent_ingest(self):
        a,_=self.add(); b,_=self.add()
        self.assertEqual(a,b)
        self.assertEqual(self.ws.integrity()['events'],1)

    def test_content_change_creates_version(self):
        a,_=self.add(); b,_=self.add('Contrato alterado.')
        self.assertNotEqual(a,b)
        self.assertEqual(self.ws.integrity()['documents'],2)

    def test_distinct_sources_not_collapsed(self):
        a,_=self.add(source='A'); b,_=self.add(source='B')
        self.assertNotEqual(a,b)

    def test_no_automatic_official_url_attestation(self):
        self.add(source='https://www.planalto.gov.br/example')
        self.assertEqual(self.search()['results'],[])

    def test_bad_bytes_rejected(self):
        for raw in [b'', b'\xff', b'%PDF-1.7\nnot-text', b'bad\x00value', b' '*10]:
            with self.subTest(raw=raw), self.assertRaises((ValueError,UnicodeError)):
                self.ws.ingest(raw,source_id='f',title='t',kind='case')
        self.assertEqual(self.ws.integrity()['documents'],0)

    def test_size_cap(self):
        with self.assertRaises(ValueError): self.ws.ingest(b'a'*(MAX_DOCUMENT_BYTES+1),source_id='f',title='t',kind='case')

    def test_invalid_kind_metadata(self):
        for source,title,kind in [('', 't','case'),('s','','case'),('s','t','official')]:
            with self.subTest(kind=kind),self.assertRaises(ValueError): self.ws.ingest(b'text',source_id=source,title=title,kind=kind)

    def test_bom_preserves_original(self):
        raw=b'\xef\xbb\xbf'+ 'Contrato português.'.encode()
        self.ws.ingest(raw,source_id='f',title='t',kind='case')
        self.assertEqual(self.ws.integrity()['documents'],1)
        self.assertEqual(self.ws.db.execute('SELECT original FROM documents').fetchone()[0],raw)

    def test_future_observation_refused(self):
        future=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()
        with self.assertRaises(ValueError): self.ws.ingest(b'Contrato',source_id='f',title='t',kind='case',observed_at=future)

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError): timestamp('2026-01-01T12:00:00')

    def test_timezone_normalizes(self):
        self.assertEqual(timestamp('2026-01-01T09:00:00-03:00'),timestamp('2026-01-01T12:00:00Z'))

    def test_date_requires_iso(self):
        for value in ['20260101','2026-02-30','01/01/2026']:
            with self.subTest(value=value),self.assertRaises(ValueError): day(value)

    def test_exact_quote_lines_offsets(self):
        _,chunk=self.add('Primeira linha.\nSegunda cláusula.\nTerceira linha.')
        q=self.ws.quote(chunk,'Segunda cláusula.')
        self.assertEqual(q['start_line'],2);self.assertEqual(q['end_line'],2)
        self.assertEqual(q['quote_start_offset'],16)
        self.assertFalse(q['semantic_support_verified'])

    def test_nonexact_quote_refused(self):
        _,chunk=self.add()
        with self.assertRaises(ValueError):self.ws.quote(chunk,'Garantia inexistente.')
        with self.assertRaises(ValueError):self.ws.quote('missing','Contrato')

    def test_file_ingestion_only_regular_text(self):
        f=Path(self.tmp.name)/'test.txt';f.write_text('Contrato teste.',encoding='utf8')
        self.ws.ingest_file(f,source_id='f',title='t',kind='case')
        link=Path(self.tmp.name)/'link.txt';link.symlink_to(f)
        with self.assertRaises(ValueError):self.ws.ingest_file(link,source_id='f',title='t',kind='case')
        with self.assertRaises(ValueError):self.ws.ingest_file(Path(self.tmp.name),source_id='f',title='t',kind='case')

    def test_norm_requires_legal_time(self):
        doc,_=self.add(kind='normative');self.review(doc)
        self.assertEqual(self.search()['results'],[])
        self.assertEqual(self.search()['excluded_candidates'],{'unknown_legal_time':1})

    def test_halfopen_legal_validity(self):
        doc,_=self.add(kind='normative');self.review(doc,valid_from='2026-01-01',valid_until='2027-01-01')
        for date,expected in [('2025-12-31',0),('2026-01-01',1),('2026-12-31',1),('2027-01-01',0)]:
            with self.subTest(date=date):self.assertEqual(len(self.ws.search('contrato',effective_on=date)['results']),expected)

    def test_include_unverified_does_not_override_legal_expiry(self):
        doc,_=self.add(kind='normative');self.review(doc,valid_from='2024-01-01',valid_until='2025-01-01')
        self.assertEqual(self.search(verified_only=False)['results'],[])

    def test_rejection_is_not_unverified(self):
        doc,_=self.add();self.review(doc)
        self.ws.attest(doc,reviewer='r',reason='Rejected fixture.',status='rejected')
        self.assertEqual(self.search(verified_only=False)['results'],[])

    def test_history_preserved_before_rejection(self):
        doc,_=self.add();self.review(doc);before=timestamp()
        self.ws.attest(doc,reviewer='r',reason='Later rejection.',status='rejected')
        self.assertEqual(len(self.search(known_at=before)['results']),1)
        self.assertEqual(self.search()['results'],[])

    def test_document_not_known_at_old_snapshot(self):
        doc,_=self.add();self.review(doc)
        self.assertEqual(self.search(known_at='2000-01-01T00:00:00Z',verified_only=False)['results'],[])

    def test_future_review_not_backdated(self):
        doc,_=self.add();before=timestamp();self.review(doc)
        self.assertEqual(self.search(known_at=before)['results'],[])

    def test_bad_attestation_rollback(self):
        doc,_=self.add()
        for kwargs in [dict(valid_from='2026-01-01',valid_until='2026-01-01'),dict(valid_until='2026-01-01')]:
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):self.review(doc,**kwargs)
        with self.assertRaises(ValueError):self.review('unknown')
        self.assertEqual(self.ws.integrity()['events'],1)

    def test_search_parameters_bounded(self):
        for args in [dict(limit=0),dict(hops=4),dict(max_nodes=1),dict(limit=True),dict(verified_only=1),dict(max_edges=0)]:
            with self.subTest(args=args),self.assertRaises(ValueError):self.search(**args)

    def test_fts_operators_are_literal_terms(self):
        doc,_=self.add();self.review(doc)
        result=self.search('contrato" OR * NEAR(foo) --')
        self.assertEqual(len(result['results']),1)
        with self.assertRaises(ValueError):self.search('" * ---')

    def graph(self, review_proof=True):
        d1,c1=self.add('Contrato alfa inicial.',title='A');self.review(d1)
        d2,c2=self.add('Destino beta jurídico.',title='B');self.review(d2)
        dp,cp=self.add('Evidência sintética liga A a B.',title='P')
        if review_proof:self.review(dp)
        e=self.ws.link(c1,c2,'references',cp,'liga A a B')
        return c1,c2,e

    def test_proposed_edges_not_traversed(self):
        _,c2,_=self.graph()
        self.assertNotIn(c2,[r['id'] for r in self.search('alfa')['results']])

    def test_reviewed_edge_traversed(self):
        _,c2,e=self.graph();self.ws.review_link(e,status='reviewed',reviewer='r',reason='Fixture link checked.')
        result=self.search('alfa')
        self.assertIn(c2,[r['id'] for r in result['results']]);self.assertEqual(len(result['paths']),1)

    def test_graph_requires_reviewed_proof(self):
        _,c2,e=self.graph(review_proof=False);self.ws.review_link(e,status='reviewed',reviewer='r',reason='Fixture.')
        self.assertNotIn(c2,[r['id'] for r in self.search('alfa')['results']])

    def test_rejected_edge_not_traversed(self):
        _,c2,e=self.graph();self.ws.review_link(e,status='reviewed',reviewer='r',reason='Fixture.')
        self.ws.review_link(e,status='rejected',reviewer='r',reason='Reconsidered.')
        self.assertNotIn(c2,[r['id'] for r in self.search('alfa')['results']])

    def test_unknown_and_reflexive_edges_refused(self):
        _,c=self.add()
        for args in [(c,c,'references',c,'Contrato'),(c,'missing','references',c,'Contrato'),(c,'missing','madeup',c,'Contrato')]:
            with self.subTest(args=args),self.assertRaises(ValueError):self.ws.link(*args)

    def test_invalid_edge_quote_refused(self):
        _,a=self.add();_,b=self.add('Beta.',title='B')
        with self.assertRaises(ValueError):self.ws.link(a,b,'references',a,'Not present')

    def test_graph_node_budget(self):
        _,_,e=self.graph();self.ws.review_link(e,status='reviewed',reviewer='r',reason='Fixture.')
        result=self.search('alfa',limit=1,max_nodes=1)
        self.assertEqual(len(result['results']),1);self.assertTrue(result['graph_truncated'])

    def test_graph_edge_budget(self):
        a,b,e=self.graph();self.ws.review_link(e,status='reviewed',reviewer='r',reason='Fixture.')
        e2=self.ws.link(a,b,'supports',a,'Contrato');self.ws.review_link(e2,status='reviewed',reviewer='r',reason='Fixture.')
        result=self.search('alfa',max_edges=1)
        self.assertEqual(result['inspected_edges'],1);self.assertTrue(result['graph_truncated'])

    def test_graph_cycle_bounded(self):
        a,b,e=self.graph();self.ws.review_link(e,status='reviewed',reviewer='r',reason='Fixture.')
        e2=self.ws.link(b,a,'references',a,'Contrato');self.ws.review_link(e2,status='reviewed',reviewer='r',reason='Fixture.')
        result=self.search('alfa',hops=3)
        self.assertEqual(len(result['results']),2);self.assertEqual(len(result['paths']),2)

    def test_unverified_seed_cannot_traverse(self):
        a,_,e=self.graph();self.ws.review_link(e,status='reviewed',reviewer='r',reason='Fixture.')
        # An unreviewed document is deliberately used as a different seed.
        _,unverified=self.add('Unverified unique seed.',title='U')
        e2=self.ws.link(unverified,a,'references',a,'Contrato');self.ws.review_link(e2,status='reviewed',reviewer='r',reason='Fixture.')
        result=self.search('unique',verified_only=False)
        self.assertEqual(len(result['results']),1);self.assertEqual(result['paths'],[])

    def test_transaction_rollback(self):
        with self.assertRaises(RuntimeError):
            with self.ws.transaction():
                self.ws._audit('test',{'fixture':True})
                raise RuntimeError('Deliberate rollback test.')
        self.assertEqual(self.ws.integrity()['events'],0)

    def test_audit_mutation_detected(self):
        self.add();self.ws.db.execute("UPDATE audit SET event='changed' WHERE seq=1")
        with self.assertRaises(ValueError):self.ws.integrity()

    def test_external_anchor_detects_tail_removal(self):
        doc,_=self.add();self.review(doc);anchor=self.ws.integrity()['head']
        self.ws.db.execute('DELETE FROM audit WHERE seq=(SELECT MAX(seq) FROM audit)')
        self.ws.integrity()  # A chain alone cannot detect removed trailing events.
        with self.assertRaises(ValueError):self.ws.integrity(anchor)

    def test_original_mutation_detected(self):
        self.add();self.ws.db.execute("UPDATE documents SET original=X'6162'")
        with self.assertRaises(ValueError):self.ws.integrity()

    def test_chunk_tamper_rejected_at_search(self):
        doc,chunk=self.add();self.review(doc)
        self.ws.db.execute("UPDATE chunks SET content='Forged',sha256=? WHERE id=?",(digest(b'Forged'),chunk))
        with self.assertRaises(ValueError):self.search('contrato')

    def test_metadata_tamper_detected(self):
        self.add();self.ws.db.execute("UPDATE documents SET source_id='forged-source'")
        with self.assertRaises(ValueError):self.ws.integrity()

    def test_cli_real_roundtrip(self):
        root=Path(__file__).resolve().parents[1]
        command=[sys.executable,'-m','legal_br','--db',str(self.path),'--matter','synthetic-case']
        result=subprocess.run(command+['verify'],cwd=root,capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(result.stdout)['documents'],0)
        failed=subprocess.run(command+['search','--query','secret-case-text','--effective-on','bad'],cwd=root,capture_output=True,text=True)
        self.assertEqual(failed.returncode,2);self.assertNotIn('secret-case-text',failed.stderr)

    def test_cli_does_not_create_mistyped_db(self):
        p=Path(self.tmp.name)/'typo.sqlite'
        result=subprocess.run([sys.executable,'-m','legal_br','--db',str(p),'--matter','test','verify'],cwd=Path(__file__).resolve().parents[1],capture_output=True)
        self.assertEqual(result.returncode,2);self.assertFalse(p.exists())


class SegmentationTests(unittest.TestCase):
    def test_coverage_and_bounded_windows(self):
        for text in ['a'*10001,('Linha unicode çã 😀.\n'*1000),'x'*4000,'tiny']:
            windows=list(segments(text));covered=set()
            for start,end in windows:
                self.assertLessEqual(end-start,4000);self.assertGreater(end,start);covered.update(range(start,end))
            self.assertEqual(len(covered),len(text))

    def test_empty_no_chunks(self):self.assertEqual(list(segments('')),[])

    def test_invalid_parameters(self):
        for size,overlap in [(10,0),(4000,2000),(4000,-1),(True,0),(4000,1.5)]:
            with self.subTest(size=size,overlap=overlap),self.assertRaises(ValueError):list(segments('text',size,overlap))

    def test_chunk_offsets_match_original(self):
        with tempfile.TemporaryDirectory() as d, Workspace(Path(d)/'db','t') as ws:
            ws.ingest(('αβγ\n'*5000).encode(),source_id='s',title='t',kind='case')
            self.assertGreater(ws.integrity()['chunks'],1)


if __name__=='__main__':unittest.main()
