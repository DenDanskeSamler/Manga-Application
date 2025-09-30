# Manga Reader Application

A modern web-based manga reading application built with Flask. The project has been reorganized to separate server and client code for easier development and deployment.

## Features

- **User Authentication**: Secure user registration and login system
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

## Configuration

### Environment Variables

Configuration is read from a `.env` file (generated from `.env`). Important variables:

- `SECRET_KEY` — required in production; keep secret
- `FLASK_ENV` — `development` / `production` / `testing` (selects config class)
- `FLASK_DEBUG` — `True`/`False` (enables Flask debug reloader)
- `FLASK_HOST` — host interface to bind (default `127.0.0.1`)
- `FLASK_PORT` — port to bind (default `8000` in `.env`)
- `DATABASE_URL` — SQLAlchemy connection string (default SQLite)

The project root `app.py` reads `.env` (if present) and starts the server using those values, so you can change the port in `.env` and simply run `python app.py`.

### Production Configuration

For production deployment:

1. Set `FLASK_ENV=production`
2. Set `FLASK_DEBUG=False`
3. Use a strong, unique `SECRET_KEY`
4. Configure a production database (PostgreSQL recommended)
5. Use a reverse proxy (nginx) with HTTPS

## Usage

### Development

Start the app from the project root. The entrypoint honors values in `.env`:

```powershell
python app.py
```

By default (from `.env`) the app runs at `http://127.0.0.1:8000`.

### Production

Use a WSGI server behind a reverse proxy. Example with Gunicorn (server module path):

```powershell
pip install gunicorn
# From project root
gunicorn server.app:app -b 0.0.0.0:8000
```

Ensure you set `FLASK_ENV=production` and a strong `SECRET_KEY` in your environment when deploying.

## API Endpoints

### Public Endpoints
- `GET /api/catalog` - Get manga catalog
- `GET /api/stats` - Get catalog statistics
- `GET /api/manga/<slug>` - Get manga details
- `GET /api/manga/<slug>/all_chapters` - Get all chapters

### Authenticated Endpoints
- `POST/DELETE /api/bookmark/<slug>` - Manage bookmarks
- `GET /api/bookmark/check/<slug>` - Check bookmark status
- `GET/POST /api/categories` - Manage categories
- `DELETE /api/history/<id>` - Delete history item

## File Structure

```
Manga-Application/
├── app.py                # Project entrypoint (loads server.app and honors .env)
├── server/               # Server-side Flask application
│   ├── app.py           # Flask application (routes, APIs)
│   └── src/
│       ├── config.py    # Configuration classes
│       ├── database/    # SQLAlchemy models
│       └── web/         # Forms and web utilities
├── client/               # Client-side code (templates & static assets)
│   ├── templates/
│   └── static/
├── data/                 # Application data (catalog, stats, manga files)
├── manga_data/           # Raw manga JSON data (large)
├── logs/                 # Log files
├── tools/                # Scrapers and helper scripts
├── requirements.txt
├── .env
└── RESTRUCTURE_NOTES.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security Features

- CSRF protection on all forms
- Secure password hashing with Werkzeug
- SQL injection prevention with SQLAlchemy ORM
- Input validation and sanitization
- Session management with Flask-Login
- Environment-based configuration

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.