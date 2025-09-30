import sqlite3
from pathlib import Path
p=Path('manga_app.db')
conn=sqlite3.connect(p)
c=conn.cursor()
c.execute('SELECT id, manga_title, manga_thumbnail, chapter_number, last_read_at FROM reading_history')
for r in c.fetchall():
    print(r)
conn.close()