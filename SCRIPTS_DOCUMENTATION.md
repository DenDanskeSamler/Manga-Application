# Scripts Documentation

This document provides an overview of all utility scripts in the Manga Application project.

## Database Management Scripts

### `create_admin.py`
**Purpose:** Create an admin user or list all users in the database.

**Usage:**
```bash
# Create a new admin user (interactive)
python create_admin.py

# List all users
python create_admin.py list
```

**Features:**
- Interactive prompts for username, email, and password
- Checks for existing users
- Hashes passwords securely
- Creates database table if it doesn't exist

---

### `migrate_db.py`
**Purpose:** Add the `is_admin` column to existing user tables.

**Usage:**
```bash
# Run migration
python migrate_db.py

# Make an existing user an admin
python migrate_db.py make-admin <username>
```

**Features:**
- Checks if column exists before adding
- Shows all users after migration
- Can promote existing users to admin

---

### `migrate_new_features.py`
**Purpose:** Comprehensive database migration for new features (admin panel, bookmarks, etc.).

**Usage:**
```bash
python migrate_new_features.py
```

**Features:**
- Creates all tables using SQLAlchemy models
- Adds missing columns to bookmark table (chapter_number, chapter_title)
- Adds missing columns to user table (is_admin, is_disabled)
- Initializes default app settings
- Safe to run multiple times (idempotent)

---

### `migrate_image_index.py`
**Purpose:** Add `image_index` column to ReadingHistory table for image-based scroll restoration.

**Usage:**
```bash
python migrate_image_index.py
```

**Features:**
- Adds image_index column if missing
- Sets default value (0) for existing records
- Enables the new image-based scroll system

---

### `migrate_scroll_offset.py`
**Purpose:** Add `scroll_offset_percent` column for precise positioning within long images.

**Usage:**
```bash
python migrate_scroll_offset.py
```

**Features:**
- Adds scroll_offset_percent column if missing
- Enhances scroll restoration for very long images
- Works in conjunction with image_index

---

### `normalize_thumbnails.py`
**Purpose:** Fix thumbnail paths in the database to use absolute URLs.

**Usage:**
```bash
python normalize_thumbnails.py
```

**Features:**
- Converts relative paths to absolute paths (e.g., `static/...` → `/static/...`)
- Fixes 404 errors on thumbnail images
- Updates bookmark and reading_history tables
- Leaves remote URLs unchanged

---

## Scraper Scripts

### `scraper.py`
**Purpose:** Step 1 - Scrape manga list from the website.

**Usage:**
```bash
python scraper.py
```

**Features:**
- Fetches manga titles and basic info from manhuaus.com
- Saves to `manga_list.json`
- Retry logic with configurable delays
- Stops on 404 (end of pages)

---

### `scraper step 2.py`
**Purpose:** Step 2 - Fetch detailed manga information and chapter lists.

**Usage:**
```bash
python "scraper step 2.py"
```

**Features:**
- Multi-threaded fetching (10 threads by default)
- Extracts full manga details (description, genres, authors, etc.)
- Fetches all chapter information
- Saves individual manga JSON files to `manga_data/`
- Retry logic for failed requests

---

### `scraper step 3.py`
**Purpose:** Step 3 - Download chapter images.

**Usage:**
```bash
python "scraper step 3.py"
```

**Features:**
- Multi-threaded image downloading
- Progress bars with tqdm
- Skips already downloaded images
- Logging to `manga_log.txt`
- Handles rate limiting and retries

---

### `scraper step 4.py`
**Purpose:** Step 4 - Build catalog and organize data.

**Usage:**
```bash
python "scraper step 4.py"
```

**Features:**
- Generates `data/catalog.json` for the web app
- Organizes manga data by folders
- Creates stats file
- Validates data structure

---

### `run_scrapers.py`
**Purpose:** Run all scraper scripts in sequence.

**Usage:**
```bash
python run_scrapers.py
```

**Features:**
- Executes scrapers 1-4 in order
- Handles errors gracefully
- Continues even if step 1 stops on 404

---

### `all_scraper.py`
**Purpose:** Daemon process that continuously runs scrapers in a loop.

**Usage:**
```bash
python all_scraper.py
```

**Features:**
- Runs scraper sequence every 2 hours
- Creates status file for web app monitoring
- Graceful shutdown on SIGINT/SIGTERM
- Logging to `logs/all_scraper.log`

---

## Utility Scripts

### `scripts/show_bookmarks.py`
**Purpose:** Display all bookmarks from the database in a formatted table.

**Usage:**
```bash
python scripts/show_bookmarks.py
```

**Features:**
- Formatted table output
- Shows user ID, manga title, chapter number, creation date
- Color-coded output with emojis

---

### `scripts/show_reading_history.py`
**Purpose:** Display all reading history entries in a formatted table.

**Usage:**
```bash
python scripts/show_reading_history.py
```

**Features:**
- Formatted table output
- Shows manga title, chapter, image index, last read time
- Sorted by most recent first

---

### `tools/scripts/db_manager.py`
**Purpose:** Comprehensive database management tool.

**Usage:**
```bash
# Create database tables
python tools/scripts/db_manager.py init

# Show statistics
python tools/scripts/db_manager.py stats

# Create admin user
python tools/scripts/db_manager.py create-admin

# Make user admin
python tools/scripts/db_manager.py make-admin

# Backup database
python tools/scripts/db_manager.py backup

# Reset database (WARNING: deletes all data)
python tools/scripts/db_manager.py reset
```

**Features:**
- Complete database lifecycle management
- Safe reset with confirmation
- Automatic backup with timestamps
- Uses Flask app context and SQLAlchemy models

---

## Recommended Script Execution Order

### First-Time Setup
1. `python migrate_new_features.py` - Set up database
2. `python create_admin.py` - Create admin user
3. `python run_scrapers.py` - Populate manga data (optional)

### Database Updates
1. `python migrate_image_index.py` - If updating to image-based scroll
2. `python migrate_scroll_offset.py` - For enhanced scroll positioning
3. `python normalize_thumbnails.py` - Fix thumbnail paths

### Maintenance
- `python tools/scripts/db_manager.py stats` - Check database status
- `python tools/scripts/db_manager.py backup` - Before major changes
- `python scripts/show_bookmarks.py` - View bookmarks
- `python scripts/show_reading_history.py` - View reading history

### Data Collection
- `python run_scrapers.py` - One-time scraper run
- `python all_scraper.py` - Continuous scraping daemon

---

## Troubleshooting

### Database Locked Error
If you encounter "database is locked" errors:
1. Stop the running application
2. Close any database viewers
3. Run the script again

### Migration Already Applied
All migration scripts are idempotent - safe to run multiple times. They check if changes already exist before applying.

### Import Errors
Make sure you're in the project root directory and have activated the virtual environment:
```bash
cd "d:\Fbamse\Python\Manga Applications 1"
& .venv\Scripts\Activate.ps1
python <script_name>.py
```

### Missing Dependencies
Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## Notes

- All migration scripts are safe to run multiple times
- Database scripts automatically create tables if they don't exist
- Scraper scripts respect rate limits and include retry logic
- Always backup your database before running reset operations
