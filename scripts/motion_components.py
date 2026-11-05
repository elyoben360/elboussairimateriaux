import html
from journal import masthead

def esc(s):return html.escape(str(s),quote=True)
def background_slides(slides):
    out='<div class="hero-slides" aria-hidden="true">'
    for i,s in enumerate(slides):
        out+='<img class="hero-background hero-slide'+(' is-active' if i==0 else '')+'" src="'+esc(s['src'])+'" width="'+str(s['width'])+'" height="'+str(s['height'])+'" alt="" data-caption="'+esc(s['caption'])+'" data-url="'+esc(s['url'])+'" data-credit="'+esc(s.get('credit',''))+'" '+('fetchpriority="high"' if not i else 'loading="lazy"')+' decoding="async">'
    return out+'</div>'
def rotation_controls():
    return '<div class="hero-controls"><span class="rotation-progress" aria-hidden="true"><span></span></span></div>'
def hero():
    slides=[dict(src=src,width=w,height=h,caption='© Banana Matériaux · '+caption+' ↗',url=url) for src,w,h,caption,url in [('/assets/references/ain-diab/04.webp',1440,939,'Livraison au camion-grue · Aïn Diab','/#references'),('/assets/depot/stock-ciment-holcim.webp',1440,810,'Ciment sur palettes · Notre dépôt','/#depot'),('/assets/depot/arrivage-madriers-coffrage.webp',808,1440,'Arrivage de madriers · Bois de coffrage','/?produit=madriers#catalogue'),('/assets/depot/panneaux-muraux-stock-10cm.webp',960,1280,'Panneaux muraux · Stock et pose','/materiaux/panneaux-muraux/')]]
    return '<section class="hero hero-photo" data-hero data-image-rotation aria-label="Notre activité en images">'+background_slides(slides)+'<div class="wrap hero-content"><div class="eyebrow">Gros œuvre · Second œuvre · Logistique</div><h1>Vos matériaux. Votre livraison. Un seul interlocuteur.</h1><p>Matériaux de construction · Préparation des commandes · Livraison chantier</p><div class="actions"><a class="btn" href="#catalogue">Choisir mes matériaux</a><a class="btn outline" href="#depot">Notre travail en images</a></div><a class="hero-credit" data-rotation-caption href="'+esc(slides[0]['url'])+'">'+esc(slides[0]['caption'])+'</a>'+rotation_controls()+'</div></section>'
def editorial_hero(articles):
    from datetime import date
    topics=[('','Tout'),('Ciment et béton','Ciment & béton'),('Acier et fer à béton','Acier'),('Nouveaux chantiers','Chantiers'),('Investissements et infrastructures','Infrastructures'),('Évolution des prix','Prix & marchés'),('Transport de marchandises et logistique','Logistique')]
    rubrics='<nav class="zi-rubrics" id="zi-rubriques" aria-label="Rubriques du journal">'+''.join('<button type="button" aria-pressed="'+('true' if not value else 'false')+'" data-zi-category="'+esc(value)+'">'+label+'</button>' for value,label in topics)+'</nav>'
    lead=''
    if articles:
        a=articles[0];url='/actualites/'+esc(a['slug'])+'/'
        lead='<div class="zi-front"><article class="zi-feature"><a class="zi-feature-photo" href="'+url+'"><img src="'+esc(a['cover'])+'" alt="'+esc(a.get('cover_alt','Illustration éditoriale'))+'" width="1200" height="630" fetchpriority="high"><span>À LA UNE</span></a><div class="zi-feature-copy"><span class="zi-kicker">'+esc(a['category'])+'</span><h2><a href="'+url+'">'+esc(a['title'])+'</a></h2><p>'+esc(a['summary'])+'</p><a class="zi-read" href="'+url+'">Lire le décryptage ↗</a><details class="zi-photo-info"><summary>À propos de la photo</summary><p>'+esc(a.get('cover_caption',''))+' · '+esc(a.get('cover_credit',''))+'</p></details></div></article><aside class="zi-brief"><span class="zi-kicker">LE FIL DU JOURNAL</span>'+''.join('<a href="/actualites/'+esc(b['slug'])+'/"><img src="'+esc(b['cover'])+'" alt="" width="80" height="80" loading="lazy"><span><small>'+esc(b['category'])+'</small><strong>'+esc(b['title'])+'</strong></span><span aria-hidden="true">↗</span></a>' for b in articles[1:4])+'<a class="zi-all" href="#journal-explorer">Toutes les actualités ↓</a></aside></div>'
    edition=max((a['date'] for a in articles),default=date.today().isoformat())
    return '<section class="zi-hero"><div class="wrap"><div class="zi-edition"><span><i></i> LE MAROC QUI SE CONSTRUIT</span><time datetime="'+edition+'">Édition du '+edition[8:10]+'/'+edition[5:7]+'/'+edition[:4]+'</time></div><div class="zi-intro"><h1>Le regard sur le terrain.</h1><p>Matériaux, marchés et chantiers. L’essentiel pour avancer.</p></div>'+lead+rubrics+'</div></section>'
def ticker(articles):
    if not articles:return ''
    return '<section class="news-ticker" data-ticker aria-label="Les titres du journal"><div class="wrap ticker-layout"><span class="ticker-label">Le journal</span><div class="ticker-window"><div class="ticker-line"><div class="ticker-set">'+''.join('<a href="/actualites/'+a['slug']+'/"><img src="'+esc(a['cover'])+'" alt="" width="60" height="44" loading="lazy"><span>'+esc(a['title'])+'</span><span aria-hidden="true">↗</span></a>' for a in articles[:8])+'</div></div></div></div></section>'
def news_controls():
    return '<div class="news-controls"><button type="button" class="gallery-arrow" data-news-prev aria-label="Article précédent">‹</button><button type="button" class="gallery-arrow" data-news-next aria-label="Article suivant">›</button></div>'
