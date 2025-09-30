from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_disabled = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookmarks = db.relationship('Bookmark', backref='user', lazy=True, cascade="all, delete-orphan")
    reading_history = db.relationship('ReadingHistory', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def __init__(self, username=None, email=None, **kwargs):
        super().__init__(**kwargs)
        if username:
            self.username = username
        if email:
            self.email = email
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_administrator(self):
        return self.is_admin
    
    def __repr__(self):
        return f'<User {self.username}>'

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    manga_slug = db.Column(db.String(200), nullable=False)
    manga_title = db.Column(db.String(200), nullable=False)
    manga_thumbnail = db.Column(db.String(500))
    # Optional chapter information for bookmarks (nullable to preserve existing records)
    chapter_number = db.Column(db.Integer)
    chapter_title = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id=None, manga_slug=None, manga_title=None, 
                 manga_thumbnail=None, chapter_number=None, chapter_title=None, **kwargs):
        super().__init__(**kwargs)
        if user_id is not None:
            self.user_id = user_id
        if manga_slug:
            self.manga_slug = manga_slug
        if manga_title:
            self.manga_title = manga_title
        if manga_thumbnail:
            self.manga_thumbnail = manga_thumbnail
        if chapter_number is not None:
            self.chapter_number = chapter_number
        if chapter_title:
            self.chapter_title = chapter_title
    
    __table_args__ = (db.UniqueConstraint('user_id', 'manga_slug', name='_user_manga_bookmark'),)
    
    def __repr__(self):
        return f'<Bookmark {self.manga_title}>'

class ReadingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    manga_slug = db.Column(db.String(200), nullable=False)
    manga_title = db.Column(db.String(200), nullable=False)
    manga_thumbnail = db.Column(db.String(500))
    chapter_number = db.Column(db.Integer, nullable=False)
    chapter_title = db.Column(db.String(200))
    # store last-known scroll position (pixels from top) for this chapter
    scroll_position = db.Column(db.Integer)
    # store last-known scroll percent (0-100) for this chapter
    scroll_percent = db.Column(db.Integer)
    last_read_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id=None, manga_slug=None, manga_title=None, 
                 manga_thumbnail=None, chapter_number=None, chapter_title=None, **kwargs):
        super().__init__(**kwargs)
        if user_id is not None:
            self.user_id = user_id
        if manga_slug:
            self.manga_slug = manga_slug
        if manga_title:
            self.manga_title = manga_title
        if manga_thumbnail:
            self.manga_thumbnail = manga_thumbnail
        if chapter_number is not None:
            self.chapter_number = chapter_number
        if chapter_title:
            self.chapter_title = chapter_title
        if kwargs.get('scroll_position') is not None:
            self.scroll_position = kwargs.get('scroll_position')
        if kwargs.get('scroll_percent') is not None:
            self.scroll_percent = kwargs.get('scroll_percent')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'manga_slug', 'chapter_number', name='_user_manga_chapter_history'),)
    
    def __repr__(self):
        return f'<ReadingHistory {self.manga_title} Ch.{self.chapter_number}>'


class AppSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_setting(key, default_value=None):
        setting = AppSettings.query.filter_by(key=key).first()
        if setting:
            # Try to parse boolean values
            if setting.value.lower() in ['true', 'false']:
                return setting.value.lower() == 'true'
            # Try to parse integer values
            try:
                return int(setting.value)
            except ValueError:
                return setting.value
        return default_value
    
    @staticmethod
    def set_setting(key, value, description=None):
        setting = AppSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
            setting.updated_at = datetime.utcnow()
            if description:
                setting.description = description
        else:
            setting = AppSettings(
                key=key,
                value=str(value),
                description=description
            )
            db.session.add(setting)
        db.session.commit()
        return setting
    
    def __repr__(self):
        return f'<AppSettings {self.key}={self.value}>'