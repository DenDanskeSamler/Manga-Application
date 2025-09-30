# Manga Reader Application

A modern web-based manga reading application built with Flask, featuring user authentication, bookmarks, reading history, and personalized categories.

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

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Manga-Application
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

6. **Initialize database**
   ```bash
   python app.py
   # Database tables will be created automatically on first run
   ```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=8000
DATABASE_URL=sqlite:///manga_app.db
```

### Production Configuration

For production deployment:

1. Set `FLASK_ENV=production`
2. Set `FLASK_DEBUG=False`
3. Use a strong, unique `SECRET_KEY`
4. Configure a production database (PostgreSQL recommended)
5. Use a reverse proxy (nginx) with HTTPS

## Usage

### Development

```bash
python app.py
```

The application will be available at `http://127.0.0.1:8000`

### Production

Use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn app:app
```

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
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── models.py           # Database models
├── forms.py            # WTForms form definitions
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── static/
│   ├── styles/        # CSS files
│   ├── js/           # JavaScript utilities
│   ├── templates/    # Jinja2 templates
│   └── Manga/        # Manga image files
└── data/
    ├── catalog.json  # Manga catalog
    ├── stats.json    # Statistics
    └── manga/        # Individual manga data
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