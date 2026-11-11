"""Build a small static portfolio; only copy public assets into dist."""
from pathlib import Path
from urllib.parse import urlsplit
import html
import json
import os
import shutil

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "now.html", "projects.html", "other.html")


def https_url(value):
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Public URLs must use HTTPS without credentials")
    return value.rstrip("/")


def build():
    config = json.loads((ROOT / "site.json").read_text())
    origin = https_url(os.getenv("SITE_URL") or config["site_url"] or
                       "https://" + os.getenv("VERCEL_PROJECT_PRODUCTION_URL", "sebastianmontemayortrujillo.github.io"))
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    production = os.getenv("VERCEL_ENV") == "production"
    for page in PAGES:
        source = (ROOT / page).read_text()
        source = source.replace("https://sebastianmontemayortrujillo.github.io", html.escape(origin, quote=True))
        # The source repository never contained og.png. Avoid broken share images.
        source = "\n".join(line for line in source.splitlines()
                           if 'og:image' not in line and 'twitter:image' not in line)
        source = source.replace('content="summary_large_image"', 'content="summary"')
        source = source.replace("</head>", '<link rel="icon" href="data:,">\n</head>')
        if not production:
            source = source.replace("</head>", '<meta name="robots" content="noindex, nofollow">\n</head>')
        for project in ("xdchess", "inehack"):
            url = config[project + "_url"]
            link = f'<a href="{html.escape(https_url(url), quote=True)}">Play the demo →</a>' if url else ""
            source = source.replace(f"<!-- {project}-demo -->", link)
        blog = config["blog_url"]
        link = ""
        if blog:
            blog = html.escape(https_url(blog), quote=True)
            link = f'''<section id="blog" aria-labelledby="blog-title">
        <h2 id="blog-title">Blog <span lang="es">en español</span></h2>
        <p>I write in Spanish about hackathons and the projects I build.</p>
        <p><a href="{blog}/" hreflang="es">Read Notas de Sebastian</a></p>
        <ul lang="es">
          <li><a href="{blog}/crab-chess-ajedrez-con-minijuegos/">Crab Chess, ajedrez con minijuegos</a></li>
          <li><a href="{blog}/voces-de-la-plaza-inehack/">Voces de la Plaza, una aventura de participación ciudadana</a></li>
        </ul>
      </section>'''
        else:
            source = source.replace('      <a href="projects.html#blog">blog</a>\n', "")
        source = source.replace("<!-- blog-link -->", link)
        (output / page).write_text(source + "\n")
    shutil.copyfile(ROOT / "style.css", output / "style.css")
    urls = [origin + ("/" if page == "index.html" else "/" + page) for page in PAGES]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{html.escape(url)}</loc></url>" for url in urls) + "</urlset>\n"
    (output / "sitemap.xml").write_text(sitemap)
    (output / "robots.txt").write_text("User-agent: *\n" + (f"Allow: /\nSitemap: {origin}/sitemap.xml\n" if production else "Disallow: /\n"))
    print(f"Built {len(PAGES)} pages for {origin}; indexing {'enabled' if production else 'disabled'}")


if __name__ == "__main__":
    build()
