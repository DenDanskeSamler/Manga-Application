# All Scraper System

Automatically runs all scraper scripts continuously in a loop, displaying status on the admin panel.

## Features

- **Automated Scraping**: Runs all 4 scraper scripts in sequence
- **Continuous Loop**: Automatically reruns every 2 hours (configurable)
- **Status Display**: Shows real-time scraper status in the admin panel
- **Graceful Shutdown**: Safely stops between operations
- **Logging**: Comprehensive logging to track scraper activity

## Files

- `all_scraper.py` - Main script that runs scrapers in a loop
- `scraper_status.json` - Status file (auto-generated, read by web app)
- `logs/all_scraper.log` - Log file

## Quick Start

### Start the scraper

```bash
nohup python3 all_scraper.py &
```

### Check status

**Web Interface (Best way):**
- Go to admin panel at `/admin`
- See "Scraper Status" section showing real-time progress

**Check process:**
```bash
ps aux | grep all_scraper
```

**View logs:**
```bash
tail -f logs/all_scraper.log
```

### Stop the scraper

```bash
# Find the process
ps aux | grep all_scraper

# Kill it
kill <PID>
```

## Configuration

Edit `all_scraper.py` to change settings:

```python
# Configuration
SCRAPER_SCRIPTS = [
    "scraper.py",
    "scraper step 2.py",
    "scraper step 3.py",
    "scraper step 4.py"
]
LOOP_INTERVAL = 2 * 60 * 60  # 2 hours in seconds
```

### Change the loop interval:

- **1 hour**: `LOOP_INTERVAL = 1 * 60 * 60`
- **4 hours**: `LOOP_INTERVAL = 4 * 60 * 60`
- **30 minutes**: `LOOP_INTERVAL = 30 * 60`

## Viewing Status

### Web Interface (Recommended)

1. Go to the admin panel: `http://your-domain/admin`
2. You'll see a "Scraper Status" section showing:
   - Active/Inactive indicator (green pulsing dot when running)
   - Current cycle number
   - Which script is currently running
   - Progress bar showing completion percentage
   - List of completed scripts with exit codes
   - Next scheduled run time (when idle)

The status updates automatically every 10 seconds.

### Command Line

Check the status file:

```bash
cat scraper_status.json
```

View logs in real-time:

```bash
tail -f logs/all_scraper.log
```

## On Server (Linux)

### Starting:

```bash
cd /srv/manga-reader/Manga-Application/
source venv/bin/activate
nohup python3 all_scraper.py &
```

### Checking if it's running:

```bash
ps aux | grep all_scraper
```

### Viewing logs:

```bash
tail -f logs/all_scraper.log
```

### Stopping:

```bash
# Find process
ps aux | grep all_scraper

# Kill it (it will finish current script gracefully)
kill <PID>
```

## How It Works

1. **Main Loop**:
   - Runs all 4 scraper scripts in sequence
   - Updates `scraper_status.json` with current progress
   - Waits 2 hours after completion
   - Repeats forever (until stopped)

2. **Web Status Display**:
   - Flask endpoint `/api/scraper/status` reads the status file
   - Admin panel polls this endpoint every 10 seconds
   - Shows real-time progress and status

3. **Graceful Shutdown**:
   - Responds to SIGTERM/SIGINT signals
   - Finishes current script before stopping
   - Updates status file to show "not running"

## Logs

All activity is logged to `logs/all_scraper.log`:

```
[2025-11-06T10:00:00] All scrapers starting...
[2025-11-06T10:00:00] Will run 4 scripts every 2.0 hours
[2025-11-06T10:00:00] === Starting scraper cycle #1 ===
[2025-11-06T10:00:00] Starting scraper.py...
[2025-11-06T10:05:23] scraper.py completed with return code 0
[2025-11-06T10:05:23] Starting scraper step 2.py...
...
```

## Safe Shutdown

**Important**: The admin panel shows when scrapers are running. Always check before shutting down:

1. Open admin panel at `/admin`
2. Check "Scraper Status" section
3. If showing "Scraper is running", wait for it to complete
4. When it shows "Scraper is not running", it's safe to shut down

## Example Server Usage

```bash
# SSH into server
ssh username@server

# Go to project directory
cd /srv/manga-reader/Manga-Application/

# Activate virtual environment
source venv/bin/activate

# Start all scrapers
nohup python3 all_scraper.py &

# Verify it's running
ps aux | grep all_scraper

# View logs
tail -f logs/all_scraper.log
# Press Ctrl+C to stop viewing

# Later, when you want to stop:
ps aux | grep all_scraper
kill <PID>
```

## Notes

- Runs in the background using nohup
- Survives terminal disconnection
- Does NOT automatically restart on server reboot
- Each scraper cycle takes approximately 5-15 minutes
- The 2-hour interval starts AFTER the previous cycle completes
