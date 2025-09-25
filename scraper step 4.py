import os
import json
import re

# Paths
INPUT_FOLDER = r"manga_data"
OUTPUT_ROOT = r"data"
CATALOG_FILE = os.path.join(OUTPUT_ROOT, "catalog.json")


def slug_to_folder(slug):
    """Convert slug into safe folder name (CamelCase)."""
    return re.sub(r'[^a-zA-Z0-9]', '', slug).title()


def save_json_if_changed(path, new_data):
    """Write JSON only if content changed."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                old_data = json.load(f)
            except:
                old_data = None
        if old_data == new_data:
            return False  # no change
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    return True


def convert_manga_file(input_file, catalog):
    with open(input_file, "r", encoding="utf-8") as f:
        manga = json.load(f)

    slug = manga["slug"]
    title = manga["title"]
    description = manga.get("summary", "")
    author = ""  # scrape didn’t include author
    thumbnail = manga.get("cover", "")

    # New fields
    url = manga.get("url", "")
    rank = manga.get("rank", "")
    alt_titles = manga.get("alternative_titles", [])
    genres = manga.get("genres", [])
    status = manga.get("status", "")
    bookmarked = manga.get("bookmarked", 0)

    # Merge all chapters into single JSON
    chapters_data = []
    for idx, ch in enumerate(manga.get("chapters", []), start=1):
        chapters_data.append({
            "number": idx,
            "title": ch.get("chapter", f"Chapter {idx}"),
            "release_date": ch.get("release_date", ""),
            "pages": ch.get("images", [])
        })

    # Calculate total chapters
    total_chapters = len(chapters_data)

    # Update catalog
    entry = next((entry for entry in catalog if entry["slug"] == slug), None)
    if entry:
        updated = False
        for key, value in [("title", title), ("author", author), ("thumbnail", thumbnail),
                           ("status", status), ("genres", genres), ("bookmarked", bookmarked),
                           ("total_chapters", total_chapters)]:  # added total_chapters
            if entry.get(key) != value:
                entry[key] = value
                updated = True
        if updated:
            print(f"✏️ Updated catalog entry for {title}")
    else:
        catalog.append({
            "slug": slug,
            "title": title,
            "author": author,
            "thumbnail": thumbnail,
            "status": status,
            "genres": genres,
            "bookmarked": bookmarked,
            "total_chapters": total_chapters  # added total_chapters
        })
        print(f"📚 Added {title} to catalog.json")

    # Prepare manga folder
    folder_name = slug_to_folder(slug)
    manga_dir = os.path.join(OUTPUT_ROOT, "manga", folder_name)
    os.makedirs(manga_dir, exist_ok=True)

    # Save merged manga JSON
    manga_json = {
        "slug": slug,
        "title": title,
        "author": author,
        "description": description,
        "thumbnail": thumbnail,
        "url": url,
        "rank": rank,
        "alternative_titles": list(dict.fromkeys(alt_titles)),
        "genres": list(dict.fromkeys(genres)),
        "status": status,
        "bookmarked": bookmarked,
        "total_chapters": total_chapters,  # added total_chapters
        "chapters": chapters_data
    }

    manga_file = os.path.join(manga_dir, f"{folder_name}.json")
    if save_json_if_changed(manga_file, manga_json):
        print(f"✅ Saved merged manga.json for {title}")
    else:
        print(f"⏭️ No changes for {title}")


def main():
    # Load catalog.json or create new
    if os.path.exists(CATALOG_FILE):
        with open(CATALOG_FILE, "r", encoding="utf-8") as f:
            try:
                catalog = json.load(f)
            except:
                catalog = []
    else:
        catalog = []

    # Loop through input folder
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".json"):
            input_file = os.path.join(INPUT_FOLDER, filename)
            convert_manga_file(input_file, catalog)

    # Save updated catalog.json
    save_json_if_changed(CATALOG_FILE, catalog)
    print("🎉 All manga converted/updated successfully!")


if __name__ == "__main__":
    main()
