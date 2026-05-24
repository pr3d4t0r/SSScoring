# Back-Fall Detection: Analysis and Design

- **Author:** Eugene Ciurana + Deirdre
- **Date:** 2026-05-24
- **Branch:** 99998-Claude-Code-integration
- **Status:** Design complete, ready for implementation

---

## 1. Problem Statement

Speed skydivers are scored on their mean vertical speed over a 1000 m window.
A skydiver who *falls on their back* inside the scoring window generates an
artificially high `speedAngle` while simultaneously braking — their score is
degraded but the cause is not flagged in the current output.

The diagnostic goal: detect the back-fall onset time and quantify its severity
from FlySight GPS data alone, without additional sensors.

The physics:

- **Forward position (e.g. 86.5°):** belly toward ground, feet in front of
  head, wing-shaped cross-section — optimal aerodynamics.
- **Back-fall position (e.g. 93.5°):** feet exposed to the air, belly facing
  up — air brake.

These two positions have nearly identical `|speedAngle|`. The angle alone
cannot distinguish them.

---

## 2. Why `speedAngle` Is Insufficient

```
speedAngle = arctan(hMetersPerSecond / vMetersPerSecond)
```

Both inputs are **magnitudes**. The GPS velocity vector has no concept of
"body facing forward vs. inverted." At 86.5° and at the 93.5° equivalent
post-flip the GPS sees the same angle, different physics.

Additionally, `hMetersPerSecond = sqrt(velN² + velE²)` — always ≥ 0. It
discards the direction of horizontal travel entirely.

---

## 3. Approach 1: Horizontal Acceleration (Partial Signal, Not Sufficient)

The aerodynamic signature of a back-fall:

- Vertical velocity continues (still falling)
- **Horizontal velocity drops sharply** — the back is now the braking surface

`d(hKMh)/dt` going strongly negative is suspicious. But this is **not
sufficient** alone because horizontal speed decreases in *every* jump — the
skydiver is always decelerating horizontally. A threshold-based trigger
generates false positives on normal deceleration.

```python
DT = 0.2  # FlySight sample interval, seconds
df['hAccelKMhS'] = df['hKMh'].diff() / DT  # km/h per second

BACK_FALL_H_ACCEL_THRESHOLD = -8.0   # km/h/s — tune empirically
BACK_FALL_ANGLE_MIN         = 70.0

backFall = (
    (df['hAccelKMhS'] < BACK_FALL_H_ACCEL_THRESHOLD) &
    (df['speedAngle']  > BACK_FALL_ANGLE_MIN) &
    (df['vKMh']        > 50.0)
)
```

The critical missing piece: this approach cannot detect whether the skydiver
is *still moving in their original direction* or has *reversed*. A back-fall
that happened gradually (common in less experienced jumpers) may decelerate
at a rate indistinguishable from normal flight.

---

## 4. Approach 2: Signed Velocity Projection (Superseded)

`hKMh` is a scalar magnitude — always ≥ 0. The U-shape/hook that coaches
recognise on speed graphs is the horizontal velocity **reversing sign**,
which magnitude-only data represents as decrease → zero → increase.

The fix requires preserving `velN` and `velE` (north/east velocity components,
both **signed**) from the raw FlySight CSV through the pipeline:

```python
def addForwardVelocity(jumpData: pd.DataFrame, nReferenceSamples: int = 10) -> pd.DataFrame:
    velN = jumpData['velN']
    velE = jumpData['velE']
    refN = velN.iloc[:nReferenceSamples].mean()
    refE = velE.iloc[:nReferenceSamples].mean()
    magnitude = np.hypot(refN, refE)
    uN, uE = refN / magnitude, refE / magnitude
    jumpData['hForwardKMh'] = (velN * uN + velE * uE) * 3.6
    return jumpData
```

`hForwardKMh` is positive when moving forward, negative when reversed. The
zero-crossing is the exact moment of direction reversal.

**Why superseded:** requires passing `velN`/`velE` through
`convertFlySight2SSScoring()` — a schema change. A coordinate-based approach
achieves the same result using `latitude`/`longitude`, which are *already in
the DataFrame schema*, with no schema changes required.

---

## 5. Coordinate-Based Direction Detection

### 5.1 The Hook Explained

On a map view, a clean jump is a straight or gently curving line moving away
from the exit point. A back-fall produces a **hairpin**: the ground track
moves away, decelerates, reverses, and moves back toward the exit point. This
is the "hook" or "U shape" that coaches recognise visually.

In time-series space: the distance from the exit point increases monotonically
on a clean jump. On a back-fall, it increases, reaches a maximum, then
**decreases**. The maximum is the onset; the magnitude of the decrease is the
severity.

### 5.2 Two Bad Trajectories

The jump run is the aircraft's line of travel — a **line** in 2D ground
space passing through the exit point. Legal skydivers move away from this
line; back-falling skydivers return toward it. Two distinct cases:

| Case | Who | Bad trajectory |
|---|---|---|
| 1 | Straight tracker | Moves toward exit point (along the jump run, backward) |
| 2 | Turned tracker | Moves toward the jump run line (perpendicular distance decreasing) |

Both cases share the same physical cause — horizontal velocity reversing —
but they appear in different geometric dimensions depending on whether the
skydiver turned post-exit.

**Case 1** is caught by: *distance from exit point decreasing.*

**Case 2** is caught by: *perpendicular distance from the jump run line
decreasing.* Distance from exit point alone can lag in this case if the
skydiver's forward progress along the jump run partially compensates the
lateral collapse.

Decomposing each position into (forward, lateral) components relative to the
jump run reference handles both cases with two clean invariants:

1. Forward component is non-decreasing throughout the scoring window.
2. Lateral absolute value is non-decreasing from turn establishment onward.

---

## 6. Reference Frame: Jump Run from Exit Coordinates

### 6.1 Establishing the Jump Run Direction

The jump run direction is not available as a parameter. It must be derived
from the data. Three options were considered:

| Option | Method | Problem |
|---|---|---|
| Pre-exit data | Use GPS track while on aircraft | Requires pre-exit recording; not always available |
| External config | DZ or meet director provides bearing | Requires input; not self-contained |
| Post-exit inertia | Use first N samples after exit | Self-contained; empirically validated (§7) |

**Selected: first 15 samples (3 seconds) post-exit.**

Exit inertia keeps the skydiver on the aircraft's track for at least 3 seconds
regardless of intended direction — even a skydiver who immediately begins
turning is still predominantly carried forward by momentum during this window.
The mean bearing over these 15 samples is the jump run reference direction.

### 6.2 Reference Frame Construction

```
Origin:           (latitude, longitude) at plotTime = 0
Forward axis:     mean bearing of samples 0–14
Lateral axis:     perpendicular to forward axis (right-hand rule)
```

At each subsequent sample, compute the 2D displacement from the origin
(haversine), decompose into (forward, lateral) signed scalars, and track
both curves over `plotTime`.

### 6.3 Diagnostic Outputs Per Jump

| Output | Definition | Clean jump value |
|---|---|---|
| Back-fall onset time | `plotTime` at max(forward component) | N/A — no maximum |
| Forward reversal depth | `max(forward) − final(forward)` in metres | 0 |
| Lateral reversal depth | `max(lateral_abs) − final(lateral_abs)` in metres | 0 |

A jump with all three outputs at zero is clean. Any non-zero reversal depth
indicates a back-fall with its severity in metres of reversed ground travel.

---

## 7. Empirical Validation

### 7.1 Test File

```
/Users/ciurana/Documents/speed-skydiving/Tracks/26-04-06/08-40-06.CSV
```

FlySight v1, 5 Hz effective sample rate (0.2 s interval), exit at index 8469
(`hMSL` = 4239.4 m), score 482.75 km/h.

### 7.2 Pre-Exit vs. Post-Exit Bearing

Aircraft bearing was estimated from 8 seconds of pre-exit GPS data and
compared to the post-exit bearing at 1-second granularity:

```python
import pandas as pd, numpy as np
from math import radians, degrees, sin, cos, atan2, sqrt

df = pd.read_csv(
    '/Users/ciurana/Documents/speed-skydiving/Tracks/26-04-06/08-40-06.CSV',
    skiprows=(1,), parse_dates=['time'],
)
df.columns = [c.strip() for c in df.columns]

exit_idx = 8469
SAMPLES_PER_SEC = 5

def bearing(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(dlon)
    return (degrees(atan2(x, y)) + 360) % 360
```

**Results:**

| Second | Phase | Bearing (°) | Δ from jump run | H. dist/s (m) |
|-------:|------:|------------:|----------------:|--------------:|
| −8 | pre-exit | 241.8° | −0.9° | 42.4 |
| −7 | pre-exit | 242.2° | −0.4° | 41.1 |
| −6 | pre-exit | 242.6° | −0.1° | 40.1 |
| −5 | pre-exit | 243.2° | +0.5° | 39.2 |
| −4 | pre-exit | 242.9° | +0.2° | 37.9 |
| −3 | pre-exit | 242.0° | −0.7° | 36.1 |
| −2 | pre-exit | 242.5° | −0.1° | 34.7 |
| −1 | pre-exit | 244.1° | +1.4° | 33.0 |
| **0** | **post-exit** | **244.7°** | **+2.0°** | **31.3** |
| **+1** | **post-exit** | **245.3°** | **+2.7°** | **30.0** |
| **+2** | **post-exit** | **245.1°** | **+2.4°** | **27.0** |

Pre-exit bearing is rock-steady within ±1.4°. Post-exit deviation peaks at
**+2.7°** — indistinguishable from pre-exit GPS variance. **The first 3
seconds post-exit are collinear with the jump run.**

### 7.3 Why Mean of All Post-Exit Angles Fails

A candidate alternative — mean bearing over all 25 seconds post-exit — was
tested and **rejected**:

| Window | Mean bearing | Δ from jump run (242.7°) |
|---|---|---|
| Pre-exit 8 s (ground truth) | 242.7° | — |
| Post-exit seconds 0–3 | 245.2° | **+2.5° ✓** |
| Post-exit seconds 0–7 | 247.2° | +4.5° marginal |
| Post-exit seconds 0–24 | 252.9° | **+10.2° ✗** |

Root cause: after the scoring window (~12 s), horizontal speed drops to
4–8 m/s. GPS bearing at that speed is dominated by wind drift and measurement
noise, not direction of travel. Seconds 20–24 show +26° to +36° deviations.
Averaging these into the reference bearing introduces a 10° systematic error
that would generate false positives in the detector.

**Conclusion: use only samples 0–14 (first 15 samples / 3 seconds).**

---

## 8. Aircraft Trajectory vs. Skydiver Trajectory

Aircraft trajectory extrapolated from exit point along jump run bearing
(245.0°) at pre-exit horizontal speed (38.0 m/s / 137 km/h), compared to the
skydiver's actual lat/lon from SSScoring at 1-second intervals.

```python
import sys, numpy as np
sys.path.insert(0, '.')
from ssscoring.flysight import getFlySightDataFromCSVFileName
from ssscoring.calc import convertFlySight2SSScoring, processJump

rawData, tag = getFlySightDataFromCSVFileName(
    '/Users/ciurana/Documents/speed-skydiving/Tracks/26-04-06/08-40-06.CSV'
)
data   = convertFlySight2SSScoring(rawData)
result = processJump(data)
jd     = result.data.reset_index(drop=True)
# Jump run bearing: mean of bearings between samples 0–14
# Aircraft position at t: project_point(exit_lat, exit_lon, bearing=245.0°, dist=38.0*t)
```

**Score: 482.75 km/h | Jump run: 245.0° | Scoring window: 0–23 s**

| t (s) | Skydiver lat | Skydiver lon | Aircraft lat | Aircraft lon | Sep. (m) | AGL (m) |
|------:|-------------:|-------------:|-------------:|-------------:|---------:|--------:|
| 0 | 13.1400347 | 101.0492177 | 13.1400347 | 101.0492177 | 0.0 | 4239.4 |
| 1 | 13.1399143 | 101.0489567 | 13.1398905 | 101.0488996 | 6.7 | 4219.3 |
| 2 | 13.1398015 | 101.0487046 | 13.1397462 | 101.0485814 | 14.7 | 4192.1 |
| 3 | 13.1396991 | 101.0484781 | 13.1396020 | 101.0482633 | 25.6 | 4156.4 |
| 4 | 13.1396113 | 101.0482781 | 13.1394578 | 101.0479451 | 39.9 | 4112.0 |
| 5 | 13.1395387 | 101.0480878 | 13.1393135 | 101.0476270 | 55.8 | 4058.7 |
| 6 | 13.1394745 | 101.0479038 | 13.1391693 | 101.0473088 | 72.8 | 3998.2 |
| 7 | 13.1394155 | 101.0477258 | 13.1390251 | 101.0469907 | 90.7 | 3929.9 |
| 8 | 13.1393548 | 101.0475578 | 13.1388808 | 101.0466726 | 109.4 | 3854.1 |
| 9 | 13.1392799 | 101.0473928 | 13.1387366 | 101.0463544 | 127.6 | 3771.3 |
| 10 | 13.1391888 | 101.0472309 | 13.1385924 | 101.0460363 | 145.4 | 3682.0 |
| 11 | 13.1390941 | 101.0470785 | 13.1384481 | 101.0457181 | 163.9 | 3586.3 |
| 12 | 13.1390162 | 101.0469460 | 13.1383039 | 101.0454000 | 185.2 | 3484.6 |
| 13 | 13.1389602 | 101.0468266 | 13.1381597 | 101.0450818 | 208.8 | 3377.1 |
| 14 | 13.1389255 | 101.0467201 | 13.1380154 | 101.0447637 | 234.8 | 3264.4 |
| 15 | 13.1389008 | 101.0466200 | 13.1378712 | 101.0444456 | 261.8 | 3147.0 |
| 16 | 13.1388701 | 101.0465185 | 13.1377270 | 101.0441274 | 288.4 | 3025.8 |
| 17 | 13.1388192 | 101.0464082 | 13.1375827 | 101.0438093 | 313.2 | 2902.1 |
| 18 | 13.1387792 | 101.0463035 | 13.1374385 | 101.0434911 | 339.1 | 2775.6 |
| 19 | 13.1387559 | 101.0462092 | 13.1372943 | 101.0431730 | 366.8 | 2646.6 |
| 20 | 13.1387469 | 101.0461209 | 13.1371500 | 101.0428549 | 395.7 | 2516.0 |
| 21 | 13.1387478 | 101.0460444 | 13.1370058 | 101.0425367 | 426.4 | 2383.3 |
| 22 | 13.1387535 | 101.0459760 | 13.1368615 | 101.0422186 | 458.0 | 2249.4 |
| 23 | 13.1387626 | 101.0459144 | 13.1367173 | 101.0419005 | 490.6 | 2115.1 |

Separation grows monotonically 0 → 491 m — clean linear divergence as the
aircraft continues horizontally while the skydiver descends. No reversal, no
hook. This is a **clean jump**, correctly characterised.

---

## 9. Implementation Design

### 9.1 What Is Already Available

| Asset | Location | Status |
|---|---|---|
| `latitude`, `longitude` per sample | SSScoring DataFrame schema | ✓ Available |
| `calculateDistance(start, end)` | `ssscoring.calc:153` | ✓ Available |
| `plotTime` column | Added by `processJump()` | ✓ Available |
| `hMetersPerSecond`, `hKMh` | SSScoring DataFrame schema | ✓ Available |
| Partial `distanceFromExit` logic | `ssscoring.calc:374–392` | Partial — per tranche, not per sample |

No schema changes required. `velN`/`velE` are **not** needed.

### 9.2 New Function: `jumpRunBearing`

```python
def jumpRunBearing(jumpData: pd.DataFrame, nSamples: int = 15) -> float:
    """
    Mean bearing over the first nSamples rows of the scoring window.
    Returns bearing in degrees [0, 360).
    """
```

Input: the scoring-window DataFrame (rows where `plotTime >= 0`).
Output: a single float — the jump run reference bearing.

### 9.3 New Function: `forwardLateralDisplacement`

```python
def forwardLateralDisplacement(
    jumpData: pd.DataFrame,
    exitLat: float,
    exitLon: float,
    jumpRunBearing: float,
) -> pd.DataFrame:
    """
    Adds two columns to jumpData:
      forwardM  — signed displacement along jump run (m), positive = ahead
      lateralM  — signed displacement perpendicular to jump run (m)
    """
```

Implementation sketch:

1. For each row, compute haversine distance and bearing from exit point.
2. `forwardM = distance × cos(bearing − jumpRunBearing)`
3. `lateralM = distance × sin(bearing − jumpRunBearing)`

### 9.4 New Function: `detectBackFall`

```python
def detectBackFall(jumpData: pd.DataFrame) -> dict:
    """
    Returns:
      {
        'backFall':          bool,
        'onsetTime':         float | None,   # plotTime seconds
        'forwardReversalM':  float,           # metres reversed on forward axis
        'lateralReversalM':  float,           # metres reversed on lateral axis
      }
    """
```

Logic:

- Compute `jumpRunBearing` from first 15 samples.
- Compute `forwardLateralDisplacement` for all rows.
- `forwardMax` = maximum of `forwardM`; index = onset time.
- `forwardReversalM` = `forwardMax − forwardM.iloc[-1]` (clamp to 0).
- `lateralReversalM` = `lateralM.abs().max() − lateralM.abs().iloc[-1]` (clamp to 0).
- `backFall` = `forwardReversalM > 0` or `lateralReversalM > 0`.

### 9.5 Integration Points

| Where | What |
|---|---|
| `processJump()` in `ssscoring.calc` | Call `detectBackFall()`, attach results to `JumpResults` |
| `JumpResults` namedtuple in `ssscoring.datatypes` | Add `backFall`, `backFallOnset`, `forwardReversalM`, `lateralReversalM` fields |
| `ssscrunner.py` / `appcommon.py` | Surface back-fall flag and severity in the UI |

### 9.6 Deferred: Judges' Visualization

A grey line on the ground-track map overlay:

- Start: exit point `(latitude, longitude)` at `plotTime = 0`
- Direction: `jumpRunBearing`
- Length: `aircraftSpeed × scoringWindowDuration` metres
- `aircraftSpeed`: mean `hMetersPerSecond` over first 15 samples (same window as bearing)

This shows judges where the aircraft was going relative to where the skydiver
actually went, making back-fall onset and severity spatially intuitive.

---

## 10. Test Data

| File | Description | Score | Notes |
|---|---|---|---|
| `/Users/ciurana/Documents/speed-skydiving/Tracks/26-04-06/08-40-06.CSV` | Good jump, FlySight v1, Thailand | 482.75 km/h | Clean — used for all validation above |

A **back-fall jump** sample is needed to validate the detector produces
non-zero reversal depth. Paths will be added here when available.

---

## 11. Summary of Decisions

| Decision | Rationale |
|---|---|
| Use lat/lon, not `velN`/`velE` | No schema change; position is smoother than velocity derivative |
| Use first 15 samples for jump run reference | Empirically validated at ±2.5° vs. pre-exit aircraft bearing |
| Reject mean of all post-exit angles | +10.2° systematic error from low-speed phase pollution |
| Two-axis decomposition (forward + lateral) | Covers both straight and turned back-fall trajectories |
| Severity in metres, not degrees | Metres are physically interpretable; degrees are reference-relative |
