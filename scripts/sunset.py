#!/usr/bin/env python3
"""Sunrise / solar noon / sunset at the venue (NOAA solar algorithm).

Keeps the "Sunset" row in the evening schedule honest whenever the party
date moves. Run it, then update that row in index.html.

    python scripts/sunset.py

Uses a 90.833 deg zenith so it accounts for atmospheric refraction and the
sun's disc radius, which matches published sunset tables to within a minute.
Set TZ to -7 for PDT or -8 for PST depending on the date.
"""

import math
from datetime import date

# Venue: 420 NE 72nd St, Seattle WA 98115 (Green Lake / Ravenna)
LAT, LON, TZ = 47.6805, -122.3210, -7  # PDT on Sep 19

def julian_day(d):
    y, m, dd = d.year, d.month, d.day
    if m <= 2:
        y -= 1; m += 12
    A = y // 100
    B = 2 - A + A // 4
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + dd + B - 1524.5

def sun_events(d, lat, lon, tz):
    jd = julian_day(d)
    T = (jd - 2451545.0) / 36525.0
    L0 = (280.46646 + T*(36000.76983 + T*0.0003032)) % 360
    M  = 357.52911 + T*(35999.05029 - 0.0001537*T)
    e  = 0.016708634 - T*(0.000042037 + 0.0000001267*T)
    C  = (math.sin(math.radians(M))*(1.914602 - T*(0.004817 + 0.000014*T))
          + math.sin(math.radians(2*M))*(0.019993 - 0.000101*T)
          + math.sin(math.radians(3*M))*0.000289)
    true_long = L0 + C
    app_long  = true_long - 0.00569 - 0.00478*math.sin(math.radians(125.04 - 1934.136*T))
    mean_obl  = 23 + (26 + (21.448 - T*(46.815 + T*(0.00059 - T*0.001813)))/60)/60
    obl_corr  = mean_obl + 0.00256*math.cos(math.radians(125.04 - 1934.136*T))
    decl = math.asin(math.sin(math.radians(obl_corr))*math.sin(math.radians(app_long)))
    y = math.tan(math.radians(obl_corr/2))**2
    eq_time = 4*math.degrees(
        y*math.sin(2*math.radians(L0)) - 2*e*math.sin(math.radians(M))
        + 4*e*y*math.sin(math.radians(M))*math.cos(2*math.radians(L0))
        - 0.5*y*y*math.sin(4*math.radians(L0))
        - 1.25*e*e*math.sin(2*math.radians(M)))
    # 90.833deg accounts for refraction + solar disc radius
    cos_ha = (math.cos(math.radians(90.833))/(math.cos(math.radians(lat))*math.cos(decl))
              - math.tan(math.radians(lat))*math.tan(decl))
    ha = math.degrees(math.acos(max(-1, min(1, cos_ha))))
    noon_min = 720 - 4*lon - eq_time + tz*60
    return (noon_min - ha*4), noon_min, (noon_min + ha*4)

def hhmm(mins):
    mins = round(mins)
    h, m = divmod(int(mins) % 1440, 60)
    ampm = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {ampm}"

for d in (date(2026,9,12), date(2026,9,19), date(2026,9,26), date(2026,8,15)):
    rise, noon, sset = sun_events(d, LAT, LON, TZ)
    tag = " <-- PARTY DATE" if d == date(2026,9,19) else ""
    print(f"{d}  sunrise {hhmm(rise)}   solar noon {hhmm(noon)}   sunset {hhmm(sset)}{tag}")
