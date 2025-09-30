import sqlite3
from pathlib import Path
p=Path('manga_app.db')
conn=sqlite3.connect(p)
c=conn.cursor()
c.execute('SELECT id, manga_title, manga_thumbnail FROM bookmark')
for r in c.fetchall():
    print(r)
conn.close()