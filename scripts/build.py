#!/usr/bin/env python3
"""Dependency-free static build. Preview includes visibly labelled drafts; production never does."""
from pathlib import Path
import argparse, json, html, shutil, re
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
BASE='https://elboussairimateriaux.com'
CATEGORIES=['Ciment et béton','Acier et fer à béton','Briques, agglos et agrégats','Évolution des prix','Nouveaux chantiers','Investissements et infrastructures','Innovations et tendances','Transport de marchandises et logistique']
def esc(value): return html.escape(str(value),quote=True)
def read(name): return (ROOT/name).read_text()
def load(name): return json.loads(read(name))
def safe_url(url):
    if not re.fullmatch(r'https://[^\s<>"\x00-\x20]+',url): raise ValueError('URL HTTPS invalide')
    return esc(url)
def header(preview=False):
    banner='<div class="preview-banner">Version de développement · Prévisualisation</div>' if preview else ''
    return banner+'<a class="skip" href="#main">Aller au contenu</a><header><nav class="wrap" aria-label="Navigation principale"><a class="logo logo-link" href="/" aria-label="El Boussairi Matériaux — Accueil">EL BOUSSAIRI<br> MATÉRIAUX<small>FOURNITURE · APPROVISIONNEMENT · TRANSPORT</small></a><div class="navitems"><a href="/#catalogue">Matériaux</a><a href="/#transport">Logistique</a><a href="/#references">Références</a><a href="/actualites/">Actualités</a><a class="nav-request" href="/#contact">Ma demande <span class="counter" id="count">0</span></a></div></nav></header>'
def footer():
    return '<footer class="footer-main"><div class="wrap"><div class="footer-grid"><div><h3>EL BOUSSAIRI MATÉRIAUX</h3><p>Fourniture, approvisionnement et livraison de matériaux pour vos chantiers.</p></div><div><h4>Contact</h4><a href="tel:+212602644454">+212 602 64 44 54</a><a href="mailto:youssef.materiauxdeconstruction@gmail.com">youssef.materiauxdeconstruction@gmail.com</a></div><div><h4>Votre chantier</h4><p>Casablanca et autres destinations selon faisabilité.</p><a href="/#contact">Préparer une commande →</a><a href="/actualites/">Actualités & Marché du BTP →</a></div></div><div class="footer-bottom"><span>© El Boussairi Matériaux</span><span>Matériaux · Approvisionnement · Livraison</span></div></div></footer><div class="mobile-request" aria-label="Accès rapide à votre demande"><a class="mobile-call" href="tel:+212602644454">Appeler</a><a class="btn" href="/#contact">Ma demande <span class="counter" id="mobileCount">0</span></a></div><div class="toast" id="toast" role="status"></div>'
def shell(title,description,body,path='/',scripts=(),preview=False,schema=None):
    robots='<meta name="robots" content="noindex,nofollow">' if preview else '<meta name="robots" content="index,follow">'
    metadata='' if preview else '<link rel="canonical" href="'+BASE+path+'">'
    if schema and not preview: metadata+='<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script>'
    return '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#172f59"><title>'+esc(title)+'</title><meta name="description" content="'+esc(description)+'">'+robots+metadata+'<link rel="alternate" type="application/rss+xml" title="Le journal BTP & logistique" href="/actualites/feed.xml"><link rel="stylesheet" href="/assets/site.css"></head><body>'+header(preview)+'<main id="main">'+body+'</main>'+footer()+''.join('<script src="'+x+'" defer></script>' for x in scripts)+'</body></html>'
def date_fr(s):
    d=date.fromisoformat(s);return f'{d.day} '+['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'][d.month-1]+f' {d.year}'
def reference_cards(refs):
    out=[]
    for r in refs:
        photos=r.get('photos',[])
        cover='<img src="'+esc(photos[0]['src'])+'" alt="'+esc(photos[0]['alt'])+'" width="'+str(photos[0]['width'])+'" height="'+str(photos[0]['height'])+'" loading="lazy">' if photos else '<div class="reference-cover-pending"><span>Villa · Aïn Diab</span><small>Galerie en attente de photographies validées</small></div>'
        out.append('<article class="reference-card" id="'+esc(r['id'])+'">'+cover+'<div class="reference-card-body"><span class="tag">'+esc(r['label'])+'</span><h3>'+esc(r['title'])+'</h3><time datetime="'+r['date']+'">'+date_fr(r['date'])+'</time><p>'+esc(r['location'])+'</p><p>'+esc(r['materials'])+'</p><button class="btn outline" type="button" data-reference="'+esc(r['id'])+'" aria-haspopup="dialog">Voir cette référence →</button></div></article>')
    return ''.join(out)
def article_card(a,preview):
    draft=a['status']!='published'
    return '<article class="article-card" data-category="'+esc(a['category'])+'" data-search="'+esc((a['title']+' '+a['summary']+' '+a['category']).lower())+'"><img src="'+esc(a['cover'])+'" alt="'+esc(a.get('cover_alt','Illustration éditoriale'))+'" width="1200" height="630" loading="lazy"><div class="article-card-body"><span class="tag">'+esc(a['category'])+'</span>'+('<div class="draft-banner">Brouillon de démonstration · Non publié</div>' if draft else '')+'<h2><a href="/actualites/'+a['slug']+'/">'+esc(a['title'])+'</a></h2><p>'+esc(a['summary'])+'</p><div class="article-meta"><time datetime="'+a['date']+'">'+date_fr(a['date'])+'</time><span>'+esc(a.get('kind','Article'))+'</span></div></div></article>'
def article_page(a,preview):
    body='<section class="section"><article class="wrap article-layout"><a class="reading-back" href="/actualites/">← Toutes les actualités</a><span class="tag">'+esc(a['category'])+'</span><h1>'+esc(a['title'])+'</h1><div class="article-meta"><time datetime="'+a['date']+'">'+date_fr(a['date'])+'</time><span>'+esc(a.get('kind','Article'))+'</span></div>'
    if a.get('event_period'):body+='<div class="article-context">Période des faits : '+esc(a['event_period'])+' · Vérification : '+esc(a.get('verification',{}).get('checked_on',''))+'</div>'
    if a['status']!='published':body+='<div class="draft-banner">Démonstration du circuit éditorial. Ce guide est un brouillon, ce n’est pas une actualité de marché et il n’est pas publié.</div>'
    body+='<p>'+esc(a['summary'])+'</p><img class="article-cover" src="'+esc(a['cover'])+'" alt="'+esc(a.get('cover_alt','Illustration éditoriale'))+'" width="1200" height="630">'
    for s in a['sections']:body+='<h2>'+esc(s['title'])+'</h2>'+''.join('<p>'+esc(p)+'</p>' for p in s['paragraphs'])
    body+='<aside class="article-sources"><h2>Sources & vérification</h2><p>'+esc(a.get('source_note',''))+'</p><ul>'+''.join('<li><a href="'+safe_url(s['url'])+'" target="_blank" rel="noopener noreferrer">'+esc(s['title'])+'</a> · '+esc(s.get('date',''))+'</li>' for s in a['sources'])+'</ul></aside><div class="actions"><a class="btn" href="/#catalogue">Préparer ma commande</a><a class="btn outline" href="/actualites/">Retour au journal</a></div></article></section>'
    schema={'@context':'https://schema.org','@type':'Article','headline':a['title'],'datePublished':a['date'],'dateModified':a['date'],'description':a['summary'],'image':BASE+a['cover'],'mainEntityOfPage':BASE+'/actualites/'+a['slug']+'/','author':{'@type':'Organization','name':'El Boussairi Matériaux'},'publisher':{'@type':'Organization','name':'El Boussairi Matériaux'}}
    return shell(a['title']+' | El Boussairi Matériaux',a['summary'],body,'/actualites/'+a['slug']+'/',preview=preview,scripts=['/assets/shared.js'],schema=schema)
def build(preview=False,out='dist'):
    target=(ROOT/out).resolve()
    if target==ROOT or ROOT not in target.parents: raise ValueError('Build output must be a subdirectory')
    if target.exists():
        for child in target.iterdir():
            if child.is_dir():shutil.rmtree(child)
            else:child.unlink()
    target.mkdir(exist_ok=True);shutil.copytree(ROOT/'assets',target/'assets')
    (target/'assets/site.css').write_text(read('src/legacy.css')+'\n'+read('src/site.css'))
    for source in ['catalogue.js','references.js','shared.js','blog.js']:
        shutil.copyfile(ROOT/'src'/source,target/'assets'/source)
    refs=load('content/references.json')
    if not preview:
        for r in refs:r.pop('pending_photos',None)
        # Validated reference photographs remain in the production build.
    (target/'assets/references-data.js').write_text('window.EBM_REFERENCES='+json.dumps(refs,ensure_ascii=False).replace('<','\\u003c')+';')
    published=sorted([a for a in load('content/articles.json') if a['status']=='published'],key=lambda a:(a['date'],a['id']),reverse=True)
    latest='<section class="section latest-news"><div class="wrap"><div class="section-heading"><div><div class="eyebrow">Le journal du secteur</div><h2>Matériaux, BTP & logistique</h2></div><a class="reading-back" href="/actualites/">Toutes les actualités →</a></div><div class="blog-grid">'+''.join(article_card(a,preview) for a in published[:3])+'</div></div></section>' if published else ''
    home=read('src/home.html').replace('{{REFERENCE_CARDS}}',reference_cards(refs)).replace('{{LATEST_NEWS}}',latest)
    (target/'index.html').write_text(shell('El Boussairi Matériaux | Fourniture & Livraison','Matériaux de construction, approvisionnement et livraison pour vos chantiers à Casablanca et autres destinations selon faisabilité.',home,preview=preview,scripts=['/assets/catalogue.js','/assets/references-data.js','/assets/references.js','/assets/shared.js']))
    articles=load('content/articles.json')
    from editorial import validate_article
    for a in articles:validate_article(a)
    visible=sorted([a for a in articles if a['status']=='published' or preview],key=lambda a:(a['date'],a['id']),reverse=True)
    if not preview:
        for a in visible:
            from editorial import check_approval
            check_approval(a)
    news=target/'actualites';news.mkdir()
    body='<section class="editorial-hero"><div class="wrap"><div class="eyebrow">Le journal</div><h1>Actualités & Marché du BTP</h1><p>Matériaux, chantiers et transport de marchandises au Maroc. Les faits, leurs sources et les repères utiles à vos approvisionnements.</p></div></section><section class="section"><div class="wrap"><div class="blog-tools"><div class="field"><label for="articleSearch">Rechercher un sujet</label><input id="articleSearch" type="search" placeholder="Ciment, acier, chantier…"></div><div class="field"><label for="articleCategory">Rubrique</label><select id="articleCategory"><option value="">Toutes les rubriques</option>'+''.join('<option>'+esc(c)+'</option>' for c in CATEGORIES)+'</select></div></div><p class="catalogue-status" id="articleStatus" role="status"></p><div class="blog-grid" id="articles">'+''.join(article_card(a,preview) for a in visible)+'</div><div class="empty-state" id="articleEmpty"'+(' hidden' if visible else '')+'><h2>Les prochaines actualités se préparent</h2><p>Les articles apparaîtront ici après vérification des sources et validation éditoriale.</p></div></div></section>'
    (news/'index.html').write_text(shell('Actualités & Marché du BTP | El Boussairi Matériaux','Le journal des matériaux et du BTP au Maroc : ciment, acier, briques, agrégats, chantiers et infrastructures.',body,'/actualites/',scripts=['/assets/blog.js','/assets/shared.js'],preview=preview))
    for a in visible:
        folder=news/a['slug'];folder.mkdir();(folder/'index.html').write_text(article_page(a,preview))
    from email.utils import format_datetime
    from datetime import datetime, timezone
    items=[]
    for a in visible:
        if a['status']!='published':continue
        u=BASE+'/actualites/'+a['slug']+'/'
        items.append('<item><title>'+esc(a['title'])+'</title><link>'+u+'</link><guid>'+u+'</guid><description>'+esc(a['summary'])+'</description><pubDate>'+format_datetime(datetime.fromisoformat(a['date']).replace(tzinfo=timezone.utc))+'</pubDate></item>')
    (news/'feed.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>El Boussairi — BTP &amp; Logistique</title><link>'+BASE+'/actualites/</link><description>Actualités sourcées du secteur au Maroc</description>'+''.join(items)+'</channel></rss>')
    links=['/','/actualites/']+['/actualites/'+a['slug']+'/' for a in visible if a['status']=='published']
    (target/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+x+'</loc></url>' for x in links)+'</urlset>')
    (target/'robots.txt').write_text('User-agent: *\nDisallow: /\n' if preview else 'User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n')
    (target/'404.html').write_text(shell('Page introuvable | El Boussairi Matériaux','Page introuvable.','<section class="section"><div class="wrap"><h1>Cette page est introuvable.</h1><a class="btn" href="/">Retour à l’accueil</a></div></section>',preview=preview))
    (target/'_headers').write_text('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n  X-Frame-Options: SAMEORIGIN\n  Content-Security-Policy: default-src \'self\'; script-src \'self\'; style-src \'self\' \'unsafe-inline\'; img-src \'self\' data:; base-uri \'self\'; object-src \'none\'; frame-ancestors \'self\'; form-action \'self\'\n')
    print('Built',target,'PREVIEW' if preview else 'PRODUCTION ARTIFACT ONLY','|',len(visible),'articles |',len(refs),'références')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--out',default='dist');args=parser.parse_args();build(args.preview,args.out)
