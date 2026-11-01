#!/usr/bin/env python3
"""Stage only generated public files for the existing Cloudflare --assets . deployment."""
from pathlib import Path
import shutil,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build import ROOT,build
build(out='dist-production')
# Remove obsolete generated articles when an article is withdrawn.
shutil.rmtree(ROOT/'actualites',ignore_errors=True)
for source in (ROOT/'dist-production').rglob('*'):
    if source.is_file():
        dest=ROOT/source.relative_to(ROOT/'dist-production')
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest)
print('Production assets staged; no deployment performed.')
