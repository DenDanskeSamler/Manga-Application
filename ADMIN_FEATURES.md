# Admin Panel and User Management Features

## Overview
The manga application now includes a comprehensive admin panel for managing users and viewing system statistics.

## New Features

### 1. Admin Panel (`/admin`)
- View all registered users
- See system statistics (total users, admins, bookmarks, reading history)
- Manage user accounts (view details, make admin, delete)
- Accessible only to users with admin privileges

### 2. User Management
- **View User Details**: Click "View" to see detailed information about a user
- **Make/Remove Admin**: Toggle admin status for any user (except yourself)
- **Delete User**: Permanently remove a user account and all associated data

### 3. Admin Access Control
- Added `is_admin` field to User model
- Admin-only decorator protects sensitive routes
- Admin link appears in header for admin users

## Database Changes

### New Column
- Added `is_admin` BOOLEAN column to `user` table (defaults to `false`)

### Migration
The application automatically adds the `is_admin` column when started. For existing installations, run:

```bash
python migrate_db.py
```

## Creating Admin Users

### Method 1: Database Script (Recommended)
```bash
# Create a new admin user
python create_admin.py

# Or migrate existing database and make user admin
python migrate_db.py make-admin <username>
```

### Method 2: Database Manager (When SQLAlchemy works)
```bash
python tools/scripts/db_manager.py create-admin
python tools/scripts/db_manager.py make-admin
```

## Admin Panel Features

### Dashboard
- **Total Users**: Count of all registered users
- **Administrators**: Number of admin users
- **Total Bookmarks**: All bookmarks across users
- **Reading History Items**: Total reading history entries

### User Management Table
- **User ID**: Unique identifier
- **Username**: Display name
- **Email**: Contact email
- **Admin Status**: Badge for admin users
- **Created Date**: Registration date
- **Actions**: View, Make/Remove Admin, Delete

### User Detail Page
- Complete user information
- Statistics (bookmarks count, reading history count)
- List of user's bookmarks with thumbnails
- Reading history with timestamps
- Chapter progress tracking

### Delete User Functionality
- **Safety Features**:
  - Cannot delete your own account
  - Requires username confirmation
  - Shows what will be deleted (bookmarks, history, etc.)
  - Cascaded deletion (automatically removes associated data)

## Security Features

1. **Admin-Only Access**: All admin routes require admin privileges
2. **Self-Protection**: Admins cannot modify their own admin status or delete themselves
3. **Confirmation Required**: User deletion requires typing the username exactly
4. **Audit Trail**: All admin actions can be logged

## API Endpoints (Admin)

- `GET /admin` - Admin dashboard
- `GET /admin/user/<id>` - User detail view
- `GET|POST /admin/delete-user/<id>` - Delete user form and processing
- `POST /admin/toggle-admin/<id>` - Toggle user admin status

## Navigation

- Admin users see an "Admin" link in the header navigation
- Link is styled in red to indicate elevated privileges
- Only visible when logged in as an admin user

## Forms

### DeleteUserForm
- `user_id`: Hidden field with user ID
- `confirm_username`: Text field requiring exact username match
- CSRF protection enabled

### Admin Toggle
- Simple POST requests for toggling admin status
- No form needed (uses button submissions)

## Templates

- `admin/panel.html` - Main admin dashboard
- `admin/user_detail.html` - Individual user details
- `admin/delete_user.html` - User deletion confirmation

## Usage Examples

### Making First Admin
After installation:
```bash
# Run migration
python migrate_db.py

# Make existing user admin
python migrate_db.py make-admin your_username
```

### Creating New Admin User
```bash
# Create new admin user from scratch
python create_admin.py
# Follow prompts to enter username, email, password
```

### Accessing Admin Panel
1. Log in as an admin user
2. Click "Admin" link in header
3. Manage users from the dashboard

## Troubleshooting

### SQLAlchemy Issues
If you encounter SQLAlchemy compatibility issues:
```bash
pip install "SQLAlchemy==1.4.50"
pip install "Flask-SQLAlchemy==3.0.5"
```

### Missing Admin Column
If the `is_admin` column is missing:
```bash
python migrate_db.py
```

### Making User Admin
To grant admin privileges to an existing user:
```bash
python migrate_db.py make-admin <username>
```

## Best Practices

1. **Create Admin First**: Always create at least one admin user after installation
2. **Backup Before Deletions**: Consider backing up the database before deleting users
3. **Limited Admin Access**: Only give admin privileges to trusted users
4. **Regular Monitoring**: Check the admin panel regularly for user activity

## Future Enhancements

Potential features for future development:
- User activity logging
- Bulk user operations
- User role system (beyond just admin/user)
- Email notifications for admin actions
- User suspension/activation
- Export user data functionality