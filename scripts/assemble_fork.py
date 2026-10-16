#!/usr/bin/env python3
"""Clone pinned upstream and apply this BR layer, without publishing or overwriting.

Network access is required for the public upstream. No remote mutation is performed.
Upstream workflows are archived before a subsequent user-directed push.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

IGNORE = shutil.ignore_patterns('.git','__pycache__','*.pyc','*.sqlite','*.sqlite-*','*.bundle','.venv','_workspace')
ROOT_BACKUPS = ('README.md','QUICKSTART.md','CLAUDE.md','CLA.md','CONTRIBUTING.md','CONNECTORS.md','.claude-plugin/marketplace.json')


def git(directory: Path | None, *args: str) -> str:
    cmd = ['git'] + (['-C',str(directory)] if directory else []) + list(args)
    return subprocess.run(cmd,check=True,text=True,capture_output=True).stdout.strip()


def assemble(source: str, destination: Path, overlay: Path, commit: str) -> dict:
    overlay = overlay.resolve(); destination = destination.resolve()
    if destination.exists():
        raise ValueError('Destination already exists; nothing was changed.')
    if destination == overlay or overlay in destination.parents or destination in overlay.parents:
        raise ValueError('Overlay and destination must be separate trees.')
    if not re.fullmatch('[0-9a-f]{40}',commit):
        raise ValueError('Require a full pinned Git commit.')
    if not (overlay/'upstream.lock.json').is_file():
        raise ValueError('Missing BR lock manifest.')
    for entry in overlay.rglob('*'):
        if '.git' not in entry.parts and entry.is_symlink():
            raise ValueError('Symlinks in overlay require explicit review.')
    # No --recurse-submodules, no remote scripts, no curl | sh.
    git(None,'clone','--no-checkout','--no-hardlinks','--',source,str(destination))
    git(destination,'checkout','-B','main',commit)
    if git(destination,'rev-parse','HEAD') != commit:
        raise ValueError('Pinned upstream commit mismatch.')
    git(destination,'remote','rename','origin','upstream')
    archive = destination/'upstream-reference'
    archive.mkdir(exist_ok=True)
    for name in ROOT_BACKUPS:
        item = destination/name
        if item.is_file():
            target=archive/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(item,target)
    if (destination/'CLA.md').is_file():
        # Original CLA remains in history and archive, not imposed on BR contributors.
        (destination/'CLA.md').unlink()
    workflows = destination/'.github/workflows'
    if workflows.exists():
        shutil.move(str(workflows),str(archive/'github-workflows'))
    shutil.copytree(overlay,destination,dirs_exist_ok=True,ignore=IGNORE)
    lock=json.loads((destination/'upstream.lock.json').read_text())
    lock['mode']='pinned-upstream-with-br-overlay'
    lock['assembled_upstream_commit']=commit
    lock['publication_status']='not_published'
    (destination/'upstream.lock.json').write_text(json.dumps(lock,indent=2,ensure_ascii=False)+'\n')
    receipt={'assembled':True,'upstream_commit':commit,'destination':str(destination),'remote_mutation':False,'committed_br_changes':False,'upstream_workflows_archived':True}
    (destination/'evidence').mkdir(exist_ok=True)
    (destination/'evidence/assembly.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination',type=Path,required=True)
    args=p.parse_args()
    overlay=Path(__file__).resolve().parents[1]
    lock=json.loads((overlay/'upstream.lock.json').read_text())
    try:
        print(json.dumps(assemble(lock['url'],args.destination,overlay,lock['commit']),indent=2))
        return 0
    except (OSError,ValueError,subprocess.CalledProcessError) as exc:
        print(f'Assembly failed ({type(exc).__name__}). No GitHub repository was created. An incomplete destination, if present, is retained for inspection.',file=sys.stderr)
        return 2


if __name__=='__main__':raise SystemExit(main())
