from pathlib import Path
import json,re,unittest,xml.etree.ElementTree as ET
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
class ProductPagesTests(unittest.TestCase):
    def test_variants_and_rebar_specs(self):
        products=json.loads((ROOT/'content/products.json').read_text())
        panel=next(p for p in products if p['slug']=='panneaux-muraux')
        self.assertEqual([v['dimension'] for v in panel['variants']],['7 cm','10 cm','15 cm'])
        self.assertTrue(any('10 cm' in f for f in panel['facts']))
        fer=next(p for p in products if p['slug']=='fer-a-beton')
        self.assertIn('Barres de 12 m',fer['facts']);self.assertIn('Conditionnement en fardeaux',fer['facts'])
    def test_new_originals_remain_private_and_rights_survive_export(self):
        for path in (ROOT/'assets/depot').glob('panneaux-muraux-stock-10cm*.webp'):
            with Image.open(path) as im:
                self.assertLessEqual(max(im.size),1280);self.assertFalse(im.getexif());self.assertIn(b'El Boussairi',im.info['xmp'])
        self.assertFalse(list((ROOT/'assets/depot').glob('*.jpg')))
    def test_indexable_product_pages_and_corresponding_image_sitemap(self):
        root=ROOT/'dist-production'
        ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','i':'http://www.google.com/schemas/sitemap-image/1.1'}
        sitemap=ET.fromstring((root/'sitemap.xml').read_text())
        for slug,count in [('panneaux-muraux',5),('fer-a-beton',3)]:
            page=(root/'materiaux'/slug/'index.html').read_text()
            self.assertIn('index,follow',page);self.assertIn('?produit='+slug,page)
            graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',page)[1])['@graph']
            self.assertEqual(sum(n['@type']=='ImageObject' for n in graph),count)
            self.assertEqual(sum(n['@type']=='Product' for n in graph),1)
            node=next(u for u in sitemap.findall('s:url',ns) if u.find('s:loc',ns).text.endswith('/materiaux/'+slug+'/'))
            self.assertEqual(len(node.findall('i:image',ns)),count)
    def test_all_public_photos_have_copyright_and_no_invented_capture_location(self):
        photos=json.loads((ROOT/'content/depot.json').read_text())
        for photo in photos:
            self.assertTrue(photo['copyrightNotice']);self.assertTrue(photo['license'].endswith('#droits-images'))
            self.assertNotIn('gps',photo);self.assertNotIn('dateTaken',photo)
