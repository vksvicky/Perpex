# Feature Roadmap, Git Branch Strategy & Multi-Device Testing Matrix

This document tracks the multi-feature development roadmap, git branch isolation strategy, and verification test matrices for all **5 supported Garmin devices**.

---

## ⌚ 1. Supported Device Specifications

| No. | Target Device ID | Device Name | Display Tech | Resolution | Radius |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `fenix7` | **Garmin Fenix 7** | MIP (Memory-in-Pixel) | `260 x 260` | `130px` |
| 2 | `epix2` | **Garmin Epix Gen 2** | AMOLED | `416 x 416` | `208px` |
| 3 | `venu3` | **Garmin Venu 3** | AMOLED | `454 x 454` | `227px` |
| 4 | `enduro3` | **Garmin Enduro 3** | Solar MIP | `280 x 280` | `140px` |
| 5 | `fenix847mm` | **Garmin Fenix 8 47mm** | AMOLED | `454 x 454` | `227px` |

---

## 🌿 2. Feature Roadmap & Git Branch Strategy

Each feature is implemented on its own dedicated git feature branch, verified across all 5 devices, and documented before merging into main.

```text
main / feature/static-dial-background (Base Engine)
 │
 ├── 1. feature/color-theme-customization   (Teal, Orange, Green, Gold, White, Red Accent Themes)
 ├── 2. feature/amoled-aod-low-power        (AMOLED Always-On Display & 10% Burn-in Protection)
 ├── 3. feature/weather-solar-body-battery (Weather Temp/Icons, Sunrise/Sunset & Body Battery)
 └── 4. feature/touch-complications-shortcuts (CIQ 4.2+ Press & Hold Complication Shortcuts)
```

### Feature Branch Breakdown:

#### 🟢 Feature 1: Color Theme Customization & On-Watch Menu Settings
- **Branch**: `feature/color-theme-customization`
- **Scope**:
  - Add `ThemeColor` property in `resources/properties.xml` and `resources/settings/settings.xml`.
  - Color Options: `Red` (Default), `Teal/Cyan`, `Orange`, `Electric Green`, `Gold/Yellow`, `Pure White`.
  - On-Watch Custom `GarminSettingsCustomView` with live accent colors, dynamic `dc.getFontHeight()` spacing, and 7-item navigation.
- **Status**: ✅ COMPLETED & MERGED.

#### 🟡 Feature 2: AMOLED Always-On Display (AOD) & Burn-In Protection
- **Branch**: `feature/amoled-aod-low-power`
- **Scope**:
  - Implement `onEnterSleep()` and `onExitSleep()` handlers in `GarminBasicWatchFaceView.mc`.
  - Dim hour/minute hands to stealth grey (`0x777777`), hide second hand, and disable animations in Low-Power Mode.
  - Enforce Garmin's 10% display pixel budget rule for AMOLED screens (`epix2`, `venu3`, `fenix847mm`).
- **Status**: ✅ COMPLETED & MERGED.

#### 🔵 Feature 3: Weather, Solar & Body Battery Data Fields
- **Branch**: `feature/weather-solar-body-battery`
- **Scope**:
  - Add `Toybox.Weather` integration: Temperature, Weather Condition Icon, Rain Chance.
  - Add Sunrise / Sunset calculation.
  - Add `Body Battery` metric (0-100%) to data slot dropdown options.
- **Status**: ⏳ NEXT UP.

#### 🟣 Feature 4: Touch Complication Press-and-Hold Shortcuts (CIQ 4.2+)
- **Branch**: `feature/touch-complications-shortcuts`
- **Scope**:
  - Integrate Garmin `Complications` API for `epix2`, `fenix7`, `enduro3`, `venu3`, and `fenix847mm`.
  - Press-and-hold on Heart Rate slot opens Heart Rate Glance; press-and-hold on Steps opens Steps Glance, etc.
- **Status**: 📅 QUEUED.

---

## 🧪 3. Verification Test Commands (All 5 Devices)

To test any feature across all 5 supported devices, run:

```bash
# 1. Test Fenix 7 (260x260 MIP)
./build.sh fenix7

# 2. Test Epix Gen 2 (416x416 AMOLED)
./build.sh epix2

# 3. Test Venu 3 (454x454 AMOLED)
./build.sh venu3

# 4. Test Enduro 3 (280x280 MIP)
./build.sh enduro3

# 5. Test Fenix 8 47mm (454x454 AMOLED)
./build.sh fenix847mm
```

---

## 📋 4. Device Verification Matrix Checklist

| Feature Branch | `fenix7` | `epix2` | `venu3` | `enduro3` | `fenix847mm` |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Base Watch Face & 5 Slots** | ✅ Passed | ✅ Passed | ✅ Passed | ✅ Passed | ✅ Passed |
| **1. `feature/color-theme-customization`** | ✅ Passed | ✅ Passed | ✅ Passed | ✅ Passed | ✅ Passed |
| **2. `feature/amoled-aod-low-power`** | ✅ Passed | ✅ Passed | ✅ Passed | ✅ Passed | ✅ Passed |
| **3. `feature/weather-solar-body-battery`** | ⏳ Pending | ⏳ Pending | ⏳ Pending | ⏳ Pending | ⏳ Pending |
| **4. `feature/touch-complications-shortcuts`** | ⏳ Pending | ⏳ Pending | ⏳ Pending | ⏳ Pending | ⏳ Pending |
