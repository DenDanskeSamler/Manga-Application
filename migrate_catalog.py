#!/usr/bin/env python3
"""
Migration Script: Convert catalog.json from old format to new format
Old format: List of manga objects with full metadata
New format: List of manga slugs only

Run this script to migrate your existing catalog.json to the new format.
The old catalog will be backed up as catalog.json.backup
"""
import json
import os
from pathlib import Path
from datetime import datetime

def migrate_catalog():
    """Migrate catalog.json from old format (objects) to new format (slugs only)."""
    
    # Define paths
    data_dir = Path("data")
    catalog_file = data_dir / "catalog.json"
    backup_file = data_dir / f"catalog.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if not catalog_file.exists():
        print(f"❌ catalog.json not found at {catalog_file}")
        return False
    
    # Load existing catalog
    try:
        with open(catalog_file, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
    except Exception as e:
        print(f"❌ Error reading catalog.json: {e}")
        return False
    
    # Check if already in new format
    if isinstance(catalog, list) and len(catalog) > 0:
        if isinstance(catalog[0], str):
            print("✅ catalog.json is already in new format (list of slugs)")
            return True
        elif not isinstance(catalog[0], dict):
            print(f"⚠️ Unknown catalog format: {type(catalog[0])}")
            return False
    
    # Backup old catalog
    print(f"📦 Creating backup at {backup_file}")
    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False
    
    # Extract slugs from old format
    slugs = []
    for manga in catalog:
        if isinstance(manga, dict) and "slug" in manga:
            slugs.append(manga["slug"])
    
    if not slugs:
        print("⚠️ No slugs found in catalog")
        return False
    
    # Save new format
    print(f"💾 Converting {len(slugs)} manga entries to new format")
    try:
        with open(catalog_file, 'w', encoding='utf-8') as f:
            json.dump(slugs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Error saving new catalog: {e}")
        print(f"⚠️ Restoring from backup...")
        # Restore backup
        with open(backup_file, 'r', encoding='utf-8') as fb:
            old_data = json.load(fb)
        with open(catalog_file, 'w', encoding='utf-8') as f:
            json.dump(old_data, f, ensure_ascii=False, indent=2)
        return False
    
    print(f"✅ Successfully migrated catalog.json!")
    print(f"   - Old format backed up to: {backup_file}")
    print(f"   - New format contains {len(slugs)} slugs")
    print(f"\nℹ️ The new catalog.json only contains manga slugs.")
    print(f"   All metadata is now loaded from manga_data/*.json files on-demand.")
    
    return True


def verify_manga_data():
    """Verify that all slugs in catalog have corresponding manga_data files."""
    
    catalog_file = Path("data/catalog.json")
    manga_data_dir = Path("manga_data")
    
    if not catalog_file.exists():
        print("❌ catalog.json not found")
        return
    
    if not manga_data_dir.exists():
        print(f"❌ manga_data directory not found at {manga_data_dir}")
        return
    
    # Load catalog
    with open(catalog_file, 'r', encoding='utf-8') as f:
        slugs = json.load(f)
    
    # Check each slug
    missing = []
    found = 0
    
    for slug in slugs:
        manga_file = manga_data_dir / f"{slug}.json"
        if manga_file.exists():
            found += 1
        else:
            missing.append(slug)
    
    print(f"\n📊 Verification Results:")
    print(f"   ✅ Found: {found} manga files")
    if missing:
        print(f"   ❌ Missing: {len(missing)} manga files")
        print(f"\n   Missing files:")
        for slug in missing[:10]:  # Show first 10
            print(f"      - {slug}.json")
        if len(missing) > 10:
            print(f"      ... and {len(missing) - 10} more")
    else:
        print(f"   ✅ All manga files present!")


if __name__ == "__main__":
    print("=" * 60)
    print("Catalog Migration Script")
    print("=" * 60)
    print()
    
    # Run migration
    success = migrate_catalog()
    
    if success:
        print()
        # Verify all files exist
        verify_manga_data()
    
    print()
    print("=" * 60)
    print("Migration Complete")
    print("=" * 60)
