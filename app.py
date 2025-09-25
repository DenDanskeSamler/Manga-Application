import json
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, send_file

BASE_DIR = Path(__file__).parent.resolve()
STATIC_DIR = BASE_DIR / "static"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")


# --- Page routes ---
@app.get("/")
def root():
    return send_from_directory(STATIC_DIR, "home.html")

@app.get("/home")
def home_page():
    return send_from_directory(STATIC_DIR, "home.html")

@app.get("/manga/<slug>")
def manga_page(slug):
    return send_from_directory(STATIC_DIR, "manga.html")


@app.get("/manga/<slug>/chapter-<int:chapter_num>")
def chapter_page(slug, chapter_num):
    return send_from_directory(STATIC_DIR, "chapter.html")


# --- Catalog and manga APIs ---
@app.get("/api/catalog")
def api_catalog():
    catalog_path = BASE_DIR / "data" / "catalog.json"
    if not catalog_path.exists():
        return jsonify([])

    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
        for manga in data:
            chapters = manga.get("chapters", [])
            manga["latest_chapter"] = max((c.get("number", 0) for c in chapters), default=0)
        return jsonify(data)
    except Exception:
        return jsonify([])


@app.get("/api/manga/<slug>")
def api_manga(slug: str):
    catalog_path = BASE_DIR / "data" / "catalog.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except Exception:
        return jsonify({}), 404

    manga_entry = next((m for m in catalog if m["slug"] == slug), None)
    if not manga_entry:
        return jsonify({}), 404

    folder_name = "".join([c for c in slug if c.isalnum()]).title()
    manga_file = BASE_DIR / "data" / "manga" / folder_name / f"{folder_name}.json"
    if not manga_file.exists():
        return jsonify({}), 404

    try:
        return jsonify(json.loads(manga_file.read_text(encoding="utf-8")))
    except Exception:
        return jsonify({}), 404


@app.get("/api/manga/<slug>/all_chapters")
def api_manga_all_chapters(slug: str):
    folder_name = "".join(c for c in slug if c.isalnum()).title()
    manga_file = BASE_DIR / "data" / "manga" / folder_name / f"{folder_name}.json"

    if not manga_file.exists():
        return jsonify({}), 404

    try:
        data = json.loads(manga_file.read_text(encoding="utf-8"))
        for chapter in data.get("chapters", []):
            if "pages" in chapter:
                fixed_pages = []
                for p in chapter["pages"]:
                    if p.startswith(("http://", "https://")):
                        fixed_pages.append(p)
                    else:
                        fixed_pages.append(f"/Manga/{slug}/{p.lstrip('/')}")
                chapter["pages"] = fixed_pages
        return jsonify(data)
    except Exception as e:
        print("Error loading chapters:", e)
        return jsonify({}), 500

# --- Serve local manga images ---
@app.route("/Manga/<slug>/<path:filename>")
def serve_manga_images(slug, filename):
    manga_dir = STATIC_DIR / "Manga" / slug
    path = (manga_dir / filename).resolve()

    if not str(path).startswith(str(manga_dir.resolve())):
        return "Not allowed", 403
    if not path.exists():
        return "Not found", 404

    return send_file(path)


if __name__ == "__main__":
    print(f"[server] Static dir: {STATIC_DIR}")
    #app.run(host="0.0.0.0", port=8000, debug=True)
    app.run(host="0.0.0.0", port=8000, debug=True, ssl_context='adhoc')


