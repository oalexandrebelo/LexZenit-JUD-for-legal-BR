"""Browser tests of the offline renderer and failure handling, NOT React Flow E2E.

Requires Playwright and an available Chromium executable. Uses generated HTML
in memory, no local-file access or external network. The route abort is an
explicit outage scenario, not a substitute/mock implementation of React Flow.
"""
from pathlib import Path
import json
import os
import shutil
import unittest
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
class OfflineDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw=sync_playwright().start()
        exe=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        cls.browser=cls.pw.chromium.launch(headless=True,executable_path=exe,args=['--no-sandbox'])
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.pw.stop()
    def setUp(self):
        self.context=self.browser.new_context(viewport={'width':1440,'height':1050})
        self.requests=[];self.errors=[]
        self.context.route('https://**/*',lambda route:route.abort())
        self.page=self.context.new_page()
        self.page.on('request',lambda request:self.requests.append(request.url))
        self.page.on('pageerror',lambda error:self.errors.append(str(error)))
        self.page.set_content((ROOT/'index.html').read_text(encoding='utf8'))
        self.page.wait_for_selector('.diagram-node')
    def tearDown(self):self.context.close()
    def test_no_network_before_explicit_activation(self):
        self.assertEqual(self.requests,[]);self.assertEqual(self.errors,[])
    def test_pipeline_and_contract_inspection(self):
        self.assertEqual(self.page.locator('.diagram-node').count(),14)
        self.page.locator('[data-node-id="citations"]').click()
        self.assertEqual(self.page.locator('#inspector h2').inner_text(),'Citações brasileiras')
        self.assertIn('runtime/legal_br/citations.py',self.page.locator('#inspector').inner_text())
    def test_all_four_views_use_their_own_nodes(self):
        for view,count in [('references',13),('privacy',7),('evaluation',7),('pipeline',14)]:
            self.page.locator(f'[data-view="{view}"]').click()
            self.assertEqual(self.page.locator('.diagram-node').count(),count)
    def test_search_never_mutates_the_canonical_graph(self):
        self.page.locator('#search').fill('Citações brasileiras')
        self.assertEqual(self.page.locator('.diagram-node').count(),1)
        self.page.locator('#search').fill('não existe este nó')
        self.assertTrue(self.page.locator('#empty').is_visible())
        self.page.locator('#search').fill('')
        self.assertEqual(self.page.locator('.diagram-node').count(),14)
    def test_status_filter_exposes_pending_components(self):
        self.page.locator('#status-filter').select_option('pending')
        self.assertEqual(self.page.locator('.diagram-node').count(),2)
        self.assertIn('Não implementado',self.page.locator('#inspector').inner_text())
    def test_keyboard_selection_and_accessible_list(self):
        n=self.page.locator('[data-node-id="xml"]');n.focus();n.press('Enter')
        self.assertEqual(self.page.locator('#inspector h2').inner_text(),'Estrutura LexML')
        self.page.locator('#list-toggle').click()
        self.assertEqual(self.page.locator('#list-panel .list-node').count(),14)
        self.assertFalse(self.page.locator('#native-canvas').is_visible())
    def test_mobile_defaults_to_readable_list_without_horizontal_overflow(self):
        self.page.set_viewport_size({'width':390,'height':844})
        self.page.wait_for_selector('#list-panel',state='visible')
        self.assertEqual(self.page.evaluate('document.documentElement.scrollWidth'),390)
        self.assertEqual(self.page.locator('#list-panel .list-node').count(),14)
    def test_export_contains_the_real_graph(self):
        with self.page.expect_download() as found:self.page.locator('#export').click()
        download=found.value
        exported=json.loads(Path(download.path()).read_text())
        self.assertEqual(len(exported['nodes']),31);self.assertFalse(exported['is_live_system'])
    def test_cdn_failure_does_not_destroy_local_documentation(self):
        self.page.locator('#activate-flow').click()
        self.page.locator('#mode-label').filter(has_text='indisponível').wait_for(timeout=25000)
        self.assertEqual(self.page.locator('.diagram-node').count(),14)
        self.page.locator('[data-node-id="hmac"]').click()
        self.assertEqual(self.page.locator('#inspector h2').inner_text(),'Pseudônimos por caso')
    def test_unverified_reference_is_visible_by_its_original_name(self):
        self.page.locator('[data-view="references"]').click()
        self.page.locator('[data-node-id="REF_OPEN_ECLI_UNCONFIRMED"]').click()
        self.assertIn('Open-ECLI-Utils',self.page.locator('#inspector h2').inner_text())
        self.assertIn('Não identificada',self.page.locator('#inspector').inner_text())

if __name__=='__main__':unittest.main(verbosity=2)
