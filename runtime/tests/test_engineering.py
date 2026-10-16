"""Synthetic contract/regression tests; not measured NER or legal accuracy."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from legal_br.citations import extract_citations, validate_cnj, parse_ecli, checked_text
from legal_br.lexml import read_lexml, article_chunks, NS
from legal_br.privacy import EntitySpan,bio_spans,pseudonymize,cpf_checksum_valid
from legal_br.evaluation import validate_split,selective_triage,evaluate_multilabel

XML=f'''<LexML xmlns="{NS}"><ProjetoNorma><Norma><Articulacao id="articulacao">
<Artigo id="art1"><Rotulo>Art. 1º</Rotulo><Caput id="art1_cpt"><p>Regra sintética, não normativa.</p></Caput>
<Paragrafo id="art1_par1"><Rotulo>§ 1º</Rotulo><p>Exceto na hipótese expressa.</p><Inciso id="art1_par1_inc1"><Rotulo>I –</Rotulo><p>Condição adicional.</p></Inciso></Paragrafo></Artigo>
<Artigo id="art2"><Rotulo>Art. 2º</Rotulo><Caput id="art2_cpt"><p>Segunda regra sintética.</p></Caput></Artigo>
</Articulacao></Norma></ProjetoNorma></LexML>'''.encode()

class CitationTests(unittest.TestCase):
    def test_law_number_not_federal_inference(self):
        c=extract_citations('Lei 14.133/2021')['citations'][0]
        self.assertIsNone(c['parts']['authority']);self.assertIsNone(c['canonical_identifier'])
        self.assertEqual(c['parts']['number'],'14133');self.assertFalse(c['existence_verified'])
    def test_two_digit_year_is_ambiguous(self):
        self.assertEqual(extract_citations('Lei 14.133/21')['citations'][0]['syntax_status'],'ambiguous_year')
    def test_article_keeps_paragraph(self):
        c=extract_citations('art. 489, § 1º')['citations'][0]
        self.assertEqual(c['parts']['paragraph'],'1');self.assertEqual(c['syntax_status'],'parent_instrument_unresolved')
    def test_court_cases_are_not_decisions(self):
        c=extract_citations('STJ – REsp 1.234.567/SP')['citations'][0]
        self.assertEqual(c['parts']['court'],'STJ');self.assertFalse(c['semantic_support_verified'])
    def test_exact_unicode_offsets(self):
        text='😀 Órgão: STF RE 1.234.567. art. 5º'
        for c in extract_citations(text)['citations']:self.assertEqual(text[c['start']:c['end']],c['surface'])
    def test_negated_reference_does_not_become_violation(self):
        r=extract_citations('Não se aplica a Lei 14.133/2021.')
        self.assertIsNone(r['legal_conclusion'])
    def test_binding_sumula_inconsistent_authority(self):
        self.assertEqual(extract_citations('Súmula Vinculante 56 do STJ')['citations'][0]['syntax_status'],'inconsistent_authority')
    def test_sumula_unidentified_court(self):
        self.assertEqual(extract_citations('Súmula 100')['citations'][0]['syntax_status'],'authority_unresolved')
    def test_cnj_modulo97(self):
        base='900000020268090001';dd=98-int(base+'00')%97
        candidate=f'9000000-{dd:02d}.2026.8.09.0001'
        self.assertTrue(validate_cnj(candidate));self.assertFalse(validate_cnj(candidate.replace(f'-{dd:02d}.','-00.')))
    def test_invalid_checksum_not_ignored(self):
        c=extract_citations('9000000-00.2026.8.09.0001')['citations'][0]
        self.assertEqual(c['syntax_status'],'invalid_checksum');self.assertIsNone(c['canonical_identifier'])
    def test_valid_cnj_not_existence_claim(self):
        self.assertFalse(extract_citations('9000000-00.2026.8.09.0001')['external_lookup_performed'])
    def test_short_reference_ambiguous(self):
        r=extract_citations('STF RE 123456 e STJ REsp 654321. Id.')['citations'][-1]
        self.assertEqual(len(r['parts']['candidate_antecedents']),2);self.assertEqual(r['syntax_status'],'requires_resolution')
    def test_short_reference_does_not_cross_paragraph(self):
        r=extract_citations('STF RE 123456\n\nId.')['citations'][-1]
        self.assertEqual(r['parts']['candidate_antecedents'],[])
    def test_deterministic_ids(self):
        self.assertEqual(extract_citations('Lei 1/2000'),extract_citations('Lei 1/2000'))
    def test_ids_bound_to_document(self):
        a=extract_citations('Lei 1/2000')['citations'][0]['citation_id']
        b=extract_citations('Lei 1/2000 contexto')['citations'][0]['citation_id'];self.assertNotEqual(a,b)
    def test_bidi_warning_not_silently_cleaned(self):
        self.assertTrue(extract_citations('Lei 1/2000\u202e')['warnings'])
    def test_empty_and_nul_rejected(self):
        for text in ['','  ','a\0b',42]:
            with self.subTest(text=text), self.assertRaises(ValueError):checked_text(text)
    def test_ecli_components(self):
        r=parse_ecli('ECLI:EU:C:2020:559');self.assertEqual(r['court'],'C');self.assertFalse(r['existence_verified'])
    def test_invalid_ecli(self):
        for value in ['ECLI:EU:1C:2020:abc','ECLI:BR:123:2026:x','ECLI:EU:C:2020:...', 'ECLI:EU:C:2020:'+'A'*26, 'ECLI:EU:C:2020:A-B']:
            with self.subTest(value=value),self.assertRaises(ValueError):parse_ecli(value)
    def test_ecli_case_insensitive_canonicalization(self):
        r=parse_ecli('ecli:eu:c:2020:abc');self.assertEqual(r['identifier'],'ECLI:EU:C:2020:ABC')
        self.assertFalse(r['registry_verified'])
    def test_br_ecli_syntax_is_not_national_registration(self):
        r=parse_ecli('ECLI:BR:FAKE:2026:X');self.assertFalse(r['registry_verified'])
        self.assertFalse(r['existence_verified'])
    def test_short_candidate_budget_is_explicit(self):
        text=' '.join('Lei '+str(i)+'/2021' for i in range(1,151))+' Id.'
        r=next(c for c in extract_citations(text)['citations'] if c['kind']=='short_reference')
        self.assertTrue(r['parts']['candidate_set_truncated']);self.assertEqual(len(r['parts']['candidate_antecedents']),128)
    def test_ecli_terminal_dot_is_ambiguous(self):
        r=extract_citations('ECLI:EU:C:2020:559.')['citations'][0]
        self.assertEqual(r['syntax_status'],'ambiguous_terminal_dot');self.assertIsNone(r['canonical_identifier'])

class LexmlTests(unittest.TestCase):
    def test_hierarchy(self):
        d=read_lexml(XML);index={n['id']:n for n in d['nodes']}
        self.assertEqual(index['art1_par1_inc1']['parent_id'],'art1_par1')
        self.assertEqual(index['art1_par1_inc1']['ancestor_ids'],['articulacao','art1','art1_par1'])
    def test_content_not_duplicated_at_parent(self):
        index={n['id']:n for n in read_lexml(XML)['nodes']}
        self.assertNotIn('Exceto',index['art1']['own_text']);self.assertIn('Exceto',index['art1_par1']['own_text'])
    def test_hash_and_schema_claim(self):
        d=read_lexml(XML);self.assertEqual(d['source_sha256'],hashlib.sha256(XML).hexdigest());self.assertFalse(d['xsd_validated'])
    def test_default_groups_article_family(self):
        chunks=article_chunks(read_lexml(XML));self.assertEqual(len(chunks),2)
        self.assertIn('Exceto',chunks[0]['text']);self.assertIn('art1_par1_inc1',chunks[0]['unit_ids'])
    def test_split_requires_siblings(self):
        chunks=article_chunks(read_lexml(XML),max_chars=64)
        first=[c for c in chunks if c['article_id']=='art1'];self.assertGreater(len(first),1)
        for c in first:self.assertTrue(c['required_context_ids'])
    def test_long_provision_retained_flagged(self):
        xml=XML.replace(b'Segunda regra sint\xc3\xa9tica.',b'Z'*200)
        chunks=article_chunks(read_lexml(xml),max_chars=64)
        self.assertTrue(any(c['oversized'] for c in chunks));self.assertIn('Z'*200,' '.join(c['text'] for c in chunks))
    def test_duplicate_id(self):
        with self.assertRaises(ValueError):read_lexml(XML.replace(b'id="art2"',b'id="art1"'))
    def test_dtd_xxe_rejected(self):
        for prefix in [b'<!DOCTYPE LexML [<!ENTITY x SYSTEM "file:///etc/passwd">]>',b'<!DOCTYPE LexML SYSTEM "https://example.invalid/a">']:
            with self.subTest(prefix=prefix),self.assertRaises(ValueError):read_lexml(prefix+XML)
    def test_foreign_namespace(self):
        with self.assertRaises(ValueError):read_lexml(XML.replace(NS.encode(),b'https://evil.invalid'))
    def test_namespace_required(self):
        with self.assertRaises(ValueError):read_lexml(XML.replace(f' xmlns="{NS}"'.encode(),b''))
    def test_xinclude_rejected(self):
        xml=XML.replace(b'</Articulacao>',b'<include xmlns="http://www.w3.org/2001/XInclude" href="file:///etc/passwd"/></Articulacao>')
        with self.assertRaises(ValueError):read_lexml(xml)
    def test_depth_and_node_budget(self):
        with self.assertRaises(ValueError):read_lexml(XML,max_depth=2)
        with self.assertRaises(ValueError):read_lexml(XML,max_nodes=2)
    def test_bad_xml(self):
        with self.assertRaises(ET.ParseError):read_lexml(XML[:-5])
    def test_missing_article(self):
        with self.assertRaises(ValueError):read_lexml(f'<LexML xmlns="{NS}"/>'.encode())
    def test_utf16_and_nonutf8_decl_rejected(self):
        with self.assertRaises((ValueError,UnicodeError)):read_lexml(XML.decode().encode('utf16'))
        with self.assertRaises(ValueError):read_lexml(b'<?xml version="1.0" encoding="ISO-8859-1"?>'+XML)
    def test_quote_amendment_context(self):
        xml=XML.replace(b'<Artigo id="art2">',b'<Alteracao id="alt1"><Artigo id="art2">').replace(b'</Articulacao>',b'</Alteracao></Articulacao>')
        d=read_lexml(xml);self.assertTrue(next(n for n in d['nodes'] if n['id']=='art2')['quoted_amendment'])
    def test_generated_locator_declared(self):
        self.assertTrue(read_lexml(XML.replace(b' id="art2"',b''))['warnings'])
    def test_chunk_budget_and_duplicate_rejected(self):
        with self.assertRaises(ValueError):article_chunks(read_lexml(XML),max_chars=True)
        d=read_lexml(XML);d['nodes'].append(d['nodes'][0])
        with self.assertRaises(ValueError):article_chunks(d)

class PrivacyTests(unittest.TestCase):
    def mask(self,text,**kwargs):return pseudonymize(text,key=b'k'*32,tenant='synthetic',matter='case-A',**kwargs)
    def test_direct_identifiers(self):
        r=self.mask('Contato teste@example.invalid, CPF 000.000.000-00, telefone (11) 90000-0000.')
        self.assertEqual(len(r['redactions']),3);self.assertNotIn('teste@',r['text']);self.assertNotIn('000.000.000-00',r['text'])
    def test_invalid_cpf_still_masked(self):
        r=self.mask('CPF 00000000000');self.assertEqual(r['redactions'][0]['checksum_valid'],False)
    def test_scope_separation(self):
        a=self.mask('Pessoa Alfa',entities=[EntitySpan(0,11,'PERSON')])
        b=pseudonymize('Pessoa Alfa',key=b'k'*32,tenant='synthetic',matter='case-B',entities=[EntitySpan(0,11,'PERSON')])
        self.assertNotEqual(a['text'],b['text'])
    def test_key_separation(self):
        a=self.mask('a@example.invalid')
        b=pseudonymize('a@example.invalid',key=b'j'*32,tenant='synthetic',matter='case-A')
        self.assertNotEqual(a['text'],b['text'])
    def test_repeat_consistency(self):
        r=self.mask('a@example.invalid e a@example.invalid')
        self.assertEqual(r['redactions'][0]['pseudonym'],r['redactions'][1]['pseudonym'])
    def test_overlap_union_no_suffix_leak(self):
        r=self.mask('Alfa teste@example.invalid fim',entities=[EntitySpan(0,15,'PERSON')])
        self.assertEqual(len(r['redactions']),1);self.assertNotIn('example',r['text']);self.assertEqual(r['redactions'][0]['labels'],['EMAIL','PERSON'])
    def test_adjacent_entities_not_merged(self):
        r=self.mask('AB',entities=[EntitySpan(0,1,'PERSON'),EntitySpan(1,2,'PERSON')]);self.assertEqual(len(r['redactions']),2)
    def test_output_offsets(self):
        r=self.mask('😀 a@example.invalid e b@example.invalid')
        for s in r['redactions']:self.assertEqual(r['text'][s['output_start']:s['output_end']],s['pseudonym'])
    def test_no_egress_guarantee(self):
        r=self.mask('Nome não reconhecido.');self.assertFalse(r['egress_authorized']);self.assertFalse(r['anonymity_guaranteed']);self.assertFalse(r['ner_model_executed'])
    def test_citations_preserved(self):
        text='Lei 14.133/2021';r=self.mask(text,entities=[EntitySpan(0,len(text),'LEGISLATION')]);self.assertEqual(r['text'],text)
    def test_no_raw_mapping(self):
        r=self.mask('a@example.invalid');self.assertNotIn('a@example.invalid',json.dumps(r['redactions']));self.assertFalse(r['mapping_persisted'])
    def test_small_key_and_bad_scope(self):
        with self.assertRaises(ValueError):pseudonymize('test',key=b'x',tenant='t',matter='m')
        with self.assertRaises(ValueError):pseudonymize('test',key=b'x'*32,tenant='',matter='m')
    def test_bad_spans(self):
        for span in [EntitySpan(-1,2,'PERSON'),EntitySpan(0,99,'PERSON'),EntitySpan(True,2,'PERSON'),EntitySpan(0,1,'UNKNOWN')]:
            with self.subTest(span=span),self.assertRaises(ValueError):self.mask('abc',entities=[span])
    def test_cannot_disable_direct_identifiers(self):
        with self.assertRaises(ValueError):self.mask('test',labels=frozenset({'PERSON'}))
    def test_strict_bio_alignment(self):
        text='Pessoa Alfa chegou.'
        spans=bio_spans(text,['Pessoa','Alfa','chegou','.'],['B-PESSOA','I-PESSOA','O','O'])
        self.assertEqual(spans[0],EntitySpan(0,11,'PERSON','conll_bio_adapter'))
    def test_bio_invalid_continuation(self):
        with self.assertRaises(ValueError):bio_spans('Pessoa',['Pessoa'],['I-PESSOA'])
    def test_bio_dropped_text(self):
        with self.assertRaises(ValueError):bio_spans('Pessoa Alfa',['Alfa'],['B-PESSOA'])
        with self.assertRaises(ValueError):bio_spans('Pessoa Alfa',['Pessoa'],['B-PESSOA'])
    def test_bio_unknown_label(self):
        with self.assertRaises(ValueError):bio_spans('A',['A'],['B-UNKNOWN'])
    def test_bio_different_repeated_entities(self):
        spans=bio_spans('A A',['A','A'],['B-PESSOA','B-PESSOA']);self.assertEqual([s.start for s in spans],[0,2])

class EvaluationTests(unittest.TestCase):
    def rows(self):
        return [dict(id=str(i),matter_id='m'+str(i),content_sha256=hashlib.sha256(str(i).encode()).hexdigest(),split=s,available_on=d,labels=['consumer']) for i,(s,d) in enumerate([('train','2025-01-01'),('dev','2026-01-01'),('test','2026-02-01')])]
    def test_split_accepts_separated(self):self.assertTrue(validate_split(self.rows(),cutoff='2025-12-31')['split_valid'])
    def test_matter_leakage(self):
        rows=self.rows();rows[1]['matter_id']=rows[0]['matter_id']
        with self.assertRaises(ValueError):validate_split(rows,cutoff='2025-12-31')
    def test_content_leakage(self):
        rows=self.rows();rows[1]['content_sha256']=rows[0]['content_sha256']
        with self.assertRaises(ValueError):validate_split(rows,cutoff='2025-12-31')
    def test_temporal_leakage(self):
        rows=self.rows();rows[0]['available_on']='2026-02-01'
        with self.assertRaises(ValueError):validate_split(rows,cutoff='2025-12-31')
    def test_unseen_labels_reported(self):
        rows=self.rows();rows[-1]['labels']=['its'];self.assertEqual(validate_split(rows,cutoff='2025-12-31')['unseen_holdout_labels'],['its'])
    def test_absent_partition_rejected(self):
        with self.assertRaises(ValueError):validate_split(self.rows()[:2],cutoff='2025-12-31')
    def test_triage_abstains_ood(self):
        r=selective_triage({'a':.99,'b':.01},threshold=.8,minimum_margin=.1,in_distribution=False);self.assertTrue(r['abstained'])
    def test_triage_tie_abstains_even_zero_margin(self):
        r=selective_triage({'a':.9,'b':.9},threshold=.8,minimum_margin=0,in_distribution=True);self.assertTrue(r['abstained'])
    def test_triage_route_proposal_not_certainty(self):
        r=selective_triage({'a':.99,'b':.01},threshold=.8,minimum_margin=.1,in_distribution=True);self.assertEqual(r['proposed_route'],'a');self.assertFalse(r['calibration_verified'])
    def test_non_finite_scores(self):
        for bad in [float('nan'),float('inf'),True]:
            with self.subTest(bad=bad),self.assertRaises(ValueError):selective_triage({'a':bad,'b':.1},threshold=.8,minimum_margin=.1,in_distribution=True)
    def test_threshold_abstains(self):
        self.assertTrue(selective_triage({'a':.4,'b':.2},threshold=.8,minimum_margin=.1,in_distribution=True)['abstained'])
    def test_metrics_abstention_fn(self):
        r=evaluate_multilabel([{'id':'a','gold':['a'],'predicted':['a'],'abstained':False},{'id':'b','gold':['b'],'predicted':[],'abstained':True}],labels=['a','b'])
        self.assertAlmostEqual(r['micro_f1'],2/3);self.assertEqual(r['coverage'],.5);self.assertEqual(r['per_label']['b']['fn'],1)
    def test_all_abstain_selective_is_null(self):
        r=evaluate_multilabel([{'id':'a','gold':['a'],'predicted':[],'abstained':True}],labels=['a']);self.assertIsNone(r['selective_exact_match'])
    def test_prediction_unknown_or_duplicate(self):
        for pred in [['z'],['a','a']]:
            with self.subTest(pred=pred),self.assertRaises(ValueError):evaluate_multilabel([{'id':'a','gold':['a'],'predicted':pred,'abstained':False}],labels=['a'])
    def test_abstain_cannot_hide_pred(self):
        with self.assertRaises(ValueError):evaluate_multilabel([{'id':'a','gold':['a'],'predicted':['a'],'abstained':True}],labels=['a'])

class CLITests(unittest.TestCase):
    def runcli(self,*args):return subprocess.run([sys.executable,'-m','legal_br.engine',*args],capture_output=True,text=True)
    def test_real_citation_cli(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'a.txt';p.write_text('Lei 14.133/2021')
            r=self.runcli('citations','--file',str(p));self.assertEqual(r.returncode,0);self.assertEqual(len(json.loads(r.stdout)['citations']),1)
    def test_real_xml_cli(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'a.xml';p.write_bytes(XML)
            r=self.runcli('lexml','--file',str(p));self.assertEqual(r.returncode,0);self.assertEqual(len(json.loads(r.stdout)['chunks']),2)
    def test_output_never_overwritten(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'out';p.write_text('keep')
            r=self.runcli('--output',str(p),'ecli','ECLI:EU:C:2020:559');self.assertEqual(r.returncode,2);self.assertEqual(p.read_text(),'keep')
    def test_secret_not_echoed_on_error(self):
        r=self.runcli('ecli','secret-invalid-value');self.assertEqual(r.returncode,2);self.assertNotIn('secret-invalid-value',r.stderr)
    def test_key_permissions(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'a.txt';p.write_text('a@example.invalid');k=Path(t)/'key';k.write_bytes(b'k'*32);k.chmod(0o644)
            r=self.runcli('privacy','--file',str(p),'--key-file',str(k),'--tenant','t','--matter','m');self.assertEqual(r.returncode,2)
            k.chmod(0o600);r=self.runcli('privacy','--file',str(p),'--key-file',str(k),'--tenant','t','--matter','m');self.assertEqual(r.returncode,0);self.assertFalse(json.loads(r.stdout)['egress_authorized'])
    def test_json_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json';p.write_text('{"scores":{"a":NaN,"b":0.1},"threshold":0.8,"minimum_margin":0.1,"in_distribution":true}')
            self.assertEqual(self.runcli('triage','--file',str(p)).returncode,2)

if __name__=='__main__':unittest.main()
