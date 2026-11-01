from pathlib import Path
from html.parser import HTMLParser
import json,re,subprocess,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build
from fixtures import fixture
ROOT=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
    def __init__(self):super().__init__();self.urls=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ['href','src'] and v:self.urls.append(v)
class BuildTests(unittest.TestCase):
    def test_all_photographs_decode(self):
        from PIL import Image
        photos=list((ROOT/'assets/references').rglob('*.webp'));self.assertEqual(len(photos),14)
        for photo in photos:
            with Image.open(photo) as im:im.verify()
    def test_production_excludes_drafts_and_pending_media(self):
        root=ROOT/'dist-production';self.assertFalse((root/'atelier').exists());self.assertFalse((root/'actualites/preparer-livraison-acces-contraint').exists());self.assertEqual(len(list((root/'assets/references/ain-diab').glob('*.webp'))),8);self.assertNotIn('pending_photos',(root/'assets/references-data.js').read_text());self.assertNotIn('noindex',(root/'index.html').read_text())
    def test_preview_links_and_images_resolve(self):
        root=ROOT/'dist'
        for file in root.rglob('*.html'):
            p=Links();p.feed(file.read_text())
            for url in p.urls:
                if not url.startswith('/') or url.startswith('//'):continue
                path=url.split('#')[0].split('?')[0] or '/';target=root/path.lstrip('/')
                if path.endswith('/'):target=target/'index.html'
                self.assertTrue(target.exists(),f'{file}: {url}')
    def test_all_catalogue_data_preserved(self):
        original=subprocess.check_output(['git','show','372f24157a942aeb4acca3a265936289b0e24844:index.html'],cwd=ROOT,text=True)
        old=json.loads(re.search(r'const DATA=(.*?);\nconst VEHICLES',original,re.S)[1]);new=json.loads((ROOT/'content/catalogue.json').read_text());self.assertEqual(old,new)
        generated=json.loads(re.search(r'const DATA=(.*?);\nconst VEHICLES',(ROOT/'src/catalogue.js').read_text(),re.S)[1]);self.assertEqual(new,generated)
    def test_footer_and_delivery_scope(self):
        s=(ROOT/'dist/index.html').read_text();self.assertIn('href="tel:+212602644454"',s);self.assertIn('href="mailto:youssef.materiauxdeconstruction@gmail.com"',s)
        for forbidden in ['Catalogue indicatif','Sans prix','Dimensions, véhicules et disponibilités à confirmer','Transport seul','location de véhicules']:
            self.assertNotIn(forbidden,s)
    def test_seo_template(self):
        a=fixture();a['status']='published';s=build.article_page(a,False);self.assertIn('application/ld+json',s);self.assertIn('rel="canonical"',s);self.assertIn('index,follow',s)
if __name__=='__main__':unittest.main()
