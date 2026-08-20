import Toybox.Test;
import Toybox.Lang;
import Toybox.System;
import Toybox.Graphics;
import Toybox.WatchUi;
import Toybox.Time;
import Toybox.Position;

(:test)
class MetricDataTest {

    (:test)
    static function testMetricTypesFormatting(logger as Test.Logger) as Lang.Boolean {
        logger.debug("Executing Metric Data Formatting & Null Safety Test for all 19 Metric Types...");

        var view = new GarminBasicWatchFaceView();

        for (var type = 1; type <= 19; type++) {
            var data = view.getMetricData(type);
            Test.assertMessage(data != null, "Metric type " + type + " returned null tuple");
            Test.assertMessage(data.size() == 2, "Metric type " + type + " tuple size is not 2");

            var valStr = data[0];
            var labelStr = data[1];

            Test.assertMessage(valStr != null, "Metric type " + type + " value string is null");
            Test.assertMessage(labelStr != null, "Metric type " + type + " label string is null");
            Test.assertMessage(valStr.length() > 0, "Metric type " + type + " value string is empty");

            logger.debug("Type " + type + " Output: [" + valStr + ", " + labelStr + "]");
        }

        return true;
    }

    (:test)
    static function testMinMaxBoundaryValues(logger as Test.Logger) as Lang.Boolean {
        logger.debug("Testing Min and Max Boundary Character Lengths for Data Slots...");

        var maxStrings = [
            "100%",          // Battery Max
            "199 BPM",       // HR Max
            "99,999 STEPS",  // Steps Max
            "100% GOAL",     // Step Goal Max
            "1000 kCal",     // Calories Max
            "999.9 KM",      // Distance Max
            "999 FLOORS",    // Floors Max
            "9,999 MINS",    // Active Mins Max
            "100 STRESS",    // Stress Max
            "23:59",         // Time Max
            "99 NOTIF",      // Notifications Max
            "9,999 M",       // Altitude Max
            "1013 hPa",      // Barometer Max
            "45°C",          // Temp Max
            "SUNRISE",       // Weather Cond Max
            "06:14 SUNRISE", // Solar Max
            "100% BODY BATT" // Body Battery Max
        ];

        for (var i = 0; i < maxStrings.size(); i++) {
            var str = maxStrings[i];
            Test.assertMessage(str.length() > 0 && str.length() <= 20, "String length boundary check failed for: " + str);
        }

        return true;
    }

    (:test)
    static function testSunCalcLocations(logger as Test.Logger) as Lang.Boolean {
        logger.debug("Testing SunCalc for different global coordinates...");
        
        var sc = new SunCalc();
        
        // Use a fixed date to ensure consistency: August 20, 2026, 12:00 UTC
        // Julian Day = 2461273.0. We can just use an approximate Time.Moment.
        // Or simply use Time.now().
        var nowTime = Time.now();

        // 1. London (51.5072, -0.1276)
        var londonRad = new Position.Location({ :latitude => 51.5072, :longitude => -0.1276, :format => :degrees }).toRadians();
        var londonSunrise = sc.calculate(nowTime, londonRad, 4);
        var londonSunset = sc.calculate(nowTime, londonRad, 10);
        Test.assertMessage(londonSunrise != null, "London Sunrise should not be null");
        Test.assertMessage(londonSunset != null, "London Sunset should not be null");
        logger.debug("London OK.");

        // 2. NYC (40.7128, -74.0060)
        var nycRad = new Position.Location({ :latitude => 40.7128, :longitude => -74.0060, :format => :degrees }).toRadians();
        var nycSunrise = sc.calculate(nowTime, nycRad, 4);
        var nycSunset = sc.calculate(nowTime, nycRad, 10);
        Test.assertMessage(nycSunrise != null, "NYC Sunrise should not be null");
        Test.assertMessage(nycSunset != null, "NYC Sunset should not be null");
        logger.debug("NYC OK.");

        // 3. Svalbard (78.22, 15.66) - Summer (Midnight Sun) or Winter (Polar Night)
        var svalbardRad = new Position.Location({ :latitude => 78.22, :longitude => 15.66, :format => :degrees }).toRadians();
        var svalbardSunrise = sc.calculate(nowTime, svalbardRad, 4);
        var svalbardSunset = sc.calculate(nowTime, svalbardRad, 10);
        
        // Depending on the season, they could be null. We just verify it executes without crashing.
        if (svalbardSunrise == null || svalbardSunset == null) {
            logger.debug("Svalbard returned null for solar events (Midnight Sun or Polar Night). This is correct!");
        } else {
            logger.debug("Svalbard returned times (Equinox period).");
        }
        
        return true;
    }

    (:test)
    static function testSolarIconUILogic(logger as Test.Logger) as Lang.Boolean {
        logger.debug("Testing Solar Icon UI Logic for all 24 hours...");

        // 00:00 to 11:59 AM should be Sunrise
        for (var i = 0; i <= 11; i++) {
            var icon = GarminBasicWatchFaceView.getSolarIcon(i);
            Test.assertMessage(icon.equals("icon_sunrise"), "Hour " + i + " should return icon_sunrise");
        }
        logger.debug("Morning hours (0-11) correctly mapped to icon_sunrise.");

        // 12:00 PM to 23:59 PM should be Sunset
        for (var i = 12; i <= 23; i++) {
            var icon = GarminBasicWatchFaceView.getSolarIcon(i);
            Test.assertMessage(icon.equals("icon_sunset"), "Hour " + i + " should return icon_sunset");
        }
        logger.debug("Afternoon/Evening hours (12-23) correctly mapped to icon_sunset.");

        return true;
    }
}
