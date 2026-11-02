from pathlib import Path
import base64,hashlib,json,re,unittest
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
class DepotSecurityTests(unittest.TestCase):
    def test_published_photos_have_no_private_exif(self):
        photos=json.loads((ROOT/'content/depot.json').read_text())
        self.assertEqual(len(photos),28)
        self.assertEqual(len({p['id'] for p in photos}),28)
        for p in photos:
            self.assertTrue(p['alt'])
            for field in ('src','thumbnail'):
                self.assertTrue(p[field].startswith('/assets/depot/'))
                with Image.open(ROOT/'dist-production'/p[field].lstrip('/')) as im:
                    self.assertFalse(im.getexif());im.verify()
    def test_csp_allows_exact_structured_data(self):
        headers=(ROOT/'dist-production/_headers').read_text()
        self.assertIn("connect-src 'self'",headers)
        self.assertIn("frame-ancestors 'none'",headers)
        self.assertNotIn("script-src 'self' 'unsafe-inline'",headers)
        for page in (ROOT/'dist-production').rglob('*.html'):
            for value in re.findall(r'<script type="application/ld\+json">(.*?)</script>',page.read_text()):
                json.loads(value)
                digest=base64.b64encode(hashlib.sha256(value.encode()).digest()).decode()
                self.assertIn("'sha256-"+digest+"'",headers)
    def test_public_artifact_excludes_internal_files(self):
        for name in ('content','src','docs','tests','.git','.env'):
            self.assertFalse((ROOT/'dist-production'/name).exists())
        self.assertEqual((ROOT/'.assetsignore').read_text().splitlines()[1],'*')
        self.assertNotIn('!content/',(ROOT/'.assetsignore').read_text())
