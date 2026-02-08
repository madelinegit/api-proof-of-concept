import pandas as pd
from geopy.geocoders import Nominatim
import time

# Load CSV
df = pd.read_csv("properties.csv")

# Make sure required columns exist
if "Unit Address" not in df.columns:
    raise Exception("Column 'Unit Address' not found in CSV")

# Create Latitude/Longitude columns if they don't exist
if "Latitude" not in df.columns:
    df["Latitude"] = None

if "Longitude" not in df.columns:
    df["Longitude"] = None

# Geocoder
geolocator = Nominatim(user_agent="property_mapper")

log_lines = []

for i, row in df.iterrows():
    address = row["Unit Address"]

    # Skip rows already geocoded
    if pd.notnull(row["Latitude"]) and pd.notnull(row["Longitude"]):
        print(f"SKIPPED: {address}")
        continue

    try:
        location = geolocator.geocode(address)

        if location:
            df.at[i, "Latitude"] = location.latitude
            df.at[i, "Longitude"] = location.longitude
            print(f"OK: {address}")
            log_lines.append(f"OK: {address}")
        else:
            print(f"FAILED: {address}")
            log_lines.append(f"FAILED: {address}")

        time.sleep(1)  # avoid rate limiting

    except Exception as e:
        print(f"ERROR: {address}")
        log_lines.append(f"ERROR: {address}")

# Save updated CSV
df.to_csv("properties_geocoded.csv", index=False)

# Save log
with open("geocode_log.txt", "w", encoding="utf-8") as f:
    for line in log_lines:
        f.write(line + "\n")

print("\nFinished.")
print("Saved: properties_geocoded.csv")
print("Saved: geocode_log.txt")
