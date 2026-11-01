"""Public product pages and a progressively enhanced photo gallery."""
import html,json
BASE='https://elboussairimateriaux.com'
def esc(s):return html.escape(str(s),quote=True)
def photo_markup(p,album=None,index=0):
    data=''
    if album:
        data=' data-photo-images="'+esc(json.dumps([{'src':x['src'],'alt':x['alt']} for x in album],ensure_ascii=False))+'" data-photo-index="'+str(index)+'"'
    return '<a class="media-visual" data-zoom'+data+' href="'+esc(p['src'])+'" aria-label="Agrandir : '+esc(p['title'])+'"><img src="'+esc(p['thumbnail'])+'" srcset="'+esc(p['thumbnail'])+' 560w, '+esc(p['src'])+' '+str(p['width'])+'w" sizes="(max-width:600px) 100vw, (max-width:960px) 50vw, 33vw" alt="'+esc(p['alt'])+'" width="'+str(p['width'])+'" height="'+str(p['height'])+'" loading="lazy" decoding="async"><span class="photo-credit" aria-hidden="true">© El Boussairi Matériaux</span><span class="photo-expand" aria-hidden="true">'+(str(len(album))+' photos ↗' if album and len(album)>1 else 'Agrandir ↗')+'</span></a>'
def album_key(p):
    if p.get('product'):return p['product']
    if p['id'] in ['palette-sacs-depot','sacs-papier-depot']:return 'conditionnement'
    if p['id'] in ['chargement-panneaux-blancs','panneaux-blancs-depot']:return 'panneaux-emballes'
    return p['id']
def albums(photos):
    groups={}
    for photo in photos:groups.setdefault(album_key(photo),[]).append(photo)
    order=['panneaux-muraux','fer-a-beton']
    return dict(sorted(groups.items(),key=lambda item:order.index(item[0]) if item[0] in order else len(order)))
ALBUM_TITLES={'panneaux-muraux':'Panneaux muraux : stock et pose','fer-a-beton':'Fer à béton : arrivage en fardeaux','madriers':'Madriers de coffrage','treillis-soudes':'Treillis soudés','ciments-colles':'Colles pour carrelage','pointes':'Pointes JP08 et JP10','polystyrene':'Polystyrène · 2 et 4 cm','conditionnement':'Conditionnement en sacs','panneaux-emballes':'Panneaux emballés'}
def gallery(photos,filtering=True):
    grouped=albums(photos)
    out='<div data-gallery>'
    if filtering:
        groups=list(dict.fromkeys(p['group'] for p in photos))
        out+='<div class="gallery-tools"><div class="field"><label for="photo-filter">Photos par thème</label><select id="photo-filter" data-photo-filter><option value="">Toutes les galeries</option>'+''.join('<option>'+esc(g)+'</option>' for g in groups)+'</select></div><p class="hint" data-photo-status role="status" aria-live="polite">'+str(len(grouped))+' galeries · '+str(len(photos))+' photos</p></div>'
    out+='<div class="depot-grid">'
    for key,pics in grouped.items():
        p=pics[0];product=p.get('product','');url='/materiaux/'+product+'/' if product in ['panneaux-muraux','fer-a-beton'] else '/?produit='+product+'#catalogue'
        out+='<figure class="depot-card" data-photo-group="'+esc('Autres' if key=='panneaux-emballes' else p['group'])+'" data-photo-count="'+str(len(pics))+'">'+photo_markup(p,pics)+'<figcaption><span class="tag">'+esc(p['category'])+'</span><h3>'+esc(ALBUM_TITLES.get(key,p['title']))+'</h3>'+('<a class="text-action" data-product="'+esc(product)+'" href="'+esc(url)+'">'+('Voir la fiche' if product in ['panneaux-muraux','fer-a-beton'] else 'Choisir ce matériau')+' →</a>' if product else '')+'</figcaption></figure>'
    out+='</div>'
    if filtering:out+='<button class="btn outline more-photos" type="button" data-photo-more hidden>Voir plus de galeries</button>'
    return out+'</div>'
def image_schema(p):
    return {'@type':'ImageObject','contentUrl':BASE+p['src'],'thumbnailUrl':BASE+p['thumbnail'],'name':p['title'],'description':p['alt'],'caption':p['caption'],'width':p['width'],'height':p['height'],'encodingFormat':p['encodingFormat'],'creditText':p['creditText'],'copyrightNotice':p['copyrightNotice'],'license':p['license'],'acquireLicensePage':p['acquireLicensePage'],'creator':{'@type':'Organization','name':'El Boussairi Matériaux'},'keywords':', '.join(p['keywords'])}
def featured(products):
    out='<section class="section featured-products" id="selection"><div class="wrap"><div class="section-heading"><div><div class="eyebrow">Notre sélection</div><h2>Des matériaux à découvrir</h2></div><a class="text-action" href="#catalogue">Tout le catalogue →</a></div><div class="featured-grid">'
    for p in products:
        out+='<article class="product-card"><a class="media-visual" href="'+p['page']+'"><img src="'+p['image']+'" width="560" height="747" alt="'+esc(p['product'])+'" loading="lazy" decoding="async"><span class="photo-credit">© El Boussairi Matériaux</span></a><div class="product-card-body"><span class="tag">'+esc(p['family'])+'</span><h3><a href="'+p['page']+'">'+esc(p['title'])+'</a></h3><ul class="product-facts">'+''.join('<li>'+esc(x)+'</li>' for x in p['facts'][:3])+'</ul><div class="actions"><a class="btn outline" href="'+p['page']+'">Voir la fiche</a><a class="btn" data-choose-product="'+p['slug']+'" href="/?produit='+p['slug']+'#catalogue">Choisir</a></div></div></article>'
    return out+'</div></div></section>'
def product_page(p,photos,shell,preview=False):
    pics=[next(x for x in photos if x['id']==key) for key in p['photos']]
    body='<section class="section"><div class="wrap"><nav class="breadcrumbs" aria-label="Fil d’Ariane"><a href="/">Accueil</a><span>›</span><a href="/#catalogue">Matériaux</a><span>›</span><span>'+esc(p['product'])+'</span></nav><div class="product-layout"><div class="product-main-image">'+photo_markup(pics[0],pics)+'<div class="product-thumbnails">'+''.join(photo_markup(photo,pics,i) for i,photo in enumerate(pics) if i)+'</div></div><div><div class="eyebrow">'+esc(p['family'])+'</div><h1>'+esc(p['title'])+'</h1><p class="intro">'+esc(p['description'])+'</p><ul class="product-facts">'+''.join('<li>'+esc(x)+'</li>' for x in p['facts'])+'</ul>'+('<p class="hint">'+esc(p['note'])+'</p>' if p.get('note') else '')+'<div class="actions"><a class="btn" href="/?produit='+p['slug']+'#catalogue">Choisir ma référence</a><a class="btn outline" href="tel:+212602644454">Appeler</a></div><p class="hint">Tarif et disponibilité confirmés à la demande.</p></div></div><div class="actions"><a class="btn outline" href="/#catalogue">Retour au catalogue</a></div></div></section>'
    schema={'@context':'https://schema.org','@graph':[{'@type':'Product','name':p['title'],'url':BASE+p['page'],'description':p['meta'],'image':[BASE+x['src'] for x in pics],'category':p['family'],'additionalProperty':[{'@type':'PropertyValue','name':'Caractéristique','value':x} for x in p['facts']]},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Accueil','item':BASE+'/'},{'@type':'ListItem','position':2,'name':p['product'],'item':BASE+p['page']}]},*[image_schema(x) for x in pics]]}
    return shell(p['title']+' | El Boussairi Matériaux',p['meta'],body,p['page'],scripts=['/assets/media.js','/assets/shared.js'],preview=preview,schema=schema,social_image=pics[0])
