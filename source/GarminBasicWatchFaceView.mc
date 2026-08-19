using Toybox.WatchUi;
using Toybox.Graphics;
using Toybox.System;
using Toybox.Time;
using Toybox.Time.Gregorian;
using Toybox.ActivityMonitor;
using Toybox.Activity;
using Toybox.Application.Properties;

class GarminBasicWatchFaceView extends WatchUi.WatchFace {
    private var centerX, centerY;
    private var radius;

    // Colour palette (dark theme)
    private const COLOR_BG         = Graphics.COLOR_BLACK;
    private const COLOR_RING_SEP   = Graphics.COLOR_DK_GRAY;
    private const COLOR_DIM_OUTER  = 0x666666;
    private const COLOR_DIM_MID    = 0x4A4A4A;
    private const COLOR_DIM_INNER  = 0x383838;
    private const COLOR_HIGHLIGHT  = 0x00CCCC; // teal
    private const COLOR_BRAND      = 0x999999;
    private const COLOR_BATT       = 0x444444;
    private const COLOR_HAND_HOUR  = Graphics.COLOR_WHITE;
    private const COLOR_HAND_MIN   = Graphics.COLOR_WHITE;
    private const COLOR_HAND_SEC   = 0xFF4444;
    private const COLOR_PIN        = 0x888888;

    var dialBg;
    var imgBattery;
    var imgBatteryRed;
    var imgBatteryOrange;
    var imgBatteryGreen;
    var imgHeart;
    var imgHeartPulse;
    var imgSteps;
    var imgFlame;
    var imgBluetooth;
    var imgDistance;
    var imgFloors;
    var imgStress;
    var imgAltitude;
    var imgBarometer;

    private var isLowPower = false;

    function initialize() {
        WatchFace.initialize();
    }

    function onLayout(dc) {
        var w = dc.getWidth();
        var h = dc.getHeight();
        centerX = w / 2;
        centerY = h / 2;
        radius  = (w < h ? w : h) / 2;
        
        dialBg           = WatchUi.loadResource(Rez.Drawables.dial_bg);
        imgBattery       = WatchUi.loadResource(Rez.Drawables.icon_battery);
        imgBatteryRed    = WatchUi.loadResource(Rez.Drawables.icon_battery_red);
        imgBatteryOrange = WatchUi.loadResource(Rez.Drawables.icon_battery_orange);
        imgBatteryGreen  = WatchUi.loadResource(Rez.Drawables.icon_battery_green);
        imgHeart         = WatchUi.loadResource(Rez.Drawables.icon_heart);
        imgHeartPulse    = WatchUi.loadResource(Rez.Drawables.icon_heart_pulse);
        imgSteps         = WatchUi.loadResource(Rez.Drawables.icon_steps);
        imgFlame         = WatchUi.loadResource(Rez.Drawables.icon_flame);
        imgBluetooth     = WatchUi.loadResource(Rez.Drawables.icon_bluetooth);
        imgDistance      = WatchUi.loadResource(Rez.Drawables.icon_distance);
        imgFloors        = WatchUi.loadResource(Rez.Drawables.icon_floors);
        imgStress        = WatchUi.loadResource(Rez.Drawables.icon_stress);
        imgAltitude      = WatchUi.loadResource(Rez.Drawables.icon_altitude);
        imgBarometer     = WatchUi.loadResource(Rez.Drawables.icon_barometer);
    }

    function onShow() {}

    function onEnterSleep() {
        isLowPower = true;
        WatchUi.requestUpdate();
    }

    function onExitSleep() {
        isLowPower = false;
        WatchUi.requestUpdate();
    }

    function onUpdate(dc) {
        var now       = Gregorian.info(Time.now(), Time.FORMAT_SHORT);
        var clockTime = System.getClockTime();

        dc.setColor(COLOR_BG, COLOR_BG);
        dc.clear();

        drawConcentricRings(dc, now);
        drawDataSlots(dc);
        drawHands(dc, clockTime.hour, clockTime.min, clockTime.sec);
    }

    // ─────────────────────────────────────────────────────────────────────
    // CUSTOMIZABLE DATA SLOTS & THEME COLOR
    // ─────────────────────────────────────────────────────────────────────
    function getPropertyVal(key, defaultVal) {
        try {
            if (Toybox.Application has :Properties) {
                var val = Properties.getValue(key);
                if (val != null) { return val; }
            }
        } catch (e) {}
        return defaultVal;
    }

    function getThemeAccentColor() {
        var themeId = getPropertyVal("ThemeColor", 1);
        if (themeId == 2) { return 0x00CCCC; }      // Teal / Cyan
        else if (themeId == 3) { return 0xFF8800; } // Warm Orange
        else if (themeId == 4) { return 0x00FF66; } // Electric Green
        else if (themeId == 5) { return 0xFFCC00; } // Gold / Yellow
        else if (themeId == 6) { return 0xFFFFFF; } // Pure White
        return 0xFF3333;                            // Vibrant Red (Default)
    }

    // ─────────────────────────────────────────────────────────────────────
    // BITMAP ICON DRAWERS (Themed Accent Bitmaps)
    // ─────────────────────────────────────────────────────────────────────
    function drawMetricIcon(dc, type, x, y, s) {
        var bmp = null;
        var themeId = getPropertyVal("ThemeColor", 1);

        if (type == 1) { bmp = imgBattery; }
        else if (type == 2) {
            // Heart Rate: Pumping animation ONLY during active workouts/activities!
            var isActivityRunning = false;
            var actInfo = Activity.getActivityInfo();
            if (actInfo != null && actInfo has :timerState && actInfo.timerState != null) {
                isActivityRunning = (actInfo.timerState == 3 || actInfo.timerState == 1);
            }

            var sec = System.getClockTime().sec;
            var isPulseBeat = isActivityRunning ? (sec % 2 == 0) : false;

            if (themeId == 2) { bmp = WatchUi.loadResource(isPulseBeat ? Rez.Drawables.icon_heart_pulse_teal : Rez.Drawables.icon_heart_teal); }
            else if (themeId == 3) { bmp = WatchUi.loadResource(isPulseBeat ? Rez.Drawables.icon_heart_pulse_orange : Rez.Drawables.icon_heart_orange); }
            else if (themeId == 4) { bmp = WatchUi.loadResource(isPulseBeat ? Rez.Drawables.icon_heart_pulse_green : Rez.Drawables.icon_heart_green); }
            else if (themeId == 5) { bmp = WatchUi.loadResource(isPulseBeat ? Rez.Drawables.icon_heart_pulse_gold : Rez.Drawables.icon_heart_gold); }
            else if (themeId == 6) { bmp = WatchUi.loadResource(isPulseBeat ? Rez.Drawables.icon_heart_pulse_white : Rez.Drawables.icon_heart_white); }
            else { bmp = isPulseBeat ? imgHeartPulse : imgHeart; }
        }
        else if (type == 3 || type == 4) {
            if (themeId == 2) { bmp = WatchUi.loadResource(Rez.Drawables.icon_steps_teal); }
            else if (themeId == 3) { bmp = WatchUi.loadResource(Rez.Drawables.icon_steps_orange); }
            else if (themeId == 4) { bmp = WatchUi.loadResource(Rez.Drawables.icon_steps_green); }
            else if (themeId == 5) { bmp = WatchUi.loadResource(Rez.Drawables.icon_steps_gold); }
            else if (themeId == 6) { bmp = WatchUi.loadResource(Rez.Drawables.icon_steps_white); }
            else { bmp = imgSteps; }
        }
        else if (type == 5) {
            if (themeId == 2) { bmp = WatchUi.loadResource(Rez.Drawables.icon_flame_teal); }
            else if (themeId == 3) { bmp = WatchUi.loadResource(Rez.Drawables.icon_flame_orange); }
            else if (themeId == 4) { bmp = WatchUi.loadResource(Rez.Drawables.icon_flame_green); }
            else if (themeId == 5) { bmp = WatchUi.loadResource(Rez.Drawables.icon_flame_gold); }
            else if (themeId == 6) { bmp = WatchUi.loadResource(Rez.Drawables.icon_flame_white); }
            else { bmp = imgFlame; }
        }
        else if (type == 6) {
            if (themeId == 2) { bmp = WatchUi.loadResource(Rez.Drawables.icon_distance_teal); }
            else if (themeId == 3) { bmp = WatchUi.loadResource(Rez.Drawables.icon_distance_orange); }
            else if (themeId == 4) { bmp = WatchUi.loadResource(Rez.Drawables.icon_distance_green); }
            else if (themeId == 5) { bmp = WatchUi.loadResource(Rez.Drawables.icon_distance_gold); }
            else if (themeId == 6) { bmp = WatchUi.loadResource(Rez.Drawables.icon_distance_white); }
            else { bmp = imgDistance; }
        }
        else if (type == 7) {
            if (themeId == 2) { bmp = WatchUi.loadResource(Rez.Drawables.icon_floors_teal); }
            else if (themeId == 3) { bmp = WatchUi.loadResource(Rez.Drawables.icon_floors_orange); }
            else if (themeId == 4) { bmp = WatchUi.loadResource(Rez.Drawables.icon_floors_green); }
            else if (themeId == 5) { bmp = WatchUi.loadResource(Rez.Drawables.icon_floors_gold); }
            else if (themeId == 6) { bmp = WatchUi.loadResource(Rez.Drawables.icon_floors_white); }
            else { bmp = imgFloors; }
        }
        else if (type == 9) {
            if (themeId == 2) { bmp = WatchUi.loadResource(Rez.Drawables.icon_stress_teal); }
            else if (themeId == 3) { bmp = WatchUi.loadResource(Rez.Drawables.icon_stress_orange); }
            else if (themeId == 4) { bmp = WatchUi.loadResource(Rez.Drawables.icon_stress_green); }
            else if (themeId == 5) { bmp = WatchUi.loadResource(Rez.Drawables.icon_stress_gold); }
            else if (themeId == 6) { bmp = WatchUi.loadResource(Rez.Drawables.icon_stress_white); }
            else { bmp = imgStress; }
        }
        else if (type == 11) {
            if (themeId == 2) { bmp = WatchUi.loadResource(Rez.Drawables.icon_bluetooth_teal); }
            else if (themeId == 3) { bmp = WatchUi.loadResource(Rez.Drawables.icon_bluetooth_orange); }
            else if (themeId == 4) { bmp = WatchUi.loadResource(Rez.Drawables.icon_bluetooth_green); }
            else if (themeId == 5) { bmp = WatchUi.loadResource(Rez.Drawables.icon_bluetooth_gold); }
            else if (themeId == 6) { bmp = WatchUi.loadResource(Rez.Drawables.icon_bluetooth_white); }
            else { bmp = imgBluetooth; }
        }
        else if (type == 12) {
            if (themeId == 2) { bmp = WatchUi.loadResource(Rez.Drawables.icon_altitude_teal); }
            else if (themeId == 3) { bmp = WatchUi.loadResource(Rez.Drawables.icon_altitude_orange); }
            else if (themeId == 4) { bmp = WatchUi.loadResource(Rez.Drawables.icon_altitude_green); }
            else if (themeId == 5) { bmp = WatchUi.loadResource(Rez.Drawables.icon_altitude_gold); }
            else if (themeId == 6) { bmp = WatchUi.loadResource(Rez.Drawables.icon_altitude_white); }
            else { bmp = imgAltitude; }
        }
        else if (type == 13) {
            if (themeId == 2) { bmp = WatchUi.loadResource(Rez.Drawables.icon_barometer_teal); }
            else if (themeId == 3) { bmp = WatchUi.loadResource(Rez.Drawables.icon_barometer_orange); }
            else if (themeId == 4) { bmp = WatchUi.loadResource(Rez.Drawables.icon_barometer_green); }
            else if (themeId == 5) { bmp = WatchUi.loadResource(Rez.Drawables.icon_barometer_gold); }
            else if (themeId == 6) { bmp = WatchUi.loadResource(Rez.Drawables.icon_barometer_white); }
            else { bmp = imgBarometer; }
        }

        if (bmp != null) {
            var iconW = bmp.getWidth();
            var iconH = bmp.getHeight();
            dc.drawBitmap((x - iconW / 2).toNumber(), (y - iconH / 2).toNumber(), bmp);
        }
    }

    // ─────────────────────────────────────────────────────────────────────
    // DATA VALUES & LABELS FORMATTING
    // ─────────────────────────────────────────────────────────────────────
    function getMetricData(type) {
        if (type == 1) { // Battery
            var stats = System.getSystemStats();
            return [(stats.battery + 0.5).toNumber().toString() + "%", ""];
        } else if (type == 2) { // Heart Rate
            if (ActivityMonitor has :getHeartRateHistory) {
                var hrIter = ActivityMonitor.getHeartRateHistory(1, true);
                var sample = hrIter.next();
                if (sample != null && sample.heartRate != ActivityMonitor.INVALID_HR_SAMPLE) {
                    return [sample.heartRate.toString(), "BPM"];
                }
            }
            return ["--", "BPM"];
        } else if (type == 3) { // Steps
            var info = ActivityMonitor.getInfo();
            var val = (info != null && info.steps != null) ? info.steps.toString() : "0";
            return [val, "STEPS"];
        } else if (type == 4) { // Step Goal %
            var info = ActivityMonitor.getInfo();
            var val = "0%";
            if (info != null && info.steps != null && info.stepGoal != null && info.stepGoal > 0) {
                val = ((info.steps.toDouble() / info.stepGoal.toDouble()) * 100).toNumber().toString() + "%";
            }
            return [val, "GOAL"];
        } else if (type == 5) { // Active Calories
            var info = ActivityMonitor.getInfo();
            var val = (info != null && info.calories != null) ? info.calories.toString() : "0";
            return [val, "kCal"];
        } else if (type == 6) { // Distance
            var info = ActivityMonitor.getInfo();
            var val = (info != null && info.distance != null) ? (info.distance / 100000.0).format("%.1f") : "0.0";
            return [val, "KM"];
        } else if (type == 7) { // Floors
            var info = ActivityMonitor.getInfo();
            var val = (info != null && info.floorsClimbed != null) ? info.floorsClimbed.toString() : "0";
            return [val, "FLOORS"];
        } else if (type == 8) { // Active Minutes
            var info = ActivityMonitor.getInfo();
            var val = (info != null && info.activeMinutesWeek != null && info.activeMinutesWeek.total != null) ? info.activeMinutesWeek.total.toString() : "0";
            return [val, "MINS"];
        } else if (type == 9) { // Stress
            var info = ActivityMonitor.getInfo();
            var val = (info != null && info has :stressScore && info.stressScore != null) ? info.stressScore.toString() : "--";
            return [val, "STRESS"];
        } else if (type == 10) { // Digital Time
            var clock = System.getClockTime();
            return [clock.hour.format("%02d") + ":" + clock.min.format("%02d"), ""];
        } else if (type == 11) { // Notifications / Phone Status
            var device = System.getDeviceSettings();
            var count = (device has :notificationCount) ? device.notificationCount : 0;
            return [count.toString(), ""];
        } else if (type == 12) { // Altitude
            var info = Activity.getActivityInfo();
            var val = (info != null && info.altitude != null) ? info.altitude.toNumber().toString() : "--";
            return [val, "METERS"];
        } else if (type == 13) { // Barometer
            var info = Activity.getActivityInfo();
            var val = (info != null && info.rawAmbientPressure != null) ? (info.rawAmbientPressure / 100.0).toNumber().toString() : "--";
            return [val, "HPA"];
        }
        return ["", ""];
    }

    function drawSingleDataSlot(dc, slotType, posX, posY, s) {
        if (slotType == 0) { return; }

        var fontValue = Graphics.FONT_XTINY;
        var fontLabel = Graphics.FONT_XTINY;

        // ─────────────────────────────────────────────────────────────────
        // BATTERY SLOT: CHARGING ANIMATION & RED-ORANGE-GREEN GRADIENT
        // ─────────────────────────────────────────────────────────────────
        if (slotType == 1) {
            var stats = System.getSystemStats();
            var pct = (stats.battery + 0.5).toNumber();
            var isCharging = (stats has :charging && stats.charging != null) ? stats.charging : false;

            var battColor = Graphics.COLOR_WHITE;
            if (isCharging) {
                // Charging Animation: Cycle Red -> Orange -> Green every second
                var sec = System.getClockTime().sec;
                var step = sec % 3;
                if (step == 0) { battColor = 0xFF3333; }       // Red
                else if (step == 1) { battColor = 0xFF8800; }  // Orange
                else { battColor = 0x00FF66; }                 // Green
            } else {
                // Battery Level Gradient: <=20 Red, <=50 Orange, >50 Green
                if (pct <= 20) { battColor = 0xFF3333; }
                else if (pct <= 50) { battColor = 0xFF8800; }
                else { battColor = 0x00FF66; }
            }

            var battText = pct.toString() + "%";
            if (isCharging) {
                battText = "CHG " + battText;
            }

            // 1. Draw Custom Battery Icon in matching color (Red, Orange, or Green)
            var battBmp = imgBatteryRed;
            if (battColor == 0xFF8800) {
                battBmp = imgBatteryOrange;
            } else if (battColor == 0x00FF66) {
                battBmp = imgBatteryGreen;
            }

            if (battBmp != null) {
                var iconW = battBmp.getWidth();
                var iconH = battBmp.getHeight();
                dc.drawBitmap((posX - iconW / 2).toNumber(), ((posY - (14 * s)) - iconH / 2).toNumber(), battBmp);
            }

            // 2. Draw Battery Percentage Text in battColor
            dc.setColor(battColor, Graphics.COLOR_TRANSPARENT);
            dc.drawText(posX, posY + (5 * s).toNumber(), fontValue, battText, Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
            return;
        }

        // ─────────────────────────────────────────────────────────────────
        // OTHER METRICS (Clean Icon + Value Layout)
        // ─────────────────────────────────────────────────────────────────
        var data = getMetricData(slotType);
        var valStr = data[0];

        // 1. Icon (Themed Accent)
        drawMetricIcon(dc, slotType, posX, posY - (8 * s).toNumber(), s);

        // 2. Bold Value (Crisp White)
        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(posX, posY + (7 * s).toNumber(), fontValue, valStr, Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
    }

    function drawDataSlots(dc) {
        var w = dc.getWidth();
        var scale = w / 260.0;
        var s = scale;

        var s1 = getPropertyVal("Slot1Metric", 1);  // Battery
        var s2 = getPropertyVal("Slot2Metric", 2);  // Heart Rate
        var s3 = getPropertyVal("Slot3Metric", 11); // Bluetooth / Notifications
        var s4 = getPropertyVal("Slot4Metric", 3);  // Steps
        var s5 = getPropertyVal("Slot5Metric", 5);  // Calories

        // Slot 1: Top Center
        drawSingleDataSlot(dc, s1, centerX, centerY - (50 * s).toNumber(), s);

        // Slot 2: Mid-Left (9 o'clock)
        drawSingleDataSlot(dc, s2, centerX - (44 * s).toNumber(), centerY - (12 * s).toNumber(), s);

        // Slot 3: Center Badge (just under pin)
        if (s3 != 0) {
            drawMetricIcon(dc, s3, centerX, centerY + (16 * s).toNumber(), s);
        }

        // Slot 4: Mid-Right (3 o'clock)
        drawSingleDataSlot(dc, s4, centerX + (44 * s).toNumber(), centerY - (12 * s).toNumber(), s);

        // Slot 5: Bottom Center (6 o'clock)
        drawSingleDataSlot(dc, s5, centerX, centerY + (44 * s).toNumber(), s);
    }

    // ─────────────────────────────────────────────────────────────────────
    // CONCENTRIC RINGS
    // ─────────────────────────────────────────────────────────────────────
    function drawConcentricRings(dc, now) {
        var TWO_PI  = Math.PI * 2.0;
        var HALF_PI = Math.PI / 2.0;
        
        // Calculate scale factor based on 260px base width
        var w = dc.getWidth();
        var h = dc.getHeight();
        var scale = w / 260.0;

        // Draw the static opaque background dial
        if (dialBg != null) {
            var bgW = dialBg.getWidth();
            var bgH = dialBg.getHeight();
            var bgX = (w - bgW) / 2;
            var bgY = (h - bgH) / 2;
            dc.drawBitmap(bgX, bgY, dialBg);
        }

        dc.setPenWidth(4);

        // ── Highlight: Days ──────────────────────────────────
        var r1       = (96 * scale).toNumber(); // radius from script
        var dayStep  = TWO_PI / 31.0;
        var d = now.day;
        var angle1 = (d - 1) * dayStep - HALF_PI;
        var degCenter1 = ((- (angle1 * 180.0 / Math.PI)).toNumber() % 360 + 360) % 360;
        
        // Arc below text
        var themeAccent = isLowPower ? 0x555555 : getThemeAccentColor();
        dc.setColor(themeAccent, Graphics.COLOR_TRANSPARENT);
        var r1_arc = r1 - (5 * scale).toNumber();
        dc.drawArc(centerX, centerY, r1_arc, Graphics.ARC_COUNTER_CLOCKWISE, (degCenter1 - 4 + 360) % 360, (degCenter1 + 4 + 360) % 360);

        // ── Highlight: Months ───────────────────────────────────────
        var r2       = (117 * scale).toNumber(); // radius from script
        var m = now.month;
        var monStep  = TWO_PI / 12.0;
        var angle2 = (m - 1) * monStep - HALF_PI;
        var degCenter2 = ((- (angle2 * 180.0 / Math.PI)).toNumber() % 360 + 360) % 360;
        
        // Arc below text
        var r2_arc = r2 - (5 * scale).toNumber();
        dc.drawArc(centerX, centerY, r2_arc, Graphics.ARC_COUNTER_CLOCKWISE, (degCenter2 - 10 + 360) % 360, (degCenter2 + 10 + 360) % 360);

        // ── Highlight: Weekdays ───────────────────────────────────────
        var r3       = (75 * scale).toNumber(); // radius from script
        var wkStep  = TWO_PI / 7.0;
        var w_day = now.day_of_week;
        var angle3 = (w_day - 1) * wkStep - HALF_PI;
        var degCenter3 = ((- (angle3 * 180.0 / Math.PI)).toNumber() % 360 + 360) % 360;
        
        // Arc below text
        var r3_arc = r3 - (5 * scale).toNumber();
        dc.drawArc(centerX, centerY, r3_arc, Graphics.ARC_COUNTER_CLOCKWISE, (degCenter3 - 16 + 360) % 360, (degCenter3 + 16 + 360) % 360);
    }

    // ─────────────────────────────────────────────────────────────────────
    // ANALOG HANDS
    // ─────────────────────────────────────────────────────────────────────
    // ─────────────────────────────────────────────────────────────────────
    // ANALOG HANDS (3D Metallic Heavy-Duty Industrial Hands)
    // ─────────────────────────────────────────────────────────────────────
    function drawRotatedPolygon(dc, cx, cy, cosA, sinA, pts, color) {
        var count = pts.size();
        var result = new [count];
        for (var i = 0; i < count; i++) {
            var p = pts[i];
            var perp = p[0];
            var along = p[1];
            var px = (cx + along * cosA - perp * sinA).toNumber();
            var py = (cy + along * sinA + perp * cosA).toNumber();
            result[i] = [px, py];
        }
        dc.setColor(color, Graphics.COLOR_TRANSPARENT);
        dc.fillPolygon(result);
    }

    function drawHands(dc, hour, min, sec) {
        var TWO_PI  = Math.PI * 2.0;
        var OFFSET  = Math.PI / 2.0;

        var w = dc.getWidth();
        var scale = w / 260.0;
        var s = scale;

        var minFrac   = min / 60.0;
        var hourAngle = (((hour % 12) / 12.0) + (minFrac / 12.0)) * TWO_PI - OFFSET;
        var minAngle  = minFrac * TWO_PI - OFFSET;
        var secAngle  = (sec / 60.0) * TWO_PI - OFFSET;

        var cosH = Math.cos(hourAngle); var sinH = Math.sin(hourAngle);
        var cosM = Math.cos(minAngle);  var sinM = Math.sin(minAngle);
        var cosS = Math.cos(secAngle);  var sinS = Math.sin(secAngle);

        var COLOR_STEEL_DARK  = isLowPower ? 0x222222 : 0x444444;
        var COLOR_STEEL_LIGHT = isLowPower ? 0x444444 : 0x888888;
        var COLOR_WHITE_LUME  = isLowPower ? 0x777777 : 0xFFFFFF;
        var COLOR_RED_ACCENT  = isLowPower ? 0x555555 : getThemeAccentColor();

        // ── HOUR HAND (Heavy-Duty 3D Metallic Fork Hand) ───────────────────
        // 1. 3D Metallic V-Fork Base (Left Dark / Right Light)
        var ptsHourForkL = [
            [0.0,     -10.0*s],
            [-5.5*s,  0.0],
            [-4.5*s,  28.0*s],
            [0.0,     28.0*s]
        ];
        var ptsHourForkR = [
            [0.0,     -10.0*s],
            [5.5*s,   0.0],
            [4.5*s,   28.0*s],
            [0.0,     28.0*s]
        ];
        var ptsHourForkSlot = [
            [-2.0*s, -2.0*s],
            [-2.2*s, 24.0*s],
            [2.2*s,  24.0*s],
            [2.0*s,  -2.0*s]
        ];
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourForkL, COLOR_STEEL_DARK);
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourForkR, COLOR_STEEL_LIGHT);
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourForkSlot, COLOR_BG);

        // 2. White Lume Main Body with Dark Bevel
        var ptsHourBodyOuter = [
            [-5.0*s, 24.0*s],
            [-4.2*s, 56.0*s],
            [0.0,    62.0*s],
            [4.2*s,  56.0*s],
            [5.0*s,  24.0*s]
        ];
        var ptsHourBodyInner = [
            [-2.4*s, 30.0*s],
            [-2.0*s, 50.0*s],
            [0.0,    55.0*s],
            [2.0*s,  50.0*s],
            [2.4*s,  30.0*s]
        ];
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourBodyOuter, COLOR_WHITE_LUME);
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourBodyInner, COLOR_BG);

        // ── MINUTE HAND (Heavy-Duty 3D Metallic Fork Hand) ─────────────────
        // 1. 3D Metallic V-Fork Base (Left Dark / Right Light)
        var ptsMinForkL = [
            [0.0,     -10.0*s],
            [-5.0*s,  0.0],
            [-4.0*s,  32.0*s],
            [0.0,     32.0*s]
        ];
        var ptsMinForkR = [
            [0.0,     -10.0*s],
            [5.0*s,   0.0],
            [4.0*s,   32.0*s],
            [0.0,     32.0*s]
        ];
        var ptsMinForkSlot = [
            [-1.8*s, -2.0*s],
            [-2.0*s, 28.0*s],
            [2.0*s,  28.0*s],
            [1.8*s,  -2.0*s]
        ];
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinForkL, COLOR_STEEL_DARK);
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinForkR, COLOR_STEEL_LIGHT);
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinForkSlot, COLOR_BG);

        // 2. White Lume Main Body
        var ptsMinBodyOuter = [
            [-4.5*s, 28.0*s],
            [-3.5*s, 86.0*s],
            [0.0,    92.0*s],
            [3.5*s,  86.0*s],
            [4.5*s,  28.0*s]
        ];
        var ptsMinBodyInner = [
            [-2.2*s, 34.0*s],
            [-1.6*s, 80.0*s],
            [0.0,    85.0*s],
            [1.6*s,  80.0*s],
            [2.2*s,  34.0*s]
        ];
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinBodyOuter, COLOR_WHITE_LUME);
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinBodyInner, COLOR_BG);

        // ── SECOND HAND (Hidden in Low-Power Ambient Mode for AMOLED Burn-In Protection) ──
        if (isLowPower) {
            dc.setColor(COLOR_STEEL_DARK, Graphics.COLOR_TRANSPARENT);
            dc.fillCircle(centerX, centerY, (7.0 * s).toNumber());
            dc.setColor(COLOR_STEEL_LIGHT, Graphics.COLOR_TRANSPARENT);
            dc.fillCircle(centerX, centerY, (4.5 * s).toNumber());
            return;
        }

        dc.setPenWidth((2.5 * s).toNumber());
        dc.setColor(COLOR_STEEL_DARK, Graphics.COLOR_TRANSPARENT);

        var tailX = (centerX - 24.0 * s * cosS).toNumber();
        var tailY = (centerY - 24.0 * s * sinS).toNumber();
        var stemX = (centerX + 85.0 * s * cosS).toNumber();
        var stemY = (centerY + 85.0 * s * sinS).toNumber();
        dc.drawLine(tailX, tailY, stemX, stemY);

        // Counterweight (Heavy steel rectangle)
        var ptsSecCounter = [
            [-3.5*s, -24.0*s],
            [-3.5*s, -12.0*s],
            [3.5*s,  -12.0*s],
            [3.5*s,  -24.0*s]
        ];
        drawRotatedPolygon(dc, centerX, centerY, cosS, sinS, ptsSecCounter, COLOR_STEEL_LIGHT);

        // Red Arrow Tip with White Outline Frame
        var ptsSecWhiteFrame = [
            [-4.0*s, 84.0*s],
            [0.0,    112.0*s],
            [4.0*s,  84.0*s],
            [0.0,    90.0*s]
        ];
        var ptsSecRedFill = [
            [-2.5*s, 87.0*s],
            [0.0,    108.0*s],
            [2.5*s,  87.0*s],
            [0.0,    92.0*s]
        ];
        drawRotatedPolygon(dc, centerX, centerY, cosS, sinS, ptsSecWhiteFrame, COLOR_WHITE_LUME);
        drawRotatedPolygon(dc, centerX, centerY, cosS, sinS, ptsSecRedFill, COLOR_RED_ACCENT);

        // ── CENTER PIN HUB (Proportional Metallic Brushed Cap) ────────────
        dc.setColor(COLOR_STEEL_DARK, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(centerX, centerY, (9.0 * s).toNumber());
        dc.setColor(0xE0E0E0, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(centerX, centerY, (7.0 * s).toNumber());
        dc.setColor(COLOR_STEEL_LIGHT, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(centerX, centerY, (4.5 * s).toNumber());
        dc.setColor(COLOR_BG, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(centerX, centerY, (2.0 * s).toNumber());
    }
}