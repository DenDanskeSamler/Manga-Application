# Manga Reader Application

A modern web-based manga reading application built with Flask. The project has been reorganized to separate server and client code for easier development and deployment.

## Features

- **User Authentication**: Secure user registration and login system
- **Admin Panel**: Comprehensive admin interface for user management
- **User Management**: View, edit, and delete user accounts (admin only)
- **Manga Catalog**: Browse and search through manga collection
- **Reading Interface**: Clean, responsive manga reading experience
- **Bookmarks**: Save favorite manga with chapter-specific bookmarks
- **Reading History**: Track reading progress across devices
- **Categories**: Organize manga into custom categories
- **Responsive Design**: Works on desktop and mobile devices
- **Genre Filtering**: Filter manga by genres with instant results

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLAlchemy with SQLite (easily configurable for PostgreSQL/MySQL)
- **Authentication**: Flask-Login with secure password hashing
- **Forms**: Flask-WTF with CSRF protection
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **UI**: Custom responsive design with dark theme

## Installation

### Prerequisites

- Python 3.10+ (3.12 tested in this workspace)
- pip (Python package installer)

### Setup (quick)

1. Clone the repository and change into it:

```powershell
git clone <repository-url>
cd "Manga-Application"
```

2. Create and activate a virtual environment:

```powershell
# Windows PowerShell
python -m venv .venv
& .venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Create a `.env` from the example and edit values (especially `SECRET_KEY`):

```powershell
copy .env
# Edit .env with your preferred editor
```

5. Run the app (project root `app.py` honors `.env` values for host/port/debug):

```powershell
python app.py
# The server will bind to FLASK_HOST:FLASK_PORT from your .env (default port 8000)
```

6. Create an admin user (after first run):

```powershell
# Method 1: Create new admin user
python create_admin.py

# Manga Reader Application

A lightweight web-based manga reader built with Flask. This README provides a concise, practical guide to get the project running locally on Windows (PowerShell) and explains common admin and maintenance tasks.

## Quick summary

- Language: Python (Flask)
- Database: SQLite by default (SQLAlchemy)
- UI: Server-rendered HTML templates + static assets in `client/`
- Entry point: `app.py` (project root) which loads the Flask app in `server.app`

## Features

- User authentication and sessions
- Admin panel for user & catalog management
- Browse/search manga catalog and view chapter lists
- Reading interface with bookmarks and history
- Category/genre filtering
- Small utility scripts for migrations and maintenance

## Requirements

- Python 3.10+ (3.12 has been used in this workspace)
- pip
- Git (optional, for cloning)

See `requirements.txt` for Python package dependencies.

## Windows (PowerShell) — Quickstart

1. Clone (if needed) and open the project folder:

	git clone <repository-url>
	cd "Manga-Application"

2. Create and activate a virtual environment:

	python -m venv .venv
	# PowerShell
	& .venv\Scripts\Activate.ps1

3. Install dependencies:

	pip install -r requirements.txt

4. Create a `.env` file (if an example exists, copy it). If no example exists, create one with at least `SECRET_KEY`:

	# If there is a .env.example file
	copy .env.example .env

	# Or create a minimal .env manually (example values):
	# SECRET_KEY=replace-me
	# FLASK_ENV=development
	# FLASK_DEBUG=True
	# FLASK_HOST=127.0.0.1
	# FLASK_PORT=8000

5. Initialize or migrate the database (project includes helper scripts):

	# Example: create/upgrade the local DB (script names present in repo)
	python migrate_db.py
	python migrate_new_features.py

6. (Optional) Normalize thumbnails / perform maintenance:

	python normalize_thumbnails.py

7. Start the app:

	# Option A: top-level entrypoint
	python app.py

	# Option B: run Flask app module directly
	& .venv\Scripts\python.exe -m server.app

Open http://127.0.0.1:8000 (or the address set in your `.env`) in your browser.

## Admin tasks

- Create an admin user interactively:

	python create_admin.py

- Promote an existing user to admin (example helper provided):

	python migrate_db.py make-admin <username>

- View logs: see `logs/` and `manga_app.log` for application activity.

## Configuration (.env)

Important settings (common):

- SECRET_KEY — required for sessions and CSRF. Use a strong random string in production.
- FLASK_ENV — `development` or `production`
- FLASK_DEBUG — `True`/`False`
- FLASK_HOST — host to bind (default `127.0.0.1`)
- FLASK_PORT — port to bind (default `8000`)
- DATABASE_URL — optional SQLAlchemy connection string (sqlite by default)
- AUTO_START_SCRAPERS — `true`/`false` (default: `true`) — automatically start the scraper daemon when the app starts

app.py at project root reads `.env` (if present) and configures the server accordingly.

Security note: Never commit secrets or production `SECRET_KEY` into the repository.

## Scraper System

The application includes an automated scraping system that runs continuously in the background:

- **Auto-start**: By default, the scraper daemon (`all_scraper.py`) starts automatically when you run `app.py`. This can be disabled by setting `AUTO_START_SCRAPERS=false` in your `.env` file.
- **Manual control**: Admins can start the scraper cycle manually from the Admin Panel using the "Start Scraping Cycle" button.
- **Live status**: The Admin Panel displays real-time scraper status, progress, and logs.
- **Continuous operation**: The scraper runs in a loop with configurable intervals (default: 2 hours between cycles).

### Scraper scripts

The scraping process consists of 4 sequential steps:
1. `scraper.py` — Scrape manga list from website
2. `scraper step 2.py` — Fetch manga details and chapters
3. `scraper step 3.py` — Download chapter images
4. `scraper step 4.py` — Build catalog and organize data

Status and progress are tracked in `scraper_status.json` at the project root.

## Running in production

For production, run the Flask WSGI app behind a reverse proxy (NGINX) or with a process manager. Example using Gunicorn (Linux):

	pip install gunicorn
	gunicorn server.app:app -b 0.0.0.0:8000

On Windows, consider using a service wrapper or deploy to a Linux host for production.

## Project layout (important files)

- app.py — top-level entrypoint that loads `server.app`
- server/ — Flask application package (routes, models, config)
- client/ — templates and static assets used by the frontend
- data/ — catalog & stats JSON used by the app
- manga_data/ — raw manga JSON files (content)
- logs/ — log files (application log: `manga_app.log`)
- create_admin.py, migrate_db.py, migrate_new_features.py — helper scripts
- requirements.txt — Python dependencies

## Maintenance & utilities

- Rebuild catalog or regenerate derived data using scripts in `tools/` (see `tools/` for available scripts).
- Use `normalize_thumbnails.py` to standardize thumbnail images and metadata.

## Contributing

1. Fork and branch: `git checkout -b feature/your-feature`
2. Make commits with clear messages
3. Run any existing tests and ensure linting (if configured)
4. Push and open a pull request

Please open issues for bugs or feature requests.

## License

This project is provided under the MIT License. See the `LICENSE` file in the repository for details.

## Support

If you run into problems, include logs from `logs/manga_app.log` and a short description, then open an issue in the GitHub repository.

---

If you'd like, I can also:

- add a small troubleshooting section with common errors seen in this project, or
- create a `.env.example` for the repository (I can draft it and add sensible defaults).

Tell me which follow-up you prefer and I'll make it.
