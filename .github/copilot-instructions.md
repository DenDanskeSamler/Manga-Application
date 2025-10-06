# Copilot Instructions for Manga Reader Application

## Project Overview
- **Purpose:** Modern web-based manga reader built with Flask, supporting user authentication, admin management, and a rich manga catalog.
- **Architecture:**
  - `app.py` (root): Entrypoint, loads Flask app from `server/app.py`.
  - `server/`: Flask app code (routes, models, config, logic).
  - `client/`: Frontend templates and static assets.
  - `data/`: Catalog and stats JSON files.
  - `manga_data/`: Individual manga JSON files (content source).
  - `logs/`: Application logs.
  - Utility scripts: `create_admin.py`, `migrate_db.py`, `migrate_new_features.py`, `normalize_thumbnails.py`.

## Developer Workflows
- **Setup:**
  - Create and activate a virtual environment: `python -m venv .venv` then `& .venv\Scripts\Activate.ps1` (Windows PowerShell).
  - Install dependencies: `pip install -r requirements.txt`.
  - Create `.env` (see below for required keys).
- **Run App:**
  - `python app.py` (honors `.env` for host/port/debug).
  - Alternate: `python -m server.app`.
- **Database Migration:**
  - `python migrate_db.py` and/or `python migrate_new_features.py`.
- **Admin User Creation:**
  - `python create_admin.py` (interactive).
- **Maintenance:**
  - `python normalize_thumbnails.py` (standardize thumbnails).
  - Scripts in `tools/` for catalog/data rebuilds.
- **Logs:**
  - Check `logs/manga_app.log` for errors and activity.

## Conventions & Patterns
- **Configuration:**
  - `.env` required; must set `SECRET_KEY`, `FLASK_HOST`, `FLASK_PORT`, etc.
  - Never commit secrets or production keys.
- **Data Flow:**
  - Manga content: JSON files in `manga_data/`.
  - Catalog/stats: `data/catalog.json`, `data/stats.json`.
  - Database: SQLite by default, SQLAlchemy ORM.
- **Frontend:**
  - HTML templates and static files in `client/`.
  - Responsive design, dark theme.
- **Testing & Linting:**
  - No formal test suite detected; validate changes by running the app and checking logs.
- **Production:**
  - For deployment, use Gunicorn (Linux) or a process manager; see README for details.

## Integration Points
- **External:**
  - Flask, SQLAlchemy, Flask-Login, Flask-WTF.
  - No third-party APIs detected; all manga data is local JSON.

## Example Patterns
- Utility scripts for admin and migration tasks (see root scripts).
- Data-driven design: manga and catalog as JSON, not hardcoded.
- Modular separation: server logic vs. client assets.

## Key Files & Directories
- `app.py`, `server/`, `client/`, `data/`, `manga_data/`, `logs/`, `tools/`

## Troubleshooting
- If the app fails to start, check `.env` and `logs/manga_app.log`.
- For database issues, rerun migration scripts.
- For missing thumbnails, run `normalize_thumbnails.py`.

---

**Feedback requested:**
If any section is unclear or missing, please specify which workflows, conventions, or integration points need more detail.
