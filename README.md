# Perpex Garmin Watch Face

A heavily customizable, data-rich watch face for Garmin Connect IQ devices. Designed for performance, battery efficiency, and strict compliance with Garmin's AMOLED Always-On Display (AOD) requirements.

## 🌟 Features
- **6 Customizable Data Slots**: Configure Battery, Heart Rate, Steps, Active Calories, Distance, Floors Climbed, Active Minutes, Stress, Altitude, Barometer, Weather Temp, Weather Conditions (Precip %, Wind, Humidity), and Solar Events (Sunrise/Sunset/Dynamic).
- **Time Formats**: Support for 12-hour (with standard 'a'/'p' abbreviations) and 24-hour time formats.
- **6 Themed Color Palettes**: Switch between Red (Default), Teal, Warm Orange, Electric Green, Gold, and Pure White.
- **Auto Night Mode**: Automatically dims the watch face based on local sunset/sunrise times or a custom schedule.
- **Battery-Aware Coloring**: Battery indicator changes color dynamically based on charge level (Green > 40%, Yellow < 40%, Red <= 20%).
- **AMOLED Burn-In Protection**: Fully compliant with Garmin's strict <10% active pixel threshold. 

---

## 🌦️ Weather Integration & Data Refresh

Perpex features native weather tracking, dynamic condition icons, and outdoor performance metrics powered by Garmin's Connect IQ `Toybox.Weather` API.

### How It Works (For Users & Developers)
1. **Zero Battery Drain**: Garmin watch faces cannot make direct HTTP web calls. Instead, the **Garmin Connect Mobile app** running on your paired smartphone fetches official weather data in the background based on your phone's GPS location and syncs it to the watch via Bluetooth Low Energy (BLE).
2. **Offline Resilience**: When off-grid or when GPS has not been used recently, the watch face extracts `observationLocationPosition` from the weather station data as an automatic fallback for high-precision civil sunrise and sunset calculations.

### Supported Weather Metrics
* **Temperature (Metric 14)**: Current temperature in Celsius (°C) or Fahrenheit (°F), configurable via watch settings (`TemperatureUnit`).
* **Dynamic Weather Condition (Metric 15)**: Displays condition-aware vector icons paired with context-sensitive values configurable via `WeatherDisplayMode`:
  - **Auto (Default)**: Automatically displays precipitation probability (e.g. `27%` with a raindrop) if precipitation chance > 0%; otherwise displays current temperature.
  - **Precipitation Only**: Rain/precipitation probability (`0–100%`).
  - **Temperature Only**: Current ambient temperature.
  - **Humidity Only**: Relative humidity (`0–100%`).
  - **Wind Speed Only**: Converted from m/s to knots (`kt`) for marine/outdoor navigation (e.g. `12kt`).
* **Condition Icons**: Automatically mapped from Garmin's condition enums to themed vector icons for Clear, Partly Cloudy, Overcast, Rain/Showers, Thunderstorms, Snow/Wintry Mix, and High Wind.

### Refresh Frequencies & Sync Cycles
* **Screen Refresh (Every 1 Minute)**: The watch face queries the watch's internal system weather cache on each `onUpdate(dc)` tick (every 60 seconds in normal mode, or every second on wrist gesture).
* **Garmin OS Phone Sync (Every 15–60 Minutes)**: The underlying weather data is updated over Bluetooth by Garmin Connect on your smartphone.
  > **Note**: If your watch is disconnected from your phone for several hours or background permissions are disabled on your phone, weather data will gracefully display `--°` or `--%` until reconnected.

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
