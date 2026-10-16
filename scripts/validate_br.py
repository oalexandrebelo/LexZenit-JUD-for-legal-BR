#!/usr/bin/env python3
"""Offline structural checks. Not a substitute for Claude CLI or legal evaluation."""
from __future__ import annotations
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

NAME = re.compile(r'^[a-z0-9][a-z0-9-]{1,63}$')
HIDDEN = re.compile('[\u200b-\u200f\u202a-\u202e\u2066-\u2069\ufeff]')


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(path: Path):
    return json.loads(path.read_text(encoding='utf8'))


def validate(root: Path) -> dict:
    root = root.resolve()
    market = load(root/'.claude-plugin/marketplace.json')
    catalog = load(root/'catalog/skills.json')
    source_list = load(root/'catalog/sources.json')
    source_ids = {s['id'] for s in source_list}
    require(len(source_ids) == len(source_list), 'Duplicate source IDs.')
    for source in source_list:
        parsed = urlsplit(source['url'])
        require(parsed.scheme == 'https' and bool(parsed.hostname), 'Invalid source URL.')
        require(source['connector_implemented'] is False, 'Unexpected connector claim.')
        require(source['full_text_bundled'] is False, 'Unexpected normative corpus claim.')
        require(source['discovery'] in {'inherited_lexguard_v2_not_rechecked','official_page_identified_this_session','catalog_seed_requires_verification'}, 'Unknown source provenance state.')
    names = [p['name'] for p in market['plugins']]
    require(names == sorted(set(names)), 'Plugin names must be unique and sorted.')
    require(catalog['plugins'] == len(names), 'Plugin count drift.')
    require(catalog['semantic_benchmark_executed'] is False, 'Unsubstantiated semantic benchmark claim.')
    for entry in market['plugins']:
        name = entry['name']
        require(NAME.fullmatch(name) is not None and name.startswith('br-'), 'Invalid BR namespace.')
        require(entry['source'] == './'+name, 'Plugin source must be a local canonical directory.')
        folder = root/name
        require(not folder.is_symlink(), 'Plugin directory symlink rejected.')
        manifest = load(folder/'.claude-plugin/plugin.json')
        for key in ('name','description','author'):
            require(manifest[key] == entry[key], f'Manifest mismatch: {name}:{key}.')
        require(not HIDDEN.search(manifest['description']), 'Invisible characters in description.')
        require(10 <= len(manifest['description']) <= 2000, 'Invalid description length.')
        require(not (folder/'.mcp.json').exists() and not (folder/'hooks').exists(), 'BR plugins must not silently add MCP or hooks.')
        require((folder/'references/POLICY.md').is_file(), 'Missing packaged policy.')
        require(load(folder/'references/sources.json'), 'Missing packaged sources.')
    seen = set()
    for skill in catalog['skills']:
        key = (skill['plugin'],skill['id'])
        require(key not in seen, 'Duplicate skill.'); seen.add(key)
        require(skill['plugin'] in names, 'Unknown plugin.')
        expected = f"{skill['plugin']}/skills/{skill['id']}/SKILL.md"
        require(skill['path'] == expected and NAME.fullmatch(skill['id']) is not None, 'Invalid skill path.')
        path = root/expected
        require(not path.is_symlink(), 'Skill symlink rejected.')
        text = path.read_text(encoding='utf8')
        require(text.startswith('---\n') and text.count('\n---\n') >= 1, 'Missing frontmatter.')
        front = text.split('\n---\n',1)[0][4:]
        fields = dict(line.split(': ',1) for line in front.splitlines() if ': ' in line)
        require(fields.get('name') == skill['id'], 'Frontmatter name drift.')
        require(bool(json.loads(fields['description'])), 'Description must be a nonempty quoted string.')
        require(fields.get('disable-model-invocation') == 'true', 'Explicit invocation required.')
        require(fields.get('allowed-tools') == 'Read, Grep, Glob, WebSearch, WebFetch', 'Unexpected tool scope.')
        require(skill['automatic_legal_decision'] is False and skill['external_connector'] is False, 'Unsubstantiated execution claim.')
        require(skill['workflow_status'] == 'authored_not_semantically_benchmarked', 'Unexpected workflow assurance level.')
        require(set(skill['source_ids']) <= source_ids, 'Dangling source reference.')
        require(len(skill['method']) > 60 and len(skill['negative_case']) > 30, 'Incomplete skill contract.')
        require('../../references/POLICY.md' in text, 'Policy not linked from skill.')
        require(not HIDDEN.search(text), 'Invisible controls in skill.')
    require(len(seen) == catalog['total'], 'Skill count drift.')
    paths = {str(p.relative_to(root)) for name in names for p in (root/name/'skills').glob('*/SKILL.md')}
    require(paths == {s['path'] for s in catalog['skills']}, 'Uncatalogued or missing skill files.')
    ontology = load(root/'ontology/br-legal.json')
    types = {node['type'] for node in ontology['nodes']}
    require(len(types) == len(ontology['nodes']), 'Duplicate ontology type.')
    require(ontology['status'] == 'design_contract_not_deployed_to_neo4j', 'Ontology deployment claim.')
    for edge in ontology['edges']:
        require(edge['from'] in types and edge['to'] in types, 'Unknown edge type endpoint.')
        require(edge['requires_evidence'] and edge['requires_review_before_legal_retrieval'], 'Unreviewed legal edge.')
    cases = [json.loads(line) for line in (root/'evals/semantic-cases.jsonl').read_text().splitlines() if line]
    require(len(cases) == catalog['total'], 'Acceptance specification count drift.')
    return {'structural_validation':'passed','plugins':len(names),'skills':len(seen),'source_records':len(source_list),'semantic_case_specifications':len(cases),'official_claude_cli_validation':False,'semantic_evaluation':False}


def main() -> int:
    try:
        root = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
        print(json.dumps(validate(root),ensure_ascii=False,indent=2))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print(f'Validation failed: {exc}',file=sys.stderr)
        return 1


if __name__=='__main__':raise SystemExit(main())
