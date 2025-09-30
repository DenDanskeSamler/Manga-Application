import json
import random
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, jsonify, send_file, redirect, url_for, request, flash
from sqlalchemy import text
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from werkzeug.exceptions import BadRequest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our models, forms, and config
from server.src.database.models import db, User, Bookmark, ReadingHistory, AppSettings
from server.src.web.forms import LoginForm, RegistrationForm, DeleteUserForm, MakeAdminForm, RemoveAdminForm, SettingsForm
from server.src.config import config_map

# Get configuration based on environment
config_name = os.environ.get('FLASK_ENV', 'development')
config_class = config_map.get(config_name, config_map['default'])

# Validate production configuration if needed
if config_name == 'production' and not os.environ.get('SECRET_KEY'):
    raise ValueError("SECRET_KEY environment variable must be set in production")

config = config_class()

app = Flask(
    __name__,
    static_folder=str(config.STATIC_DIR),
    template_folder=str(config.TEMPLATE_DIR),
    static_url_path="/static"
)

# Apply configuration
app.config.from_object(config)

# Configure logging
log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
app.logger.setLevel(log_level)

# Initialize extensions
db.init_app(app)

# Initialize database and run migrations
with app.app_context():
    db.create_all()
    
    # Runtime-safe migration: add optional chapter columns to Bookmark if they don't exist
    try:
        # Use string literal for table name to avoid type checker issues
        table_name = 'bookmark'
        res = db.session.execute(text(f"PRAGMA table_info({table_name});")).fetchall()
        existing_cols = [r[1] for r in res]
        altered = False
        if 'chapter_number' not in existing_cols:
            db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN chapter_number INTEGER"))
            altered = True
        if 'chapter_title' not in existing_cols:
            db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN chapter_title VARCHAR(200)"))
            altered = True
        if altered:
            db.session.commit()
            app.logger.info('[migration] Added chapter columns to Bookmark table')
    except Exception as e:
        app.logger.error(f'Migration check error: {e}')
    
    # Runtime-safe migration: add new columns to User if they don't exist
    try:
        user_table = 'user'
        res = db.session.execute(text(f"PRAGMA table_info({user_table});")).fetchall()
        existing_cols = [r[1] for r in res]
        altered = False
        if 'is_admin' not in existing_cols:
            db.session.execute(text(f"ALTER TABLE {user_table} ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL"))
            altered = True
        if 'is_disabled' not in existing_cols:
            db.session.execute(text(f"ALTER TABLE {user_table} ADD COLUMN is_disabled BOOLEAN DEFAULT 0 NOT NULL"))
            altered = True

            altered = True
        if altered:
            db.session.commit()
            app.logger.info('[migration] Added new columns to User table')
    except Exception as e:
        app.logger.error(f'User table migration error: {e}')
    
    # Initialize default settings if they don't exist
    try:
        if not AppSettings.query.first():
            default_settings = [
                ('require_registration', 'false', 'Require user registration to access the site'),
                ('max_users', '1000', 'Maximum number of users allowed')
            ]
            
            for key, value, description in default_settings:
                setting = AppSettings(key=key, value=value, description=description)
                db.session.add(setting)
            
            db.session.commit()
            app.logger.info('[migration] Initialized default settings')
    except Exception as e:
        app.logger.error(f'Settings initialization error: {e}')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Admin required decorator
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_administrator():
            flash('Admin access required.')
            return redirect(url_for('root'))
        return f(*args, **kwargs)
    return decorated_function

# --- Authentication routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('root'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.is_disabled:
                flash('This account has been disabled. Please contact an administrator.')
                return render_template('login.html', form=form)
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('root'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('root'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('root'))

# --- Page routes ---
@app.get("/")
@app.get("/page-<int:page_num>")
def root(page_num=1):
    """Renders the homepage with pagination."""
    return render_template("index.html", current_page=page_num)

@app.get("/latest")
@app.get("/latest/page-<int:page_num>")
def latest(page_num=1):
    """Renders the latest updates page with pagination."""
    return render_template("index.html", current_page=page_num, sort="latest")

@app.get("/popular")
@app.get("/popular/page-<int:page_num>")
def popular(page_num=1):
    """Renders the popular manga page with pagination."""
    return render_template("index.html", current_page=page_num, sort="popular")

@app.get("/manga/<slug>")
def manga_page(slug):
    return render_template("manga.html", slug=slug)

@app.get("/manga/<slug>/chapter-<int:chapter_num>")
def chapter_page(slug, chapter_num):
    # Record reading history if user is logged in
    if current_user.is_authenticated:
        # Get manga details for history
        catalog_path = config.DATA_DIR / "catalog.json"
        if catalog_path.exists():
            try:
                catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
                manga_entry = next((m for m in catalog if m["slug"] == slug), None)
                if manga_entry:
                    # Get or create history entry
                    history_entry = ReadingHistory.query.filter_by(
                        user_id=current_user.id,
                        manga_slug=slug,
                        chapter_number=chapter_num
                    ).first()
                    
                    if history_entry:
                        history_entry.last_read_at = datetime.utcnow()
                    else:
                        history_entry = ReadingHistory(
                            user_id=current_user.id,
                            manga_slug=slug,
                            manga_title=manga_entry.get("title", ""),
                            manga_thumbnail=manga_entry.get("thumbnail", ""),
                            chapter_number=chapter_num
                        )
                        db.session.add(history_entry)
                    
                    db.session.commit()
            except Exception as e:
                print(f"Error recording reading history: {e}")
    
    return render_template("chapter.html", slug=slug, chapter_num=chapter_num)

# User feature pages
@app.get("/bookmarks")
def bookmarks():
    if current_user.is_authenticated:
        bookmarks = Bookmark.query.filter_by(user_id=current_user.id).order_by(Bookmark.created_at.desc()).all()
        return render_template("bookmarks.html", bookmarks=bookmarks)
    return render_template("bookmarks.html", bookmarks=[])

@app.get("/history")
def history():
    if current_user.is_authenticated:
        history = ReadingHistory.query.filter_by(user_id=current_user.id).order_by(ReadingHistory.last_read_at.desc()).all()
        return render_template("history.html", history=history)
    return render_template("history.html", history=[])

@app.get("/random")
def random_manga():
    """Redirect to a random manga page chosen from the catalog.

    If the catalog cannot be read or is empty, fall back to the homepage.
    """
    catalog_path = config.BASE_DIR / "data" / "catalog.json"
    if not catalog_path.exists():
        return redirect(url_for('root'))

    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        if not isinstance(catalog, list) or len(catalog) == 0:
            return redirect(url_for('root'))

        # Pick only entries that have a slug
        slugs = [m.get('slug') for m in catalog if m.get('slug')]
        if not slugs:
            return redirect(url_for('root'))

        chosen = random.choice(slugs)
        return redirect(url_for('manga_page', slug=chosen))
    except Exception:
        return redirect(url_for('root'))

# --- Genre routes (filter by genre) ---
@app.get("/genre/<genre>")
@app.get("/genre/<genre>/page-<int:page_num>")
def genre_page(genre, page_num=1):
    """Renders the homepage but pre-filters by a genre.

    The client-side catalog code will receive the `genre` template variable and
    apply the filter once the catalog is loaded. This keeps rendering fast and
    reuses the existing index.html template.
    """
    # pass the raw genre slug (usually lowercased) to the template
    return render_template("index.html", current_page=page_num, genre=genre)

# --- Catalog and manga APIs ---
@app.get("/api/catalog")
def api_catalog():
    catalog_path = config.DATA_DIR / "catalog.json"
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

@app.get("/api/stats")
def api_stats():
    """Get statistics about the manga catalog."""
    stats_path = config.DATA_DIR / "stats.json"
    if not stats_path.exists():
        return jsonify({"manga_count": 0, "chapter_count": 0})

    try:
        stats = json.loads(stats_path.read_text(encoding="utf-8"))
        return jsonify(stats)
    except Exception:
        return jsonify({"manga_count": 0, "chapter_count": 0})

@app.get("/api/manga/<slug>")
def api_manga(slug: str):
    catalog_path = config.DATA_DIR / "catalog.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except Exception:
        return jsonify({}), 404

    manga_entry = next((m for m in catalog if m["slug"] == slug), None)
    if not manga_entry:
        return jsonify({}), 404

    folder_name = "".join([c for c in slug if c.isalnum()]).title()
    manga_file = config.DATA_DIR / "manga" / folder_name / f"{folder_name}.json"
    if not manga_file.exists():
        return jsonify({}), 404

    try:
        return jsonify(json.loads(manga_file.read_text(encoding="utf-8")))
    except Exception:
        return jsonify({}), 404

@app.get("/api/manga/<slug>/all_chapters")
def api_manga_all_chapters(slug: str):
    folder_name = "".join(c for c in slug if c.isalnum()).title()
    manga_file = config.DATA_DIR / "manga" / folder_name / f"{folder_name}.json"

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
        app.logger.error(f"Error loading chapters for {slug}: {e}")
        return jsonify({"error": "Failed to load chapters"}), 500

# --- Serve local manga images ---
@app.route("/Manga/<slug>/<path:filename>")
def serve_manga_images(slug, filename):
    manga_dir = config.STATIC_DIR / "Manga" / slug
    path = (manga_dir / filename).resolve()

    if not str(path).startswith(str(manga_dir.resolve())):
        return "Not allowed", 403
    if not path.exists():
        return "Not found", 404

    return send_file(path)

# --- API routes for user features ---
@app.route("/api/bookmark/<slug>", methods=["POST", "DELETE"])
@login_required
def bookmark_api(slug):
    if request.method == "POST":
        # Validate slug input
        if not slug or len(slug) > 200:
            return jsonify({"error": "Invalid manga slug"}), 400
            
        # Add bookmark (or update existing bookmark with chapter info)
        existing = Bookmark.query.filter_by(user_id=current_user.id, manga_slug=slug).first()

        # Optional chapter info from the client
        try:
            data = request.get_json(silent=True) or {}
        except BadRequest:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        chapter_number = data.get('chapter_number')
        chapter_title = data.get('chapter_title')
        
        # Validate chapter data if provided
        if chapter_number is not None:
            try:
                chapter_number = int(chapter_number)
                if chapter_number < 0:
                    return jsonify({"error": "Chapter number must be non-negative"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid chapter number"}), 400
                
        if chapter_title and len(chapter_title) > 200:
            return jsonify({"error": "Chapter title too long"}), 400

        # If bookmark already exists and chapter info provided, update the bookmark
        if existing:
            if chapter_number is not None or chapter_title:
                try:
                    existing.chapter_number = int(chapter_number) if chapter_number is not None else existing.chapter_number
                except Exception:
                    existing.chapter_number = existing.chapter_number
                if chapter_title:
                    existing.chapter_title = chapter_title
                db.session.commit()
                return jsonify({"status": "updated"})
            return jsonify({"status": "already_bookmarked"}), 400

        # Get manga details
        catalog_path = config.DATA_DIR / "catalog.json"
        if catalog_path.exists():
            try:
                catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
                manga_entry = next((m for m in catalog if m["slug"] == slug), None)
                if manga_entry:
                    # Create bookmark and attach optional chapter metadata (nullable)
                    bookmark = Bookmark(
                        user_id=current_user.id,
                        manga_slug=slug,
                        manga_title=manga_entry.get("title", ""),
                        manga_thumbnail=manga_entry.get("thumbnail", ""),
                        chapter_number=int(chapter_number) if chapter_number is not None else None,
                        chapter_title=chapter_title if chapter_title else None
                    )
                    db.session.add(bookmark)
                    db.session.commit()
                    return jsonify({"status": "bookmarked"})
            except Exception as e:
                app.logger.error(f"Error adding bookmark: {e}")
        
        return jsonify({"status": "error"}), 500
    
    elif request.method == "DELETE":
        # Remove bookmark
        bookmark = Bookmark.query.filter_by(user_id=current_user.id, manga_slug=slug).first()
        if bookmark:
            db.session.delete(bookmark)
            db.session.commit()
            return jsonify({"status": "removed"})
        return jsonify({"status": "not_found"}), 404

@app.route("/api/bookmark/check/<slug>")
@login_required  
def check_bookmark(slug):
    bookmark = Bookmark.query.filter_by(user_id=current_user.id, manga_slug=slug).first()
    return jsonify({"bookmarked": bookmark is not None})

@app.route("/api/history/<int:history_id>", methods=["DELETE"])
@login_required
def delete_history_item(history_id):
    history_item = ReadingHistory.query.filter_by(id=history_id, user_id=current_user.id).first()
    if history_item:
        db.session.delete(history_item)
        db.session.commit()
        return jsonify({"status": "deleted"})
    return jsonify({"status": "not_found"}), 404

@app.route("/api/history/clear", methods=["DELETE"])
@login_required
def clear_history():
    ReadingHistory.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({"status": "cleared"})

# --- Admin routes ---
@app.route('/admin')
@admin_required
def admin_panel():
    """Admin panel showing all users and system statistics."""
    users = User.query.order_by(User.created_at.desc()).all()
    
    # Get statistics
    total_users = User.query.count()
    total_admins = User.query.filter_by(is_admin=True).count()
    disabled_users = User.query.filter_by(is_disabled=True).count()
    total_bookmarks = Bookmark.query.count()
    total_history = ReadingHistory.query.count()
    
    stats = {
        'total_users': total_users,
        'total_admins': total_admins,
        'disabled_users': disabled_users,
        'total_bookmarks': total_bookmarks,
        'total_history': total_history
    }
    
    return render_template('admin/panel.html', users=users, stats=stats)

@app.route('/admin/user/<int:user_id>')
@admin_required
def admin_user_detail(user_id):
    """View detailed information about a specific user."""
    user = User.query.get_or_404(user_id)
    user_bookmarks = Bookmark.query.filter_by(user_id=user_id).all()
    user_history = ReadingHistory.query.filter_by(user_id=user_id).order_by(ReadingHistory.last_read_at.desc()).all()
    
    # Group reading history by manga
    grouped_history = {}
    for item in user_history:
        manga_key = item.manga_slug
        if manga_key not in grouped_history:
            grouped_history[manga_key] = {
                'manga_title': item.manga_title,
                'manga_thumbnail': item.manga_thumbnail,
                'manga_slug': item.manga_slug,
                'chapters': [],
                'latest_read': item.last_read_at
            }
        
        grouped_history[manga_key]['chapters'].append({
            'number': item.chapter_number,
            'title': item.chapter_title,
            'read_at': item.last_read_at
        })
        
        # Update latest read time if this chapter was read more recently
        if item.last_read_at > grouped_history[manga_key]['latest_read']:
            grouped_history[manga_key]['latest_read'] = item.last_read_at
    
    # Sort grouped history by latest read time (most recent first)
    grouped_history_list = sorted(grouped_history.values(), key=lambda x: x['latest_read'], reverse=True)
    
    return render_template('admin/user_detail.html', 
                         user=user, 
                         bookmarks=user_bookmarks, 
                         history=user_history,
                         grouped_history=grouped_history_list)

@app.route('/admin/delete-user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_delete_user(user_id):
    """Delete a user account (admin only)."""
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin_panel'))
    
    form = DeleteUserForm()
    
    if form.validate_on_submit():
        if form.confirm_username.data == user.username:
            # Delete user and all associated data (cascaded by relationships)
            username = user.username
            db.session.delete(user)
            db.session.commit()
            flash(f'User "{username}" has been deleted successfully.', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Username confirmation does not match.', 'error')
    
    return render_template('admin/delete_user.html', user=user, form=form)

@app.route('/admin/toggle-admin/<int:user_id>', methods=['POST'])
@admin_required
def admin_toggle_admin(user_id):
    """Toggle admin status of a user."""
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from removing their own admin status
    if user.id == current_user.id:
        flash('You cannot modify your own admin status.', 'error')
        return redirect(url_for('admin_panel'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = "granted" if user.is_admin else "revoked"
    flash(f'Admin privileges {status} for user "{user.username}".', 'success')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/toggle-disabled/<int:user_id>', methods=['POST'])
@admin_required
def admin_toggle_disabled(user_id):
    """Toggle disabled status of a user."""
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from disabling themselves
    if user.id == current_user.id:
        flash('You cannot disable your own account.', 'error')
        return redirect(url_for('admin_panel'))
    
    user.is_disabled = not user.is_disabled
    db.session.commit()
    
    status = "disabled" if user.is_disabled else "enabled"
    flash(f'User "{user.username}" has been {status}.', 'success')
    
    return redirect(url_for('admin_panel'))


@app.route('/admin/delete-user-direct/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user_direct(user_id):
    """Directly delete a user account (admin only). This bypasses the confirmation page and should
    only be used by trusted admins. Prevents deleting your own account."""
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin_panel'))

    username = user.username
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{username}" has been deleted successfully.', 'success')
    except Exception as e:
        app.logger.error(f'Error deleting user {user_id}: {e}')
        db.session.rollback()
        flash('An error occurred while deleting the user.', 'error')

    return redirect(url_for('admin_panel'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    """Admin settings page."""
    form = SettingsForm()
    
    if form.validate_on_submit():
        # Save settings to database
        AppSettings.set_setting('require_registration', form.require_registration.data, 'Require user registration to access the site')
        AppSettings.set_setting('max_users', form.max_users.data or 1000, 'Maximum number of users')
        
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('admin_settings'))
    else:
        # Load current settings
        form.require_registration.data = AppSettings.get_setting('require_registration', False)
        form.max_users.data = AppSettings.get_setting('max_users', 1000)
    
    return render_template('admin/settings.html', form=form)



if __name__ == "__main__":
    app.logger.info(f"[server] Static dir: {config.STATIC_DIR}")
    app.logger.info(f"[server] Template dir: {config.TEMPLATE_DIR}")
    
    # Use environment variables for configuration
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')  # More secure default
    port = int(os.environ.get('FLASK_PORT', '8000'))
    
    if debug_mode:
        app.logger.warning("Running in DEBUG mode - not suitable for production!")
    
    app.run(host=host, port=port, debug=debug_mode)