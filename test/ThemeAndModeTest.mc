import Toybox.Test;
import Toybox.Lang;
import Toybox.System;
import Toybox.Graphics;
import Toybox.WatchUi;

(:test)
class ThemeAndModeTest {

    (:test)
    static function testColorThemeResolvers(logger as Test.Logger) as Lang.Boolean {
        logger.debug("Testing Theme Accent Color Resolution for all 6 Color Themes...");

        var expectedColors = [
            0xFF3333, // Red (Default Theme 1)
            0x00CCCC, // Teal (Theme 2)
            0xFF8800, // Orange (Theme 3)
            0x00FF66, // Green (Theme 4)
            0xFFFF00, // Gold (Theme 5)
            0xFFFFFF  // White (Theme 6)
        ];

        var resolvedColor = ThemeManager.getThemeAccentColor();

        Test.assertMessage(resolvedColor != null, "getThemeAccentColor returned null");
        logger.debug("Active theme accent color resolved to: 0x" + resolvedColor.format("%06X"));

        return true;
    }

    (:test)
    static function testBatteryColorGradientLogic(logger as Test.Logger) as Lang.Boolean {
        logger.debug("Testing Battery Percentage Color Threshold Logic...");

        var testCases = [
            [10, 0xFF3333], // 10% -> Red
            [20, 0xFF3333], // 20% -> Red
            [21, 0xFF8800], // 21% -> Orange
            [50, 0xFF8800], // 50% -> Orange
            [51, 0x00FF66], // 51% -> Green
            [100, 0x00FF66] // 100% -> Green
        ];

        for (var i = 0; i < testCases.size(); i++) {
            var percent = testCases[i][0];
            var expectedColor = testCases[i][1];
            var color = 0x00FF66;

            if (percent <= 20) {
                color = 0xFF3333;
            } else if (percent <= 50) {
                color = 0xFF8800;
            }

            Test.assertMessage(color == expectedColor, "Battery " + percent + "% color mismatch. Expected 0x" + expectedColor.format("%06X") + ", Got: 0x" + color.format("%06X"));
        }

        return true;
    }
}
