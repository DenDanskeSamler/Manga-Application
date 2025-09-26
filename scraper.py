import requests
import json
import os
from bs4 import BeautifulSoup
import time

BASE_URL = "https://manhuaus.com"
OUTPUT_FILE = "manga_list.json"
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds between retries

# Load existing data
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        manga_data = json.load(f)
else:
    manga_data = {}

def fetch_page(page):
    url = f"{BASE_URL}/page/{page}/"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                print(f"Page {page} returned status 404 - stopping scraper.")
                exit(1)
            else:
                print(f"Page {page} returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")

        print(f"Retrying page {page} ({attempt}/{MAX_RETRIES}) in {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)

    # ❌ Stop the program if all retries fail
    print(f"Failed to fetch page {page} after {MAX_RETRIES} retries. Exiting program.")
    exit(1)

def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    mangas = []

    for item in soup.select(".page-item-detail.manga"):
        title_tag = item.select_one(".post-title a")
        img_tag = item.select_one(".item-thumb img")
        if not title_tag or not img_tag:
            continue

        title = title_tag.get_text(strip=True)
        url = title_tag["href"]
        img = img_tag.get("data-src") or img_tag.get("src")

        chapters = []
        for ch in item.select(".list-chapter .chapter-item a"):
            chapters.append({
                "chapter_title": ch.get_text(strip=True),
                "chapter_url": ch["href"]
            })

        mangas.append({
            "title": title,
            "url": url,
            "image": img,
            "chapters": chapters
        })

    return mangas

def save_data():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(manga_data, f, ensure_ascii=False, indent=2)

def crawl_all():
    page = 1
    while True:
        print(f"Fetching page {page}...")
        html = fetch_page(page)  # ❌ Will exit program if fails

        if not html or "page-item-detail" not in html:
            print(f"No content on page {page}. Exiting program.")
            exit(1)

        mangas = parse_page(html)
        new_count = 0

        for m in mangas:
            if m["title"] in manga_data:
                existing_chapters = {ch["chapter_url"] for ch in manga_data[m["title"]]["chapters"]}
                for ch in m["chapters"]:
                    if ch["chapter_url"] not in existing_chapters:
                        manga_data[m["title"]]["chapters"].append(ch)
            else:
                manga_data[m["title"]] = m
                new_count += 1

        print(f"Added {new_count} new mangas. Total: {len(manga_data)}")
        save_data()

        page += 1

if __name__ == "__main__":
    crawl_all()
