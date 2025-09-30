#!/usr/bin/env python3
"""
Main entry point for the Manga Application.
This file imports the Flask app from the server directory.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env if present
load_dotenv(project_root / '.env')

# Import the Flask app from the server directory
from server.app import app

if __name__ == "__main__":
    # Read runtime configuration from environment (or fall back to sensible defaults)
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', os.environ.get('PORT', '8000')))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Start the Flask app with explicit host/port so environment settings are honored
    app.run(host=host, port=port, debug=debug_mode)
