import configparser
from influxdb import InfluxDBClient
import sys
import time
import socket
import threading

# Load configuration
config = configparser.RawConfigParser()
config.read("config.ini", encoding="utf-8")

# Database Configuration
HOST = config.get("DATABASE", "HOST")
PORT = config.getint("DATABASE", "PORT")
DATABASE = config.get("DATABASE", "DATABASE")
USERNAME = config.get("DATABASE", "DBUSER", fallback=None)
PASSWORD = config.get("DATABASE", "DBPASSWORD", fallback=None)

# Cleaner Configuration
MEASUREMENT = config.get("CLEANER", "MEASUREMENT")
ENTITY_ID = config.get("CLEANER", "ENTITY_ID")
THRESHOLD = config.getint("CLEANER", "THRESHOLD")
COMPARE_MODE = config.get("CLEANER", "COMPARE_MODE").strip()
ACTION_MODE = config.get("CLEANER", "ACTION_MODE", fallback="delete").strip().lower()
NEW_VALUE = 0.0  # Default value for overwriting

# Validate COMPARE_MODE
if COMPARE_MODE not in [">", "<"]:
    sys.exit("❌ Invalid COMPARE_MODE! Use '>' or '<'.")

# Validate ACTION_MODE
if ACTION_MODE not in ["delete", "overwrite"]:
    sys.exit("❌ Invalid ACTION_MODE! Use 'delete' or 'overwrite'.")

# Validate NEW_VALUE when in overwrite mode
if ACTION_MODE == "overwrite":
    new_value_str = config.get("CLEANER", "NEW_VALUE", fallback="").strip()
    try:
        NEW_VALUE = float(new_value_str) if new_value_str else 0.0
    except ValueError:
        sys.exit("❌ Error: 'NEW_VALUE' in config.ini is not a valid number!")

# Time range filter
START_TIME = config.get("CLEANER", "START_TIME", fallback="")
END_TIME = config.get("CLEANER", "END_TIME", fallback="")

print("\n================================================")
print("Welcome to the InfluxDB Cleanup Script!")
print("================================================")

# Spinner function for database query
def spinner(stop_event):
    spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    while not stop_event.is_set():
        for char in spinner_chars:
            sys.stdout.write(f"\r🔍 Searching the database... {char} ")
            sys.stdout.flush()
            time.sleep(0.1)

# Connect to InfluxDB
try:
    print(f"🔌 Connecting to InfluxDB at {HOST}:{PORT} ...")

    # Check if the host is reachable
    try:
        socket.create_connection((HOST, PORT), timeout=3)
    except (socket.timeout, ConnectionRefusedError):
        sys.exit(f"❌ No connection to InfluxDB at {HOST}:{PORT}. Is the server online?")

    client = InfluxDBClient(host=HOST, port=PORT, username=USERNAME, password=PASSWORD)

    # Test database connection
    if not client.ping():
        sys.exit("❌ InfluxDB is not responding. Is the service running?")

    # Check if the database exists
    dbs = [db['name'] for db in client.get_list_database()]
    if DATABASE not in dbs:
        sys.exit(f"❌ The database '{DATABASE}' does not exist on the server {HOST}.")

    # Set database
    client.switch_database(DATABASE)
    print(f"✅ Connected to InfluxDB. Database '{DATABASE}' selected.")

except Exception as e:
    sys.exit(f"\n❌ Connection error: {e}")

# Display settings
print("================================================")
print("Settings for Data Cleanup:")
print("================================================")
print(f"Influx Host:       {HOST}:{PORT}")
print(f"Influx DB:         {DATABASE}")
print(f"Entity_ID:         {ENTITY_ID}")
print(f"Measurement:       {MEASUREMENT}")
print(f"Compare Operator:  {COMPARE_MODE}")
print(f"Threshold:         {THRESHOLD}")
print(f"Mode:              {ACTION_MODE}")
if ACTION_MODE == "overwrite":
    print(f"Overwrite Value:   {NEW_VALUE}")
print("================================================")

# Confirm before execution
confirm_config = input("👉 Search database for matching entries? (Y/N): ").strip().lower()
if confirm_config != 'y':
    print("🚫 Operation cancelled.")
    client.close()
    sys.exit(0)

# Build query
query = f'''
SELECT time, value FROM "{MEASUREMENT}"
WHERE "entity_id"::tag = '{ENTITY_ID}' AND value {COMPARE_MODE} {THRESHOLD}
'''
if START_TIME and END_TIME:
    query += f" AND time >= '{START_TIME}' AND time <= '{END_TIME}'"

# Start spinner for query execution
stop_spinner = threading.Event()
spinner_thread = threading.Thread(target=spinner, args=(stop_spinner,))
spinner_thread.start()

try:
    result = client.query(query)
    points = list(result.get_points())
    stop_spinner.set()
    spinner_thread.join()
    print("\r✅ Database query completed.                 ")

except Exception as e:
    stop_spinner.set()
    spinner_thread.join()
    sys.exit(f"\n❌ Error retrieving data: {e}")

# Handle query results
total_points = len(points)

if total_points == 0:
    print("✅ No values found. No action required.")
    client.close()
    sys.exit(0)

# Display first 20 results
print(f"\n🔍 Found {total_points} entries with value {COMPARE_MODE} {THRESHOLD}.\n")
print("\n📋 First 20 found values:")
print("┌────────────────────────────────────┬──────────────┐")
print("│        Timestamp                   │     Value    │")
print("├────────────────────────────────────┼──────────────┤")

for point in points[:20]:
    print(f"│ {point['time']}        │ {point['value']:>12} │")

print("└────────────────────────────────────┴──────────────┘")

if total_points > 20:
    print(f"... and {total_points - 20} more entries.")

confirm_points = input(f"\n👉 Do you want to {'delete' if ACTION_MODE == 'delete' else 'overwrite'} these values? (Y/N): ").strip().lower()
if confirm_points != 'y':
    print("🚫 Operation cancelled. No data was modified.")
    client.close()
    sys.exit(0)

# Progress bar function
def update_progress(iteration, total, length=40):
    percent = (iteration / total) * 100
    bar = "█" * int(length * iteration / total) + "-" * (length - int(length * iteration / total))
    sys.stdout.write(f"\r[{bar}] {percent:.1f}% ({iteration}/{total})")
    sys.stdout.flush()

# Execute deletion or overwrite
print(f"\n🚀 Starting {'deletion' if ACTION_MODE == 'delete' else 'overwriting'}...")

for i, point in enumerate(points, start=1):
    time_str = point["time"]
    try:
        if ACTION_MODE == "delete":
            client.query(f'''DELETE FROM "{MEASUREMENT}" WHERE time = '{time_str}' AND "entity_id"::tag = '{ENTITY_ID}' ''')
        else:
            client.write_points([{
                "measurement": MEASUREMENT,
                "tags": {"entity_id": ENTITY_ID},
                "time": time_str,
                "fields": {"value": NEW_VALUE}
            }])
        update_progress(i, total_points)
    except Exception as e:
        print(f"\n❌ Error modifying {time_str}: {e}")

print(f"\n✅ All values successfully {'deleted' if ACTION_MODE == 'delete' else 'overwritten'}.")
client.close()
