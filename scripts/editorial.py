#!/usr/bin/env python3
"""File-based editorial workflow; no external publication capability and no credentials."""
import argparse,copy,hashlib,json,re
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
STATES=['proposed','selected','writing','review','approved','published']
def validate_article(a):
    required=['id','slug','status','title','summary','category','date','cover','sections','sources','instagram']
    if any(k not in a for k in required):raise ValueError('Article incomplet')
    if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',a['slug']):raise ValueError('Slug invalide')
    if a['status'] not in STATES:raise ValueError('Statut invalide')
    if date.fromisoformat(a['date'])>date.today():raise ValueError('Date future interdite')
    if not a['title'].strip() or not a['sections']:raise ValueError('Contenu vide')
    for s in a['sources']:
        if not re.fullmatch(r'https://[^\s<>"\x00-\x20]+',s['url']):raise ValueError('Source HTTPS invalide')
        date.fromisoformat(s['date'])
    slides=a['instagram']['slides']
    if not 4<=len(slides)<=6:raise ValueError('Prévoir 4 à 6 diapositives')
    if slides[-1]['title']!="Lire l'article complet — lien en bio":raise ValueError('Dernière diapositive incorrecte')
    return True
def digest(a):
    payload={k:v for k,v in a.items() if k not in ['status','approvals']}
    return hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def check_approval(a,target='site'):
    validate_article(a)
    approval=a.get('approvals',{}).get(target,{})
    if not a.get('verified') or not approval.get('approved_by') or not approval.get('evidence') or approval.get('digest')!=digest(a):raise ValueError('Validation explicite et vérification requises pour '+target)
    if a.get('kind','')=='Actualité' and not a['sources']:raise ValueError('Actualité sans sources')
    return True
def transition(a,new_status,approval=None,target='site'):
    a=copy.deepcopy(a);validate_article(a)
    if new_status not in STATES:raise ValueError('Statut inconnu')
    if STATES.index(new_status)!=STATES.index(a['status'])+1:raise ValueError('Étape de validation manquante')
    if new_status=='approved':
        if approval:a.setdefault('approvals',{})[target]=approval
        check_approval(a,target)
    if new_status=='published':check_approval(a,target)
    a['status']=new_status;return a
def release_payload(a,target='site'):
    check_approval(a,target)
    return {'target':target,'article_id':a['id'],'digest':digest(a),'mode':'reviewed-export-only','content':a}
def meta_payload(a,image_urls):
    check_approval(a,'instagram')
    if len(image_urls)!=len(a['instagram']['slides']):raise ValueError('Nombre de visuels incorrect')
    if any(not re.fullmatch(r'https://[^\s<>"\x00-\x20]+\.jpe?g(?:\?[^\s]*)?',u) for u in image_urls):raise ValueError('Images JPEG HTTPS requises')
    return {'children':[{'image_url':u,'is_carousel_item':True} for u in image_urls],'parent':{'media_type':'CAROUSEL','caption':a['instagram']['caption']},'publish':False}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['validate','export']);p.add_argument('--article',required=True);p.add_argument('--target',choices=['site','instagram'],default='site');p.add_argument('--out');args=p.parse_args();articles=json.loads((ROOT/'content/articles.json').read_text());a=next(x for x in articles if x['id']==args.article)
    if args.command=='validate':validate_article(a);print('Structure valide. Statut:',a['status'],'· empreinte:',digest(a))
    else:
        if not args.out:p.error('--out requis')
        Path(args.out).write_text(json.dumps(release_payload(a,args.target),ensure_ascii=False,indent=2));print('Export validé uniquement. Aucune publication réseau.')
