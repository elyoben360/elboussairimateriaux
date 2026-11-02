#!/usr/bin/env python3
"""Render a dated preparation lot only; never schedule or publish."""
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image, ImageOps
import instagram_pack as layout

ROOT = Path(__file__).resolve().parents[1]

def main():
    path = ROOT / sys.argv[1]
    batch = json.loads(path.read_text())
    assert batch['mode'] == 'preparation_only'
    # Keep the older renderer unchanged for already archived scheduled files.
    source = Path(layout.__file__).read_text().split("if __name__=='__main__':")[0]
    source = source.replace("font=font(13)", "font=font(20)")
    source = source.replace('size=64', 'size=58')
    source = source.replace('944,29,M,leading=1.4', '944,38,M,leading=1.22')
    namespace = {'__file__': layout.__file__, '__name__': 'dated_layout'}
    exec(compile(source, layout.__file__, 'exec'), namespace)
    for post in batch['posts']:
        post['images'] = [namespace['render'](post, slide, i)
                          for i, slide in enumerate(post['slides'])]
        post['content_hash'] = hashlib.sha256(json.dumps(
            {'caption': post['caption'], 'slides': post['slides']},
            ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        post['image_hashes'] = []
        for i, image in enumerate(post['images']):
            file = ROOT / image.lstrip('/')
            with Image.open(file) as im:
                assert im.size == (1080, 1350) and im.format == 'JPEG'
                assert not im.getexif()
            post['image_hashes'].append({'page': i + 1, 'path': image.lstrip('/'),
                'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
    path.write_text(json.dumps(batch, ensure_ascii=False, indent=2) + '\n')
    sheet = Image.new('RGB', (1350, 1350), '#071d39')
    for column, post in enumerate(batch['posts']):
        for row, image in enumerate(post['images']):
            with Image.open(ROOT / image.lstrip('/')) as im:
                sheet.paste(ImageOps.fit(im, (270, 337)), (column * 270, row * 337))
    sheet.save(ROOT / 'assets/instagram' / ('apercu-' + batch['date'] + '.jpg'), quality=92)
    print('Prepared', len(batch['posts']), 'carousels; no publishing operation.')

if __name__ == '__main__':
    main()
