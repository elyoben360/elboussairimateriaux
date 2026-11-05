#!/usr/bin/env python3
"""Export the built development site as a self-contained HTML preview; no hosting or publication."""
from pathlib import Path
import base64,json,mimetypes,re,argparse
ROOT=Path(__file__).resolve().parents[1]
def export(out):
    dist=ROOT/'dist';cache={}
    def asset(path):
        if path not in cache:
            p=dist/path.lstrip('/');mime=mimetypes.guess_type(p.name)[0] or 'application/octet-stream';cache[path]='data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
        return cache[path]
    paths=['/','/actualites/','/actualites/preparer-livraison-acces-contraint/','/atelier/'];pages={}
    for path in paths:
        s=(dist/path.lstrip('/')/'index.html').read_text()
        s=re.sub(r'<link rel="stylesheet" href="([^"]+)">',lambda m:'<style>'+(dist/m[1].lstrip('/')).read_text()+'</style>',s)
        s=re.sub(r'<script src="([^"]+)" defer></script>',lambda m:'<script>'+(dist/m[1].lstrip('/')).read_text().replace('</script','<\\/script')+'</script>',s)
        # Replace local image paths in both markup and reference data.
        for p in dist.rglob('*'):
            if p.is_file() and p.suffix.lower() in ['.webp','.jpg','.svg']:
                url='/'+str(p.relative_to(dist));s=s.replace(url,asset(url))
        routing=r"""<script>document.addEventListener('click',e=>{const a=e.target.closest('a');if(!a)return;const href=a.getAttribute('href');if(!href||!href.startsWith('/'))return;const u=new URL(href,'https://preview.invalid');if(!['/','/actualites/','/actualites/preparer-livraison-acces-contraint/','/atelier/'].includes(u.pathname))return;e.preventDefault();parent.postMessage({type:'ebm-preview-route',path:u.pathname,hash:u.hash},'*')});<\/script>""".replace('<\\/script>','</script>')
        s=s.replace('</body>',routing+'</body>');pages[path]=s
    payload=json.dumps(pages,ensure_ascii=False).replace('<','\\u003c')
    route_js=r"""const frame=document.getElementById("preview");function show(path,hash){let page=pages[path]||pages["/"];if(hash){const bodyEnd=String.fromCharCode(60)+"/body>",start=String.fromCharCode(60)+"script>",end=String.fromCharCode(60)+"/script>";const code='addEventListener("load",()=>{const e=document.getElementById('+JSON.stringify(hash.slice(1))+');if(e)e.scrollIntoView()})';page=page.replace(bodyEnd,start+code+end+bodyEnd)}frame.srcdoc=page}addEventListener("message",e=>{if(e.source===frame.contentWindow&&e.data?.type==="ebm-preview-route"&&pages[e.data.path])show(e.data.path,e.data.hash)});show("/","");"""
    html='<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Banana Matériaux — Aperçu de développement</title><style>html,body{margin:0;height:100%;background:#f8f7f4}iframe{display:block;width:100%;height:100%;border:0}</style><iframe id="preview" title="Prévisualisation du site Banana Matériaux" sandbox="allow-scripts allow-forms allow-popups allow-downloads allow-same-origin"></iframe><script>const pages='+payload+';'+route_js+'</script></html>'
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(html);print('Self-contained preview:',out,len(html),'characters')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();export(Path(a.out))
