#!/usr/bin/env python3
"""
Scraper Step 4: Build catalog and organize data
REFACTORED: catalog.json now only contains slugs, all metadata is in manga_data/*.json files
"""
import os
import json
import re

# Paths
INPUT_FOLDER = r"manga_data"
OUTPUT_ROOT = r"data"
CATALOG_FILE = os.path.join(OUTPUT_ROOT, "catalog.json")


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


def get_chapter_number(chapter_title):
    """Extracts the first number from a chapter title string."""
    match = re.search(r'(\d+(\.\d+)?)', str(chapter_title))
    if not match:
        return 0
    num_str = match.group(1)
    # Return int if it's a whole number, otherwise float
    return int(float(num_str)) if float(num_str).is_integer() else float(num_str)


def convert_manga_file(input_file, catalog):
    """Process a manga file and update the simple catalog with just the slug."""
    with open(input_file, "r", encoding="utf-8") as f:
        manga = json.load(f)

    slug = manga["slug"]
    title = manga["title"]
    description = manga.get("summary", "")
    author = manga.get("author", "")
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
    for ch in manga.get("chapters", []):
        chapter_num = get_chapter_number(ch.get("chapter"))
        chapters_data.append({
            "number": int(chapter_num) if isinstance(chapter_num, float) and chapter_num.is_integer() else chapter_num,
            "title": ch.get("chapter", f"Chapter {chapter_num}"),
            "release_date": ch.get("release_date", ""),
            "pages": ch.get("images", [])
        })

    # Calculate total chapters
    total_chapters = len(chapters_data)
    
    # Get the last 2 chapters for metadata
    latest_chapters = [
        {"number": int(c["number"]) if isinstance(c["number"], float) and c["number"].is_integer() else c["number"],
        "release_date": c["release_date"]}
        for c in chapters_data[-2:]
    ]

    # Update catalog - now just stores slug
    if slug not in catalog:
        catalog.append(slug)
        print(f"📚 Added {title} to catalog.json")

    # Save the FULL manga data to manga_data folder
    # This keeps all metadata in the individual manga files
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
        "total_chapters": total_chapters,
        "latest_chapters": latest_chapters,
        "chapters": chapters_data
    }

    # Save directly to manga_data folder (update the source file)
    if save_json_if_changed(input_file, manga_json):
        print(f"✅ Updated {title} in manga_data/")
    else:
        print(f"⏭️ No changes for {title}")
    
    return manga_json  # Return for stats calculation


def main():
    # Load catalog.json or create new - now just a list of slugs
    if os.path.exists(CATALOG_FILE):
        with open(CATALOG_FILE, "r", encoding="utf-8") as f:
            try:
                catalog = json.load(f)
                # Handle migration from old format to new format
                if isinstance(catalog, list) and len(catalog) > 0 and isinstance(catalog[0], dict):
                    print("⚠️ Migrating old catalog format to new format (slugs only)")
                    catalog = [m["slug"] for m in catalog if "slug" in m]
            except:
                catalog = []
    else:
        catalog = []

    # Track manga data for stats
    all_manga = []
    
    # Loop through input folder
    for filename in sorted(os.listdir(INPUT_FOLDER)):
        if filename.endswith(".json"):
            input_file = os.path.join(INPUT_FOLDER, filename)
            manga_data = convert_manga_file(input_file, catalog)
            if manga_data:
                all_manga.append(manga_data)

    # Calculate stats from actual manga data
    total_manga = len(all_manga)
    total_chapters = sum(m.get('total_chapters', 0) for m in all_manga)
    
    # Track genre stats
    genre_stats = {}
    for manga in all_manga:
        for genre in manga.get('genres', []):
            if genre in genre_stats:
                genre_stats[genre] += 1
            else:
                genre_stats[genre] = 1
    
    # Sort genres by count, then alphabetically
    sorted_genres = sorted(genre_stats.items(), key=lambda x: (-x[1], x[0]))
    genre_data = [{"name": genre, "count": count} for genre, count in sorted_genres]

    # Save stats.json
    stats_file = os.path.join(OUTPUT_ROOT, "stats.json")
    stats_data = {
        "manga_count": total_manga,
        "chapter_count": total_chapters,
        "genres": genre_data
    }
    save_json_if_changed(stats_file, stats_data)

    # Save updated catalog.json (now just slugs)
    save_json_if_changed(CATALOG_FILE, catalog)
    print("🎉 All manga converted/updated successfully!")
    print(f"📊 Stats: {total_manga} manga, {total_chapters} chapters")
    print(f"📁 catalog.json now contains {len(catalog)} slugs")


if __name__ == "__main__":
    main()
