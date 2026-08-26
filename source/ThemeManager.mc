import Toybox.Application.Properties;
import Toybox.System;
import Toybox.Time;
import Toybox.Weather;
import Toybox.WatchUi;

module ThemeManager {

    function getPropertyVal(key, defaultVal) {
        try {
            if (Toybox.Application has :Properties) {
                var val = Properties.getValue(key);
                if (val != null) { return val; }
            }
        } catch (e) {}
        return defaultVal;
    }

    function isNightModeActive() {
        var mode = getPropertyVal("NightMode", 1);
        if (mode == 0) { return false; } // Disabled / Off
        if (mode == 3) { return true; }  // Always On

        if (mode == 1) { // Auto (Sunset to Sunrise)
            if (Toybox has :Weather && Weather has :getSunset && Weather has :getSunrise) {
                var cond = (Weather has :getCurrentConditions) ? Weather.getCurrentConditions() : null;
                var pos = (cond != null && cond.observationLocationPosition != null) ? cond.observationLocationPosition : null;
                if (pos != null) {
                    var nowTime = Time.now();
                    var sunrise = Weather.getSunrise(pos, nowTime);
                    var sunset  = Weather.getSunset(pos, nowTime);
                    if (sunrise != null && nowTime.lessThan(sunrise)) { return true; }
                    if (sunset != null && !nowTime.lessThan(sunset)) { return true; }
                }
            }
            var hour = System.getClockTime().hour;
            return (hour < 6 || hour >= 22);
        } else if (mode == 2) { // Scheduled
            var startH = getPropertyVal("NightStartHour", 22);
            var endH   = getPropertyVal("NightEndHour", 6);
            var hour   = System.getClockTime().hour;
            if (startH > endH) {
                return (hour >= startH || hour < endH);
            } else {
                return (hour >= startH && hour < endH);
            }
        }
        return false;
    }

    function getNightColorHex() {
        var ncVal = getPropertyVal("NightModeColor", 0);
        if (ncVal == 1) { return 0xFF8800; } // Night Amber
        if (ncVal == 2) { return 0x00FF00; } // Stealth Green
        return 0xFF0000;                     // Tactical Red (Default)
    }

    function getThemeAccentColor() {
        if (isNightModeActive()) {
            return getNightColorHex();
        }
        var themeId = getPropertyVal("ThemeColor", 1);
        if (themeId == 2) { return 0x00CCCC; }      // Teal / Cyan
        else if (themeId == 3) { return 0xFF8800; } // Warm Orange (Pure Orange)
        else if (themeId == 4) { return 0x00FF66; } // Electric Green
        else if (themeId == 5) { return 0xFFFF00; } // Gold / Yellow (Pure Bright Yellow)
        else if (themeId == 6) { return 0xFFFFFF; } // Pure White
        return 0xFF3333;                            // Vibrant Red (Default)
    }

    function getThemeDrawable(redRes, tealRes, orangeRes, greenRes, goldRes, whiteRes, themeId) {
        if (themeId == 2) { return WatchUi.loadResource(tealRes); }
        if (themeId == 3) { return WatchUi.loadResource(orangeRes); }
        if (themeId == 4) { return WatchUi.loadResource(greenRes); }
        if (themeId == 5) { return WatchUi.loadResource(goldRes); }
        if (themeId == 6) { return WatchUi.loadResource(whiteRes); }
        return WatchUi.loadResource(redRes);
    }

    function loadThemedBitmap(baseName, themeId) {
        if (baseName.equals("icon_battery")) { return getThemeDrawable(Rez.Drawables.icon_battery_red, Rez.Drawables.icon_battery_teal, Rez.Drawables.icon_battery_orange, Rez.Drawables.icon_battery_green, Rez.Drawables.icon_battery_gold, Rez.Drawables.icon_battery_white, themeId); }
        if (baseName.equals("icon_steps")) { return getThemeDrawable(Rez.Drawables.icon_steps_red, Rez.Drawables.icon_steps_teal, Rez.Drawables.icon_steps_orange, Rez.Drawables.icon_steps_green, Rez.Drawables.icon_steps_gold, Rez.Drawables.icon_steps_white, themeId); }
        if (baseName.equals("icon_step_goal")) { return getThemeDrawable(Rez.Drawables.icon_step_goal_red, Rez.Drawables.icon_step_goal_teal, Rez.Drawables.icon_step_goal_orange, Rez.Drawables.icon_step_goal_green, Rez.Drawables.icon_step_goal_gold, Rez.Drawables.icon_step_goal_white, themeId); }
        if (baseName.equals("icon_flame")) { return getThemeDrawable(Rez.Drawables.icon_flame_red, Rez.Drawables.icon_flame_teal, Rez.Drawables.icon_flame_orange, Rez.Drawables.icon_flame_green, Rez.Drawables.icon_flame_gold, Rez.Drawables.icon_flame_white, themeId); }
        if (baseName.equals("icon_distance")) { return getThemeDrawable(Rez.Drawables.icon_distance_red, Rez.Drawables.icon_distance_teal, Rez.Drawables.icon_distance_orange, Rez.Drawables.icon_distance_green, Rez.Drawables.icon_distance_gold, Rez.Drawables.icon_distance_white, themeId); }
        if (baseName.equals("icon_floors")) { return getThemeDrawable(Rez.Drawables.icon_floors_red, Rez.Drawables.icon_floors_teal, Rez.Drawables.icon_floors_orange, Rez.Drawables.icon_floors_green, Rez.Drawables.icon_floors_gold, Rez.Drawables.icon_floors_white, themeId); }
        if (baseName.equals("icon_active_mins")) { return getThemeDrawable(Rez.Drawables.icon_active_mins_red, Rez.Drawables.icon_active_mins_teal, Rez.Drawables.icon_active_mins_orange, Rez.Drawables.icon_active_mins_green, Rez.Drawables.icon_active_mins_gold, Rez.Drawables.icon_active_mins_white, themeId); }
        if (baseName.equals("icon_stress")) { return getThemeDrawable(Rez.Drawables.icon_stress_red, Rez.Drawables.icon_stress_teal, Rez.Drawables.icon_stress_orange, Rez.Drawables.icon_stress_green, Rez.Drawables.icon_stress_gold, Rez.Drawables.icon_stress_white, themeId); }
        if (baseName.equals("icon_bluetooth")) { return getThemeDrawable(Rez.Drawables.icon_bluetooth_red, Rez.Drawables.icon_bluetooth_teal, Rez.Drawables.icon_bluetooth_orange, Rez.Drawables.icon_bluetooth_green, Rez.Drawables.icon_bluetooth_gold, Rez.Drawables.icon_bluetooth_white, themeId); }
        if (baseName.equals("icon_altitude")) { return getThemeDrawable(Rez.Drawables.icon_altitude_red, Rez.Drawables.icon_altitude_teal, Rez.Drawables.icon_altitude_orange, Rez.Drawables.icon_altitude_green, Rez.Drawables.icon_altitude_gold, Rez.Drawables.icon_altitude_white, themeId); }
        if (baseName.equals("icon_barometer")) { return getThemeDrawable(Rez.Drawables.icon_barometer_red, Rez.Drawables.icon_barometer_teal, Rez.Drawables.icon_barometer_orange, Rez.Drawables.icon_barometer_green, Rez.Drawables.icon_barometer_gold, Rez.Drawables.icon_barometer_white, themeId); }
        if (baseName.equals("icon_weather_temp")) { return getThemeDrawable(Rez.Drawables.icon_weather_temp_red, Rez.Drawables.icon_weather_temp_teal, Rez.Drawables.icon_weather_temp_orange, Rez.Drawables.icon_weather_temp_green, Rez.Drawables.icon_weather_temp_gold, Rez.Drawables.icon_weather_temp_white, themeId); }
        if (baseName.equals("icon_weather_cond")) { return getThemeDrawable(Rez.Drawables.icon_weather_cond_red, Rez.Drawables.icon_weather_cond_teal, Rez.Drawables.icon_weather_cond_orange, Rez.Drawables.icon_weather_cond_green, Rez.Drawables.icon_weather_cond_gold, Rez.Drawables.icon_weather_cond_white, themeId); }
        if (baseName.equals("icon_sunrise")) { return getThemeDrawable(Rez.Drawables.icon_sunrise_red, Rez.Drawables.icon_sunrise_teal, Rez.Drawables.icon_sunrise_orange, Rez.Drawables.icon_sunrise_green, Rez.Drawables.icon_sunrise_gold, Rez.Drawables.icon_sunrise_white, themeId); }
        if (baseName.equals("icon_sunset")) { return getThemeDrawable(Rez.Drawables.icon_sunset_red, Rez.Drawables.icon_sunset_teal, Rez.Drawables.icon_sunset_orange, Rez.Drawables.icon_sunset_green, Rez.Drawables.icon_sunset_gold, Rez.Drawables.icon_sunset_white, themeId); }
        if (baseName.equals("icon_body_battery")) { return getThemeDrawable(Rez.Drawables.icon_body_battery_red, Rez.Drawables.icon_body_battery_teal, Rez.Drawables.icon_body_battery_orange, Rez.Drawables.icon_body_battery_green, Rez.Drawables.icon_body_battery_gold, Rez.Drawables.icon_body_battery_white, themeId); }
        return null;
    }
}
