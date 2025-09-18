import os
import json
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Paths
MANGA_LIST_FILE = "manga_list.json"
OUTPUT_FOLDER = "manga_data"
NUM_THREADS = 10
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load manga list
if not os.path.exists(MANGA_LIST_FILE):
    print(f"❌ {MANGA_LIST_FILE} not found. Run the initial scraper first.")
    exit()

with open(MANGA_LIST_FILE, "r", encoding="utf-8") as f:
    manga_list = json.load(f)

def fetch_html(url):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                return r.text
            else:
                print(f"Page {url} returned status {r.status_code}")
        except Exception as e:
            print(f"⚠️ Error fetching {url}: {e}")

        print(f"Retrying {url} ({attempt}/{MAX_RETRIES}) in {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)
    return None

def slugify(text):
    return re.sub(r"[^\w\d-]+", "-", text.lower()).strip("-")

def parse_relative_date(text):
    now = datetime.now()
    if "ago" not in text:
        try:
            dt = datetime.strptime(text, "%B %d, %Y")
            return dt.strftime("%d-%m-%Y")
        except:
            return text
    number = int(re.search(r"\d+", text).group())
    if "hour" in text or "minute" in text:
        dt = now
    elif "day" in text:
        dt = now - timedelta(days=number)
    else:
        dt = now
    return dt.strftime("%d-%m-%Y")

def chapter_number(chapter_title):
    match = re.search(r"(\d+)", chapter_title)
    return int(match.group(1)) if match else 0

def scrape_manga_details(manga):
    html = fetch_html(manga["url"])
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    data = {
        "title": manga.get("title"),
        "slug": slugify(manga.get("title")),
        "url": manga.get("url"),
        "cover": manga.get("image"),
        "rank": None,
        "alternative_titles": [],
        "genres": [],
        "status": None,
        "bookmarked": 0,
        "summary": "",
        "chapters": []
    }

    # Rank
    rank_heading = soup.select_one(".post-content_item .summary-heading h5")
    if rank_heading and "Rank" in rank_heading.get_text(strip=True):
        parent_item = rank_heading.find_parent("div", class_="post-content_item")
        rank_content = parent_item.select_one(".summary-content") if parent_item else None
        data["rank"] = rank_content.get_text(strip=True) if rank_content else None

    # Alternative Titles
    alt_title_divs = soup.select(".post-content_item")
    for div in alt_title_divs:
        heading = div.select_one(".summary-heading h5")
        if heading and "Alternative" in heading.get_text(strip=True):
            content = div.select_one(".summary-content")
            if content:
                data["alternative_titles"] = [t.strip() for t in content.get_text(strip=True).split(",")]

    # Genres
    data["genres"] = [a.get_text(strip=True) for a in soup.select(".genres-content a")]

    # Status
    status_heading = soup.select_one(".post-status .post-content_item .summary-heading h5")
    if status_heading and "Status" in status_heading.get_text(strip=True):
        parent_item = status_heading.find_parent("div", class_="post-content_item")
        status_content = parent_item.select_one(".summary-content") if parent_item else None
        data["status"] = status_content.get_text(strip=True) if status_content else None

    # Bookmarks
    bookmark_tag = soup.select_one(".add-bookmark .action_detail span")
    if bookmark_tag:
        numbers = re.findall(r"\d+", bookmark_tag.get_text())
        data["bookmarked"] = int(numbers[0]) if numbers else 0

    # Summary
    desc_tag = soup.select_one(".description-summary .summary__content")
    if desc_tag:
        data["summary"] = desc_tag.get_text(" ", strip=True)

    # Chapters
    for ch in soup.select(".listing-chapters_wrap .wp-manga-chapter a"):
        title = ch.get_text(strip=True)
        url = ch["href"]
        date_tag = ch.find_next("span", class_="chapter-release-date")
        release_date = parse_relative_date(date_tag.get_text(strip=True)) if date_tag else None
        data["chapters"].append({
            "chapter": title,
            "url": url,
            "release_date": release_date
        })

    # Sort chapters numerically
    data["chapters"] = sorted(data["chapters"], key=lambda x: chapter_number(x["chapter"]))

    return data

def save_manga(manga):
    slug = slugify(manga["title"])
    file_path = os.path.join(OUTPUT_FOLDER, f"{slug}.json")

    print(f"🔎 Scraping: {manga['title']}")
    manga_data = scrape_manga_details(manga)
    if not manga_data:
        print(f"⚠️ Failed to scrape: {manga['title']}")
        return

    # Check if file exists
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            old_data = json.load(f)

        # Update only fields that changed
        for key in ["rank", "alternative_titles", "genres", "status", "bookmarked", "summary", "cover"]:
            if manga_data.get(key) and manga_data[key] != old_data.get(key):
                old_data[key] = manga_data[key]

        # Merge chapters: only add new ones
        old_chapters = {ch["chapter"]: ch for ch in old_data.get("chapters", [])}
        for ch in manga_data.get("chapters", []):
            if ch["chapter"] not in old_chapters:
                old_chapters[ch["chapter"]] = ch
        # Sort chapters
        old_data["chapters"] = sorted(old_chapters.values(), key=lambda x: chapter_number(x["chapter"]))

        manga_data = old_data

    # Save updated data
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(manga_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved/Updated: {file_path}")


# Multithreading
with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
    futures = [executor.submit(save_manga, manga) for name, manga in manga_list.items()]
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"⚠️ Thread exception: {e}")
