from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = 'bananamateriaux.ma'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.canonicals = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.urls.extend(attrs[k] for k in ('href', 'src') if attrs.get(k))
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))


class DomainMigrationTests(unittest.TestCase):
    def test_production_domain_and_local_links(self):
        root = ROOT / 'dist-production'
        pages = list(root.rglob('*.html'))
        self.assertGreater(len(pages), 10, 'Build production before running tests')
        for page in pages:
            text = page.read_text()
            self.assertNotIn('elboussairimateriaux.com', text, str(page))
            parser = Links()
            parser.feed(text)
            self.assertEqual(len(parser.canonicals), 1, str(page))
            self.assertEqual(urlsplit(parser.canonicals[0]).netloc, DOMAIN)
            for url in parser.urls:
                parsed = urlsplit(url)
                if parsed.scheme and parsed.scheme not in ('http', 'https'):
                    continue
                if parsed.netloc and parsed.netloc != DOMAIN:
                    continue
                if not parsed.path or parsed.path.startswith('/api/'):
                    continue
                path = unquote(parsed.path)
                target = root / path.lstrip('/') if path.startswith('/') else page.parent / path
                if path.endswith('/'):
                    target = target / 'index.html'
                self.assertTrue(target.is_file(), f'{page.relative_to(root)}: {url}')

    def test_feed_sitemap_robots_and_photo_links_use_new_domain(self):
        root = ROOT / 'dist-production'
        for name in ('sitemap.xml', 'robots.txt', 'actualites/feed.xml', 'assets/album-data.js'):
            text = (root / name).read_text()
            self.assertNotIn('elboussairimateriaux.com', text, name)
            if name != 'assets/album-data.js':
                self.assertIn('https://' + DOMAIN, text, name)


if __name__ == '__main__':
    unittest.main()
