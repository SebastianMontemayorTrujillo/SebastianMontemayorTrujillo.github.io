import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('build', Path(__file__).with_name('build.py'))
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class BuildTests(unittest.TestCase):
    def test_rejects_non_https_and_credentials(self):
        for value in ['javascript:alert(1)', 'http://example.com', 'https://user:secret@example.com']:
            with self.assertRaises(ValueError):
                build.https_url(value)

    def test_preview_and_production_metadata_and_public_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = {'site_url': 'https://seb.example', 'blog_url': 'https://blog.example',
                      'xdchess_url': 'https://chess.example', 'inehack_url': 'https://game.example',
                      'google_site_verification': 'test-google', 'bing_site_verification': 'test-bing'}
            (root / 'site.json').write_text(json.dumps(config))
            for page in build.PAGES:
                (root / page).write_text((build.ROOT / page).read_text())
            (root / 'style.css').write_text('body {}')
            (root / '.env').write_text('PRIVATE=do-not-copy')
            for env in ['preview', 'production']:
                with patch.object(build, 'ROOT', root), patch.dict(os.environ, {'VERCEL_ENV': env, 'SITE_URL': ''}):
                    build.build()
                output = root / 'dist'
                text = (output / 'projects.html').read_text()
                self.assertEqual('noindex' in text, env == 'preview')
                self.assertIn('https://chess.example', text)
                self.assertIn('https://game.example', text)
                self.assertIn('https://blog.example', text)
                self.assertIn('name="google-site-verification" content="test-google"', text)
                self.assertIn('name="msvalidate.01" content="test-bing"', text)
                self.assertIn('href="privacidad.html"', text)
                self.assertIn('id="blog"', text)
                self.assertIn('https://blog.example/crab-chess-ajedrez-con-minijuegos/', text)
                self.assertIn('id="crab-chess"', text)
                self.assertIn('id="voces-de-la-plaza"', text)
                for page in build.PAGES:
                    self.assertIn('href="projects.html"', (output / page).read_text())
                    self.assertIn('href="projects.html#blog"', (output / page).read_text())
                self.assertNotIn('github.io', text)
                self.assertNotIn('og.png', text)
                self.assertFalse((output / '.env').exists())
                xml = ET.parse(output / 'sitemap.xml')
                self.assertEqual(len(xml.findall('{*}url')), len(build.PAGES))
                self.assertIn('https://seb.example/projects.html', (output / 'sitemap.xml').read_text())
                self.assertEqual('Disallow: /' in (output / 'robots.txt').read_text(), env == 'preview')


if __name__ == '__main__':
    unittest.main()
