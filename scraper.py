# scraper.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# Common file extensions to ignore
SKIP_EXTENSIONS = [
    ".jpg", ".jpeg", ".png", ".gif", ".svg",
    ".mp4", ".webm", ".avi", ".mov",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".ppt", ".pptx", ".zip", ".rar", ".exe"
]

def is_valid_page(url):
    # Skip if it ends with a static file extension
    return not any(url.lower().endswith(ext) for ext in SKIP_EXTENSIONS)

def scrape_site(base_url, max_pages=30):
    visited = set()
    to_visit = [base_url]
    all_texts = {}

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited or not is_valid_page(url):
            continue

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Failed to fetch {url}: {e}")
            continue

        print(f"✅ Crawling: {url}")
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove non-text elements
        for tag in soup(["script", "style", "img", "video", "iframe", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        all_texts[url] = text

        # Extract and filter internal links
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)

            # Only same domain and valid HTML pages
            if parsed.netloc == urlparse(base_url).netloc:
                clean_url = parsed.scheme + "://" + parsed.netloc + parsed.path
                if clean_url not in visited and clean_url not in to_visit and is_valid_page(clean_url):
                    to_visit.append(clean_url)

        visited.add(url)
        time.sleep(0.5)

    return "\n\n".join(all_texts.values())
