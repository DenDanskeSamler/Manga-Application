import subprocess
import sys

# Run scraper.py first
print("Running scraper.py...")
result1 = subprocess.run([sys.executable, "scraper.py"])
if result1.returncode != 0:
    print(f"scraper.py stopped with return code {result1.returncode} (likely due to 404)")

# Then run scraper step 2.py
print("Running scraper step 2.py...")
result2 = subprocess.run([sys.executable, "scraper step 2.py"])
if result2.returncode != 0:
    print(f"scraper step 2.py failed with return code {result2.returncode}")
    sys.exit(1)

# Then run scraper step 3.py
print("Running scraper step 3.py...")
result3 = subprocess.run([sys.executable, "scraper step 3.py"])
if result3.returncode != 0:
    print(f"scraper step 3.py failed with return code {result3.returncode}")
    sys.exit(1)

print("Scripts execution completed.")
