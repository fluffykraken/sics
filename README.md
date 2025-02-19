# 🚀 Simple InfluxDB Cleanup Script for Home Assistant (`SICS`)

The **Simple InfluxDB Cleanup Script (SICS)** is a lightweight and efficient tool designed to **clean up invalid or excessive data points** in an **InfluxDB 1.x database**. 

It has been **specifically tested with Home Assistant sensor data**, where sensor spikes and incorrect readings can occur over time.  
With `SICS`, you can **automate the cleanup process** using custom **thresholds** and **time filters**.

---

## 🛠 Features
✅ **Delete or overwrite** values in an InfluxDB measurement  
✅ **Filter by time range** (`START_TIME` and `END_TIME`)  
✅ **Configurable threshold** for identifying invalid data  
✅ **Works with InfluxDB 1.x (not tested on 2.x)**  
✅ **Made for Home Assistant sensor data based on entity_id tags**  

---

## 📦 Installation & Setup
### **1️⃣ Install Required Dependencies**
Ensure you have Python installed, then install the required packages:
```bash
pip install influxdb
```

### **2️⃣ Clone the Repository**
```bash
git clone https://github.com/fluffykraken/sics.git
cd sics
```

### **3️⃣ Configure `config.ini`**
Modify the `config.ini` file to match your setup and requirements.  
⚠️ Do not include comments (e.g., `# this is a comment`) in the `config.ini` file, as they are not supported.

```ini
[DATABASE]
HOST = 192.168.1.100 # your influxDB host
PORT = 8086 # influxDB port
DATABASE = home_assistant  # Your Home Assistant InfluxDB database name
DBUSER = "admin"  # InfluxDB username; set to None if authentication is not required
DBPASSWORD = "mysecurepassword"  # InfluxDB password; set to None if authentication is not required

[CLEANER]
MEASUREMENT = W  # Example: Power measurement
ENTITY_ID = sensor.energy_meter_1  # The entity ID for which you want to modify the data
HRESHOLD = 4200000  # The value threshold; entries above/below this will be deleted or overwritten
COMPARE_MODE = ">"  # Comparison operator: ">" to target values above THRESHOLD, "<" to target values below THRESHOLD
ACTION_MODE = delete  # Options: delete, overwrite
NEW_VALUE = 42  # New value to set when ACTION_MODE = "overwrite"; ignored if ACTION_MODE = "delete"
START_TIME = 2024-02-01T00:00:00Z  # Optional
END_TIME = 2024-02-29T23:59:59Z  # Optional
```
🔹 **Options:**  
- `ACTION_MODE = delete` → **Removes entries** exceeding the threshold  
- `ACTION_MODE = overwrite` → **Replaces values** exceeding the threshold with `NEW_VALUE`  
- If `START_TIME` and `END_TIME` are **not specified**, the script will search the **entire dataset**  

---

## 🚀 Running the Script
Simply execute:
```bash
python sics.py
```

The script will:
1. **Connect to InfluxDB**
2. **Find all matching values** based on the threshold & time range
3. **Display the first and last 10 entries found for better visibility before data modification or deletion.**
4. **Prompt for confirmation before deleting/overwriting**
5. **Process data with a smooth progress bar**

### ** Example Output**
```
================================================
Welcome to the InfluxDB Cleanup Script!
================================================
Influx Host:       192.168.1.100:8086
Influx DB:         home_assistant
Entity_ID:         sensor.energy_meter_1
Measurement:       W
Compare Operator:  >
Threshold:         4200000
Mode:              delete
================================================
👉 Search database for matching entries? (Y/N): y

🔍 Searching the database... ⠹
✅ Database query completed.

🔍 Found entries with value > 4200000: 25

┌───────────────────────────────┬──────────────┐
│        Timestamp              │     Value    │
├───────────────────────────────┼──────────────┤
│ 2024-02-17T10:30:45.123456Z   │    1654321   │
│ 2024-02-17T10:30:50.654321Z   │    1902345   │
│ 2024-02-17T10:31:05.432167Z   │    1704567   │
│ 2024-02-17T10:31:20.321789Z   │    1756789   │
│ 2024-02-17T10:31:35.987654Z   │    1805678   |
| ...                           │              |
└───────────────────────────────┴──────────────┘
... and 5 more entries.

👉 Do you want to delete these values? (Y/N): y

🚀 Starting deletion...
[███████████------] 60.0% (15/25)
✅ All values were successfully deleted.
```

---

## ⚠️ Limitations
🔹 **Only tested with Home Assistant sensor data.**  
🔹 **Not tested with other InfluxDB datasets.**  
🔹 **Designed for InfluxDB 1.x (may not work with 2.x).**
🔹 **Using overwrite mode, writes only entity_id and value at the moment, all other tags e.g. "friendly_name", "device_class",... will be gone**


---

## 🛠 Troubleshooting
❌ **InfluxDB connection error?**  
- Ensure InfluxDB is running:  
  ```bash
  systemctl status influxdb
  ```
- Verify the **IP, port, username, and password** in `config.ini`

❌ **Nothing happens when running the script?**  
- Ensure **Python 3+** is installed:  
  ```bash
  python --version
  ```
- Run the script with explicit Python3:
  ```bash
  python3 influxdb_cleanup.py
  ```

❌ **Script doesn’t find any values?**  
- Check if the `THRESHOLD` is **too high/low**
- If you want to target values below 0, set COMPARE_MODE to "<" and use a negative THRESHOLD e.g. -42000000
- Remove `START_TIME` and `END_TIME` to scan all data  
- Verify the `MEASUREMENT` and `ENTITY_ID` match actual database values in influxDB
---
## ⚠️ Important Notice: Backup & Disclaimer
Before running this script, **ensure you have a full backup of your InfluxDB database**.  
**Data modifications (deletions or overwrites) are irreversible!** If something goes wrong, **your data may be permanently lost**.
Always test on a non-production database first before using it on live data.

### 📌 Backup Recommendation
Run the following command to create a backup before using this script:
```bash
influxd backup -portable /path/to/backup
```
For more details, refer to the [InfluxDB Backup Documentation](https://docs.influxdata.com/influxdb/v1.8/administration/backup_and_restore/).

---

⚠️ **Use this script at your own risk!**  
I take **no responsibility** for any **data loss, corruption, or unintended consequences** resulting from the use of this script.  
By using this script, you **accept full responsibility** for any changes made to your InfluxDB database.  
I am not liable for any damage caused by running this script.
Always test on a **non-production database first** before using it on live data. 

---

## 📜 License
This project is **MIT licensed**. You are free to use, modify, and distribute it.  

---

## 💡 Credits
Created by **fluffykraken**  
Inspired by the need to clean up **spikes and incorrect readings** in InfluxDB for **Home Assistant**, because it's a PITA doing it manually
