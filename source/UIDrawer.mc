import Toybox.Graphics;
import Toybox.System;
import Toybox.Activity;
import Toybox.ActivityMonitor;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.Math;
import Toybox.WatchUi;

module UIDrawer {

    function getSlotX(slotId, w, offsetX) {
        var centerX = (w / 2) + offsetX;
        var s = w / 260.0;
        
        switch (w) {
            case 260:
                switch (slotId) {
                    case 1: return centerX;
                    case 2: return centerX - 44;
                    case 3: return centerX + 40;
                    case 4: return centerX;
                    case 5: return centerX - 36;
                    case 6: return centerX + 36;
                    case 7: return centerX;
                }
                break;
            case 280:
                switch (slotId) {
                    case 1: return centerX;
                    case 2: return centerX - 47;
                    case 3: return centerX + 43;
                    case 4: return centerX;
                    case 5: return centerX - 39;
                    case 6: return centerX + 39;
                    case 7: return centerX;
                }
                break;
            default:
                switch (slotId) {
                    case 1: return centerX;
                    case 2: return centerX - (44 * s).toNumber();
                    case 3: return centerX + (40 * s).toNumber();
                    case 4: return centerX;
                    case 5: return centerX - (36 * s).toNumber();
                    case 6: return centerX + (36 * s).toNumber();
                    case 7: return centerX;
                }
                break;
        }
        return centerX;
    }

    function getSlotY(slotId, w, h, offsetY) {
        var centerY = (h / 2) + offsetY;
        var s = w / 260.0;
        
        switch (w) {
            case 260:
                switch (slotId) {
                    case 1: return centerY - 48;
                    case 2: return centerY - 26;
                    case 3: return centerY - 26;
                    case 4: return centerY + 16;
                    case 5: return centerY + 30;
                    case 6: return centerY + 30;
                    case 7: return centerY + 54;
                }
                break;
            case 280:
                switch (slotId) {
                    case 1: return centerY - 52;
                    case 2: return centerY - 28;
                    case 3: return centerY - 28;
                    case 4: return centerY + 17;
                    case 5: return centerY + 32;
                    case 6: return centerY + 32;
                    case 7: return centerY + 58;
                }
                break;
            default:
                switch (slotId) {
                    case 1: return centerY - (48 * s).toNumber();
                    case 2: return centerY - (26 * s).toNumber();
                    case 3: return centerY - (26 * s).toNumber();
                    case 4: return centerY + (16 * s).toNumber();
                    case 5: return centerY + (30 * s).toNumber();
                    case 6: return centerY + (30 * s).toNumber();
                    case 7: return centerY + (54 * s).toNumber();
                }
                break;
        }
        return centerY;
    }

    function getSlotScale(w) {
        if (w == 260) {
            return 1.0;
        } else if (w == 280) {
            return 280.0 / 260.0;
        }
        return w / 260.0;
    }

    function drawMetricIcon(dc, type, x, y, s) {
        var bmp = null;
        var themeId = ThemeManager.getPropertyVal("ThemeColor", 1);

        switch (type) {
            case 1:
                bmp = ThemeManager.loadThemedBitmap("icon_battery", themeId);
                break;
            case 2:
                // Heart Rate: Pumping animation ONLY during active workouts/activities!
                var isActivityRunning = false;
                var actInfo = Activity.getActivityInfo();
                if (actInfo != null && actInfo has :timerState && actInfo.timerState != null) {
                    isActivityRunning = (actInfo.timerState == 3 || actInfo.timerState == 1);
                }

                var sec = System.getClockTime().sec;
                var isPulseBeat = isActivityRunning ? (sec % 2 == 0) : false;

                switch (themeId) {
                    case 2: bmp = WatchUi.loadResource(isPulseBeat ? Rez.Drawables.icon_heart_pulse_teal : Rez.Drawables.icon_heart_teal); break;
                    case 3: bmp = WatchUi.loadResource(isPulseBeat ? Rez.Drawables.icon_heart_pulse_orange : Rez.Drawables.icon_heart_orange); break;
                    case 4: bmp = WatchUi.loadResource(isPulseBeat ? Rez.Drawables.icon_heart_pulse_green : Rez.Drawables.icon_heart_green); break;
                    case 5: bmp = WatchUi.loadResource(isPulseBeat ? Rez.Drawables.icon_heart_pulse_gold : Rez.Drawables.icon_heart_gold); break;
                    case 6: bmp = WatchUi.loadResource(isPulseBeat ? Rez.Drawables.icon_heart_pulse_white : Rez.Drawables.icon_heart_white); break;
                    default: bmp = WatchUi.loadResource(isPulseBeat ? Rez.Drawables.icon_heart_pulse_red : Rez.Drawables.icon_heart_red); break;
                }
                break;
            case 3: bmp = ThemeManager.loadThemedBitmap("icon_steps", themeId); break;
            case 4: bmp = ThemeManager.loadThemedBitmap("icon_step_goal", themeId); break;
            case 5: bmp = ThemeManager.loadThemedBitmap("icon_flame", themeId); break;
            case 6: bmp = ThemeManager.loadThemedBitmap("icon_distance", themeId); break;
            case 7: bmp = ThemeManager.loadThemedBitmap("icon_floors", themeId); break;
            case 8: bmp = ThemeManager.loadThemedBitmap("icon_active_mins", themeId); break;
            case 9: bmp = ThemeManager.loadThemedBitmap("icon_stress", themeId); break;
            case 11: bmp = ThemeManager.loadThemedBitmap("icon_bluetooth", themeId); break;
            case 12: bmp = ThemeManager.loadThemedBitmap("icon_altitude", themeId); break;
            case 13: bmp = ThemeManager.loadThemedBitmap("icon_barometer", themeId); break;
            case 14: bmp = ThemeManager.loadThemedBitmap("icon_weather_temp", themeId); break;
            case 15: bmp = ThemeManager.loadThemedBitmap("icon_weather_cond", themeId); break;
            case 16:
                var nowInfo = Gregorian.info(Time.now(), Time.FORMAT_SHORT);
                bmp = ThemeManager.loadThemedBitmap(MetricProvider.getSolarIcon(nowInfo.hour), themeId);
                break;
            case 17: bmp = ThemeManager.loadThemedBitmap("icon_body_battery", themeId); break;
            case 18: bmp = ThemeManager.loadThemedBitmap("icon_sunrise", themeId); break;
            case 19: bmp = ThemeManager.loadThemedBitmap("icon_sunset", themeId); break;
        }

        if (bmp != null) {
            var iconW = bmp.getWidth();
            var iconH = bmp.getHeight();
            dc.drawBitmap((x - iconW / 2).toNumber(), (y - iconH / 2).toNumber(), bmp);
        }
    }

    function drawSingleDataSlot(dc, slotType, slotId, posX, posY, s, customFont, isLowPower) {
        if (slotType == 0) { return; }

        var fontValue = Graphics.FONT_XTINY;
        if (customFont != null) {
            fontValue = customFont;
        }

        if (slotType == 1) {
            var stats = System.getSystemStats();
            var pct = (stats.battery + 0.5).toNumber();
            var isCharging = (stats has :charging && stats.charging != null) ? stats.charging : false;

            var battColor = Graphics.COLOR_WHITE;
            if (isCharging) {
                var sec = System.getClockTime().sec;
                var step = sec % 3;
                switch (step) {
                    case 0: battColor = 0xFF3333; break;
                    case 1: battColor = 0xFF8800; break;
                    default: battColor = 0x00FF66; break;
                }
            } else {
                if (pct <= 20) { battColor = 0xFF3333; }
                else if (pct <= 50) { battColor = 0xFF8800; }
                else { battColor = 0x00FF66; }
            }

            var battText = pct.toString() + "%";
            if (isCharging) {
                battText = "CHG " + battText;
            }

            var battRes = Rez.Drawables.icon_battery_red;
            switch (battColor) {
                case 0xFF8800: battRes = Rez.Drawables.icon_battery_orange; break;
                case 0x00FF66: battRes = Rez.Drawables.icon_battery_green; break;
            }
            var battBmp = WatchUi.loadResource(battRes);

            if (battBmp != null) {
                var iconW = battBmp.getWidth();
                var iconH = battBmp.getHeight();
                dc.drawBitmap((posX - iconW / 2).toNumber(), ((posY - (13 * s)) - iconH / 2).toNumber(), battBmp);
            }

            dc.setColor(battColor, Graphics.COLOR_TRANSPARENT);
            dc.drawText(posX, posY + (9 * s).toNumber(), fontValue, battText, Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
            return;
        }

        var data = MetricProvider.getMetricData(slotType);
        var valStr = data[0];

        drawMetricIcon(dc, slotType, posX, posY - (13 * s).toNumber(), s);

        var valColor = isLowPower ? 0x888888 : Graphics.COLOR_WHITE;
        dc.setColor(valColor, Graphics.COLOR_TRANSPARENT);
        dc.drawText(posX, posY + (9 * s).toNumber(), fontValue, valStr, Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
    }

    function drawDataSlots(dc, aodOffsetX, aodOffsetY, customFont, isLowPower) {
        var w = dc.getWidth();
        var h = dc.getHeight();
        var s = w / 260.0;

        var s1 = ThemeManager.getPropertyVal("Slot1Metric", 1);  
        var s2 = ThemeManager.getPropertyVal("Slot2Metric", 2);  
        var s3 = ThemeManager.getPropertyVal("Slot3Metric", 3);  
        var s4 = ThemeManager.getPropertyVal("Slot4Metric", 11); 
        var s5 = ThemeManager.getPropertyVal("Slot5Metric", 16); 
        var s6 = ThemeManager.getPropertyVal("Slot6Metric", 14); 
        var s7 = ThemeManager.getPropertyVal("Slot7Metric", 5);  

        var sc = getSlotScale(w);
        
        drawSingleDataSlot(dc, s1, 1, getSlotX(1, w, aodOffsetX), getSlotY(1, w, h, aodOffsetY), sc, customFont, isLowPower);
        drawSingleDataSlot(dc, s2, 2, getSlotX(2, w, aodOffsetX), getSlotY(2, w, h, aodOffsetY), sc, customFont, isLowPower);
        drawSingleDataSlot(dc, s3, 3, getSlotX(3, w, aodOffsetX), getSlotY(3, w, h, aodOffsetY), sc, customFont, isLowPower);
        
        if (s4 != 0) { 
            drawMetricIcon(dc, s4, getSlotX(4, w, aodOffsetX), getSlotY(4, w, h, aodOffsetY), sc); 
        }
        
        drawSingleDataSlot(dc, s5, 5, getSlotX(5, w, aodOffsetX), getSlotY(5, w, h, aodOffsetY), sc, customFont, isLowPower);
        drawSingleDataSlot(dc, s6, 6, getSlotX(6, w, aodOffsetX), getSlotY(6, w, h, aodOffsetY), sc, customFont, isLowPower);
        drawSingleDataSlot(dc, s7, 7, getSlotX(7, w, aodOffsetX), getSlotY(7, w, h, aodOffsetY), sc, customFont, isLowPower);
    }

    function drawConcentricRings(dc, now, dialBg, isLowPower, centerX, centerY) {
        if (isLowPower) { return; } 

        var TWO_PI  = Math.PI * 2.0;
        var HALF_PI = Math.PI / 2.0;
        
        var w = dc.getWidth();
        var h = dc.getHeight();
        var scale = w / 260.0;

        if (dialBg != null) {
            var bgW = dialBg.getWidth();
            var bgH = dialBg.getHeight();
            var bgX = (w - bgW) / 2;
            var bgY = (h - bgH) / 2;
            dc.drawBitmap(bgX, bgY, dialBg);
        }

        dc.setPenWidth(4);

        var r1       = (96 * scale).toNumber(); 
        var dayStep  = TWO_PI / 31.0;
        var d = now.day;
        var angle1 = (d - 1) * dayStep - HALF_PI;
        var degCenter1 = ((- (angle1 * 180.0 / Math.PI)).toNumber() % 360 + 360) % 360;
        
        var themeAccent = isLowPower ? 0x555555 : ThemeManager.getThemeAccentColor();
        dc.setColor(themeAccent, Graphics.COLOR_TRANSPARENT);
        var r1_arc = r1 - (5 * scale).toNumber();
        dc.drawArc(centerX, centerY, r1_arc, Graphics.ARC_COUNTER_CLOCKWISE, (degCenter1 - 4 + 360) % 360, (degCenter1 + 4 + 360) % 360);

        var r2       = (117 * scale).toNumber();
        var m = now.month;
        var monStep  = TWO_PI / 12.0;
        var angle2 = (m - 1) * monStep - HALF_PI;
        var degCenter2 = ((- (angle2 * 180.0 / Math.PI)).toNumber() % 360 + 360) % 360;
        
        var r2_arc = r2 - (5 * scale).toNumber();
        dc.drawArc(centerX, centerY, r2_arc, Graphics.ARC_COUNTER_CLOCKWISE, (degCenter2 - 10 + 360) % 360, (degCenter2 + 10 + 360) % 360);

        var r3       = (75 * scale).toNumber();
        var wkStep  = TWO_PI / 7.0;
        var w_day = now.day_of_week;
        var angle3 = (w_day - 1) * wkStep - HALF_PI;
        var degCenter3 = ((- (angle3 * 180.0 / Math.PI)).toNumber() % 360 + 360) % 360;
        
        var r3_arc = r3 - (5 * scale).toNumber();
        dc.drawArc(centerX, centerY, r3_arc, Graphics.ARC_COUNTER_CLOCKWISE, (degCenter3 - 16 + 360) % 360, (degCenter3 + 16 + 360) % 360);
    }

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

    function drawHands(dc, hour, min, sec, isLowPower, centerX, centerY) {
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
        var COLOR_RED_ACCENT  = isLowPower ? 0x555555 : ThemeManager.getThemeAccentColor();
        var COLOR_BG          = Graphics.COLOR_BLACK;

        var ptsHourForkL = [ [0.0, -10.0*s], [-5.5*s, 0.0], [-4.5*s, 28.0*s], [0.0, 28.0*s] ];
        var ptsHourForkR = [ [0.0, -10.0*s], [5.5*s, 0.0], [4.5*s, 28.0*s], [0.0, 28.0*s] ];
        var ptsHourForkSlot = [ [-2.0*s, -2.0*s], [-2.2*s, 24.0*s], [2.2*s, 24.0*s], [2.0*s, -2.0*s] ];
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourForkL, COLOR_STEEL_DARK);
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourForkR, COLOR_STEEL_LIGHT);
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourForkSlot, COLOR_BG);

        var ptsHourBodyOuter = [ [-5.0*s, 24.0*s], [-4.2*s, 56.0*s], [0.0, 62.0*s], [4.2*s, 56.0*s], [5.0*s, 24.0*s] ];
        var ptsHourBodyInner = [ [-2.4*s, 30.0*s], [-2.0*s, 50.0*s], [0.0, 55.0*s], [2.0*s, 50.0*s], [2.4*s, 30.0*s] ];
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourBodyOuter, COLOR_WHITE_LUME);
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourBodyInner, COLOR_BG);

        var ptsMinForkL = [ [0.0, -10.0*s], [-5.0*s, 0.0], [-4.0*s, 32.0*s], [0.0, 32.0*s] ];
        var ptsMinForkR = [ [0.0, -10.0*s], [5.0*s, 0.0], [4.0*s, 32.0*s], [0.0, 32.0*s] ];
        var ptsMinForkSlot = [ [-1.8*s, -2.0*s], [-2.0*s, 28.0*s], [2.0*s, 28.0*s], [1.8*s, -2.0*s] ];
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinForkL, COLOR_STEEL_DARK);
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinForkR, COLOR_STEEL_LIGHT);
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinForkSlot, COLOR_BG);

        var ptsMinBodyOuter = [ [-4.5*s, 28.0*s], [-3.5*s, 86.0*s], [0.0, 92.0*s], [3.5*s, 86.0*s], [4.5*s, 28.0*s] ];
        var ptsMinBodyInner = [ [-2.2*s, 34.0*s], [-1.6*s, 80.0*s], [0.0, 85.0*s], [1.6*s, 80.0*s], [2.2*s, 34.0*s] ];
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinBodyOuter, COLOR_WHITE_LUME);
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinBodyInner, COLOR_BG);

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

        var ptsSecCounter = [ [-3.5*s, -24.0*s], [-3.5*s, -12.0*s], [3.5*s, -12.0*s], [3.5*s, -24.0*s] ];
        drawRotatedPolygon(dc, centerX, centerY, cosS, sinS, ptsSecCounter, COLOR_STEEL_LIGHT);

        var ptsSecWhiteFrame = [ [-4.0*s, 84.0*s], [0.0, 112.0*s], [4.0*s, 84.0*s], [0.0, 90.0*s] ];
        var ptsSecRedFill = [ [-2.5*s, 87.0*s], [0.0, 108.0*s], [2.5*s, 87.0*s], [0.0, 92.0*s] ];
        drawRotatedPolygon(dc, centerX, centerY, cosS, sinS, ptsSecWhiteFrame, COLOR_WHITE_LUME);
        drawRotatedPolygon(dc, centerX, centerY, cosS, sinS, ptsSecRedFill, COLOR_RED_ACCENT);

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
