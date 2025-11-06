#!/usr/bin/env python3
"""
Display all bookmarks from the manga application database.
"""
import sqlite3
from pathlib import Path

def show_bookmarks():
    """Display all bookmarks in a formatted table."""
    db_path = Path(__file__).parent.parent / 'manga_app.db'
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, user_id, manga_title, manga_thumbnail, chapter_number, chapter_title, created_at FROM bookmark ORDER BY created_at DESC')
        bookmarks = cursor.fetchall()
        
        if not bookmarks:
            print("No bookmarks found in database")
            return
        
        print(f"\n📚 Bookmarks ({len(bookmarks)} total)")
        print("=" * 100)
        print(f"{'ID':<5} {'User ID':<8} {'Manga Title':<40} {'Chapter':<8} {'Created At':<20}")
        print("-" * 100)
        
        for bookmark in bookmarks:
            bookmark_id, user_id, manga_title, thumbnail, chapter_num, chapter_title, created_at = bookmark
            chapter_display = f"Ch. {chapter_num}" if chapter_num else "N/A"
            manga_display = manga_title[:37] + "..." if len(manga_title) > 40 else manga_title
            created_display = created_at[:19] if created_at else "N/A"
            
            print(f"{bookmark_id:<5} {user_id:<8} {manga_display:<40} {chapter_display:<8} {created_display:<20}")
        
        print("=" * 100)
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    show_bookmarks()