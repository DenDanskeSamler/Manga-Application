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
import threading
import re

# Configuration
SCRAPER_SCRIPTS = [
    {"name": "scraper.py", "description": "Scraping manga list from website"},
    {"name": "scraper step 2.py", "description": "Fetching manga details and chapters"},
    {"name": "scraper step 3.py", "description": "Downloading chapter images"},
    {"name": "scraper step 4.py", "description": "Building catalog and organizing data"}
]
LOOP_INTERVAL = 2 * 60 * 60  # 2 hours in seconds
STATUS_FILE = "scraper_status.json"
LOG_FILE = "logs/all_scraper.log"

# For live status messages from scrapers
status_message = None
status_message_lock = threading.Lock()

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
    # Attach live message if present
    global status_message
    with status_message_lock:
        if status_message:
            status_data["live_message"] = status_message
        elif "live_message" in status_data:
            del status_data["live_message"]
    
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        log_message(f"Error updating status file: {e}")

def set_live_message(msg):
    """Set a live status message to be displayed."""
    global status_message, status_data
    with status_message_lock:
        status_message = msg if msg else None
    
    # Update status file immediately if status_data exists
    if 'status_data' in globals() and status_data:
        status_data["last_update"] = datetime.now().isoformat()
        update_status(status_data)

def monitor_scraper_output(process, script_name):
    """Monitor scraper output and extract progress information."""
    try:
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            line = line.strip()
            if line:
                # Log the output
                print(line)
                
                # Try to extract useful info from output
                # Pattern for "Page X" or "Scraping page X"
                page_match = re.search(r'(?:page|Page)\s+(\d+)', line, re.IGNORECASE)
                if page_match:
                    page_num = page_match.group(1)
                    set_live_message(f"{script_name}: Processing page {page_num}")
                
                # Pattern for "Processing X" or "Fetching X"
                elif re.search(r'(?:processing|fetching|scraping)', line, re.IGNORECASE):
                    # Extract first meaningful word after the action
                    set_live_message(f"{script_name}: {line[:80]}")
                
                # Pattern for manga titles or file operations
                elif re.search(r'(?:manga|chapter|saving|writing)', line, re.IGNORECASE):
                    set_live_message(f"{script_name}: {line[:80]}")
    except Exception as e:
        log_message(f"Error monitoring output: {e}")

def run_scraper(script_name, script_description):
    """Run a single scraper script and return its exit code."""
    log_message(f"Starting {script_name}...")
    set_live_message(f"{script_description}...")
    
    try:
        # Run the script, passing the status file path as an env variable
        env = os.environ.copy()
        env["SCRAPER_STATUS_FILE"] = STATUS_FILE
        env["SCRAPER_LIVE_MESSAGE"] = "1"
        
        # Capture output to monitor progress
        result = subprocess.Popen(
            [sys.executable, script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env
        )
        
        # Monitor output in separate thread
        monitor_thread = threading.Thread(
            target=monitor_scraper_output,
            args=(result, script_name),
            daemon=True
        )
        monitor_thread.start()
        
        # Wait for completion
        exit_code = result.wait()
        monitor_thread.join(timeout=2)
        
        set_live_message("")
        log_message(f"{script_name} completed with return code {exit_code}")
        return exit_code
        
    except Exception as e:
        set_live_message("")
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
    
    for idx, script_info in enumerate(SCRAPER_SCRIPTS):
        if not running:
            log_message("Shutdown requested, stopping scraper execution.")
            break

        script_name = script_info["name"]
        script_description = script_info["description"]

        # Set current script and update status before running
        status_data["current_script"] = script_name
        status_data["current_description"] = script_description
        status_data["last_update"] = datetime.now().isoformat()
        update_status(status_data)

        exit_code = run_scraper(script_name, script_description)

        # Immediately update completed scripts and progress
        status_data["completed_scripts"].append({
            "name": script_name,
            "description": script_description,
            "exit_code": exit_code,
            "completed_at": datetime.now().isoformat()
        })
        status_data["last_update"] = datetime.now().isoformat()

        # If not last script, set next script as current for status
        if idx + 1 < len(SCRAPER_SCRIPTS):
            next_script = SCRAPER_SCRIPTS[idx + 1]
            status_data["current_script"] = next_script["name"]
            status_data["current_description"] = next_script["description"]
        else:
            status_data["current_script"] = None
            status_data["current_description"] = None

        update_status(status_data)

        # Check for critical failures (except scraper.py which can exit with 1 on 404)
        if exit_code != 0 and script_name != "scraper.py":
            log_message(f"Critical error in {script_name}, stopping cycle.")
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
