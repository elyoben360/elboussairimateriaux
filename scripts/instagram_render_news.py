#!/usr/bin/env python3
"""Compose real photographs and exact editorial text; no social network calls."""
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
NAVY, ORANGE, CREAM = '#071d39', '#ff6500', '#f7f3e9'
FONT = '/usr/share/fonts/truetype/dejavu/'

def font(size, bold=False, serif=False):
    return ImageFont.truetype(FONT + ('DejaVuSerif.ttf' if serif else
        'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), size)

def wrap(draw, value, f, width):
    lines, line = [], ''
    for word in value.split():
        trial = (line + ' ' + word).strip()
        if line and draw.textlength(trial, font=f) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines

def block(draw, value, x, y, width, size, fill, bold=False, serif=False,
          max_lines=None, minimum=38):
    while True:
        f = font(size, bold, serif)
        lines = wrap(draw, value, f, width)
        if not max_lines or len(lines) <= max_lines:
            break
        size -= 2
        if size < minimum:
            raise ValueError('Text cannot fit: ' + value)
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += round(size * 1.21)
    return y

def photo(im, slide, box):
    with Image.open(ROOT / slide['photo'].lstrip('/')) as source:
        view = ImageOps.fit(source.convert('RGB'),
            (box[2] - box[0], box[3] - box[1]), centering=(.5, .5))
        im.paste(view, box[:2])

def render(post, slide, index):
    style = (post['layout'] + index) % 3
    light = style == 1
    bg, ink, muted = (CREAM, NAVY, '#405269') if light else (NAVY, CREAM, '#c1ccda')
    im = Image.new('RGB', (1080, 1350), bg)
    draw = ImageDraw.Draw(im)
    with Image.open(ROOT / 'assets/zone-industrielle-logo.webp') as logo:
        im.paste(ImageOps.fit(logo.convert('RGB'), (86, 86)), (54, 34))
    draw.text((164, 42), 'ZONE INDUSTRIELLE', font=font(27, True), fill=ink)
    draw.text((164, 84), 'LE JOURNAL · MAROC', font=font(21), fill=ORANGE)
    draw.text((916, 54), f'{index+1:02d}/{len(post["slides"]):02d}', font=font(25), fill=ink)
    draw.line((54, 141, 1026, 141), fill=ORANGE, width=5)
    if style == 0:
        photo(im, slide, (0, 166, 1080, 587))
        y = block(draw, slide['photo_notice'], 54, 604, 972, 24, muted, max_lines=2, minimum=24)
        y = block(draw, slide['credit_short'], 54, y+4, 972, 24, muted, max_lines=2, minimum=24)
        draw.text((54, 726), post['series'].upper(), font=font(23, True), fill=ORANGE)
        y = block(draw, slide['title'], 54, 774, 972, 62, ink, serif=True, max_lines=3, minimum=50)
        y = block(draw, slide['body'], 54, y+22, 972, 38, muted)
        if y > 1178:
            raise ValueError('Body overflows: '+post['id']+' '+str(index))
    else:
        draw.text((54, 179), post['series'].upper(), font=font(23, True), fill=ORANGE)
        y = block(draw, slide['title'], 54, 228, 972, 62, ink, serif=True, max_lines=3, minimum=50)
        y = block(draw, slide['body'], 54, y+22, 972, 38, muted)
        if y > 663:
            raise ValueError('Text/photo overlap: '+post['id']+' '+str(index))
        photo(im, slide, (54, 682, 1026, 1038))
        draw.rectangle((54, 1038, 1026, 1045), fill=ORANGE)
        y = block(draw, slide['photo_notice'], 54, 1063, 972, 24, muted, max_lines=2, minimum=24)
        y = block(draw, slide['credit_short'], 54, y+4, 972, 24, muted, max_lines=2, minimum=24)
        if y > 1180:
            raise ValueError('Credit overflows: '+post['id'])
    draw.line((54, 1194, 1026, 1194), fill='#8996a7', width=1)
    draw.text((54, 1211), 'LIRE L’ARTICLE · LIEN EN BIO' if index == len(post['slides'])-1
        else 'ZONE INDUSTRIELLE · 4 NOVEMBRE 2026', font=font(25, True), fill=ORANGE)
    draw.text((54, 1250), post['source_short'], font=font(21), fill=ink)
    draw.text((54, 1283), 'creativecommons.org/licenses/by-sa/4.0/' if post.get('artwork_license')
        else 'elboussairimateriaux.com/actualites/', font=font(22), fill=muted)
    out = ROOT / 'assets/instagram' / post['id'] / f'{index+1:02d}.jpg'
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, quality=89, optimize=True, exif=b'')
    return '/' + str(out.relative_to(ROOT))

def main():
    path = ROOT / sys.argv[1]
    batch = json.loads(path.read_text())
    assert batch['mode'] == 'preparation_only'
    for post in batch['posts']:
        post['images'] = [render(post, slide, i) for i, slide in enumerate(post['slides'])]
        post['content_hash'] = hashlib.sha256(json.dumps({'caption':post['caption'],
            'slides':post['slides'], 'cta_url':post['cta_url']}, ensure_ascii=False,
            sort_keys=True).encode()).hexdigest()
        post['image_hashes'] = []
        for i, image in enumerate(post['images']):
            file = ROOT / image.lstrip('/')
            with Image.open(file) as im:
                assert im.size == (1080, 1350) and im.format == 'JPEG' and not im.getexif()
            post['image_hashes'].append({'page':i+1, 'path':image.lstrip('/'),
                'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
        post['cover_photo_sha256'] = hashlib.sha256((ROOT /
            post['slides'][0]['photo'].lstrip('/')).read_bytes()).hexdigest()
    path.write_text(json.dumps(batch, ensure_ascii=False, indent=2)+'\n')
    sheet = Image.new('RGB', (1350, 1350), NAVY)
    for col, post in enumerate(batch['posts']):
        for row, image in enumerate(post['images']):
            with Image.open(ROOT / image.lstrip('/')) as im:
                sheet.paste(ImageOps.fit(im, (270, 337)), (col*270, row*337))
    sheet.save(ROOT/'assets/instagram'/('apercu-'+batch['date']+'.jpg'), quality=91)
    print('Prepared', len(batch['posts']), 'posts. No publication or scheduling.')

if __name__ == '__main__':
    main()
