import requests
import sqlite3
import json

def setup_database():
    with sqlite3.connect("Locations.bd") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            description TEXT,
            latitude REAL,
            longitude REAL
        )
        """)
        conn.commit()

def fetch_nyc_data():
    url = "https://data.cityofnewyork.us/resource/if26-z6xq.json"
    response = requests.get(url)
    data = response.json()
    print(f"Fetched {len(data)} entries from NYC Open Data")
    return data


def save_to_db(data):
    with sqlite3.connect("Locations.bd") as conn:
        cursor = conn.cursor()
        for item in data:
            name = item.get("site_name") or item.get("name") or "Unknown"
            address = item.get("address") or "NYC"
            description = item.get("borough") or "Food Program"

            try:
                lat = float(item.get("latitude"))
                lon = float(item.get("longitude"))
            except:
                continue  # skip entries without coordinates

            cursor.execute("""
                INSERT OR IGNORE INTO locations (name, address, description, latitude, longitude)
                VALUES (?, ?, ?, ?, ?)
            """, (name, address, description, lat, lon))
        conn.commit()

def export_json():
    with sqlite3.connect("Locations.bd") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, address, description, latitude, longitude FROM locations")
        data = [
            {"name": n, "address": a, "description": d, "lat": lat, "lng": lng}
            for n, a, d, lat, lng in cursor.fetchall()
        ]

        with open("locations.json", "w") as f:
            json.dump(data, f, indent=2)

setup_database()
data = fetch_nyc_data()
save_to_db(data)
export_json()
print("JSON file created! Use locations.json in your HTML page.")