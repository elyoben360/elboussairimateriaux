#!/usr/bin/env python3
"""Render real-photo editorial carousels. No external publish or generated imagery."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/instagram';OUT.mkdir(exist_ok=True)
N='#071d39';O='#ff6500';C='#f7f3e9';M='#aabccc'
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
def font(n,b=False,serif=False):return ImageFont.truetype(SERIF if serif else BOLD if b else SANS,n)
def lines(d,text,f,width):
    result=[];line=''
    for word in text.split():
        trial=(line+' '+word).strip()
        if d.textlength(trial,font=f)>width and line:result.append(line);line=word
        else:line=trial
    if line:result.append(line)
    return result

def text(d,value,xy,width,size,fill,bold=False,serif=False,leading=1.22):
    x,y=xy;f=font(size,bold,serif)
    for line in lines(d,value,f,width):d.text((x,y),line,font=f,fill=fill);y+=round(size*leading)
    return y

def render(post,slide,i):
    im=Image.new('RGB',(1080,1350),N);d=ImageDraw.Draw(im)
    logo=Image.open(ROOT/'assets/zone-industrielle-logo.webp').convert('RGB');logo=ImageOps.fit(logo,(78,78));im.paste(logo,(52,34))
    d.text((154,42),'ZONE INDUSTRIELLE',font=font(23,True),fill=C);d.text((154,80),'LE JOURNAL · MAROC',font=font(15),fill=O)
    d.text((936,61),f'{i+1:02d} / 04',font=font(17),fill=M)
    photo=Image.open(ROOT/slide['photo'].lstrip('/')).convert('RGB');photo=ImageOps.fit(photo,(1080,460),centering=(.5,.45));im.paste(photo,(0,150))
    d.rectangle((0,602,1080,610),fill=O)
    d.rounded_rectangle((52,574,52+int(d.textlength(post['series'].upper(),font=font(17,True)))+36,620),radius=4,fill=O)
    d.text((70,584),post['series'].upper(),font=font(17,True),fill=N)
    d.text((54,646),post.get('photo_notice','PHOTOGRAPHIE DE NOTRE ACTIVITÉ · © BANANA MATÉRIAUX'),font=font(13),fill=M)
    size=64
    while len(lines(d,slide['title'],font(size,serif=True),968))>3 and size>45:size-=2
    y=text(d,slide['title'],(54,696),968,size,C,serif=True,leading=1.12)
    y=text(d,slide['body'],(56,y+26),944,29,M,leading=1.4)
    if y>1160:raise ValueError('Text exceeds safe area: '+post['id'])
    d.line((54,1194,1026,1194),fill='#31465e',width=2)
    d.text((56,1220),post.get('footer_cta','ENREGISTREZ CE CONSEIL') if i<3 else post.get('final_cta','LIRE LE JOURNAL · LIEN EN BIO'),font=font(19,True),fill=O)
    d.text((56,1264),'bananamateriaux.ma',font=font(18),fill=C)
    d.text((946,1258),'→',font=font(38),fill=O)
    path=OUT/post['id']/f'{i+1:02d}.jpg';path.parent.mkdir(exist_ok=True);im.save(path,quality=93,optimize=True,exif=b'')
    return '/assets/instagram/'+post['id']+'/'+path.name

if __name__=='__main__':
    data=json.loads((ROOT/'content/instagram-queue.json').read_text())
    for p in data['posts']:
        p['images']=[render(p,s,i) for i,s in enumerate(p['slides'])]
        p['content_hash']=hashlib.sha256(json.dumps({'caption':p['caption'],'slides':p['slides']},ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    (ROOT/'content/instagram-queue.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    # Public export contains only reusable content, never credentials or account data.
    (OUT/'pack.json').write_text(json.dumps({'posts':[{k:p[k] for k in ['id','title','caption','images','content_hash']} for p in data['posts']]},ensure_ascii=False,indent=2)+'\n')
    thumbs=[]
    for p in data['posts']:
        img=Image.open(ROOT/p['images'][0].lstrip('/'));thumbs.append(ImageOps.fit(img,(270,338)))
    contact=Image.new('RGB',(270*5,338),N)
    for i,im in enumerate(thumbs):contact.paste(im,(i*270,0))
    contact.save(OUT/'apercu.jpg',quality=92)
    print('Rendered',len(data['posts']),'carousels; publication not performed.')
