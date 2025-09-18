import os
import json
import requests
from bs4 import BeautifulSoup
import re

# Paths
MANGA_LIST_FILE = "manga_list.json"
OUTPUT_FOLDER = "manga_data"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

if not os.path.exists(MANGA_LIST_FILE):
    print(f"❌ {MANGA_LIST_FILE} not found. Run the initial scraper first.")
    exit()

with open(MANGA_LIST_FILE, "r", encoding="utf-8") as f:
    manga_list = json.load(f)

def fetch_html(url):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.text
    except Exception as e:
        print(f"⚠️ Error fetching {url}: {e}")
    return None

def slugify(text):
    return re.sub(r"[^\w\d-]+", "-", text.lower()).strip("-")

def chapter_number(chapter_title):
    """Extract numeric part of chapter for proper sorting"""
    match = re.search(r"(\d+)", chapter_title)
    return int(match.group(1)) if match else 0

def scrape_manga_details(manga):
    html = fetch_html(manga["url"])
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")
    data = {}

    data["title"] = manga.get("title")
    data["slug"] = slugify(manga.get("title"))
    data["url"] = manga.get("url")
    data["cover"] = manga.get("image")

    rank_tag = soup.find("div", class_="post-content_item", string=lambda t: t and "Rank" in t)
    if rank_tag:
        rank_value = rank_tag.find_next("div", class_="summary-content")
        data["rank"] = rank_value.get_text(strip=True) if rank_value else None

    alt_tag = soup.find("div", class_="post-content_item", string=lambda t: t and "Alternative" in t)
    if alt_tag:
        alt_value = alt_tag.find_next("div", class_="summary-content")
        data["alternative_titles"] = [t.strip() for t in alt_value.get_text(strip=True).split(",")] if alt_value else []

    data["genres"] = [a.get_text(strip=True) for a in soup.select(".genres-content a")]

    # Status
    status_heading = soup.select_one(".post-content_item .summary-heading h5")
    if status_heading and "Status" in status_heading.get_text():
        status_value_tag = status_heading.find_parent(".post-content_item").select_one(".summary-content")
        data["status"] = status_value_tag.get_text(strip=True) if status_value_tag else None

    bookmark_tag = soup.select_one(".add-bookmark .action_detail span")
    if bookmark_tag:
        numbers = re.findall(r"\d+", bookmark_tag.get_text())
        data["bookmarked"] = int(numbers[0]) if numbers else 0

    desc_tag = soup.select_one(".description-summary .summary__content")
    data["summary"] = desc_tag.get_text(" ", strip=True) if desc_tag else ""

    # Scrape chapters
    chapters = []
    for ch in soup.select(".listing-chapters_wrap .wp-manga-chapter a"):
        title = ch.get_text(strip=True)
        url = ch["href"]
        date_tag = ch.find_next("span", class_="chapter-release-date")
        release_date = date_tag.get_text(strip=True) if date_tag else None
        chapters.append({"chapter": title, "url": url, "release_date": release_date})
    data["chapters"] = chapters

    return data

# Main loop with update logic
for name, manga in manga_list.items():
    print(f"🔎 Updating: {name}")
    scraped_data = scrape_manga_details(manga)
    if not scraped_data:
        print(f"⚠️ Failed to scrape {name}")
        continue

    slug = scraped_data["slug"]
    file_path = os.path.join(OUTPUT_FOLDER, f"{slug}.json")

    # Load existing data if available
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    # Merge scraped data into existing data
    updated_data = existing_data.copy()
    updated_data.update({
        "title": scraped_data["title"],
        "url": scraped_data["url"],
        "cover": scraped_data["cover"],
        "rank": scraped_data.get("rank"),
        "alternative_titles": scraped_data.get("alternative_titles"),
        "genres": scraped_data.get("genres"),
        "status": scraped_data.get("status"),
        "bookmarked": scraped_data.get("bookmarked"),
        "summary": scraped_data.get("summary")
    })

    # Merge chapters (add only new ones)
    existing_chapters = {c["chapter"]: c for c in existing_data.get("chapters", [])}
    for ch in scraped_data["chapters"]:
        if ch["chapter"] not in existing_chapters:
            existing_chapters[ch["chapter"]] = ch

    # Sort chapters numerically (newest last)
    updated_data["chapters"] = sorted(
        existing_chapters.values(),
        key=lambda x: chapter_number(x["chapter"])
    )

    # Save back to file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Updated: {file_path}")
