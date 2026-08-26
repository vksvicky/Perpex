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
        var val = "";
        var label = "";
        var info = null;

        switch (type) {
            case 1: // Battery
                var stats = System.getSystemStats();
                val = (stats.battery + 0.5).toNumber().toString() + "%";
                break;
            case 2: // Heart Rate
                val = "--";
                label = "BPM";
                if (ActivityMonitor has :getHeartRateHistory) {
                    var hrIter = ActivityMonitor.getHeartRateHistory(1, true);
                    var sample = hrIter.next();
                    if (sample != null && sample.heartRate != ActivityMonitor.INVALID_HR_SAMPLE) {
                        val = sample.heartRate.toString();
                    }
                }
                break;
            case 3: // Steps
                info = ActivityMonitor.getInfo();
                val = (info != null && info.steps != null) ? info.steps.toString() : "0";
                label = "STEPS";
                break;
            case 4: // Step Goal %
                info = ActivityMonitor.getInfo();
                val = "0%";
                label = "GOAL";
                if (info != null && info.steps != null && info.stepGoal != null && info.stepGoal > 0) {
                    val = ((info.steps.toDouble() / info.stepGoal.toDouble()) * 100).toNumber().toString() + "%";
                }
                break;
            case 5: // Active Calories
                info = ActivityMonitor.getInfo();
                val = (info != null && info.calories != null) ? info.calories.toString() : "0";
                label = "kCal";
                break;
            case 6: // Distance
                info = ActivityMonitor.getInfo();
                val = (info != null && info.distance != null) ? (info.distance / 100000.0).format("%.1f") : "0.0";
                label = "KM";
                break;
            case 7: // Floors
                info = ActivityMonitor.getInfo();
                val = (info != null && info has :floorsClimbed && info.floorsClimbed != null) ? info.floorsClimbed.toString() : "0";
                label = "FLOORS";
                break;
            case 8: // Active Minutes
                info = ActivityMonitor.getInfo();
                val = (info != null && info has :activeMinutesWeek && info.activeMinutesWeek != null && info.activeMinutesWeek.total != null) ? info.activeMinutesWeek.total.toString() : "0";
                label = "MINS";
                break;
            case 9: // Stress
                info = ActivityMonitor.getInfo();
                val = (info != null && info has :stressScore && info.stressScore != null) ? info.stressScore.toString() : "--";
                label = "STRESS";
                break;
            case 10: // Digital Time
                var clock = System.getClockTime();
                val = formatTimeString(clock.hour, clock.min);
                break;
            case 11: // Notifications / Phone Status
                var device = System.getDeviceSettings();
                var count = (device has :notificationCount) ? device.notificationCount : 0;
                val = count.toString();
                break;
            case 12: // Altitude
                info = Activity.getActivityInfo();
                val = (info != null && info has :altitude && info.altitude != null) ? info.altitude.toNumber().toString() : "--";
                label = "METERS";
                break;
            case 13: // Barometer
                info = Activity.getActivityInfo();
                val = (info != null && info has :rawAmbientPressure && info.rawAmbientPressure != null) ? (info.rawAmbientPressure / 100.0).toNumber().toString() : "--";
                label = "HPA";
                break;
            case 14: // Weather Temp
                var unitVal = ThemeManager.getPropertyVal("TemperatureUnit", 0);
                var isFahrenheit = (unitVal == 1);
                label = "WEATHER";
                val = isFahrenheit ? "70°F" : "21°C";
                if (Toybox has :Weather && Weather has :getCurrentConditions) {
                    var cond = Weather.getCurrentConditions();
                    if (cond != null && cond.temperature != null) {
                        var temp = cond.temperature;
                        if (isFahrenheit) {
                            temp = (temp * 9.0 / 5.0) + 32.0;
                        }
                        val = temp.toNumber().toString() + (isFahrenheit ? "°F" : "°C");
                    }
                }
                break;
            case 15: // Weather Condition
                val = "CLOUDY";
                if (Toybox has :Weather && Weather has :getCurrentConditions) {
                    var cond = Weather.getCurrentConditions();
                    if (cond != null) {
                        if (cond.precipitationChance != null && cond.precipitationChance > 0) {
                            val = cond.precipitationChance.toString() + "% RAIN";
                        } else if (cond.condition != null) {
                            var c = cond.condition;
                            switch (c) {
                                case Weather.CONDITION_CLEAR:
                                case Weather.CONDITION_FAIR:
                                    val = "CLEAR";
                                    break;
                                case Weather.CONDITION_CLOUDY:
                                case Weather.CONDITION_MOSTLY_CLOUDY:
                                case Weather.CONDITION_PARTLY_CLOUDY:
                                    val = "CLOUDY";
                                    break;
                                case Weather.CONDITION_RAIN:
                                case Weather.CONDITION_SHOWERS:
                                case Weather.CONDITION_HEAVY_RAIN:
                                    val = "RAIN";
                                    break;
                                case Weather.CONDITION_SNOW:
                                    val = "SNOW";
                                    break;
                                default:
                                    val = "WEATHER";
                                    break;
                            }
                        }
                    }
                }
                break;
            case 16: // Sunrise / Sunset (Dynamic)
                var pos = LocationHelper.getBestLocation();
                var nowTime = Time.now();
                var nowInfo = Gregorian.info(nowTime, Time.FORMAT_SHORT);
                val = "--:--";
                label = (nowInfo.hour < 12) ? "SUNRISE" : "SUNSET";
                if (pos != null) {
                    var sc = new SunCalc();
                    var posRad = pos.toRadians();
                    if (nowInfo.hour < 12) {
                        var sunrise = sc.calculate(nowTime, posRad, 4); // SUNRISE
                        if (sunrise != null) {
                            var infoSunrise = Gregorian.info(sunrise, Time.FORMAT_SHORT);
                            val = formatTimeString(infoSunrise.hour, infoSunrise.min);
                        }
                    } else {
                        var sunset = sc.calculate(nowTime, posRad, 10); // SUNSET
                        if (sunset != null) {
                            var infoSunset = Gregorian.info(sunset, Time.FORMAT_SHORT);
                            val = formatTimeString(infoSunset.hour, infoSunset.min);
                        }
                    }
                }
                break;
            case 17: // Body Battery
                val = "85%";
                label = "BODY BATT";
                if (Toybox has :SensorHistory && SensorHistory has :getBodyBatteryHistory) {
                    var bbIter = SensorHistory.getBodyBatteryHistory({:period => 1});
                    if (bbIter != null) {
                        var sample = bbIter.next();
                        if (sample != null && sample.data != null) {
                            val = sample.data.toNumber().toString() + "%";
                        }
                    }
                }
                break;
            case 18: // Sunrise Only
                val = "06:14";
                label = "SUNRISE";
                if (Toybox has :Weather && Weather has :getSunrise) {
                    var cond = (Weather has :getCurrentConditions) ? Weather.getCurrentConditions() : null;
                    var wPos = (cond != null && cond.observationLocationPosition != null) ? cond.observationLocationPosition : null;
                    if (wPos != null) {
                        var wSunrise = Weather.getSunrise(wPos, Time.now());
                        if (wSunrise != null) {
                            var infoWSunrise = Gregorian.info(wSunrise, Time.FORMAT_SHORT);
                            val = formatTimeString(infoWSunrise.hour, infoWSunrise.min);
                        }
                    }
                }
                break;
            case 19: // Sunset Only
                val = "18:45";
                label = "SUNSET";
                if (Toybox has :Weather && Weather has :getSunset) {
                    var cond = (Weather has :getCurrentConditions) ? Weather.getCurrentConditions() : null;
                    var wPos = (cond != null && cond.observationLocationPosition != null) ? cond.observationLocationPosition : null;
                    if (wPos != null) {
                        var wSunset = Weather.getSunset(wPos, Time.now());
                        if (wSunset != null) {
                            var infoWSunset = Gregorian.info(wSunset, Time.FORMAT_SHORT);
                            val = formatTimeString(infoWSunset.hour, infoWSunset.min);
                        }
                    }
                }
                break;
        }

        return [val, label];
    }
}
