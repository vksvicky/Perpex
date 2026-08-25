# Perpex Garmin Watch Face

A heavily customizable, data-rich watch face for Garmin Connect IQ devices. Designed for performance, battery efficiency, and strict compliance with Garmin's AMOLED Always-On Display (AOD) requirements.

## 🌟 Features
- **7 Customizable Data Slots**: Configure Battery, Heart Rate, Steps, Active Calories, Distance, Floors Climbed, Active Minutes, Stress, Altitude, Barometer, Weather, and Solar Events.
- **6 Themed Color Palettes**: Switch between Red (Default), Teal, Warm Orange, Electric Green, Gold, and Pure White.
- **Auto Night Mode**: Automatically dims the watch face based on local sunset/sunrise times or a custom schedule.
- **Battery-Aware Coloring**: Battery indicator changes color dynamically based on charge level (Green > 40%, Yellow < 40%, Red <= 20%).
- **AMOLED Burn-In Protection**: Fully compliant with Garmin's strict <10% active pixel threshold. 

---

## ⌚ Installation (For Users)

1. Download the **Connect IQ Store** app on your smartphone.
2. Search for **Perpex Watch Face** (or use the direct link once published).
3. Tap **Install** and sync your watch.
4. **Customization**: Open the Connect IQ app, go to *My Device > My Watch Faces > Perpex > Settings* to change metrics, colors, and Night Mode preferences.

---

## 🛠️ Development (For Developers)

### Prerequisites
- [Connect IQ SDK](https://developer.garmin.com/connect-iq/sdk/) (v4.2.0 or higher recommended)
- `developer_key.der` placed in the root directory.

### Building & Running
You can use the included bash script to easily compile and run the project:

```bash
# Run headless unit tests (No UI)
./run_tests.sh unit

# Run exhaustive UI Snapshot tests (Generates visual_report.html)
./run_tests.sh ui

# Launch the normal watch face directly in the simulator (e.g., epix2)
./run_tests.sh sim epix2
```

### Memory Profiling
To ensure the watch face stays within strict Garmin memory limits (typically ~114KB - 128KB max for watch faces), use the profiling script:
```bash
./profile_memory.sh
```
This tests the foreground memory peak across multiple devices (fenix7, epix2, enduro3, fenix847mm, fr255, venu3s).

---

## 🧪 Testing & Compliance

### Always-On Display (AOD) Burn-In Protection
Garmin AMOLED devices require watch faces to adhere to strict burn-in protection guidelines in Low Power mode. Specifically, the watch face must use **less than 10% active pixels**, and no single pixel can remain static for more than 3 minutes. 

To ensure compliance, the watch face utilizes a global coordinate shift `(-2 to +2 pixels)` every minute.

**How to verify in the Connect IQ Simulator:**
1. Run `./run_tests.sh sim epix2`.
2. Navigate to **Settings > Low Power Mode**.
3. Navigate to **File > View Heat Map**.
4. Use **Simulation > Time > Fast Forward** to let the simulation run for an extended period.

**Latest Test Results (Epix 2):**
- 24-Hour simulation finished, no screen burn-in detected.
- Peak Luminance Usage: **1.27%** (Well below the 10% limit).

## 📄 License
MIT License. See [ATTRIBUTION.md](ATTRIBUTION.md) for icon and font attributions.
