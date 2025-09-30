#!/usr/bin/env python3
"""
Simple script to create an admin user without importing the full app
"""
import os
import sys
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash
from datetime import datetime

# Path to the database
db_path = Path(__file__).parent / "manga_app.db"

def create_admin_user():
    """Create an admin user directly using sqlite3"""
    print("Creating admin user...")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    
    if not all([username, email, password]):
        print("❌ All fields are required")
        return
    
    # Hash the password
    password_hash = generate_password_hash(password)
    created_at = datetime.utcnow().isoformat()
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user table exists, create it if not
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(128),
                is_admin BOOLEAN DEFAULT 0 NOT NULL,
                created_at DATETIME
            )
        """)
        
        # Check if username or email already exists
        cursor.execute("SELECT username FROM user WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            print("❌ Username or email already exists")
            return
        
        # Insert the admin user
        cursor.execute("""
            INSERT INTO user (username, email, password_hash, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, password_hash, True, created_at))
        
        conn.commit()
        print(f"✓ Admin user '{username}' created successfully")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

def show_users():
    """Show all users in the database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, email, is_admin, created_at FROM user")
        users = cursor.fetchall()
        
        if users:
            print("\n📋 Current Users:")
            print("ID | Username | Email | Admin | Created")
            print("-" * 50)
            for user in users:
                admin_status = "Yes" if user[3] else "No"
                print(f"{user[0]} | {user[1]} | {user[2]} | {admin_status} | {user[4]}")
        else:
            print("No users found in database")
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        show_users()
    else:
        create_admin_user()