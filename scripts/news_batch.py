#!/usr/bin/env python3
"""Accept researched news under the owner's standing site-publication policy.
This validates evidence metadata; the scheduled researcher must read the sources.
No generated credentials, network calls, or Instagram publication occur here.
"""
import argparse,copy,json,re
from datetime import datetime,date
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit
from editorial import validate_article,digest
ROOT=Path(__file__).resolve().parents[1]
def canonical(url):
    p=urlsplit(url)
    if p.scheme!='https' or not p.hostname or p.username or p.password:raise ValueError('Source HTTPS publique requise')
    return urlunsplit(('https',p.netloc.lower(),p.path.rstrip('/'),'',''))
def matches(host,domains):return any(host==d or host.endswith('.'+d) for d in domains)
def accept(existing,batch,policy,today):
    if not policy.get('automatic_site_publication'):raise ValueError('Publication automatique non autorisée')
    if len(batch)>policy.get('max_articles_per_run',len(batch)):raise ValueError('Limite par passage dépassée')
    current=copy.deepcopy(existing);seen={canonical(s['url']) for a in current for s in a['sources']};slugs={a['slug'] for a in current};ids={a['id'] for a in current}
    count=sum(a['date']==today.isoformat() and a['status']=='published' for a in current)
    if count+len(batch)>policy['max_articles_per_day']:raise ValueError('Limite quotidienne dépassée')
    for incoming in batch:
        a=copy.deepcopy(incoming);validate_article(a)
        if a['slug'] in slugs or a['id'] in ids:raise ValueError('Article déjà présent')
        v=a.get('verification',{})
        if v.get('checked_on')!=today.isoformat() or not v.get('facts_checked') or not v.get('date_checked') or not v.get('evidence'):raise ValueError('Sources et dates à vérifier aujourd’hui')
        if a.get('category') not in policy['categories']:raise ValueError('Rubrique hors périmètre')
        if not a.get('event_period'):raise ValueError('Période des faits obligatoire')
        if not a['sources']:raise ValueError('Actualité sans sources')
        primary=False;dates=[];new_urls=[]
        for s in a['sources']:
            u=canonical(s['url']);host=urlsplit(u).hostname
            if u in seen:raise ValueError('Source ou sujet déjà publié')
            is_primary=matches(host,policy['primary_domains']);primary|=is_primary
            if not is_primary and not matches(host,policy['press_domains']):raise ValueError('Éditeur hors liste de confiance')
            d=date.fromisoformat(s['date'])
            if d>today:raise ValueError('Source datée dans le futur')
            dates.append(d);new_urls.append(u)
        if not primary and len(set(urlsplit(u).hostname for u in new_urls))<2:raise ValueError('Deux éditeurs indépendants requis en l’absence de source primaire')
        if (today-max(dates)).days>policy['max_source_age_days']:raise ValueError('Information trop ancienne pour le fil récent')
        if not (ROOT/a['cover'].lstrip('/')).is_file() or not a['cover'].startswith('/assets/'):raise ValueError('Illustration locale requise')
        a['date']=today.isoformat();a['kind']='Actualité';a['verified']=True;a['status']='published';a.pop('approvals',None)
        a['approvals']={'site':{'approved_by':'Publication automatique — politique autorisée le '+policy['authorization_date'],'evidence':policy['authorization']+' Vérification documentaire : '+v['evidence'],'digest':digest(a)}}
        current.append(a);slugs.add(a['slug']);ids.add(a['id']);seen.update(new_urls)
    return current
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);args=p.parse_args()
    from build import CATEGORIES
    policy=json.loads((ROOT/'content/editorial-policy.json').read_text());policy['categories']=CATEGORIES
    today=datetime.now(ZoneInfo(policy['timezone'])).date()
    old=json.loads((ROOT/'content/articles.json').read_text());batch=json.loads(Path(args.batch).read_text())
    new=accept(old,batch,policy,today)
    (ROOT/'content/articles.json').write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n')
    print('Accepted',len(new)-len(old),'sourced site articles; Instagram disabled.')
