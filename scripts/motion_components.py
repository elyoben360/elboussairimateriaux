import html

def esc(s):return html.escape(str(s),quote=True)
def background_slides(slides):
    out='<div class="hero-slides" aria-hidden="true">'
    for i,s in enumerate(slides):
        out+='<img class="hero-background hero-slide'+(' is-active' if i==0 else '')+'" src="'+esc(s['src'])+'" width="'+str(s['width'])+'" height="'+str(s['height'])+'" alt="" data-caption="'+esc(s['caption'])+'" data-url="'+esc(s['url'])+'" data-credit="'+esc(s.get('credit',''))+'" '+('fetchpriority="high"' if not i else 'loading="lazy"')+' decoding="async">'
    return out+'</div>'
def rotation_controls():
    return '<div class="hero-controls"><span class="rotation-progress" aria-hidden="true"><span></span></span></div>'
def hero():
    slides=[dict(src=src,width=w,height=h,caption='© El Boussairi Matériaux · '+caption+' ↗',url=url) for src,w,h,caption,url in [('/assets/references/ain-diab/04.webp',1440,939,'Livraison au camion-grue · Aïn Diab','/#references'),('/assets/depot/stock-ciment-holcim.webp',1440,810,'Ciment sur palettes · Notre dépôt','/#depot'),('/assets/depot/arrivage-madriers-coffrage.webp',808,1440,'Arrivage de madriers · Bois de coffrage','/?produit=madriers#catalogue'),('/assets/depot/panneaux-muraux-stock-10cm.webp',960,1280,'Panneaux muraux · Stock et pose','/materiaux/panneaux-muraux/')]]
    return '<section class="hero hero-photo" data-hero data-image-rotation aria-label="Notre activité en images">'+background_slides(slides)+'<div class="wrap hero-content"><div class="eyebrow">Gros œuvre · Second œuvre · Logistique</div><h1>Vos matériaux. Votre livraison. Un seul interlocuteur.</h1><p>Matériaux de construction · Préparation des commandes · Livraison chantier</p><div class="actions"><a class="btn" href="#catalogue">Choisir mes matériaux</a><a class="btn outline" href="#depot">Notre travail en images</a></div><a class="hero-credit" data-rotation-caption href="'+esc(slides[0]['url'])+'">'+esc(slides[0]['caption'])+'</a>'+rotation_controls()+'</div></section>'
def editorial_hero(articles):
    # Only published article photographs, deduplicated on every build.
    slides=[];seen=set()
    for a in articles:
        if a['status']!='published' or not a.get('cover') or a['cover'] in seen:continue
        seen.add(a['cover'])
        slides.append(dict(src=a['cover'],width=a.get('cover_width',1200),height=a.get('cover_height',630),caption='À lire : '+a['title']+' ↗',url='/actualites/'+a['slug']+'/',credit=a.get('cover_credit','')))
    out='<section class="editorial-hero"'+(' data-image-rotation' if slides else '')+'>'+background_slides(slides)+'<div class="wrap hero-content"><div class="eyebrow">Le journal</div><h1>Actualités & Marché du BTP</h1><p>Matériaux, chantiers et transport de marchandises au Maroc. Des faits vérifiés, leurs sources et des images adaptées à chaque sujet.</p>'
    if slides:out+='<a class="hero-credit" data-rotation-caption href="'+esc(slides[0]['url'])+'">'+esc(slides[0]['caption'])+'</a><small class="editorial-image-credit" data-rotation-credit>'+esc(slides[0]['credit'])+'</small>'+rotation_controls()
    return out+'</div></section>'
def ticker(articles):
    if not articles:return ''
    return '<section class="news-ticker" data-ticker aria-label="Les titres du journal"><div class="wrap ticker-layout"><span class="ticker-label">Le journal</span><div class="ticker-window"><div class="ticker-line"><div class="ticker-set">'+''.join('<a href="/actualites/'+a['slug']+'/"><img src="'+esc(a['cover'])+'" alt="" width="60" height="44" loading="lazy"><span>'+esc(a['title'])+'</span><span aria-hidden="true">↗</span></a>' for a in articles[:8])+'</div></div></div></div></section>'
def news_controls():
    return '<div class="news-controls"><button type="button" class="gallery-arrow" data-news-prev aria-label="Article précédent">‹</button><button type="button" class="gallery-arrow" data-news-next aria-label="Article suivant">›</button></div>'
