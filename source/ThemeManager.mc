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

        switch (mode) {
            case 0: // Disabled / Off
                return false;
            case 3: // Always On
                return true;
            case 1: // Auto (Sunset to Sunrise)
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
                var hour1 = System.getClockTime().hour;
                return (hour1 < 6 || hour1 >= 22);
            case 2: // Scheduled
                var startH = getPropertyVal("NightStartHour", 22);
                var endH   = getPropertyVal("NightEndHour", 6);
                var hour2  = System.getClockTime().hour;
                if (startH > endH) {
                    return (hour2 >= startH || hour2 < endH);
                } else {
                    return (hour2 >= startH && hour2 < endH);
                }
            default:
                return false;
        }
    }

    function getNightColorHex() {
        var ncVal = getPropertyVal("NightModeColor", 0);
        switch (ncVal) {
            case 1: return 0xFF8800; // Night Amber
            case 2: return 0x00FF00; // Stealth Green
            default: return 0xFF0000; // Tactical Red (Default)
        }
    }

    function getThemeAccentColor() {
        if (isNightModeActive()) {
            return getNightColorHex();
        }
        var themeId = getPropertyVal("ThemeColor", 1);
        switch (themeId) {
            case 2: return 0x00CCCC;      // Teal / Cyan
            case 3: return 0xFF8800;      // Warm Orange (Pure Orange)
            case 4: return 0x00FF66;      // Electric Green
            case 5: return 0xFFFF00;      // Gold / Yellow (Pure Bright Yellow)
            case 6: return 0xFFFFFF;      // Pure White
            default: return 0xFF3333;     // Vibrant Red (Default)
        }
    }

    function getThemeDrawable(redRes, tealRes, orangeRes, greenRes, goldRes, whiteRes, themeId) {
        switch (themeId) {
            case 2: return WatchUi.loadResource(tealRes);
            case 3: return WatchUi.loadResource(orangeRes);
            case 4: return WatchUi.loadResource(greenRes);
            case 5: return WatchUi.loadResource(goldRes);
            case 6: return WatchUi.loadResource(whiteRes);
            default: return WatchUi.loadResource(redRes);
        }
    }

    function loadThemedBitmap(baseName, themeId) {
        switch (baseName) {
            case "icon_battery": return getThemeDrawable(Rez.Drawables.icon_battery_red, Rez.Drawables.icon_battery_teal, Rez.Drawables.icon_battery_orange, Rez.Drawables.icon_battery_green, Rez.Drawables.icon_battery_gold, Rez.Drawables.icon_battery_white, themeId);
            case "icon_steps": return getThemeDrawable(Rez.Drawables.icon_steps_red, Rez.Drawables.icon_steps_teal, Rez.Drawables.icon_steps_orange, Rez.Drawables.icon_steps_green, Rez.Drawables.icon_steps_gold, Rez.Drawables.icon_steps_white, themeId);
            case "icon_step_goal": return getThemeDrawable(Rez.Drawables.icon_step_goal_red, Rez.Drawables.icon_step_goal_teal, Rez.Drawables.icon_step_goal_orange, Rez.Drawables.icon_step_goal_green, Rez.Drawables.icon_step_goal_gold, Rez.Drawables.icon_step_goal_white, themeId);
            case "icon_flame": return getThemeDrawable(Rez.Drawables.icon_flame_red, Rez.Drawables.icon_flame_teal, Rez.Drawables.icon_flame_orange, Rez.Drawables.icon_flame_green, Rez.Drawables.icon_flame_gold, Rez.Drawables.icon_flame_white, themeId);
            case "icon_distance": return getThemeDrawable(Rez.Drawables.icon_distance_red, Rez.Drawables.icon_distance_teal, Rez.Drawables.icon_distance_orange, Rez.Drawables.icon_distance_green, Rez.Drawables.icon_distance_gold, Rez.Drawables.icon_distance_white, themeId);
            case "icon_floors": return getThemeDrawable(Rez.Drawables.icon_floors_red, Rez.Drawables.icon_floors_teal, Rez.Drawables.icon_floors_orange, Rez.Drawables.icon_floors_green, Rez.Drawables.icon_floors_gold, Rez.Drawables.icon_floors_white, themeId);
            case "icon_active_mins": return getThemeDrawable(Rez.Drawables.icon_active_mins_red, Rez.Drawables.icon_active_mins_teal, Rez.Drawables.icon_active_mins_orange, Rez.Drawables.icon_active_mins_green, Rez.Drawables.icon_active_mins_gold, Rez.Drawables.icon_active_mins_white, themeId);
            case "icon_stress": return getThemeDrawable(Rez.Drawables.icon_stress_red, Rez.Drawables.icon_stress_teal, Rez.Drawables.icon_stress_orange, Rez.Drawables.icon_stress_green, Rez.Drawables.icon_stress_gold, Rez.Drawables.icon_stress_white, themeId);
            case "icon_bluetooth": return getThemeDrawable(Rez.Drawables.icon_bluetooth_red, Rez.Drawables.icon_bluetooth_teal, Rez.Drawables.icon_bluetooth_orange, Rez.Drawables.icon_bluetooth_green, Rez.Drawables.icon_bluetooth_gold, Rez.Drawables.icon_bluetooth_white, themeId);
            case "icon_altitude": return getThemeDrawable(Rez.Drawables.icon_altitude_red, Rez.Drawables.icon_altitude_teal, Rez.Drawables.icon_altitude_orange, Rez.Drawables.icon_altitude_green, Rez.Drawables.icon_altitude_gold, Rez.Drawables.icon_altitude_white, themeId);
            case "icon_barometer": return getThemeDrawable(Rez.Drawables.icon_barometer_red, Rez.Drawables.icon_barometer_teal, Rez.Drawables.icon_barometer_orange, Rez.Drawables.icon_barometer_green, Rez.Drawables.icon_barometer_gold, Rez.Drawables.icon_barometer_white, themeId);
            case "icon_weather_temp": return getThemeDrawable(Rez.Drawables.icon_weather_temp_red, Rez.Drawables.icon_weather_temp_teal, Rez.Drawables.icon_weather_temp_orange, Rez.Drawables.icon_weather_temp_green, Rez.Drawables.icon_weather_temp_gold, Rez.Drawables.icon_weather_temp_white, themeId);
            case "icon_weather_cond": return getThemeDrawable(Rez.Drawables.icon_weather_cond_red, Rez.Drawables.icon_weather_cond_teal, Rez.Drawables.icon_weather_cond_orange, Rez.Drawables.icon_weather_cond_green, Rez.Drawables.icon_weather_cond_gold, Rez.Drawables.icon_weather_cond_white, themeId);
            case "icon_sunrise": return getThemeDrawable(Rez.Drawables.icon_sunrise_red, Rez.Drawables.icon_sunrise_teal, Rez.Drawables.icon_sunrise_orange, Rez.Drawables.icon_sunrise_green, Rez.Drawables.icon_sunrise_gold, Rez.Drawables.icon_sunrise_white, themeId);
            case "icon_sunset": return getThemeDrawable(Rez.Drawables.icon_sunset_red, Rez.Drawables.icon_sunset_teal, Rez.Drawables.icon_sunset_orange, Rez.Drawables.icon_sunset_green, Rez.Drawables.icon_sunset_gold, Rez.Drawables.icon_sunset_white, themeId);
            case "icon_body_battery": return getThemeDrawable(Rez.Drawables.icon_body_battery_red, Rez.Drawables.icon_body_battery_teal, Rez.Drawables.icon_body_battery_orange, Rez.Drawables.icon_body_battery_green, Rez.Drawables.icon_body_battery_gold, Rez.Drawables.icon_body_battery_white, themeId);
            default: return null;
        }
    }
}
