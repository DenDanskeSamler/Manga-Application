# Catalog Refactoring Guide

## Overview
The manga application has been refactored so that **catalog.json** now contains only manga slugs (names), while all detailed metadata is stored in individual **manga_data/*.json** files.

## What Changed?

### Before (Old System)
- **catalog.json**: Large file (~31MB) with full metadata for all manga (title, author, genres, chapters, etc.)
- **data/manga/**: Separate folder structure with individual manga JSON files
- Data duplication between catalog and manga files
- Slow catalog loading due to large file size

### After (New System)
- **catalog.json**: Small file with just manga slugs (e.g., `["one-punch-man", "naruto", ...]`)
- **manga_data/*.json**: Each file contains complete manga data (metadata + chapters)
- No data duplication
- Fast catalog loading, metadata loaded on-demand
- Single source of truth for manga data

## Files Modified

### 1. **scraper step 4 new.py** (New Scraper)
- Creates simple catalog.json with only slugs
- Updates manga_data/*.json files with full metadata
- Run this instead of the old "scraper step 4.py"

### 2. **server/src/utils/manga_loader.py** (New Helper Module)
- `load_manga_by_slug()`: Load single manga data
- `load_all_manga()`: Load all manga data files
- `build_catalog_from_manga_data()`: Build catalog from manga files
- `get_manga_chapter()`: Get specific chapter data
- `load_catalog_slugs()`: Load slugs from catalog.json

### 3. **server/app.py** (Updated Routes)
Updated endpoints to use manga_loader:
- `/api/catalog` - Builds catalog from manga_data files
- `/api/manga/<slug>` - Returns full manga data
- `/api/manga/<slug>/all_chapters` - Returns manga with fixed page URLs
- `/random` - Redirects to random manga
- Reading history and bookmarks now load from manga_data

### 4. **migrate_catalog.py** (Migration Script)
- Converts old catalog.json (objects) to new format (slugs)
- Creates backup before migration
- Verifies all manga files exist

## How to Use

### Step 1: Run Migration (One-time)
```bash
python migrate_catalog.py
```
This will:
- Backup your current catalog.json
- Convert it to the new format (just slugs)
- Verify all manga files exist

### Step 2: Use New Scraper
From now on, use the new scraper:
```bash
python "scraper step 4 new.py"
```

Or rename it to replace the old one:
```bash
# Windows
move "scraper step 4.py" "scraper step 4.old"
move "scraper step 4 new.py" "scraper step 4.py"
```

### Step 3: Run the App
Everything else works the same:
```bash
python app.py
```

## API Changes

### New Endpoints
All these were already in use by the frontend, but now they read from manga_data/:

- `GET /api/catalog` - Returns full catalog built from manga_data files
- `GET /api/manga/<slug>` - Returns complete manga data
- `GET /api/manga/<slug>/all_chapters` - Returns manga with chapter data
- `GET /api/manga/<slug>/chapter/<num>` - Returns specific chapter

### Frontend Compatibility
✅ No frontend changes needed! The frontend was already using the `/api/catalog` endpoint.

## Benefits

### 1. **Faster Initial Load**
- Old catalog.json: ~31MB (31,484 lines)
- New catalog.json: ~100KB (just slugs)
- 300x smaller file size!

### 2. **No Data Duplication**
- Single source of truth in manga_data/*.json
- Catalog generated on-demand from actual data

### 3. **Better Scalability**
- Only load manga data when needed
- Memory efficient for large catalogs
- Easy to cache individual manga

### 4. **Easier Maintenance**
- Update manga data in one place (manga_data/)
- Catalog automatically reflects changes
- Simpler scraper logic

## File Structure

```
project/
├── data/
│   ├── catalog.json          # Just slugs now! ["slug1", "slug2", ...]
│   ├── catalog.json.backup.*  # Auto-created backups
│   └── stats.json            # Generated statistics
│
├── manga_data/               # Source of truth!
│   ├── one-punch-man.json    # Full manga data
│   ├── naruto.json
│   └── ...                   # All manga files
│
├── server/
│   ├── app.py                # Updated to use manga_loader
│   └── src/
│       └── utils/
│           └── manga_loader.py  # New helper functions
│
├── scraper step 4 new.py     # Use this scraper now
├── migrate_catalog.py        # Run once to migrate
└── README_REFACTORING.md     # This file
```

## Troubleshooting

### Catalog loads empty
- Check that catalog.json exists in data/
- Run `python migrate_catalog.py` to convert old format
- Verify manga_data/ directory has .json files

### Manga not found errors
- Ensure manga_data/<slug>.json exists
- Run verification: `python migrate_catalog.py` (has built-in verification)
- Check file naming matches slug exactly

### Slow catalog loading
- If still slow, check if catalog.json is still in old format
- Re-run migration script
- Clear browser cache

## Reverting (If Needed)

If you need to revert to the old system:
1. Restore from backup: `catalog.json.backup.*`
2. Use old "scraper step 4.py"
3. Revert changes to server/app.py (use git)

## Future Improvements

- [ ] Cache built catalog in memory with TTL
- [ ] Add API endpoint to rebuild catalog
- [ ] Implement pagination for large catalogs
- [ ] Add search/filter at API level
- [ ] Compress manga_data files (gzip)

## Questions?

Check the logs:
- `logs/manga_app.log` - Application errors
- Server console - Real-time debugging

---
**Migration Date**: 2025-11-12
**Version**: 2.0 (Refactored Catalog)
