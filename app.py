import hashlib
import json
import os
import secrets
import time
from pathlib import Path

from flask import Flask, request, redirect, session, send_from_directory, url_for, jsonify, send_file

BASE_DIR = Path(__file__).parent.resolve()
STATIC_DIR = BASE_DIR / "static"
USERS_FILE = BASE_DIR / "users.json"


def ensure_users_file() -> None:
	if not USERS_FILE.exists():
		USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
		USERS_FILE.write_text("{}", encoding="utf-8")
		print(f"[accounts] Initialized empty users file at {USERS_FILE}")


def load_users() -> dict:
	ensure_users_file()
	try:
		with USERS_FILE.open("r", encoding="utf-8") as f:
			data = json.load(f)
			return data if isinstance(data, dict) else {}
	except Exception:
		return {}


def save_users(users: dict) -> bool:
	try:
		USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
		USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")
		print(f"[accounts] Saved {len(users)} user(s) to {USERS_FILE}")
		return True
	except Exception as exc:
		print(f"[accounts] Failed to save users.json: {exc}")
		return False


def hash_password(password: str, salt: str) -> str:
	return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")  # demo only


def is_logged_in() -> bool:
	return bool(session.get("username"))


@app.before_request
def _ensure_users_file():
	try:
		ensure_users_file()
	except Exception as exc:
		print(f"[accounts] Could not ensure users file: {exc}")


@app.route("/")
def root():
	if is_logged_in():
		return redirect(url_for("home"))
	return send_from_directory(STATIC_DIR, "index.html")


@app.route("/home")
def home_page():
    if not is_logged_in():
        return redirect(url_for("root"))
    return send_from_directory(STATIC_DIR, "home.html")



@app.route("/signup.html")
def signup_page():
	if is_logged_in():
		return redirect(url_for("home"))
	return send_from_directory(STATIC_DIR, "signup.html")


@app.route("/manga/<slug>")
def manga_page(slug):
    if not is_logged_in():
        return redirect(url_for("root"))
    return send_from_directory(STATIC_DIR, "manga.html")


@app.route("/manga/<slug>/chapter-<int:chapter_num>")
def chapter_page(slug, chapter_num):
    if not is_logged_in():
        return redirect(url_for("root"))
    return send_from_directory(STATIC_DIR, "chapter.html")


@app.get("/me")
def me():
	if not is_logged_in():
		return jsonify({"username": None}), 401
	return jsonify({"username": session.get("username")})


@app.post("/login")
def login():
	username = (request.form.get("username") or "").strip()
	password = (request.form.get("password") or "").strip()
	users = load_users()
	user = users.get(username)
	if username and password and user:
		expected = hash_password(password, user.get("salt", ""))
		if expected == user.get("password_hash"):
			session["username"] = username
			return redirect(url_for("home"))
	return redirect(url_for("root", error="invalid"))


@app.post("/signup")
def signup():
	username = (request.form.get("username") or "").strip()
	password = (request.form.get("password") or "").strip()
	if not username:
		return redirect(url_for("signup_page", error="user_missing"))
	if not password:
		return redirect(url_for("signup_page", error="pass_missing"))
	if len(username) < 3:
		return redirect(url_for("signup_page", error="user_short"))
	if len(password) < 4:
		return redirect(url_for("signup_page", error="pass_short"))

	users = load_users()
	if username in users:
		return redirect(url_for("signup_page", error="exists"))

	salt = secrets.token_hex(16)
	password_hash = hash_password(password, salt)
	users[username] = {"salt": salt, "password_hash": password_hash, "created": int(time.time())}
	if not save_users(users):
		return "Failed to save account on server (check write permissions)", 500

	session["username"] = username
	return redirect(url_for("home"))


@app.get("/logout")
def logout():
	session.pop("username", None)
	return redirect(url_for("root"))


# --- Catalog and manga APIs ---
@app.get("/api/catalog")
def api_catalog():
    catalog_path = BASE_DIR / "data" / "catalog.json"
    if not catalog_path.exists():
        return jsonify([])

    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
        # Add latest_chapter number to each manga entry
        for manga in data:
            chapters = manga.get("chapters", [])
            if chapters:
                manga["latest_chapter"] = max(c.get("number", 0) for c in chapters)
            else:
                manga["latest_chapter"] = 0
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
	manga_dir = BASE_DIR / "data" / "manga" / folder_name
	manga_file = manga_dir / f"{folder_name}.json"

	if not manga_file.exists():
		return jsonify({}), 404

	try:
		data = json.loads(manga_file.read_text(encoding="utf-8"))
		return jsonify(data)
	except Exception:
		return jsonify({}), 404


@app.get("/api/manga/<slug>/all_chapters")
def api_manga_all_chapters(slug: str):
	folder_name = "".join([c for c in slug if c.isalnum()]).title()
	manga_dir = BASE_DIR / "data" / "manga" / folder_name
	manga_file = manga_dir / f"{folder_name}.json"  # single file with all chapters

	if not manga_file.exists():
		return jsonify({}), 404

	try:
		data = json.loads(manga_file.read_text(encoding="utf-8"))

		# Rewrite local pages to absolute URLs if needed
		for chapter in data.get("chapters", []):
			if "pages" in chapter:
				chapter["pages"] = [
					p if p.startswith("http") else f"/Manga/{slug}/{p.lstrip('/')}" 
					for p in chapter["pages"]
				]

		return jsonify(data)
	except Exception as e:
		print(f"Error loading chapters: {e}")
		return jsonify({}), 500



# --- Serve local manga images ---
@app.route("/Manga/<slug>/<path:filename>")
def serve_manga_images(slug, filename):
    manga_dir = BASE_DIR / "static" / "manga" / slug
    path = (manga_dir / filename).resolve()

    if not str(path).startswith(str(manga_dir.resolve())):
        return "Not allowed", 403
    if not path.exists():
        return "Not found", 404

    return send_file(path)

@app.route("/Manga/<path:filename>")
def manga_static(filename):
    manga_dir = STATIC_DIR / "Manga"
    path = (manga_dir / filename).resolve()

    if not str(path).startswith(str(manga_dir.resolve())):
        return "Not allowed", 403
    if not path.exists():
        return "Not found", 404

    return send_file(path)



if __name__ == "__main__":
	print(f"[server] Static dir: {STATIC_DIR}")
	print(f"[server] Users file: {USERS_FILE}")
	#app.run(host="127.0.0.1", port=8000, debug=False)
	app.run(host="0.0.0.0", port=8000, debug=False)
	
