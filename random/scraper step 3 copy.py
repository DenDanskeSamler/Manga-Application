import os
import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

OUTPUT_FOLDER = "manga_data"
MAX_RETRIES = 3
THREADS = 10  # Number of concurrent chapter fetches

# Fetch HTML with retries
def fetch_html(url, retries=MAX_RETRIES):
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"⚠️ Error fetching {url} (attempt {attempt}/{retries}): {e}")
            sleep(2)
    print(f"❌ Failed to fetch {url} after {retries} attempts")
    return None

# Extract images from a chapter page
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
    images = [img.get("data-src") or img.get("src") for img in soup.select("div.page-break img.wp-manga-chapter-img")]
    chapter["images"] = [img.strip() for img in images if img]
    return chapter

# Process one manga file
def process_manga_file(file_path, manga_index, total_manga):
    with open(file_path, "r", encoding="utf-8") as f:
        manga_data = json.load(f)

    chapters = manga_data.get("chapters", [])

    # Only process chapters that don't already have images
    chapters_to_download = [ch for ch in chapters if not ch.get("images")]
    total_chapters = len(chapters)
    done_chapters = total_chapters - len(chapters_to_download)

    if not chapters_to_download:
        print(f"✅ All chapters already have images for {os.path.basename(file_path)} ({manga_index}/{total_manga} manga)")
        return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        future_to_chapter = {executor.submit(get_chapter_images, ch): ch for ch in chapters_to_download}

        for future in as_completed(future_to_chapter):
            chapter = future_to_chapter[future]
            try:
                updated_chapter = future.result()
                # Replace chapter in the list
                for i, ch in enumerate(manga_data["chapters"]):
                    if ch["chapter"] == updated_chapter["chapter"]:
                        manga_data["chapters"][i] = updated_chapter
                        done_chapters += 1
                        # Save after each chapter
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(manga_data, f, ensure_ascii=False, indent=2)
                        print(
                            f"✅ Updated {updated_chapter['chapter']} in {os.path.basename(file_path)} "
                            f"({done_chapters}/{total_chapters} chapters, {manga_index}/{total_manga} manga)"
                        )
                        break
            except Exception as e:
                print(f"⚠️ Failed to process chapter {chapter.get('chapter')}: {e}")

# Main loop over manga JSON files
manga_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".json")]
total_manga = len(manga_files)

for idx, filename in enumerate(manga_files, start=1):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    print(f"🔄 Processing {filename} ({idx}/{total_manga} manga)")
    process_manga_file(file_path, idx, total_manga)
