"""Structural and real local-Git integration tests; no remote services or mocks."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py')
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj

validator=module('validate_br');assembler=module('assemble_fork')

class RepositoryTests(unittest.TestCase):
    def test_marketplace_and_all_contracts(self):
        report=validator.validate(ROOT)
        self.assertEqual(report['plugins'],40)
        self.assertEqual(report['skills'],182)

    def test_sources_provenance_not_fabricated_connectors(self):
        for item in json.loads((ROOT/'catalog/sources.json').read_text()):
            self.assertFalse(item['connector_implemented'])
            if item['discovery']=='catalog_seed_requires_verification':self.assertIsNone(item['observed_on'])

    def test_shell_script_syntax(self):
        for script in ('publish_github.sh','publish_independent.sh'):
            subprocess.run(['bash','-n',str(ROOT/'scripts'/script)],check=True)

    def test_read_only_tool_scope(self):
        catalog=json.loads((ROOT/'catalog/skills.json').read_text())
        for skill in catalog['skills']:
            text=(ROOT/skill['path']).read_text().split('\n---\n',1)[0]
            self.assertNotIn('Bash',text);self.assertNotIn('Write',text)

    def test_no_remote_runtime_dependency(self):
        runtime=(ROOT/'runtime/legal_br/store.py').read_text()
        for statement in ['import requests','import httpx','import openai','import anthropic']:
            self.assertNotIn(statement,runtime)


class AssemblyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)
        self.up=self.base/'upstream';self.up.mkdir()
        self.overlay=self.base/'overlay';self.overlay.mkdir()
        (self.up/'.github/workflows').mkdir(parents=True)
        (self.up/'.github/workflows/old.yml').write_text('name: archived fixture\n')
        (self.up/'.claude-plugin').mkdir()
        (self.up/'.claude-plugin/marketplace.json').write_text('{"name":"fixture-upstream"}')
        (self.up/'README.md').write_text('Original upstream test fixture.\n')
        (self.up/'CLA.md').write_text('Original test CLA.\n')
        (self.up/'vendor').mkdir();(self.up/'vendor/unchanged.txt').write_text('Retained vendor test content.\n')
        assembler.git(None,'init',str(self.up))
        assembler.git(self.up,'config','user.name','Local integration test')
        assembler.git(self.up,'config','user.email','test@example.invalid')
        assembler.git(self.up,'add','.')
        assembler.git(self.up,'commit','-m','Synthetic upstream fixture')
        self.sha=assembler.git(self.up,'rev-parse','HEAD')
        (self.overlay/'upstream.lock.json').write_text(json.dumps({'commit':self.sha,'url':str(self.up)}))
        (self.overlay/'README.md').write_text('BR overlay fixture.\n')
        (self.overlay/'.claude-plugin').mkdir();(self.overlay/'.claude-plugin/marketplace.json').write_text('{"name":"fixture-br"}')
        (self.overlay/'.github/workflows').mkdir(parents=True)
        (self.overlay/'.github/workflows/br.yml').write_text('name: local test BR\n')
        self.dest=self.base/'assembled'

    def tearDown(self):self.temp.cleanup()

    def build(self):return assembler.assemble(str(self.up),self.dest,self.overlay,self.sha)

    def test_real_clone_preserves_history_and_source(self):
        receipt=self.build()
        self.assertEqual(assembler.git(self.dest,'rev-parse','HEAD'),self.sha)
        self.assertFalse(receipt['remote_mutation'])
        self.assertEqual((self.up/'README.md').read_text(),'Original upstream test fixture.\n')
        self.assertEqual((self.dest/'README.md').read_text(),'BR overlay fixture.\n')

    def test_archive_upstream_workflows_and_cla(self):
        self.build()
        self.assertFalse((self.dest/'.github/workflows/old.yml').exists())
        self.assertTrue((self.dest/'upstream-reference/github-workflows/old.yml').exists())
        self.assertTrue((self.dest/'.github/workflows/br.yml').exists())
        self.assertTrue((self.dest/'upstream-reference/CLA.md').exists())
        self.assertFalse((self.dest/'CLA.md').exists())

    def test_vendor_preserved_marketplace_replaced(self):
        self.build()
        self.assertEqual((self.dest/'vendor/unchanged.txt').read_text(),'Retained vendor test content.\n')
        self.assertEqual(json.loads((self.dest/'.claude-plugin/marketplace.json').read_text())['name'],'fixture-br')
        self.assertTrue((self.dest/'upstream-reference/.claude-plugin/marketplace.json').exists())

    def test_refuses_existing_destination(self):
        self.dest.mkdir();(self.dest/'keep').write_text('must survive')
        with self.assertRaises(ValueError):self.build()
        self.assertEqual((self.dest/'keep').read_text(),'must survive')

    def test_refuses_nested_destination(self):
        with self.assertRaises(ValueError):assembler.assemble(str(self.up),self.overlay/'child',self.overlay,self.sha)

    def test_refuses_unpinned_commit(self):
        with self.assertRaises(ValueError):assembler.assemble(str(self.up),self.dest,self.overlay,'main')
        self.assertFalse(self.dest.exists())

    def test_refuses_overlay_symlinks(self):
        (self.overlay/'symlink').symlink_to(self.up/'README.md')
        with self.assertRaises(ValueError):self.build()

    def test_assembly_does_not_set_origin_or_commit_br(self):
        self.build()
        self.assertEqual(assembler.git(self.dest,'remote'),'upstream')
        self.assertTrue(assembler.git(self.dest,'status','--porcelain'))
        lock=json.loads((self.dest/'upstream.lock.json').read_text())
        self.assertEqual(lock['mode'],'pinned-upstream-with-br-overlay')
        self.assertEqual(lock['publication_status'],'not_published')

if __name__=='__main__':unittest.main()
