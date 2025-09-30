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
    
    __table_args__ = (db.UniqueConstraint('user_id', 'manga_slug', 'chapter_number', name='_user_manga_chapter_history'),)
    
    def __repr__(self):
        return f'<ReadingHistory {self.manga_title} Ch.{self.chapter_number}>'