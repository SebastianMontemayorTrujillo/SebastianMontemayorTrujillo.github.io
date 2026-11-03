"""Generate the GitHub Pages migration separately from Vercel's public files."""
from pathlib import Path
import html
import json
from build import https_url, PAGES, ROOT

origin = https_url(json.loads((ROOT / 'site.json').read_text())['site_url'])
if origin == 'https://sebastianmontemayortrujillo.github.io':
    raise ValueError('Set the verified new production URL before generating redirects')
output = ROOT / 'github-pages'
output.mkdir(exist_ok=True)
for page in PAGES:
    url = html.escape(origin + ('/' if page == 'index.html' else '/' + page), quote=True)
    (output / page).write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Site moved — Sebastian Montemayor Trujillo</title>
<link rel="canonical" href="{url}"><meta http-equiv="refresh" content="0;url={url}">
</head><body><p>My website has moved. <a href="{url}">Continue to the new page →</a></p></body></html>
''')
(output / '.nojekyll').touch()
print(f'Generated {len(PAGES)} redirects in {output}; publish only after checking the new site')
