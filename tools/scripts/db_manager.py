#!/usr/bin/env python3
"""
Database management script for Manga Application
"""
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from server.app import app
from server.src.database.models import db, User, Bookmark, ReadingHistory


def create_tables():
    """Create all database tables."""
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully")


def drop_tables():
    """Drop all database tables."""
    with app.app_context():
        db.drop_all()
        print("✓ Database tables dropped successfully")


def reset_database():
    """Reset the database (drop and recreate tables)."""
    print("⚠️  This will delete all data. Are you sure? (y/N): ", end="")
    confirm = input().strip().lower()
    if confirm == 'y':
        drop_tables()
        create_tables()
        print("✓ Database reset completed")
    else:
        print("Database reset cancelled")


def backup_database():
    """Create a backup of the database."""
    db_path = Path("manga_app.db")
    if not db_path.exists():
        print("❌ Database file not found")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(f"manga_app_backup_{timestamp}.db")
    
    shutil.copy2(db_path, backup_path)
    print(f"✓ Database backed up to {backup_path}")





def show_stats():
    """Show database statistics."""
    with app.app_context():
        users = User.query.count()
        bookmarks = Bookmark.query.count()
        history = ReadingHistory.query.count()
        
        print("\n📊 Database Statistics:")
        print(f"Users: {users}")
        print(f"Bookmarks: {bookmarks}")
        print(f"Reading History: {history}")


def create_admin_user():
    """Create an admin user."""
    with app.app_context():
        print("Creating admin user...")
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        
        if not all([username, email, password]):
            print("❌ All fields are required")
            return
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            print("❌ Username already exists")
            return
        
        if User.query.filter_by(email=email).first():
            print("❌ Email already registered")
            return
        
        user = User(username=username, email=email)
        user.set_password(password)
        user.is_admin = True  # Set as admin
        db.session.add(user)
        db.session.commit()
        
        print(f"✓ Admin user '{username}' created successfully")


def make_user_admin():
    """Make an existing user an admin."""
    with app.app_context():
        print("Make existing user an admin...")
        username = input("Username: ").strip()
        
        if not username:
            print("❌ Username is required")
            return
        
        user = User.query.filter_by(username=username).first()
        if not user:
            print("❌ User not found")
            return
        
        if user.is_admin:
            print(f"ℹ️  User '{username}' is already an admin")
            return
        
        user.is_admin = True
        db.session.commit()
        
        print(f"✓ User '{username}' is now an admin")


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Database Management Script")
        print("\nUsage: python db_manager.py <command>")
        print("\nCommands:")
        print("  init         - Create database tables")
        print("  reset        - Reset database (WARNING: deletes all data)")
        print("  backup       - Create database backup")
        print("  stats        - Show database statistics")
        print("  create-admin - Create an admin user")
        print("  make-admin   - Make existing user an admin")

        return
    
    command = sys.argv[1].lower()
    
    if command == "init":
        create_tables()
    elif command == "reset":
        reset_database()
    elif command == "backup":
        backup_database()
    elif command == "stats":
        show_stats()
    elif command == "create-admin":
        create_admin_user()
    elif command == "make-admin":
        make_user_admin()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python db_manager.py' to see available commands")


if __name__ == "__main__":
    main()