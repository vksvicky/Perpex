import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;
import Toybox.ActivityMonitor;
import Toybox.Activity;
import Toybox.Weather;
import Toybox.SensorHistory;

module MetricProvider {

    function formatTimeString(hour, min) {
        var timeFormat = ThemeManager.getPropertyVal("TimeFormat", 0);
        if (timeFormat == 1) {
            var ampm = (hour < 12) ? "a" : "p";
            var hour12 = hour % 12;
            if (hour12 == 0) { hour12 = 12; }
            return hour12.toString() + ":" + min.format("%02d") + ampm;
        } else {
            return hour.format("%02d") + ":" + min.format("%02d");
        }
    }

    function getSolarIcon(hour) {
        if (hour >= 12) {
            return "icon_sunset";
        }
        return "icon_sunrise";
    }

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
            return [formatTimeString(clock.hour, clock.min), ""];
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
        } else if (type == 14) { // Weather Temp
            var unitVal = ThemeManager.getPropertyVal("TemperatureUnit", 0);
            var isFahrenheit = (unitVal == 1);
            if (Toybox has :Weather && Weather has :getCurrentConditions) {
                var cond = Weather.getCurrentConditions();
                if (cond != null && cond.temperature != null) {
                    var temp = cond.temperature;
                    if (isFahrenheit) {
                        temp = (temp * 9.0 / 5.0) + 32.0;
                    }
                    return [temp.toNumber().toString() + (isFahrenheit ? "°F" : "°C"), "WEATHER"];
                }
            }
            return [isFahrenheit ? "70°F" : "21°C", "WEATHER"];
        } else if (type == 15) { // Weather Condition
            if (Toybox has :Weather && Weather has :getCurrentConditions) {
                var cond = Weather.getCurrentConditions();
                if (cond != null) {
                    var str = "";
                    if (cond.precipitationChance != null && cond.precipitationChance > 0) {
                        str = cond.precipitationChance.toString() + "% RAIN";
                    } else if (cond.condition != null) {
                        var c = cond.condition;
                        if (c == Weather.CONDITION_CLEAR || c == Weather.CONDITION_FAIR) { str = "CLEAR"; }
                        else if (c == Weather.CONDITION_CLOUDY || c == Weather.CONDITION_MOSTLY_CLOUDY || c == Weather.CONDITION_PARTLY_CLOUDY) { str = "CLOUDY"; }
                        else if (c == Weather.CONDITION_RAIN || c == Weather.CONDITION_SHOWERS || c == Weather.CONDITION_HEAVY_RAIN) { str = "RAIN"; }
                        else if (c == Weather.CONDITION_SNOW) { str = "SNOW"; }
                        else { str = "WEATHER"; }
                    }
                    if (!str.equals("")) { return [str, ""]; }
                }
            }
            return ["CLOUDY", ""];
        } else if (type == 16) { // Sunrise / Sunset (Dynamic)
            var pos = LocationHelper.getBestLocation();
            if (pos != null) {
                var nowTime = Time.now();
                var sc = new SunCalc();
                var posRad = pos.toRadians();
                var nowInfo = Gregorian.info(nowTime, Time.FORMAT_SHORT);
                
                if (nowInfo.hour < 12) {
                    var sunrise = sc.calculate(nowTime, posRad, 4); // 4 = SUNRISE
                    if (sunrise != null) {
                        var info = Gregorian.info(sunrise, Time.FORMAT_SHORT);
                        return [formatTimeString(info.hour, info.min), "SUNRISE"];
                    }
                    return ["--:--", "SUNRISE"];
                } else {
                    var sunset = sc.calculate(nowTime, posRad, 10); // 10 = SUNSET
                    if (sunset != null) {
                        var info = Gregorian.info(sunset, Time.FORMAT_SHORT);
                        return [formatTimeString(info.hour, info.min), "SUNSET"];
                    }
                    return ["--:--", "SUNSET"];
                }
            }
            var fallbackInfo = Gregorian.info(Time.now(), Time.FORMAT_SHORT);
            return ["--:--", fallbackInfo.hour < 12 ? "SUNRISE" : "SUNSET"];
        } else if (type == 17) { // Body Battery
            if (Toybox has :SensorHistory && SensorHistory has :getBodyBatteryHistory) {
                var bbIter = SensorHistory.getBodyBatteryHistory({:period => 1});
                if (bbIter != null) {
                    var sample = bbIter.next();
                    if (sample != null && sample.data != null) {
                        return [sample.data.toNumber().toString() + "%", "BODY BATT"];
                    }
                }
            }
            return ["85%", "BODY BATT"];
        } else if (type == 18) { // Sunrise Only
            if (Toybox has :Weather && Weather has :getSunrise) {
                var cond = (Weather has :getCurrentConditions) ? Weather.getCurrentConditions() : null;
                var pos = (cond != null && cond.observationLocationPosition != null) ? cond.observationLocationPosition : null;
                if (pos != null) {
                    var sunrise = Weather.getSunrise(pos, Time.now());
                    if (sunrise != null) {
                        var info = Gregorian.info(sunrise, Time.FORMAT_SHORT);
                        return [formatTimeString(info.hour, info.min), "SUNRISE"];
                    }
                }
            }
            return ["06:14", "SUNRISE"];
        } else if (type == 19) { // Sunset Only
            if (Toybox has :Weather && Weather has :getSunset) {
                var cond = (Weather has :getCurrentConditions) ? Weather.getCurrentConditions() : null;
                var pos = (cond != null && cond.observationLocationPosition != null) ? cond.observationLocationPosition : null;
                if (pos != null) {
                    var sunset = Weather.getSunset(pos, Time.now());
                    if (sunset != null) {
                        var info = Gregorian.info(sunset, Time.FORMAT_SHORT);
                        return [formatTimeString(info.hour, info.min), "SUNSET"];
                    }
                }
            }
            return ["18:45", "SUNSET"];
        }
        return ["", ""];
    }
}
