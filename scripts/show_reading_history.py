#!/usr/bin/env python3
"""
Display all reading history entries from the manga application database.
"""
import sqlite3
from pathlib import Path

def show_reading_history():
    """Display all reading history in a formatted table."""
    db_path = Path(__file__).parent.parent / 'manga_app.db'
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, manga_title, manga_thumbnail, chapter_number, 
                   scroll_position, image_index, scroll_offset_percent, last_read_at 
            FROM reading_history 
            ORDER BY last_read_at DESC
        ''')
        history = cursor.fetchall()
        
        if not history:
            print("No reading history found in database")
            return
        
        print(f"\n📖 Reading History ({len(history)} total)")
        print("=" * 120)
        print(f"{'ID':<5} {'User':<6} {'Manga Title':<35} {'Ch.':<6} {'Img':<5} {'Last Read':<20}")
        print("-" * 120)
        
        for entry in history:
            entry_id, user_id, manga_title, thumbnail, chapter_num, scroll_pos, img_idx, scroll_pct, last_read = entry
            manga_display = manga_title[:32] + "..." if len(manga_title) > 35 else manga_title
            chapter_display = str(chapter_num) if chapter_num else "N/A"
            img_display = str(img_idx) if img_idx is not None else "0"
            last_read_display = last_read[:19] if last_read else "N/A"
            
            print(f"{entry_id:<5} {user_id:<6} {manga_display:<35} {chapter_display:<6} {img_display:<5} {last_read_display:<20}")
        
        print("=" * 120)
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    show_reading_history()