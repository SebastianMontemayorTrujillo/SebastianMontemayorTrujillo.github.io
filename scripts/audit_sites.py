"""Check public search readiness without collecting visitor data."""
import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen
import xml.etree.ElementTree as ET

SITES = (
    ("https://sebastianmontemayortrujillo.github.io", "sitemap.xml"),
    ("https://sebastian-notas.vercel.app", "sitemap_index.xml"),
    ("https://xdchess.vercel.app", "sitemap.xml"),
    ("https://sebastian-voces-de-la-plaza.vercel.app", "sitemap.xml"),
)
PRIVACY = "https://sebastianmontemayortrujillo.github.io/privacidad.html"


class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = None
        self.description = ""
        self.robots = ""
        self.links = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "meta" and attrs.get("name") in ("robots", "description"):
            setattr(self, attrs["name"], attrs.get("content", ""))
        if tag == "a":
            self.links.append(attrs.get("href", ""))


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, target):
        return None


def fetch(url, opener=None):
    request = Request(url, headers={"User-Agent": "SebastianSiteHealth/1.0"})
    try:
        response = (opener.open if opener else urlopen)(request, timeout=30)
    except HTTPError as error:
        response = error
    with response:
        return response.status, response.headers, response.read(2 * 1024 * 1024).decode("utf-8", errors="replace")


def audit():
    checks = []
    for origin, sitemap in SITES:
        errors = []
        try:
            status, headers, body = fetch(origin + "/")
            head = Head()
            head.feed(body)
            if status != 200:
                errors.append(f"HTML status {status}")
            if head.canonical != origin + "/":
                errors.append("Canonical differs from production origin")
            if not head.description:
                errors.append("Description missing")
            if "noindex" in (head.robots + " " + headers.get("X-Robots-Tag", "")).lower():
                errors.append("Production HTML has noindex")
            if PRIVACY not in head.links and "privacidad.html" not in head.links:
                errors.append("Privacy link missing")
            robot_status, _, robots = fetch(origin + "/robots.txt")
            if robot_status != 200 or re.search(r"(?im)^\s*Disallow:\s*/\s*$", robots):
                errors.append("Robots missing or blocks the root")
            sitemap_status, _, xml = fetch(origin + "/" + sitemap)
            locations = [node.text for node in ET.fromstring(xml).iter() if node.tag.endswith("}loc")]
            if sitemap_status != 200 or not locations or any(not value.startswith(origin + "/") for value in locations):
                errors.append("Sitemap invalid or contains another origin")
        except Exception as error:
            errors.append(type(error).__name__)
        checks.append({"origin": origin, "errors": errors})

    opener = build_opener(NoRedirect())
    for path in ("/", "/now.html", "/projects.html?from=health", "/other.html"):
        errors = []
        try:
            status, headers, _ = fetch("https://sebastian-portfolio-psi.vercel.app" + path, opener)
            if status not in (301, 308) or headers.get("Location") != SITES[0][0] + path:
                errors.append("Permanent route-preserving redirect missing")
        except Exception as error:
            errors.append(type(error).__name__)
        checks.append({"legacy_path": path, "errors": errors})
    try:
        privacy_status, _, _ = fetch(PRIVACY)
        checks.append({"privacy": PRIVACY, "errors": [] if privacy_status == 200 else [f"HTTP {privacy_status}"]})
    except Exception as error:
        checks.append({"privacy": PRIVACY, "errors": [type(error).__name__]})
    return {"checked_at": datetime.now(timezone.utc).isoformat(), "scope": "Public technical readiness; search-engine index status requires account access", "checks": checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("search-health.json"))
    args = parser.parse_args()
    report = audit()
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    failed = sum(bool(check["errors"]) for check in report["checks"])
    print(f"{len(report['checks']) - failed}/{len(report['checks'])} public checks passed")
    for check in report["checks"]:
        if check["errors"]:
            print(json.dumps(check, ensure_ascii=False))
    raise SystemExit(bool(failed))
