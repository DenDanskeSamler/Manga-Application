"""
All Scrapers - Continuously runs scrapers in sequence with configurable intervals.
Creates a status file that the web app can read to display scraper status.
"""

import subprocess
import sys
import time
import json
import os
from datetime import datetime
import signal

# Configuration
SCRAPER_SCRIPTS = [
    "scraper.py",
    "scraper step 2.py",
    "scraper step 3.py",
    "scraper step 4.py"
]
LOOP_INTERVAL = 2 * 60 * 60  # 2 hours in seconds
STATUS_FILE = "scraper_status.json"
LOG_FILE = "logs/all_scraper.log"

# Global flag for graceful shutdown
running = True

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global running
    print(f"\n[{datetime.now().isoformat()}] Received shutdown signal. Finishing current operation...")
    log_message("Received shutdown signal. Finishing current operation...")
    running = False

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def log_message(message):
    """Write log message to file and console."""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}")

def update_status(status_data):
    """Update the status JSON file."""
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        log_message(f"Error updating status file: {e}")

def run_scraper(script_name):
    """Run a single scraper script and return its exit code."""
    log_message(f"Starting {script_name}...")
    
    status = {
        "running": True,
        "current_script": script_name,
        "start_time": datetime.now().isoformat(),
        "last_update": datetime.now().isoformat(),
        "completed_scripts": [],
        "total_scripts": len(SCRAPER_SCRIPTS),
        "cycle_number": status_data.get("cycle_number", 1)
    }
    update_status(status)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True
        )
        
        log_message(f"{script_name} completed with return code {result.returncode}")
        return result.returncode
        
    except Exception as e:
        log_message(f"Error running {script_name}: {e}")
        return -1

def run_all_scrapers():
    """Run all scraper scripts in sequence."""
    global status_data
    
    cycle_num = status_data.get("cycle_number", 0) + 1
    log_message(f"=== Starting scraper cycle #{cycle_num} ===")
    
    status_data = {
        "running": True,
        "current_script": None,
        "start_time": datetime.now().isoformat(),
        "last_update": datetime.now().isoformat(),
        "completed_scripts": [],
        "total_scripts": len(SCRAPER_SCRIPTS),
        "cycle_number": cycle_num,
        "next_run": None
    }
    update_status(status_data)
    
    for idx, script in enumerate(SCRAPER_SCRIPTS):
        if not running:
            log_message("Shutdown requested, stopping scraper execution.")
            break

        # Set current script and update status before running
        status_data["current_script"] = script
        status_data["last_update"] = datetime.now().isoformat()
        update_status(status_data)

        exit_code = run_scraper(script)

        # Immediately update completed scripts and progress
        status_data["completed_scripts"].append({
            "name": script,
            "exit_code": exit_code,
            "completed_at": datetime.now().isoformat()
        })
        status_data["last_update"] = datetime.now().isoformat()

        # If not last script, set next script as current for status
        if idx + 1 < len(SCRAPER_SCRIPTS):
            status_data["current_script"] = SCRAPER_SCRIPTS[idx + 1]
        else:
            status_data["current_script"] = None

        update_status(status_data)

        # Check for critical failures (except scraper.py which can exit with 1 on 404)
        if exit_code != 0 and script != "scraper.py":
            log_message(f"Critical error in {script}, stopping cycle.")
            break
    
    log_message(f"=== Scraper cycle #{cycle_num} completed ===")
    
    # Mark as not running
    status_data["running"] = False
    status_data["last_update"] = datetime.now().isoformat()
    status_data["end_time"] = datetime.now().isoformat()
    
    if running:
        # Calculate next run time
        next_run = datetime.now().timestamp() + LOOP_INTERVAL
        status_data["next_run"] = datetime.fromtimestamp(next_run).isoformat()
        log_message(f"Next scraper run scheduled at {status_data['next_run']}")
    
    update_status(status_data)

def main():
    """Main loop."""
    global running, status_data
    
    log_message("All scrapers starting...")
    log_message(f"Will run {len(SCRAPER_SCRIPTS)} scripts every {LOOP_INTERVAL/3600} hours")
    
    # Initialize status
    status_data = {
        "running": False,
        "current_script": None,
        "start_time": None,
        "last_update": datetime.now().isoformat(),
        "completed_scripts": [],
        "total_scripts": len(SCRAPER_SCRIPTS),
        "cycle_number": 0,
        "next_run": datetime.now().isoformat()
    }
    update_status(status_data)
    
    try:
        while running:
            # Run all scrapers
            run_all_scrapers()
            
            if not running:
                break
            
            # Wait for the interval before next run
            log_message(f"Waiting {LOOP_INTERVAL/3600} hours before next cycle...")
            
            # Sleep in small increments to allow for graceful shutdown
            sleep_time = 0
            while sleep_time < LOOP_INTERVAL and running:
                time.sleep(10)  # Check every 10 seconds
                sleep_time += 10
    
    except Exception as e:
        log_message(f"Fatal error: {e}")
        status_data["running"] = False
        status_data["error"] = str(e)
        update_status(status_data)
    
    finally:
        log_message("All scrapers stopped.")
        status_data["running"] = False
        status_data["last_update"] = datetime.now().isoformat()
        update_status(status_data)

if __name__ == "__main__":
    main()
