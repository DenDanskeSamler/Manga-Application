import os
import re
import json
import logging
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
from datetime import datetime, timedelta

OUTPUT_FOLDER = "manga_data"
UPDATED_FOLDER = "manga_data_updated"  # new folder for updated JSONs
LOG_FILE = "manga_log.txt"
MAX_RETRIES = 3
THREADS = 10  # Number of concurrent chapter fetches

# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler()  # keeps console output
    ]
)
logger = logging.getLogger(__name__)

# Track summary of updates
summary_updates = {}

# --- Ensure new folder exists ---
os.makedirs(UPDATED_FOLDER, exist_ok=True)

# --- Helpers ---
def fetch_html(url, retries=MAX_RETRIES):
    """Fetch HTML with retries"""
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            return r.text
        except Exception as e:
            logger.warning(f"Error fetching {url} (attempt {attempt}/{retries}): {e}")
            sleep(2)
    logger.error(f"Failed to fetch {url} after {retries} attempts")
    return None

def chapter_number(ch):
    """Extract numeric part from 'Chapter X' string for sorting"""
    match = re.search(r'(\d+)', ch.get("chapter", ""))
    return int(match.group(1)) if match else 0

def parse_release_date(raw_text: str) -> str:
    """Convert site date text into DD-MM-YYYY format"""
    raw_text = raw_text.strip().lower()
    today = datetime.now()

    if "hour" in raw_text or "minute" in raw_text:
        return today.strftime("%d-%m-%Y")
    elif "yesterday" in raw_text:
        return (today - timedelta(days=1)).strftime("%d-%m-%Y")
    elif "day" in raw_text:
        days = int(re.search(r'(\d+)', raw_text).group(1))
        return (today - timedelta(days=days)).strftime("%d-%m-%Y")
    else:
        try:
            dt = datetime.strptime(raw_text, "%d-%m-%Y")
            return dt.strftime("%d-%m-%Y")
        except Exception:
            return today.strftime("%d-%m-%Y")  # fallback

def normalize_chapter(ch):
    """Ensure consistent key order for chapter objects"""
    return {
        "chapter": ch.get("chapter"),
        "url": ch.get("url"),
        "release_date": ch.get("release_date"),
        "images": ch.get("images", []),
    }

# --- Cover fetch + validation ---
def is_valid_image(url):
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            return True
    except Exception as e:
        logger.warning(f"Invalid image URL {url}: {e}")
    return False

def fetch_cover(manga_url):
    html = fetch_html(manga_url)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    cover = soup.select_one("div.summary_image img")
    if cover:
        return cover.get("data-src") or cover.get("src")
    return None

def ensure_valid_cover(manga_data, manga_url, manga_name):
    cover_url = manga_data.get("cover")
    if not cover_url or not is_valid_image(cover_url):
        logger.info(f"🔄 Refetching cover for {manga_name}...")
        new_cover = fetch_cover(manga_url)
        if new_cover and is_valid_image(new_cover):
            manga_data["cover"] = new_cover
            logger.info(f"✅ Updated cover for {manga_name}")
        else:
            logger.warning(f"⚠️ Failed to fetch a valid cover for {manga_name}")
    return manga_data

# --- Chapter image scraper ---
def get_chapter_images(chapter):
    url = chapter.get("url")
    if not url:
        chapter["images"] = []
        return chapter
    html = fetch_html(url)
    if not html:
        chapter["images"] = []
        return chapter
    soup = BeautifulSoup(html, "html.parser")
    images = [img.get("data-src") or img.get("src")
              for img in soup.select("div.page-break img.wp-manga-chapter-img")]
    chapter["images"] = [img.strip() for img in images if img]
    return chapter

# --- Update missing chapters ---
def update_manga_chapters(manga_data, manga_url, manga_name):
    html = fetch_html(manga_url)
    if not html:
        return manga_data
    soup = BeautifulSoup(html, "html.parser")
    chapter_items = soup.select("ul.main li.wp-manga-chapter")

    new_chapters = []
    chapter_dates = {}
    for li in chapter_items:
        a = li.select_one("a")
        date_tag = li.select_one("span.chapter-release-date i")
        if not a:
            continue
        url = a.get("href")
        title = a.get_text(strip=True)
        release_text = date_tag.get_text(strip=True) if date_tag else ""
        release_date = parse_release_date(release_text) if release_text else None
        chapter_dates[title] = release_date
        new_chapters.append({
            "chapter": title,
            "url": url,
            "release_date": release_date,
            "images": []
        })

    existing = {ch["chapter"]: ch for ch in manga_data.get("chapters", [])}
    added_chapters = []
    for ch in new_chapters:
        if ch["chapter"] not in existing:
            manga_data.setdefault("chapters", []).append(ch)
            added_chapters.append(ch["chapter"])
            logger.info(f"🆕 Added new chapter: {ch['chapter']}")

    for ch in manga_data.get("chapters", []):
        if not ch.get("release_date") and ch["chapter"] in chapter_dates:
            ch["release_date"] = chapter_dates[ch["chapter"]]
            logger.info(f"📅 Added release_date for {ch['chapter']}: {ch['release_date']}")

    if added_chapters:
        manga_data["chapters"].sort(key=chapter_number)
        summary_updates[manga_name] = added_chapters

    return manga_data

# --- Process one manga JSON file ---
def process_manga_file(file_path, manga_index, total_manga):
    with open(file_path, "r", encoding="utf-8") as f:
        manga_data = json.load(f)

    manga_name = os.path.basename(file_path)
    manga_url = manga_data.get("url")
    new_file_path = os.path.join(UPDATED_FOLDER, manga_name)

    # Copy original file if not exists in updated folder
    if not os.path.exists(new_file_path):
        with open(new_file_path, "w", encoding="utf-8") as f:
            json.dump(manga_data, f, ensure_ascii=False, indent=2)

    if manga_url:
        manga_data = ensure_valid_cover(manga_data, manga_url, manga_name)
        manga_data = update_manga_chapters(manga_data, manga_url, manga_name)
        manga_data["chapters"].sort(key=chapter_number)
        manga_data["chapters"] = [normalize_chapter(ch) for ch in manga_data["chapters"]]

        # Save updates to new folder
        with open(new_file_path, "w", encoding="utf-8") as f:
            json.dump(manga_data, f, ensure_ascii=False, indent=2)

    chapters = manga_data.get("chapters", [])
    chapters_to_download = [ch for ch in chapters if not ch.get("images")]
    total_chapters = len(chapters)
    done_chapters = total_chapters - len(chapters_to_download)

    if not chapters_to_download:
        logger.info(f"✅ All chapters already have images for {manga_name} "
                    f"({manga_index}/{total_manga} manga)")
        return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        future_to_chapter = {executor.submit(get_chapter_images, ch): ch
                             for ch in chapters_to_download}

        for future in as_completed(future_to_chapter):
            chapter = future_to_chapter[future]
            try:
                updated_chapter = future.result()
                for i, ch in enumerate(manga_data["chapters"]):
                    if ch["chapter"] == updated_chapter["chapter"]:
                        manga_data["chapters"][i] = updated_chapter
                        done_chapters += 1
                        manga_data["chapters"].sort(key=chapter_number)
                        manga_data["chapters"] = [normalize_chapter(c) for c in manga_data["chapters"]]

                        # Save to updated folder
                        with open(new_file_path, "w", encoding="utf-8") as f:
                            json.dump(manga_data, f, ensure_ascii=False, indent=2)

                        logger.info(
                            f"✅ Updated {updated_chapter['chapter']} in {manga_name} "
                            f"({done_chapters}/{total_chapters} chapters, {manga_index}/{total_manga} manga)"
                        )
                        break
            except Exception as e:
                logger.error(f"⚠️ Failed to process chapter {chapter.get('chapter')}: {e}")

# --- Main loop ---
manga_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".json")]
total_manga = len(manga_files)

for idx, filename in enumerate(manga_files, start=1):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    logger.info(f"🔄 Processing {filename} ({idx}/{total_manga} manga)")
    process_manga_file(file_path, idx, total_manga)

# --- Final Summary ---
if summary_updates:
    logger.info("\n📌 Update Summary:")
    for manga_name, chapters in summary_updates.items():
        logger.info(f"   ➕ {manga_name}: {', '.join(chapters)}")
else:
    logger.info("\n📌 No new chapters were added this run.")
