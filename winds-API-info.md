# Winds Aloft API Research

## Use Case

Worldwide winds data in 1k ft increments between 14k ft and 0k AGL for drop zone
wind profiles.  DZ coordinates and elevations are already available in the DZ
resource CSV.

---

## NOAA Aviation Weather Center API

- **URL:** https://aviationweather.gov/data/api/
- **Coverage:** US only — not suitable for worldwide DZs
- **Auth:** No API key required
- **Rate limits:** 100 req/min total; max 1 req/min per thread
- **Requirements:** Must set a custom `User-Agent` header
- **Verdict:** Dead end for international use

---

## Open-Meteo (recommended)

- **URL:** https://open-meteo.com/en/docs
- **Coverage:** Worldwide (uses GFS + best-available regional model per location)
- **Auth:** None for non-commercial/open-source; API key + commercial license for
  commercial use
- **Cost:** Free tier is genuinely free for non-commercial use
- **Wind data:** Speed and direction at 19 pressure levels (1000 hPa → 30 hPa)

### Relevant pressure levels for 0–14k ft AGL

| Pressure (hPa) | Approx MSL altitude |
|---|---|
| 1000 | ~110 m / ~360 ft |
| 975  | ~320 m / ~1,050 ft |
| 950  | ~540 m / ~1,770 ft |
| 925  | ~770 m / ~2,525 ft |
| 900  | ~1,000 m / ~3,280 ft |
| 850  | ~1,460 m / ~4,790 ft |
| 800  | ~1,950 m / ~6,400 ft |
| 750  | ~2,470 m / ~8,100 ft |
| 700  | ~3,010 m / ~9,875 ft |
| 650  | ~3,600 m / ~11,810 ft |
| 600  | ~4,200 m / ~13,780 ft |

Pressure levels are MSL.  Convert to AGL using DZ elevation from the DZ resource
CSV.  Interpolate to 1k ft AGL grid with standard atmosphere.

### Integration sketch

```python
import openmeteo_requests  # or plain httpx/requests

# DZ lat/lon/elevation already in DZ resource CSV
params = {
    "latitude": dz_lat,
    "longitude": dz_lon,
    "hourly": [
        "wind_speed_1000hPa", "wind_direction_1000hPa",
        "wind_speed_975hPa",  "wind_direction_975hPa",
        "wind_speed_950hPa",  "wind_direction_950hPa",
        "wind_speed_925hPa",  "wind_direction_925hPa",
        "wind_speed_900hPa",  "wind_direction_900hPa",
        "wind_speed_850hPa",  "wind_direction_850hPa",
        "wind_speed_800hPa",  "wind_direction_800hPa",
        "wind_speed_750hPa",  "wind_direction_750hPa",
        "wind_speed_700hPa",  "wind_direction_700hPa",
        "wind_speed_650hPa",  "wind_direction_650hPa",
        "wind_speed_600hPa",  "wind_direction_600hPa",
    ],
}
# interpolate pressure-level MSL altitudes → 1k ft AGL grid using dz_elevation
```
