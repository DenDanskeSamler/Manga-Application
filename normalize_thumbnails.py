#!/usr/bin/env python3
"""
Normalize manga_thumbnail values in the SQLite database so local thumbnails
use absolute `/static/...` paths. This fixes 404s where templates render
relative URLs like `static/thumbnail/...` which the browser resolves
relative to the current page (e.g. `/admin/user/static/...`).

Usage:
    python normalize_thumbnails.py

This script updates `bookmark` and `reading_history` tables.
"""
import sqlite3
from pathlib import Path
import re

DB_PATH = Path(__file__).parent / 'manga_app.db'
TABLES = [
    ('bookmark', 'manga_thumbnail'),
    ('reading_history', 'manga_thumbnail')
]

def normalize(value: str) -> str:
    if not value:
        return value
    v = value.strip()
    # Leave remote URLs untouched
    if v.startswith('http://') or v.startswith('https://'):
        return v
    # Already absolute (starts with /static/ or /)
    if v.startswith('/'):
        return v
    # Stored as 'static/thumbnail/...' -> add leading slash
    if v.startswith('static/'):
        return '/' + v
    # Stored as 'thumbnail/...'
    if v.startswith('thumbnail/'):
        return '/static/' + v
    # If it's just filename like 'one-punch-man-thumb.png'
    if re.search(r'\.(png|jpg|jpeg|gif|webp)$', v, re.IGNORECASE):
        return '/static/thumbnail/' + v
    # Fallback: return as-is
    return v


def run():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    total_changed = 0
    for table, col in TABLES:
        try:
            cursor.execute(f"SELECT id, {col} FROM {table}")
        except sqlite3.Error as e:
            print(f"Skipping table {table}: {e}")
            continue

        rows = cursor.fetchall()
        changed = 0
        for row in rows:
            row_id, thumb = row
            if thumb is None:
                continue
            new_thumb = normalize(thumb)
            if new_thumb != thumb:
                cursor.execute(f"UPDATE {table} SET {col} = ? WHERE id = ?", (new_thumb, row_id))
                changed += 1
        if changed:
            conn.commit()
        print(f"Table {table}: {changed} thumbnails normalized")
        total_changed += changed

    print(f"Total thumbnails changed: {total_changed}")
    conn.close()

if __name__ == '__main__':
    run()
