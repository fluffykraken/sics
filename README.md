# sics
Simple InfluxDB CleanUp Script for Home Assistant
This script helps **clean up invalid or excessive data points** in an InfluxDB 1.x database.  
It has been **only tested with data from Home Assistant**, where sensor data is stored in InfluxDB.

## 🛠 Features
✅ **Delete or overwrite** values in an InfluxDB measurement  
✅ **Filter by time range** (`START_TIME` and `END_TIME`)  
✅ **Configurable threshold** for identifying invalid data  
✅ **Interactive**  
✅ **Error handling and database connection checks**  
✅ **Works with InfluxDB 1.x (not tested on 2.x)**  
✅ **Only tested with Home Assistant sensor data for entities**  

---

## 📦 Installation & Setup
### **1️⃣ Install Required Dependencies**
Ensure you have Python installed, then install the required packages:
```bash
pip install influxdb
