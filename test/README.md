# Perpex Watch Face - Testing Architecture

This repository uses a comprehensive two-pronged testing strategy to ensure software quality, visual precision, maintainability, and regression stability across all 9 targeted Garmin hardware variants (both MIP and AMOLED displays).

We adhere to the Open-Closed Principle (OCP) and Single Responsibility Principle (SRP) by modularizing our test frameworks.

---

## Targeted Device Matrix

| Device ID | Hardware Class | Resolution | Display Type |
|---|---|---|---|
| `fenix7s` | Fenix 7S / 7S Pro | 240×240 | Memory-in-Pixel (MIP) |
| `fenix7` | Fenix 7 / Fenix 8 Solar 47mm | 260×260 | MIP Solar |
| `fr255` | Forerunner 255 / 255 Music | 260×260 | MIP Running |
| `enduro3` | Enduro 3 / Fenix 7X / Fenix 8 Solar 51mm | 280×280 | MIP Solar Ultra |
| `venu2s` | Venu 2S | 360×360 | AMOLED Small |
| `epix2pro42mm` | Epix 2 Pro 42mm / Venu 3S | 390×390 | AMOLED Medium |
| `venu2` | Venu 2 / Venu 2 Plus / Epix Gen 2 | 416×416 | AMOLED Standard |
| `venu3` | Venu 3 / Forerunner 965 / Fenix 8 47mm | 454×454 | AMOLED High-Res |
| `venusq2` | Venu Sq 2 | 320×360 | AMOLED Rectangular |

---

## 1. Monkey C Unit Tests (`./run_tests.sh unit`)

These tests are written in Monkey C and run natively in the headless Connect IQ Simulator for each target device.

* **`MetricDataTest.mc`**: Validates the core logic of `MetricProvider.mc`. Asserts that the correct string, label, and icon are returned for all 19 metric types. Tests the `has` hardware fallbacks for devices lacking sensors (e.g. Barometer or Altimeter on Venu Sq 2).
* **`SlotPositioningTest.mc`**: Validates slot coordinate math, resolution scaling across all 5 resolution classes, and asserts strict vertical icon-to-text clearance across all devices.
* **`ThemeAndModeTest.mc`**: Validates `ThemeManager.mc`, ensuring active theme accent colors resolve correctly, battery color gradient thresholds apply properly, and night mode / low-power overrides function as intended.
* **`TestMatrix.mc`**: Runs an exhaustive 40-scenario test matrix verifying boundary string lengths, uniform slot assignments, charging states, and active/AOD transitions.
* **`SunCalc.mc`**: Validates solar sunrise/sunset and civil twilight calculations across multiple global coordinates (London, New York, Svalbard equinox).

### Running Unit Tests:
```bash
# Run unit tests across all devices
./run_tests.sh unit

# Run unit tests for a specific device
./run_tests.sh unit fenix7
./run_tests.sh unit venu3
```

---

## 2. Python Visual UI & Regression Tests (`./run_tests.sh ui`)

Because taking screenshots of all possible metric permutations is infeasible, we use an automated visual UI test harness that systematically modifies `resources/properties.xml`, compiles the `.prg`, boots the simulator, captures screenshots, and validates layouts both programmatically and visually.

The visual test harness lives in `test_ui/` and is organized into modular components:

* **`config_manager.py`**: Intercepts `properties.xml`, injects scenario properties temporarily, and guarantees restoration upon completion or failure.
* **`simulator_driver.py`**: Manages the Connect IQ Simulator lifecycle. Captures screenshots to a temporary buffer, validates circular watch face cropping before saving to disk, and purges stale artifacts and boot-screen frames.
* **`layout_validator.py`**: Programmatic zone-based layout assertion engine (no baseline required):
  - **Dial Sanity**: Confirms the simulator rendered a real dark dial rather than an uninitialized screen.
  - **Slot Rendered**: Verifies active slots contain bright content.
  - **Bezel Overflow**: Confirms pixels do not bleed outside the circular or rectangular screen boundary.
  - **Ring Collision**: Asserts slot content remains within the safe dial area without encroaching onto the concentric date/month rings.
  - **Inter-Slot Overlap**: Derives bounding boxes for adjacent slot pairs `(1,2)`, `(1,3)`, `(2,4)`, `(3,5)`, `(4,6)`, `(5,6)` and asserts no shared pixels outside the central pivot.
* **`image_utils.py`**: Generates a 3-panel composite `[ BASELINE | CURRENT | DIFF ]`:
  - Masks the central analog hand pivot ($r = 15\%$) to eliminate false positives from clock hand movements.
  - Calculates mathematical pixel variance percentage between baseline and current screenshots.
  - Flags visual regressions when variance exceeds $5.0\%$.
* **`test_permutations.py`**: Runs 3 zero-duplicate permutation passes that collectively force every metric (1–21) to render on the watch face.
* **`test_themes.py`**: Validates color themes (Vibrant Red, Teal, Orange, Green, Gold, Pure White) and Night Modes (Red, Amber, Green).
* **`test_weather.py`**: Validates weather condition icons, temperatures, and precipitation formatting.

### Running Visual UI Tests:

```bash
# Run focused visual matrix across all 9 devices (~48 total passes)
./run_tests.sh ui

# Run visual tests for a single device
./run_tests.sh ui --device fenix7s
./run_tests.sh ui --device venu3

# Run exhaustive full matrix (21 passes per device)
./run_tests.sh ui --full
```

---

## 3. Visual Baseline Management (`--update-baselines`)

Visual regression testing compares current screenshots against reference baselines stored in `test_output/baselines/`.

### Capturing & Updating Baselines:
```bash
# Capture fresh baselines for all devices on the current branch
./run_tests.sh ui --update-baselines

# Capture fresh baselines for a single device
./run_tests.sh ui --update-baselines --device fenix7s
```

* **Automatic Backups**: Before modifying `test_output/baselines/`, the runner automatically creates a timestamped backup directory (e.g. `test_output/baselines_backup_20260904_165546/`).
* **Validation Guard**: Baselines are **only** written to disk if screenshot capture succeeds and layout validation passes, preventing corrupted boot screens from polluting reference images.

---

## 4. Interpreting the Visual Report (`test_output/visual_report.html`)

Running `./run_tests.sh ui` produces an interactive gallery at `test_output/visual_report.html`.

### Table Columns:
1. **Pass & Assertions**: Test pass name, description, active slots, pass/fail badge, and any flagged layout or visual regression issues.
2. **Watch Face Screenshot**: Raw cropped screenshot of the current watch face.
3. **Layout Zones & Clearance**: Debug overlay showing:
   - **Green Bounding Boxes**: Passing slot zones with clear margins.
   - **Red Bounding Boxes**: Overlapping, overflowing, or empty slot zones.
   - **Orange Inner Circle**: The boundary of the concentric date/month rings.
   - **Blue Center Circle**: The central hands exclusion boundary ($r = 15\%$).
4. **Baseline Comparison (Diff)**: 3-panel composite:
   - **BASELINE** (blue tinted): The reference baseline on disk.
   - **CURRENT** (green labelled): The newly captured screenshot.
   - **DIFF** (red highlights): Pixel difference overlay showing changes.
   - **Thin Grey Circle in DIFF**: Outlines the $15\%$ central hands mask boundary, indicating the area excluded from diffing to avoid clock hand false positives.

---

## 5. Manual Interactive Simulator (`./run_tests.sh sim`)

To manually interact with the watch face in the Connect IQ Simulator without running automated tests:

```bash
./run_tests.sh sim fenix7
./run_tests.sh sim venu3
./run_tests.sh sim enduro3
```
*(Accepts any valid device ID, e.g. `fenix7s`, `venu2`, `epix2pro42mm`, etc.).*
