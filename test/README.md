# Perpex Watch Face - Testing Architecture

This repository uses a two-pronged testing strategy to ensure software quality, maintainability, and stability across all 6 targeted Garmin hardware variants (MIP and AMOLED displays). We strictly adhere to the Open-Closed Principle (OCP) and Single Responsibility Principle (SRP) by modularizing our testing frameworks.

## 1. Monkey C Unit Tests (`run_tests.sh`)
These tests are written in Monkey C and run natively in the Connect IQ Simulator for each device.
- **`MetricDataTest.mc`**: Validates the core logic of `MetricProvider.mc`. Asserts that the correct string, label, and icon are returned for all 19 metric types. Crucially tests the `has` hardware fallbacks for devices lacking a Barometer or Altimeter (e.g. Venu Sq 2).
- **`SlotPositioningTest.mc`**: Validates the positioning logic dynamically without rendering, ensuring each of the 7 slots returns valid coordinate sets. Tests permutations of slots vs metrics by invoking the provider in a loop.
- **`ThemeAndModeTest.mc`**: Validates `ThemeManager.mc`, ensuring the correct colors are returned based on the currently active theme index, and handles special conditions like AOD mode and Night Mode.

To run all devices:
```bash
./run_tests.sh unit
# or just: ./run_tests.sh
```

To run unit tests for a specific device:
```bash
./run_tests.sh unit fenix7
./run_tests.sh unit fenix847mm
```

## 2. Python Modular Visual UI Tests (`run_ui_tests.py`)
Because it's practically impossible to take a screenshot of all $19^7$ (893 million) combinations of metrics across slots, we created a modular UI Python test runner that systematically modifies `resources/properties.xml`, compiles the `.prg`, boots the simulator, and snapshots the screen. 

The tests are broken down in `test_ui/` to respect SRP:
- **`config_manager.py`**: Intercepts `properties.xml` and swaps slot values temporarily, restoring them upon completion or failure.
- **`simulator_driver.py`**: Manages the Garmin simulator lifecycle, finding screen boundaries, and taking screenshots with mathematical pixel-level diffing.
- **`test_permutations.py`**: Injects 3 sequential permutation configurations that collectively force every single one of the 19 metrics to render on the watch face at least once, testing all 7 slots.
- **`test_themes.py`**: Tests the global color theme configurations (e.g. Red, Teal, Orange).

To run all devices:
```bash
./run_tests.sh ui
```

To run visual UI tests for a single target device:
```bash
./run_tests.sh ui fenix7
./run_tests.sh ui fenix847mm
# Or directly with python:
python3 run_ui_tests.py fenix7
```
This generates an exhaustive `test_output/visual_report.html` gallery containing the visual validations, side-by-side pixel diff masks, and scenario metadata.

## 3. Manual Simulator Validation
If you just want to boot the simulator and manually view the normal watch face (without running any headless unit tests or Python automated UI tests), the bash script includes a helper `sim` mode:

```bash
./run_tests.sh sim fenix7
```
*(You can pass any device ID to the `sim` command, e.g. `epix2`, `venusq2`, `enduro3`).*
