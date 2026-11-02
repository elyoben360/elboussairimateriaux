#!/usr/bin/env python3
"""Dependency-free static build. Preview includes visibly labelled drafts; production never does."""
from pathlib import Path
import argparse, json, html, shutil, re, hashlib, base64
from datetime import date
from journal import offer,community,privacy
from product_pages import gallery,featured,product_page,image_schema,photo_markup
from motion_components import hero,ticker,news_controls,editorial_hero
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
    return banner+'<a class="skip" href="#main">Aller au contenu</a><header><nav class="wrap" aria-label="Navigation principale"><a class="logo logo-link" translate="no" href="/" aria-label="El Boussairi Matériaux — Accueil">EL BOUSSAIRI<br> MATÉRIAUX<small>FOURNITURE · APPROVISIONNEMENT · TRANSPORT</small></a><button type="button" class="menu-toggle" aria-expanded="false" aria-controls="site-menu">Menu</button><div class="language-control" translate="no"><span class="language-current" aria-hidden="true"><span data-language-flag>🇫🇷</span><span data-language-code>FR</span><span class="language-chevron">⌄</span></span><label class="sr-only" for="site-language">Langue du site</label><select id="site-language" aria-label="Langue du site"><option value="fr" lang="fr">🇫🇷 Français</option><option value="en" lang="en">🇬🇧 English</option><option value="ar" lang="ar">🇲🇦 العربية</option><option value="zh" lang="zh">🇨🇳 中文（普通话）</option><option value="de" lang="de">🇩🇪 Deutsch</option><option value="nl" lang="nl">🇳🇱 Nederlands</option><option value="ru" lang="ru">🇷🇺 Русский</option><option value="pl" lang="pl">🇵🇱 Polski</option></select></div><div class="navitems" id="site-menu"><a href="/#catalogue">Matériaux</a><a href="/#transport">Logistique</a><a href="/#references">Références</a><a href="/#depot">Notre dépôt</a><a class="zi-entry" href="/actualites/">ZI · Zone Industrielle ↗</a><a class="nav-request" href="/#contact">Ma demande <span class="counter" id="count">0</span></a></div></nav></header>'
def journal_header(preview=False):
    language=header(False).split('<div class="language-control"',1)[1].split('<div class="navitems"',1)[0]
    language='<div class="language-control"'+language
    return '<a class="skip" href="#main">Aller au contenu</a><header class="zi-header"><nav class="wrap" aria-label="Navigation du journal"><a class="zi-wordmark" href="/actualites/"><img src="/assets/zone-industrielle-logo.webp" width="48" height="48" alt="ZI"><span>ZONE INDUSTRIELLE<small>LE JOURNAL · MAROC</small></span></a><div class="zi-navigation">'+language+'<a href="/actualites/#articles">À la une</a><button type="button" data-zi-account>Espace lecteur</button><a href="/actualites/#zi-rubriques">Rubriques</a></div></nav></header>'
def journal_footer():
    return '<footer class="zi-footer"><div class="wrap"><strong>ZONE INDUSTRIELLE</strong><p>Matériaux · Chantiers · Industrie — Le regard sur le Maroc qui se construit.</p><div class="actions"><a href="/actualites/">Le journal</a><a href="/actualites/confidentialite/">Confidentialité & espace lecteur</a><a href="/#catalogue">Vos matériaux avec El Boussairi Matériaux ↗</a></div><small>Édité par El Boussairi Matériaux</small></div></footer><div class="toast" id="toast" role="status"></div><a class="back-top" href="#main" aria-label="Revenir en haut" hidden>↑</a>'
def footer():
    return '<footer class="footer-main"><div class="wrap"><div class="footer-grid"><div><h3 translate="no">EL BOUSSAIRI MATÉRIAUX</h3><p>Fourniture, approvisionnement et livraison de matériaux pour vos chantiers.</p></div><div><h4>Contact</h4><a href="tel:+212602644454">+212 602 64 44 54</a><a href="mailto:youssef.materiauxdeconstruction@gmail.com">youssef.materiauxdeconstruction@gmail.com</a><a class="social-link" href="https://www.instagram.com/zoneindustielle" target="_blank" rel="noopener noreferrer" aria-label="Instagram — zoneindustielle (nouvel onglet)"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".8" fill="currentColor" stroke="none"/></svg></a></div><div><h4>Votre chantier</h4><p>Casablanca et autres destinations selon faisabilité.</p><a href="/#contact">Préparer une commande →</a><a href="/actualites/">Zone Industrielle →</a><a href="/actualites/confidentialite/">Confidentialité & espace lecteur</a></div></div><p class="map-attribution"><a href="https://commons.wikimedia.org/wiki/File:Location_map_Greater_Casablanca.png" target="_blank" rel="noopener noreferrer" title="Carte du Grand Casablanca, 2012, convertie en WebP">© OpenStreetMap · Dr. Blofeld</a> · <a href="https://creativecommons.org/licenses/by-sa/2.0/" target="_blank" rel="noopener noreferrer">CC BY-SA 2.0</a></p><div class="footer-bottom"><span>© El Boussairi Matériaux</span><span>Matériaux · Livraison</span></div><p class="image-rights" id="droits-images">Photographies de notre travail · © El Boussairi Matériaux. Réutilisation sur autorisation : <a href="mailto:youssef.materiauxdeconstruction@gmail.com">nous contacter</a>.</p></div></footer><div class="mobile-request" aria-label="Accès rapide à votre demande"><a class="mobile-call" href="tel:+212602644454">Appeler</a><a class="btn" href="/#contact">Ma demande <span class="counter" id="mobileCount">0</span></a></div><div class="toast" id="toast" role="status"></div><a class="back-top" href="#main" aria-label="Revenir en haut" hidden>↑</a>'
def shell(title,description,body,path='/',scripts=(),preview=False,schema=None,social_image=None):
    journal=path.startswith('/actualites/')
    if journal:
        scripts=[*scripts,'/assets/journal.js']
    robots='<meta name="robots" content="noindex,nofollow">' if preview else '<meta name="robots" content="index,follow,max-image-preview:large">'
    metadata='' if preview else '<link rel="canonical" href="'+BASE+path+'">'
    if not preview:
        image=(social_image or {}).get('src','/assets/depot/stock-ciment-holcim.webp')
        image_alt=(social_image or {}).get('alt','Ciment sur palettes dans notre dépôt')
        if schema and schema.get('@type')=='Article':
            image=schema['image'];image=image.get('contentUrl') if isinstance(image,dict) else image;image_alt=schema['headline']
        if image.startswith('/'):image=BASE+image
        metadata+='<meta property="og:type" content="'+('article' if schema and schema.get('@type')=='Article' else 'website')+'"><meta property="og:locale" content="fr_MA"><meta property="og:site_name" content="'+('Zone Industrielle' if journal else 'El Boussairi Matériaux')+'"><meta property="og:title" content="'+esc(title)+'"><meta property="og:description" content="'+esc(description)+'"><meta property="og:url" content="'+BASE+esc(path)+'"><meta property="og:image" content="'+esc(image)+'"><meta property="og:image:alt" content="'+esc(image_alt)+'"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="'+esc(title)+'"><meta name="twitter:description" content="'+esc(description)+'"><meta name="twitter:image" content="'+esc(image)+'"><meta name="twitter:image:alt" content="'+esc(image_alt)+'"><meta name="author" content="El Boussairi Matériaux">'
    if schema and not preview: metadata+='<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script>'
    return '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#172f59"><title>'+esc(title)+'</title><meta name="description" content="'+esc(description)+'">'+robots+metadata+'<link rel="alternate" type="application/rss+xml" title="Zone Industrielle" href="/actualites/feed.xml"><link rel="stylesheet" href="/assets/site.css">'+('<link rel="stylesheet" href="/assets/journal.css">' if journal else '')+'</head><body'+(' class="zi-page"' if journal else '')+'>'+(journal_header(preview) if journal else header(preview))+'<main id="main">'+body+'</main>'+(journal_footer() if journal else footer())+''.join('<script src="'+x+'" defer></script>' for x in ['/assets/album-data.js',*scripts,'/assets/translations.js','/assets/i18n.js'])+'</body></html>'
def date_fr(s):
    d=date.fromisoformat(s);return f'{d.day} '+['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'][d.month-1]+f' {d.year}'
def reference_cards(refs):
    out=[]
    for r in refs:
        photos=r.get('photos',[])
        cover='<img src="'+esc(photos[0]['src'])+'" alt="'+esc(photos[0]['alt'])+'" width="'+str(photos[0]['width'])+'" height="'+str(photos[0]['height'])+'" loading="lazy">' if photos else '<div class="reference-cover-pending"><span>Villa · Aïn Diab</span><small>Galerie en attente de photographies validées</small></div>'
        out.append('<article class="reference-card" id="'+esc(r['id'])+'">'+'<div class="owned-photo">'+cover+'<span class="photo-credit">© El Boussairi Matériaux</span></div><div class="reference-card-body"><span class="tag">'+esc(r['label'])+'</span><h3>'+esc(r['title'])+'</h3><time datetime="'+r['date']+'">'+date_fr(r['date'])+'</time><p>'+esc(r['location'])+'</p><p>'+esc(r['materials'])+'</p><button class="btn outline" type="button" data-reference="'+esc(r['id'])+'" aria-haspopup="dialog">Voir cette référence →</button></div></article>')
    return ''.join(out)
def article_card(a,preview):
    draft=a['status']!='published';url='/actualites/'+a['slug']+'/'
    return '<article class="article-card" data-category="'+esc(a['category'])+'" data-kind="'+esc(a.get('kind','Article'))+'" data-search="'+esc((a['title']+' '+a['summary']+' '+a['category']).lower())+'"><a class="owned-photo" href="'+url+'" aria-label="Lire : '+esc(a['title'])+'"><img src="'+esc(a['cover'])+'" alt="'+esc(a.get('cover_alt','Illustration éditoriale'))+'" width="'+str(a.get('cover_width',1200))+'" height="'+str(a.get('cover_height',630))+'" loading="lazy" decoding="async"><span class="photo-credit">'+esc(a.get('cover_credit','Illustration éditoriale'))+'</span></a><div class="article-card-body"><span class="tag">'+esc(a['category'])+'</span>'+('<div class="draft-banner">Brouillon · Non publié</div>' if draft else '')+'<h2><a href="'+url+'">'+esc(a['title'])+'</a></h2><p>'+esc(a['summary'])+'</p><div class="article-meta"><time datetime="'+a['date']+'">'+date_fr(a['date'])+'</time><span>'+esc(a.get('kind','Article'))+'</span><span>'+str(len(a['sources']))+' source'+('s' if len(a['sources'])>1 else '')+'</span></div><a class="text-action" href="'+url+'">Lire l’article →</a></div></article>'
def article_page(a,preview):
    body='<section class="section"><article class="wrap article-layout"><a class="reading-back" href="/actualites/">← Le journal</a><span class="tag">'+esc(a['category'])+'</span><h1>'+esc(a['title'])+'</h1><div class="article-meta"><time datetime="'+a['date']+'">'+date_fr(a['date'])+'</time><span>'+esc(a.get('kind','Article'))+'</span></div>'
    if a.get('event_period'):body+='<details class="article-context"><summary>Période couverte</summary><p>'+esc(a['event_period'])+'</p></details>'
    if a['status']!='published':body+='<div class="draft-banner">Brouillon de démonstration · Non publié.</div>'
    body+='<p>'+esc(a['summary'])+'</p>'
    album=[]
    if a.get('photo_ids'):
        photos=load('content/depot.json');album=[next(p for p in photos if p['id']==key) for key in a['photo_ids']]
    if album:body+='<figure class="article-photo">'+photo_markup(album[0],album)+'<div class="product-thumbnails">'+''.join(photo_markup(p,album,i) for i,p in enumerate(album) if i)+'</div><figcaption>'+esc(a.get('cover_caption',''))+('<br><a href="'+safe_url(a['cover_source'])+'" target="_blank" rel="noopener noreferrer">Source et auteur</a> · <a href="'+safe_url(a['cover_license_url'])+'" target="_blank" rel="noopener noreferrer">Licence '+esc(a['cover_provenance']['license'])+'</a> · Copie redimensionnée et convertie en WebP.' if a.get('cover_source') else '')+'</figcaption></figure>'
    else:body+='<figure class="article-photo"><div class="owned-photo"><img class="article-cover" src="'+esc(a['cover'])+'" alt="'+esc(a.get('cover_alt','Illustration éditoriale'))+'" width="'+str(a.get('cover_width',1200))+'" height="'+str(a.get('cover_height',630))+'"><span class="photo-credit">'+esc(a.get('cover_credit','Illustration éditoriale'))+'</span></div><figcaption>'+esc(a.get('cover_caption',''))+('<br><a href="'+safe_url(a['cover_source'])+'" target="_blank" rel="noopener noreferrer">Source et auteur</a> · <a href="'+safe_url(a['cover_license_url'])+'" target="_blank" rel="noopener noreferrer">Licence '+esc(a['cover_provenance']['license'])+'</a> · Copie redimensionnée et convertie en WebP.' if a.get('cover_source') else '')+'</figcaption></figure>'
    for i,section in enumerate(a['sections']):
        body+='<h2>'+esc(section['title'])+'</h2>'+''.join('<p>'+esc(value)+'</p>' for value in section['paragraphs'])
    body+=offer(a,'end')+community(a)
    body+='<aside class="article-sources"><h2>Sources</h2><p>'+esc(a.get('source_note',''))+'</p><ul>'+''.join('<li><a href="'+safe_url(source['url'])+'" target="_blank" rel="noopener noreferrer">'+esc(source['title'])+'</a> · '+esc(source.get('date',''))+'</li>' for source in a['sources'])+'</ul></aside><div class="actions"><a class="btn outline" href="/actualites/">Poursuivre dans le journal →</a></div></article></section>'
    image={'@type':'ImageObject','contentUrl':BASE+a['cover'],'url':BASE+a['cover'],'caption':a.get('cover_alt','Illustration éditoriale'),'creditText':a.get('cover_credit','El Boussairi Matériaux'),'copyrightNotice':a.get('cover_credit','© El Boussairi Matériaux'),'license':a.get('cover_license_url',BASE+'/#droits-images'),'acquireLicensePage':a.get('cover_source',BASE+'/#contact'),'creator':{'@type':'Person' if a.get('cover_source') else 'Organization','name':a.get('cover_provenance',{}).get('author','El Boussairi Matériaux')}}
    schema={'@context':'https://schema.org','@type':'Article','headline':a['title'],'datePublished':a['date'],'dateModified':a.get('updated_on',a['date']),'description':a['summary'],'image':image,'mainEntityOfPage':BASE+'/actualites/'+a['slug']+'/','articleSection':a['category'],'inLanguage':'fr-MA','keywords':[a['category'],'BTP Maroc','matériaux de construction'],'citation':[x['url'] for x in a['sources']],'author':{'@type':'Organization','name':'El Boussairi Matériaux'},'publisher':{'@type':'Organization','name':'Zone Industrielle','logo':{'@type':'ImageObject','url':BASE+'/assets/zone-industrielle-logo.webp'},'parentOrganization':{'@type':'Organization','name':'El Boussairi Matériaux'}}}
    return shell(a['title']+' | Zone Industrielle',a['summary'],body,'/actualites/'+a['slug']+'/',preview=preview,scripts=['/assets/media.js','/assets/motion.js','/assets/shared.js'],schema=schema)
def validate_article_translations(articles):
    """Fail publication if any published article lacks a complete locale."""
    source=read('src/translations.js')
    dictionaries=json.loads(source.split('=',1)[1].strip().rstrip(';'))
    languages=('en','ar','zh','de','nl','ru','pl')
    for article in articles:
        fields=[article['title'],article['summary'],article.get('event_period',''),article.get('source_note',''),article.get('cover_caption','')]
        for section in article.get('sections',[]):
            fields.extend([section['title'],*section.get('paragraphs',[])])
        for language in languages:
            missing=[value for value in fields if value and not dictionaries.get(language,{}).get(' '.join(value.split()))]
            if missing:raise ValueError('Traduction incomplète : '+article['id']+' / '+language+' / '+missing[0][:80])

def build(preview=False,out='dist'):
    target=(ROOT/out).resolve()
    if target==ROOT or ROOT not in target.parents: raise ValueError('Build output must be a subdirectory')
    if target.exists():
        for child in target.iterdir():
            if child.is_dir():shutil.rmtree(child)
            else:child.unlink()
    target.mkdir(exist_ok=True);shutil.copytree(ROOT/'assets',target/'assets')
    (target/'assets/site.css').write_text(read('src/legacy.css')+'\n'+read('src/site.css'))
    for source in ['catalogue.js','references.js','shared.js','blog.js','media.js','motion.js','i18n.js','translations.js','journal.js']:
        shutil.copyfile(ROOT/'src'/source,target/'assets'/source)
    refs=load('content/references.json')
    if not preview:
        for r in refs:r.pop('pending_photos',None)
        # Validated reference photographs remain in the production build.
    (target/'assets/references-data.js').write_text('window.EBM_REFERENCES='+json.dumps(refs,ensure_ascii=False).replace('<','\\u003c')+';')
    published=sorted([a for a in load('content/articles.json') if a['status']=='published'],key=lambda a:(a['date'],a['id']),reverse=True)
    if not preview:validate_article_translations(published)
    market=[a for a in published if a.get('kind')!='Notre activité']
    latest='<section class="section latest-news"><div class="wrap" data-news-carousel><div class="section-heading"><div><div class="eyebrow">Le journal</div><h2>Zone Industrielle</h2></div><div><a class="text-action" href="/actualites/">Tous les articles →</a>'+news_controls()+'</div></div><div class="blog-grid news-track" data-news-track>'+''.join(article_card(a,preview) for a in market[:8])+'</div></div></section>' if published else ''
    photos=load('content/depot.json')
    from product_pages import albums
    photo_albums=list(albums(photos).values())+[r['photos'] for r in refs if r.get('photos')]
    photo_index={}
    for group in photo_albums:
        if len(group)<2:continue
        compact=[{'src':p.get('thumbnail',p['src']),'full':p['src'],'alt':p['alt']} for p in group]
        for p in group:
            for key in [p['src'],p.get('thumbnail',p['src'])]:photo_index[key]=compact
    (target/'assets/album-data.js').write_text('window.EBM_ALBUMS='+json.dumps(photo_index,ensure_ascii=False).replace('<','\\u003c')+';')
    products=load('content/products.json')
    gallery_html='<section class="section" id="depot"><div class="wrap"><div class="eyebrow">Notre travail</div><h2>Du dépôt au chantier</h2><p class="intro">Matériaux · Arrivages · Manutention · Pose</p>'+gallery(photos)+'</div></section>'
    schema={'@context':'https://schema.org','@graph':[{'@type':'Organization','@id':BASE+'/#entreprise','name':'El Boussairi Matériaux','url':BASE+'/','telephone':'+212602644454','email':'youssef.materiauxdeconstruction@gmail.com'},{'@type':'WebSite','@id':BASE+'/#site','url':BASE+'/','name':'El Boussairi Matériaux','inLanguage':'fr-MA','publisher':{'@id':BASE+'/#entreprise'}},{'@type':'ImageGallery','name':'Matériaux et travail sur le terrain','url':BASE+'/#depot','inLanguage':'fr','image':[image_schema(p) for p in photos]}]}
    home=read('src/home.html').replace('{{HERO}}',hero()+ticker(market)).replace('{{DEPOT_GALLERY}}',gallery_html).replace('{{FEATURED_PRODUCTS}}',featured(products)).replace('{{REFERENCE_CARDS}}',reference_cards(refs)).replace('{{LATEST_NEWS}}',latest)
    (target/'index.html').write_text(shell('El Boussairi Matériaux | Fourniture & Livraison','Matériaux de construction, approvisionnement et livraison pour vos chantiers à Casablanca et autres destinations selon faisabilité.',home,preview=preview,schema=schema,scripts=['/assets/catalogue.js','/assets/references-data.js','/assets/references.js','/assets/media.js','/assets/motion.js','/assets/shared.js']))
    for product in products:
        folder=target/product['page'].strip('/');folder.mkdir(parents=True,exist_ok=True);(folder/'index.html').write_text(product_page(product,photos,shell,preview))
    articles=load('content/articles.json')
    from editorial import validate_article
    for a in articles:validate_article(a)
    visible=sorted([a for a in articles if a['status']=='published' or preview],key=lambda a:(a['date'],a['id']),reverse=True)
    if not preview:
        for a in visible:
            from editorial import check_approval
            check_approval(a)
    news=target/'actualites';news.mkdir()
    body=editorial_hero(market)+'<section class="section"><div class="wrap" data-news-carousel><div class="blog-tools"><div class="field"><label for="articleKind">À consulter</label><select id="articleKind"><option value="market">Marché & projets</option><option value="activity">Notre activité</option><option value="all">Tout le journal</option></select></div><div class="field"><label for="articleSearch">Rechercher un sujet</label><input id="articleSearch" type="search" placeholder="Ciment, acier, chantier…"></div><div class="field"><label for="articleCategory">Rubrique</label><select id="articleCategory"><option value="">Toutes les rubriques</option>'+''.join('<option>'+esc(c)+'</option>' for c in CATEGORIES)+'</select></div></div><div class="article-status-row"><p class="catalogue-status" id="articleStatus" role="status"></p><button type="button" class="clear-news" id="clearNews">Réinitialiser</button></div>'+news_controls()+'<div class="blog-grid news-track" data-news-track id="articles">'+''.join(article_card(a,preview) for a in visible)+'</div><div class="empty-state" id="articleEmpty"'+(' hidden' if visible else '')+'><h2>Les prochaines actualités se préparent</h2><p>Les articles apparaîtront ici après vérification des sources et validation éditoriale.</p></div></div></section>'
    (news/'index.html').write_text(shell('Zone Industrielle | Matériaux · Chantiers · Industrie','Le journal des matériaux et du BTP au Maroc : ciment, acier, briques, agrégats, chantiers et infrastructures.',ticker([a for a in visible if a.get('kind')!='Notre activité'])+body,'/actualites/',scripts=['/assets/blog.js','/assets/motion.js','/assets/shared.js'],preview=preview))
    for a in visible:
        folder=news/a['slug'];folder.mkdir();(folder/'index.html').write_text(article_page(a,preview))
    from email.utils import format_datetime
    from datetime import datetime, timezone
    items=[]
    for a in visible:
        if a['status']!='published':continue
        u=BASE+'/actualites/'+a['slug']+'/'
        items.append('<item><title>'+esc(a['title'])+'</title><link>'+u+'</link><guid>'+u+'</guid><description>'+esc(a['summary'])+'</description><pubDate>'+format_datetime(datetime.fromisoformat(a['date']).replace(tzinfo=timezone.utc))+'</pubDate></item>')
    (news/'feed.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Zone Industrielle — Matériaux &amp; BTP</title><link>'+BASE+'/actualites/</link><description>Actualités sourcées du secteur au Maroc</description>'+''.join(items)+'</channel></rss>')
    policy_dir=news/'confidentialite';policy_dir.mkdir()
    (policy_dir/'index.html').write_text(shell('Vos données | Zone Industrielle','Vos choix et vos données personnelles.',privacy(),'/actualites/confidentialite/',scripts=['/assets/shared.js'],preview=preview))
    server_dir=ROOT/'server';server_dir.mkdir(exist_ok=True)
    (server_dir/'articles.json').write_text(json.dumps([a['slug'] for a in published]))
    links=['/','/actualites/','/actualites/confidentialite/']+[p['page'] for p in products]+['/actualites/'+a['slug']+'/' for a in visible if a['status']=='published']
    (target/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'+''.join('<url><loc>'+BASE+x+'</loc>'+(''.join('<image:image><image:loc>'+BASE+p['src']+'</image:loc></image:image>' for p in photos if x=='/' or p.get('product')==x.strip('/').split('/')[-1]) if x=='/' or x.startswith('/materiaux/') else '')+'</url>' for x in links)+'</urlset>')
    (target/'robots.txt').write_text('User-agent: *\nDisallow: /\n' if preview else 'User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n')
    (target/'404.html').write_text(shell('Page introuvable | El Boussairi Matériaux','Page introuvable.','<section class="section"><div class="wrap"><h1>Cette page est introuvable.</h1><a class="btn" href="/">Retour à l’accueil</a></div></section>',preview=preview))
    hashes=set()
    for page in target.rglob('*.html'):
        for script in re.findall(r'<script type="application/ld\+json">(.*?)</script>',page.read_text(),re.S):
            hashes.add("'sha256-"+base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()+"'")
    policy="default-src 'self'; script-src 'self' "+' '.join(sorted(hashes))+"; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; upgrade-insecure-requests"
    (target/'_headers').write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()\n  X-Frame-Options: DENY\n  Strict-Transport-Security: max-age=31536000\n  Cross-Origin-Resource-Policy: same-origin\n  Cross-Origin-Opener-Policy: same-origin\n  Content-Security-Policy: "+policy+"\n/assets/depot/*\n  Cache-Control: public, max-age=86400, must-revalidate\n  X-Robots-Tag: max-image-preview:large\n")
    print('Built',target,'PREVIEW' if preview else 'PRODUCTION ARTIFACT ONLY','|',len(visible),'articles |',len(refs),'références')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--out',default='dist');args=parser.parse_args();build(args.preview,args.out)
