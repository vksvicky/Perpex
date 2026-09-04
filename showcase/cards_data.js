const SHOWCASE_CARDS = [
  {
    "id": "showcase_perm1_core_activity", "category": "metrics", "title": "Core Fitness & Activity Metrics",
    "subtitle": "Daily performance dashboard: Battery gauge, Heart Rate, Steps, Calories & Distance", "image": "images/showcase_perm1_core_activity.png", "annotated": "annotated/showcase_perm1_core_activity.png",
    "slots": [
      {"slot": 1, "name": "Battery Level", "val": "85%", "desc": "Dynamic color-coded gauge tracking battery charge remaining", "setting": "Slot1Metric = 1", "left": 50.0, "top": 30.04},
      {"slot": 2, "name": "Heart Rate", "val": "74 BPM", "desc": "Continuous pulse monitoring with live animated heart", "setting": "Slot2Metric = 2", "left": 33.26, "top": 40.56},
      {"slot": 3, "name": "Step Count", "val": "8,420", "desc": "Daily cumulative steps tracking active movement", "setting": "Slot3Metric = 3", "left": 66.74, "top": 40.56},
      {"slot": 4, "name": "Step Goal %", "val": "84%", "desc": "Percentage completion toward daily active target", "setting": "Slot4Metric = 4", "left": 33.26, "top": 60.3},
      {"slot": 5, "name": "Active Calories", "val": "540 kCal", "desc": "Estimated active metabolic burn expenditure", "setting": "Slot5Metric = 5", "left": 66.74, "top": 60.3},
      {"slot": 6, "name": "Distance", "val": "6.2 KM", "desc": "Total distance traveled today in kilometers", "setting": "Slot6Metric = 6", "left": 50.0, "top": 69.96},
    ]
  },
  {
    "id": "showcase_perm2_sensors_alerts", "category": "metrics", "title": "Sensors, Alerts & Atmosphere",
    "subtitle": "Environmental and connectivity vitals: Elevation, Barometer, Stress, Floors & Alerts", "image": "images/showcase_perm2_sensors_alerts.png", "annotated": "annotated/showcase_perm2_sensors_alerts.png",
    "slots": [
      {"slot": 1, "name": "Floors Climbed", "val": "14 fl", "desc": "Vertical flights of stairs climbed today", "setting": "Slot1Metric = 7", "left": 50.0, "top": 30.04},
      {"slot": 2, "name": "Active Minutes", "val": "45 min", "desc": "Moderate and vigorous intensity activity minutes accumulated", "setting": "Slot2Metric = 8", "left": 33.26, "top": 40.56},
      {"slot": 3, "name": "Stress Level", "val": "28", "desc": "Real-time all-day physiological stress score", "setting": "Slot3Metric = 9", "left": 66.74, "top": 40.56},
      {"slot": 4, "name": "Notifications", "val": "3", "desc": "Unread notification counter and smartphone Bluetooth status", "setting": "Slot4Metric = 11", "left": 33.26, "top": 60.3},
      {"slot": 5, "name": "Altitude", "val": "342 m", "desc": "Real-time barometric altitude elevation above sea level", "setting": "Slot5Metric = 12", "left": 66.74, "top": 60.3},
      {"slot": 6, "name": "Barometer", "val": "1013 hPa", "desc": "Ambient atmospheric sea-level pressure monitoring", "setting": "Slot6Metric = 13", "left": 50.0, "top": 69.96},
    ]
  },
  {
    "id": "showcase_perm3_solar_weather_recovery", "category": "metrics", "title": "Weather, Solar & Training Status",
    "subtitle": "Performance & environment: Ambient Weather, Solar Times, Body Battery, Recovery & VO2 Max", "image": "images/showcase_perm3_solar_weather_recovery.png", "annotated": "annotated/showcase_perm3_solar_weather_recovery.png",
    "slots": [
      {"slot": 1, "name": "Weather Temp", "val": "22\u00b0C", "desc": "Outdoor temperature from connected weather provider", "setting": "Slot1Metric = 14", "left": 50.0, "top": 30.04},
      {"slot": 2, "name": "Weather Condition", "val": "Sunny", "desc": "Context-aware dynamic condition icon (Clear Skies)", "setting": "Slot2Metric = 15", "left": 33.26, "top": 40.56},
      {"slot": 3, "name": "Solar Event", "val": "19:42", "desc": "Next sunrise/sunset calculation with offline GPS fallback", "setting": "Slot3Metric = 16", "left": 66.74, "top": 40.56},
      {"slot": 4, "name": "Body Battery", "val": "76%", "desc": "Garmin Firstbeat real-time bodily energy reserve", "setting": "Slot4Metric = 17", "left": 33.26, "top": 60.3},
      {"slot": 5, "name": "Recovery Time", "val": "18 hrs", "desc": "Hours remaining before next recommended training session", "setting": "Slot5Metric = 20", "left": 66.74, "top": 60.3},
      {"slot": 6, "name": "VO2 Max", "val": "52", "desc": "Cardiovascular aerobic fitness capacity score", "setting": "Slot6Metric = 21", "left": 50.0, "top": 69.96},
    ]
  },
  {
    "id": "showcase_weather_rain", "category": "weather", "title": "Precipitation & Rain Override",
    "subtitle": "Dynamic weather detection displaying precipitation probability & condition icons", "image": "images/showcase_weather_rain.png", "annotated": "annotated/showcase_weather_rain.png",
    "slots": [
      {"slot": 1, "name": "Rain Probability", "val": "85%", "desc": "Precipitation probability with animated raindrop icon", "setting": "Slot1Metric = 15 (Override: Rain)", "left": 50.0, "top": 30.04},
      {"slot": 2, "name": "Heart Rate", "val": "74 BPM", "desc": "Continuous pulse monitoring", "setting": "Slot2Metric = 2", "left": 33.26, "top": 40.56},
      {"slot": 3, "name": "Step Count", "val": "8,420", "desc": "Daily step progress", "setting": "Slot3Metric = 3", "left": 66.74, "top": 40.56},
      {"slot": 4, "name": "Step Goal %", "val": "84%", "desc": "Percentage completion toward goal", "setting": "Slot4Metric = 4", "left": 33.26, "top": 60.3},
      {"slot": 5, "name": "Active Calories", "val": "540 kCal", "desc": "Estimated active calorie expenditure", "setting": "Slot5Metric = 5", "left": 66.74, "top": 60.3},
      {"slot": 6, "name": "Distance", "val": "6.2 KM", "desc": "Total distance traveled", "setting": "Slot6Metric = 6", "left": 50.0, "top": 69.96},
    ]
  },
  {
    "id": "showcase_weather_wind", "category": "weather", "title": "High Wind & Nautical Conditions",
    "subtitle": "Marine/outdoor wind speed detection with dynamic condition indicators", "image": "images/showcase_weather_wind.png", "annotated": "annotated/showcase_weather_wind.png",
    "slots": [
      {"slot": 1, "name": "Wind Velocity", "val": "12 kt", "desc": "Wind speed in knots with high-wind warning icon", "setting": "Slot1Metric = 15 (Override: Wind)", "left": 50.0, "top": 30.04},
      {"slot": 2, "name": "Heart Rate", "val": "74 BPM", "desc": "Continuous pulse monitoring", "setting": "Slot2Metric = 2", "left": 33.26, "top": 40.56},
      {"slot": 3, "name": "Step Count", "val": "8,420", "desc": "Daily step progress", "setting": "Slot3Metric = 3", "left": 66.74, "top": 40.56},
      {"slot": 4, "name": "Step Goal %", "val": "84%", "desc": "Percentage completion toward goal", "setting": "Slot4Metric = 4", "left": 33.26, "top": 60.3},
      {"slot": 5, "name": "Active Calories", "val": "540 kCal", "desc": "Estimated active calorie expenditure", "setting": "Slot5Metric = 5", "left": 66.74, "top": 60.3},
      {"slot": 6, "name": "Distance", "val": "6.2 KM", "desc": "Total distance traveled", "setting": "Slot6Metric = 6", "left": 50.0, "top": 69.96},
    ]
  },
  {
    "id": "showcase_theme_teal", "category": "themes", "title": "Theme: Tactical Teal & Cyan",
    "subtitle": "High-contrast tactical aqua accent for aviation and aquatic readability", "image": "images/showcase_theme_teal.png", "annotated": "annotated/showcase_theme_teal.png",
    "slots": [
      {"slot": 1, "name": "Battery Level", "val": "85%", "desc": "Battery level in Teal accent", "setting": "ThemeColor = 2", "left": 50.0, "top": 30.04},
      {"slot": 2, "name": "Heart Rate", "val": "74 BPM", "desc": "Pulse monitor with teal highlight", "setting": "Slot2Metric = 2", "left": 33.26, "top": 40.56},
      {"slot": 3, "name": "Step Count", "val": "8,420", "desc": "Step counter with teal icon", "setting": "Slot3Metric = 3", "left": 66.74, "top": 40.56},
      {"slot": 4, "name": "Step Goal %", "val": "84%", "desc": "Step goal percentage", "setting": "Slot4Metric = 4", "left": 33.26, "top": 60.3},
      {"slot": 5, "name": "Active Calories", "val": "540 kCal", "desc": "Active calories in teal accent", "setting": "Slot5Metric = 5", "left": 66.74, "top": 60.3},
      {"slot": 6, "name": "Distance", "val": "6.2 KM", "desc": "Distance traveled", "setting": "Slot6Metric = 6", "left": 50.0, "top": 69.96},
    ]
  },
  {
    "id": "showcase_theme_orange", "category": "themes", "title": "Theme: Warm Amber Orange",
    "subtitle": "High-visibility sunset orange accent engineered for twilight and fog", "image": "images/showcase_theme_orange.png", "annotated": "annotated/showcase_theme_orange.png",
    "slots": [
      {"slot": 1, "name": "Battery Level", "val": "85%", "desc": "Battery level in Orange accent", "setting": "ThemeColor = 3", "left": 50.0, "top": 30.04},
      {"slot": 2, "name": "Heart Rate", "val": "74 BPM", "desc": "Pulse monitor with orange highlight", "setting": "Slot2Metric = 2", "left": 33.26, "top": 40.56},
      {"slot": 3, "name": "Step Count", "val": "8,420", "desc": "Step counter with orange icon", "setting": "Slot3Metric = 3", "left": 66.74, "top": 40.56},
      {"slot": 4, "name": "Step Goal %", "val": "84%", "desc": "Step goal percentage", "setting": "Slot4Metric = 4", "left": 33.26, "top": 60.3},
      {"slot": 5, "name": "Active Calories", "val": "540 kCal", "desc": "Active calories in orange accent", "setting": "Slot5Metric = 5", "left": 66.74, "top": 60.3},
      {"slot": 6, "name": "Distance", "val": "6.2 KM", "desc": "Distance traveled", "setting": "Slot6Metric = 6", "left": 50.0, "top": 69.96},
    ]
  },
  {
    "id": "showcase_theme_green", "category": "themes", "title": "Theme: Electric Green",
    "subtitle": "Vibrant tactical field green for intense outdoor daylight clarity", "image": "images/showcase_theme_green.png", "annotated": "annotated/showcase_theme_green.png",
    "slots": [
      {"slot": 1, "name": "Battery Level", "val": "85%", "desc": "Battery level in Green accent", "setting": "ThemeColor = 4", "left": 50.0, "top": 30.04},
      {"slot": 2, "name": "Heart Rate", "val": "74 BPM", "desc": "Pulse monitor with green highlight", "setting": "Slot2Metric = 2", "left": 33.26, "top": 40.56},
      {"slot": 3, "name": "Step Count", "val": "8,420", "desc": "Step counter with green icon", "setting": "Slot3Metric = 3", "left": 66.74, "top": 40.56},
      {"slot": 4, "name": "Step Goal %", "val": "84%", "desc": "Step goal percentage", "setting": "Slot4Metric = 4", "left": 33.26, "top": 60.3},
      {"slot": 5, "name": "Active Calories", "val": "540 kCal", "desc": "Active calories in green accent", "setting": "Slot5Metric = 5", "left": 66.74, "top": 60.3},
      {"slot": 6, "name": "Distance", "val": "6.2 KM", "desc": "Distance traveled", "setting": "Slot6Metric = 6", "left": 50.0, "top": 69.96},
    ]
  },
  {
    "id": "showcase_night_red", "category": "night", "title": "Tactical Red Night Mode",
    "subtitle": "Preserves rhodopsin dark adaptation for night tactical operations", "image": "images/showcase_night_red.png", "annotated": "annotated/showcase_night_red.png",
    "slots": [
      {"slot": 1, "name": "Night Battery", "val": "85%", "desc": "Red luminescent battery readout", "setting": "NightModeColor = 0 (Red)", "left": 50.0, "top": 30.04},
      {"slot": 2, "name": "Night HR", "val": "74 BPM", "desc": "Subdued red pulse tracking", "setting": "Slot2Metric = 2", "left": 33.26, "top": 40.56},
      {"slot": 3, "name": "Night Steps", "val": "8,420", "desc": "Red step counter", "setting": "Slot3Metric = 3", "left": 66.74, "top": 40.56},
      {"slot": 4, "name": "Night Goal", "val": "84%", "desc": "Red step target percentage", "setting": "Slot4Metric = 4", "left": 33.26, "top": 60.3},
      {"slot": 5, "name": "Night Calories", "val": "540 kCal", "desc": "Nocturnal calorie burn", "setting": "Slot5Metric = 5", "left": 66.74, "top": 60.3},
      {"slot": 6, "name": "Night Distance", "val": "6.2 KM", "desc": "Night tactical distance tracking", "setting": "Slot6Metric = 6", "left": 50.0, "top": 69.96},
    ]
  },
  {
    "id": "showcase_night_green", "category": "night", "title": "Stealth Green Night Mode",
    "subtitle": "Aviation-spec night vision goggle (NVG) green phosphor aesthetic", "image": "images/showcase_night_green.png", "annotated": "annotated/showcase_night_green.png",
    "slots": [
      {"slot": 1, "name": "NVG Battery", "val": "85%", "desc": "Green phosphor battery readout", "setting": "NightModeColor = 2 (Green)", "left": 50.0, "top": 30.04},
      {"slot": 2, "name": "NVG HR", "val": "74 BPM", "desc": "Subdued green pulse tracking", "setting": "Slot2Metric = 2", "left": 33.26, "top": 40.56},
      {"slot": 3, "name": "NVG Steps", "val": "8,420", "desc": "Green phosphor step counter", "setting": "Slot3Metric = 3", "left": 66.74, "top": 40.56},
      {"slot": 4, "name": "NVG Goal", "val": "84%", "desc": "Green step target percentage", "setting": "Slot4Metric = 4", "left": 33.26, "top": 60.3},
      {"slot": 5, "name": "NVG Calories", "val": "540 kCal", "desc": "NVG-compatible calorie burn", "setting": "Slot5Metric = 5", "left": 66.74, "top": 60.3},
      {"slot": 6, "name": "NVG Distance", "val": "6.2 KM", "desc": "Night mission distance tracking", "setting": "Slot6Metric = 6", "left": 50.0, "top": 69.96},
    ]
  },
  {
    "id": "showcase_low_power_aod", "category": "aod", "title": "Low-Power AMOLED Always-On Display",
    "subtitle": "Burn-in protection keeping pixel luminance under 10% with skeletonized hands", "image": "images/showcase_low_power_aod.png", "annotated": "annotated/showcase_low_power_aod.png",
    "slots": [
      {"slot": 1, "name": "AOD Battery", "val": "85%", "desc": "Minimal outline battery indicator", "setting": "AOD Active", "left": 50.0, "top": 30.04},
      {"slot": 2, "name": "AOD Time", "val": "10:08", "desc": "Skeletonized hollow hands preventing OLED burn-in", "setting": "Low Power Mode", "left": 33.26, "top": 40.56},
      {"slot": 3, "name": "AOD Date", "val": "SUN 18", "desc": "High-contrast date complication", "setting": "Always-On Display", "left": 66.74, "top": 40.56},
      {"slot": 4, "name": "AOD Ring", "val": "Calendar", "desc": "Subtle low-lum calendar indicators", "setting": "Pixel Load < 10%", "left": 33.26, "top": 60.3},
      {"slot": 5, "name": "AOD Steps", "val": "8,420", "desc": "Dimmed step count readout", "setting": "Burn-in Safe", "left": 66.74, "top": 60.3},
      {"slot": 6, "name": "AOD Pulse", "val": "74", "desc": "Single-color low-power pulse reading", "setting": "AMOLED Protection", "left": 50.0, "top": 69.96},
    ]
  },
];
