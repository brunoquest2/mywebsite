#!/usr/bin/env python3
"""Merge Bruno Moreira's public Behance RSS feed into the static site data."""

from __future__ import annotations
import html, json, re, sys, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "behance-projects.json"
FEED_URL = "https://www.behance.net/bm_marketing.xml"
IMAGE_HOST = "mir-s3-cdn-cf.behance.net"

class DescriptionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text: list[str] = []
        self.images: list[str] = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "img":
            src = dict(attrs).get("src")
            if src:
                self.images.append(src)
    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if cleaned:
            self.text.append(cleaned)

def valid_https_url(value: str, host: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.hostname == host

def parse_feed(xml_data: bytes) -> list[dict[str, str]]:
    root = ET.fromstring(xml_data)
    items: list[dict[str, str]] = []
    for item in root.findall("./channel/item"):
        title = html.unescape((item.findtext("title") or "").strip())
        link = (item.findtext("link") or "").strip()
        description = item.findtext("description") or ""
        project_match = re.search(r"/gallery/(\d+)(?:/|$)", link)
        if not title or not project_match or not valid_https_url(link, "www.behance.net"):
            continue
        parsed = DescriptionParser()
        parsed.feed(description)
        image_url = next((url for url in parsed.images if valid_https_url(url, IMAGE_HOST)), "")
        if "/projects/404/" in image_url:
            image_url = image_url.replace("/projects/404/", "/projects/max_808_webp/", 1)
        summary = html.unescape(" ".join(parsed.text)).strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        items.append({"id": project_match.group(1), "title": title, "url": link, "image": image_url, "summary": summary, "publishedAt": pub_date})
    return items

def read_existing() -> list[dict[str, str]]:
    if not DATA_FILE.exists():
        return []
    try:
        stored = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise RuntimeError(f"Could not read {DATA_FILE}: {error}") from error
    return [project for project in stored.get("projects", []) if isinstance(project, dict) and project.get("id")]

def main() -> int:
    request = urllib.request.Request(FEED_URL, headers={"User-Agent": "BrunoMoreiraPortfolioSync/1.0 (+https://brunomoreira.com.br)"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"Behance RSS returned HTTP {response.status}")
        incoming = parse_feed(response.read())
    if not incoming:
        raise RuntimeError("Behance RSS contained no valid public projects; keeping existing data")
    records = incoming
    old_records = read_existing()
    if records == old_records:
        print(f"Behance data unchanged; {len(records)} projects retained.")
        return 0
    payload = {"source": FEED_URL, "syncedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "projects": records}
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Synchronized {len(incoming)} feed entries; {len(records)} projects retained.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"Behance sync failed: {error}", file=sys.stderr)
        raise SystemExit(1)
