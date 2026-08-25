import Toybox.Test;
import Toybox.Lang;
import Toybox.System;
import Toybox.Graphics;
import Toybox.Math;

(:test)
class SlotPositioningTest {

    (:test)
    static function testSlotCoordinatesAndResolutionScaling(logger as Test.Logger) as Lang.Boolean {
        logger.debug("Testing Slot Coordinates & Scaling Math across all 5 Resolution Classes...");

        var resolutions = [
            [260, 260], // Fenix 7 / Fenix 9 Pro Solar 47mm / FR255
            [280, 280], // Enduro 3 / Fenix 9 Pro Solar 51mm / Fenix 7X
            [390, 390], // Epix 2 Pro 42mm / Fenix 8 43mm
            [416, 416], // Epix Gen 2 47mm / Venu 3
            [454, 454]  // Fenix 8 / Fenix 9 Pro 47mm/51mm / Epix Pro 51mm
        ];

        for (var i = 0; i < resolutions.size(); i++) {
            var w = resolutions[i][0];
            var h = resolutions[i][1];
            var centerX = w / 2;
            var centerY = h / 2;
            var s = w / 260.0;
            var radius = w / 2;

            logger.debug("Resolution: " + w + "x" + h + " | Scale Factor s: " + s);

            // Test 7 Slot Positions
            var slots = [
                [centerX, centerY - (48 * s).toNumber()],                // Slot 1: Top Center
                [centerX - (44 * s).toNumber(), centerY - (26 * s).toNumber()], // Slot 2: Upper-Left
                [centerX + (40 * s).toNumber(), centerY - (26 * s).toNumber()], // Slot 3: Upper-Right
                [centerX, centerY + (16 * s).toNumber()],                // Slot 4: Center Badge
                [centerX - (44 * s).toNumber(), centerY + (36 * s).toNumber()], // Slot 5: Lower-Left
                [centerX + (44 * s).toNumber(), centerY + (36 * s).toNumber()], // Slot 6: Lower-Right
                [centerX, centerY + (54 * s).toNumber()]                 // Slot 7: Bottom Center
            ];

            for (var k = 0; k < slots.size(); k++) {
                var sx = slots[k][0];
                var sy = slots[k][1];

                // Verify slot is within screen boundaries
                var distFromCenter = Math.sqrt(Math.pow(sx - centerX, 2) + Math.pow(sy - centerY, 2));
                Test.assertMessage(distFromCenter < radius, "Slot " + (k + 1) + " exceeds screen radius on " + w + "x" + h);
            }
        }

        return true;
    }

    (:test)
    static function testIconTextVerticalClearance(logger as Test.Logger) as Lang.Boolean {
        logger.debug("Testing Icon-to-Text Vertical Gap & Overlap Clearance...");

        var resolutions = [260, 280, 390, 416, 454];
        var iconHeights = [18, 20, 24, 26, 28];
        var fontHeights = [16, 18, 14, 14, 14]; // MIP vs AMOLED

        for (var i = 0; i < resolutions.size(); i++) {
            var w = resolutions[i];
            var s = w / 260.0;
            var iconH = iconHeights[i];
            var fontH = fontHeights[i];

            // Icon Y-Offset: -13 * s
            // Text Y-Offset: +9 * s
            var iconCenterY = -13.0 * s;
            var textCenterY = 9.0 * s;

            var iconBottomY = iconCenterY + (iconH / 2.0);
            var textTopY = textCenterY - (fontH / 2.0);

            var gap = textTopY - iconBottomY;

            logger.debug("Res: " + w + "x" + w + " | Icon Bottom: " + iconBottomY.format("%.1f") + " | Text Top: " + textTopY.format("%.1f") + " | Gap: " + gap.format("%.1f") + "px");

            // Vertical gap must be strictly positive (>= 2.5px) to prevent overlap
            Test.assertMessage(gap >= 2.5, "Vertical overlap detected on " + w + "x" + w + "! Gap is: " + gap);
        }

        return true;
    }
}
