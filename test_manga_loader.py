#!/usr/bin/env python3
"""
Test script for the new manga_loader module
Run this to verify the refactoring works correctly
"""
from pathlib import Path
import sys

# Add server to path
sys.path.insert(0, str(Path(__file__).parent))

from server.src.utils.manga_loader import (
    load_catalog_slugs,
    load_manga_by_slug,
    build_catalog_from_manga_data,
    get_manga_chapter
)

def test_manga_loader():
    """Test all manga_loader functions."""
    
    print("=" * 60)
    print("Testing Manga Loader Module")
    print("=" * 60)
    
    # Define paths
    catalog_file = Path("data/catalog.json")
    manga_data_dir = Path("manga_data")
    
    # Test 1: Load catalog slugs
    print("\n1️⃣ Testing load_catalog_slugs()...")
    slugs = load_catalog_slugs(catalog_file)
    print(f"   ✅ Loaded {len(slugs)} slugs from catalog")
    if slugs:
        print(f"   First 5 slugs: {slugs[:5]}")
    
    # Test 2: Load single manga
    print("\n2️⃣ Testing load_manga_by_slug()...")
    if slugs:
        test_slug = slugs[0]
        manga = load_manga_by_slug(test_slug, manga_data_dir)
        if manga:
            print(f"   ✅ Loaded manga: {manga.get('title')}")
            print(f"   - Slug: {manga.get('slug')}")
            print(f"   - Chapters: {manga.get('total_chapters')}")
            print(f"   - Status: {manga.get('status')}")
        else:
            print(f"   ❌ Failed to load manga: {test_slug}")
    
    # Test 3: Build catalog
    print("\n3️⃣ Testing build_catalog_from_manga_data()...")
    # Test with just first 5 slugs for speed
    test_slugs = slugs[:5] if len(slugs) > 5 else slugs
    catalog = build_catalog_from_manga_data(manga_data_dir, test_slugs)
    print(f"   ✅ Built catalog with {len(catalog)} entries")
    if catalog:
        print(f"   First entry: {catalog[0].get('title')}")
        print(f"   Fields: {list(catalog[0].keys())}")
    
    # Test 4: Get specific chapter
    print("\n4️⃣ Testing get_manga_chapter()...")
    if slugs and manga:
        chapter = get_manga_chapter(test_slug, 1, manga_data_dir)
        if chapter:
            print(f"   ✅ Loaded chapter 1")
            print(f"   - Title: {chapter.get('title')}")
            print(f"   - Pages: {len(chapter.get('pages', []))}")
        else:
            print(f"   ⚠️ Chapter 1 not found for {test_slug}")
    
    # Test 5: Verify catalog format
    print("\n5️⃣ Verifying catalog.json format...")
    if slugs:
        if isinstance(slugs[0], str):
            print(f"   ✅ Catalog is in NEW format (list of strings)")
        elif isinstance(slugs[0], dict):
            print(f"   ⚠️ Catalog is in OLD format (list of objects)")
            print(f"   Run: python migrate_catalog.py")
        else:
            print(f"   ❌ Unknown catalog format: {type(slugs[0])}")
    
    print("\n" + "=" * 60)
    print("All Tests Complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_manga_loader()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
