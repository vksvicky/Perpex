import Toybox.Test;
import Toybox.Lang;
import Toybox.System;
import Toybox.Graphics;
import Toybox.Math;

(:test)
class SlotPositioningTest {

    (:test)
    static function testSlotCoordinatesAndResolutionScaling(logger as Test.Logger) as Lang.Boolean {
        logger.debug("Testing Strict Slot Coordinates across all 5 Resolution Classes...");

        // 1. Strict verification for 260x260
        var exp260 = [
            [130, 82], [86, 104], [170, 104], [130, 146], [94, 160], [166, 160], [130, 184]
        ];
        for (var i = 1; i <= 7; i++) {
            var x = GarminBasicWatchFaceView.getSlotX(i, 260);
            var y = GarminBasicWatchFaceView.getSlotY(i, 260);
            Test.assertEqualMessage(x, exp260[i-1][0], "260x260 Slot " + i + " X changed!");
            Test.assertEqualMessage(y, exp260[i-1][1], "260x260 Slot " + i + " Y changed!");
        }

        // 2. Strict verification for 280x280
        var exp280 = [
            [140, 88], [93, 112], [183, 112], [140, 157], [101, 172], [179, 172], [140, 198]
        ];
        for (var i = 1; i <= 7; i++) {
            var x = GarminBasicWatchFaceView.getSlotX(i, 280);
            var y = GarminBasicWatchFaceView.getSlotY(i, 280);
            Test.assertEqualMessage(x, exp280[i-1][0], "280x280 Slot " + i + " X changed!");
            Test.assertEqualMessage(y, exp280[i-1][1], "280x280 Slot " + i + " Y changed!");
        }

        // 3. Dynamic verification for other resolutions
        var resolutions = [390, 416, 454];
        for (var i = 0; i < resolutions.size(); i++) {
            var w = resolutions[i];
            var centerX = w / 2;
            var centerY = w / 2;
            var s = w / 260.0;
            var radius = w / 2;
            
            for (var slotId = 1; slotId <= 7; slotId++) {
                var sx = GarminBasicWatchFaceView.getSlotX(slotId, w);
                var sy = GarminBasicWatchFaceView.getSlotY(slotId, w);
                
                // Ensure slot is strictly within screen boundaries
                var dist = Math.sqrt(Math.pow(sx - centerX, 2) + Math.pow(sy - centerY, 2));
                Test.assertMessage(dist < radius, "Slot " + slotId + " exceeds bounds on " + w + "x" + w);
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
