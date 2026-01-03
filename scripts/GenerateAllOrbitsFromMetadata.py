from skyfield.api import load, EarthSatellite, wgs84
import pandas as pd
import numpy as np

# =========================================================
# LOAD TLE FILE
# =========================================================
tle_path = "../data/starlink_tle.txt"

with open(tle_path, "r") as f:
    lines = f.readlines()

# Each satellite has 3 lines: name, line1, line2
satellites = []
for i in range(0, len(lines), 3):
    name = lines[i].strip()
    line1 = lines[i+1].strip()
    line2 = lines[i+2].strip()
    satellites.append((name, line1, line2))

print(f"Loaded {len(satellites)} satellites")

# =========================================================
# TIME SETUP
# =========================================================
ts = load.timescale()
start_time = ts.now()

minutes = np.arange(0, 24 * 60, 10)  # 24 hours, 10 min step
times = ts.utc(
    start_time.utc_datetime().year,
    start_time.utc_datetime().month,
    start_time.utc_datetime().day,
    start_time.utc_datetime().hour,
    start_time.utc_datetime().minute + minutes
)

# =========================================================
# PROPAGATE ORBITS
# =========================================================
rows = []

for name, line1, line2 in satellites[:500]:  # limit for testing
    try:
        sat = EarthSatellite(line1, line2, name, ts)
        geocentric = sat.at(times)
        subpoint = wgs84.subpoint(geocentric)

        for t, lat, lon, alt in zip(
            times,
            subpoint.latitude.degrees,
            subpoint.longitude.degrees,
            subpoint.elevation.m
        ):
            rows.append([
                name,
                t.utc_iso(),
                lat,
                lon,
                alt
            ])

    except Exception as e:
        print(f"⚠️ Skipped {name}: {e}")

# =========================================================
# SAVE OUTPUT
# =========================================================
df = pd.DataFrame(
    rows,
    columns=["Satellite Name", "Time (UTC)", "Latitude", "Longitude", "Altitude (m)"]
)

df.to_csv("../data/all_satellite_orbits.csv", index=False)

print("✅ Orbit generation complete")
print(f"Rows generated: {len(df)}")
