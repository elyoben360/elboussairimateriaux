#!/usr/bin/env python3
"""Render exact editorial text into brand-consistent JPEG slides; never posts online."""
from pathlib import Path
import argparse,json,textwrap
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def wrap(draw,text,font,width):
    lines=[]
    for para in text.split('\n'):
        line=''
        for word in para.split():
            trial=(line+' '+word).strip()
            if draw.textlength(trial,font=font)>width and line:lines.append(line);line=word
            else:line=trial
        lines.append(line)
    return lines
def render(a,out):
    out.mkdir(parents=True,exist_ok=True)
    for i,s in enumerate(a['instagram']['slides'],1):
        im=Image.new('RGB',(1080,1350),'#172f59');d=ImageDraw.Draw(im)
        d.rectangle((760,180,1000,1120),fill='#203d68');d.rectangle((630,600,735,1120),fill='#284572');d.line((80,190,410,190),fill='#ac8754',width=5)
        d.text((80,65),'BANANA',font=ImageFont.truetype(SERIF,36),fill='white');d.text((80,112),'MATÉRIAUX',font=ImageFont.truetype(SANS,23),fill='#d7b988')
        d.text((80,235),'LE JOURNAL BTP · MAROC',font=ImageFont.truetype(SANS,23),fill='#d7b988')
        font=ImageFont.truetype(SERIF,66)
        while len(wrap(d,s['title'],font,900))>4:font=ImageFont.truetype(SERIF,font.size-2)
        y=340
        for line in wrap(d,s['title'],font,900):d.text((80,y),line,font=font,fill='white');y+=font.size+23
        y+=36;font=ImageFont.truetype(SANS,34)
        for line in wrap(d,s['text'],font,850):d.text((80,y),line,font=font,fill='#e2e8f1');y+=55
        if y>1130:raise ValueError('Slide text overflow')
        d.line((80,1190,1000,1190),fill='#ac8754',width=2);d.text((80,1220),'BROUILLON · NON PUBLIÉ',font=ImageFont.truetype(SANS,20),fill='#d7b988');d.text((930,1220),f'{i}/{len(a["instagram"]["slides"])}',font=ImageFont.truetype(SANS,24),fill='white')
        im.save(out/f'{i:02}.jpg',quality=90,optimize=True)
    (out/'legende.txt').write_text(a['instagram']['caption']);(out/'dossier.json').write_text(json.dumps({'article_id':a['id'],'status':a['status'],'instagram':a['instagram'],'publish':False},ensure_ascii=False,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--article',required=True);p.add_argument('--out',required=True);args=p.parse_args();a=next(x for x in json.loads((ROOT/'content/articles.json').read_text()) if x['id']==args.article);render(a,Path(args.out))
