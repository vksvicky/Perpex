using Toybox.WatchUi;
using Toybox.Graphics;
using Toybox.System;
using Toybox.Time;
using Toybox.Time.Gregorian;

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

    function initialize() {
        WatchFace.initialize();
    }

    function onLayout(dc) {
        var w = dc.getWidth();
        var h = dc.getHeight();
        centerX = w / 2;
        centerY = h / 2;
        radius  = (w < h ? w : h) / 2;
    }

    function onShow() {}

    function onUpdate(dc) {
        var now       = Gregorian.info(Time.now(), Time.FORMAT_SHORT);
        var clockTime = System.getClockTime();

        dc.setColor(COLOR_BG, COLOR_BG);
        dc.clear();

        drawConcentricRings(dc, now);
        drawBrandAndComplications(dc);
        drawHands(dc, clockTime.hour, clockTime.min, clockTime.sec);
    }

    function drawCharAtAngle(dc, char, r, a, isBottom) {
        var x = (centerX + r * Math.cos(a)).toNumber();
        var y = (centerY + r * Math.sin(a)).toNumber();

        var aDeg = (a * 180.0 / Math.PI).toNumber();
        var tangent;
        if (isBottom) {
            tangent = 90 - aDeg;
        } else {
            tangent = 270 - aDeg;
        }
        tangent = ((tangent % 360) + 360) % 360;

        var idx = tangent / 3;
        var font = CurvedFonts.getFont(idx);
        if (font != null) {
            dc.drawText(x, y, font, char,
                Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
        } else {
            dc.drawText(x, y, Graphics.FONT_XTINY, char,
                Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
        }
    }

    // Draw a multi-char label along the arc at radius r, centred at centerAngle.
    // Bottom half (sin > 0): reverse character order for head-on left-to-right readability.
    function drawCurvedLabel(dc, label, r, centerAngle, charArcSpacing) {
        var chars      = label.toUpper().toCharArray();
        var n          = chars.size();
        var charArc    = charArcSpacing / r;
        var startAngle = centerAngle - ((n - 1.0) * charArc / 2.0);
        var isBottom   = (Math.sin(centerAngle) > 0.0);
        for (var i = 0; i < n; i++) {
            var ci = isBottom ? (n - 1 - i) : i;
            drawCharAtAngle(dc, chars[ci].toString(), r, startAngle + i * charArc, isBottom);
        }
    }

    // ─────────────────────────────────────────────────────────────────────
    // CONCENTRIC RINGS
    // ─────────────────────────────────────────────────────────────────────
    function drawConcentricRings(dc, now) {
        var r1 = radius - 15;  // Outermost: Days   1–31
        var r2 = radius - 45;  // Middle:    Months JAN–DEC
        var r3 = radius - 70;  // Inner:     Weekdays SUN–SAT

        // Subtle separator circles
        dc.setPenWidth(2);
        dc.setColor(COLOR_RING_SEP, Graphics.COLOR_TRANSPARENT);
        dc.drawCircle(centerX, centerY, r1 + 12);
        dc.drawCircle(centerX, centerY, r1 - 15);
        dc.drawCircle(centerX, centerY, r2 - 15);
        dc.drawCircle(centerX, centerY, r3 - 15);

        var TWO_PI  = Math.PI * 2.0;
        var HALF_PI = Math.PI / 2.0;

        // ── Outer ring: Days 1–31 ──────────────────────────────────────
        var dayStep = TWO_PI / 31.0;
        for (var d = 1; d <= 31; d++) {
            var angle = ((d - 1) * dayStep) - HALF_PI;
            if (d == now.day) {
                dc.setColor(COLOR_HIGHLIGHT, Graphics.COLOR_TRANSPARENT);
            } else {
                dc.setColor(COLOR_DIM_OUTER, Graphics.COLOR_TRANSPARENT);
            }
            // Use tighter spacing (6.0) for numbers so they look like a single unit
            drawCurvedLabel(dc, d.toString(), r1, angle, 6.0);
        }

        // ── Middle ring: Months ────────────────────────────────────────
        var months  = ["JAN","FEB","MAR","APR","MAY","JUN",
                       "JUL","AUG","SEP","OCT","NOV","DEC"];
        var monStep = TWO_PI / 12.0;
        for (var m = 0; m < 12; m++) {
            var angle = (m * monStep) - HALF_PI;
            if (m + 1 == now.month) {
                dc.setColor(COLOR_HIGHLIGHT, Graphics.COLOR_TRANSPARENT);
            } else {
                dc.setColor(COLOR_DIM_MID, Graphics.COLOR_TRANSPARENT);
            }
            // Normal spacing (10.0) for letters
            drawCurvedLabel(dc, months[m], r2, angle, 10.0);
        }

        // ── Inner ring: Weekdays ───────────────────────────────────────
        // day_of_week: 1=SUN … 7=SAT
        var days    = ["SUN","MON","TUE","WED","THU","FRI","SAT"];
        var wkStep  = TWO_PI / 7.0;
        for (var w = 0; w < 7; w++) {
            var angle = (w * wkStep) - HALF_PI;
            if (w + 1 == now.day_of_week) {
                dc.setColor(COLOR_HIGHLIGHT, Graphics.COLOR_TRANSPARENT);
            } else {
                dc.setColor(COLOR_DIM_INNER, Graphics.COLOR_TRANSPARENT);
            }
            // Normal spacing (10.0) for letters
            drawCurvedLabel(dc, days[w], r3, angle, 10.0);
        }
    }

    // ─────────────────────────────────────────────────────────────────────
    // BRAND + COMPLICATIONS
    // ─────────────────────────────────────────────────────────────────────
    function drawBrandAndComplications(dc) {
        var justify = Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER;

        dc.setColor(COLOR_BRAND, Graphics.COLOR_TRANSPARENT);
        dc.drawText(centerX, centerY - 18, Graphics.FONT_XTINY, "PERPEX", justify);

        var batt = System.getSystemStats().battery;
        dc.setColor(COLOR_BATT, Graphics.COLOR_TRANSPARENT);
        dc.drawText(centerX, centerY + 18, Graphics.FONT_XTINY,
            batt.format("%d") + "%", justify);
    }

    // ─────────────────────────────────────────────────────────────────────
    // ANALOG HANDS
    // ─────────────────────────────────────────────────────────────────────
    function drawHands(dc, hour, min, sec) {
        var TWO_PI  = Math.PI * 2.0;
        var OFFSET  = Math.PI / 2.0;

        var minFrac   = min / 60.0;
        var hourAngle = (((hour % 12) / 12.0) + (minFrac / 12.0)) * TWO_PI - OFFSET;
        var minAngle  = minFrac * TWO_PI - OFFSET;
        var secAngle  = (sec / 60.0) * TWO_PI - OFFSET;

        var cosH = Math.cos(hourAngle); var sinH = Math.sin(hourAngle);
        var cosM = Math.cos(minAngle);  var sinM = Math.sin(minAngle);
        var cosS = Math.cos(secAngle);  var sinS = Math.sin(secAngle);

        // Hour hand
        var hLen = (radius - 72).toNumber();
        dc.setPenWidth(6);
        dc.setColor(COLOR_HAND_HOUR, Graphics.COLOR_TRANSPARENT);
        dc.drawLine(centerX - (10 * cosH).toNumber(), centerY - (10 * sinH).toNumber(),
                    centerX + (hLen * cosH).toNumber(), centerY + (hLen * sinH).toNumber());

        // Minute hand
        var mLen = (radius - 45).toNumber();
        dc.setPenWidth(3);
        dc.setColor(COLOR_HAND_MIN, Graphics.COLOR_TRANSPARENT);
        dc.drawLine(centerX - (10 * cosM).toNumber(), centerY - (10 * sinM).toNumber(),
                    centerX + (mLen * cosM).toNumber(), centerY + (mLen * sinM).toNumber());

        // Second hand with counterweight
        var sLen = (radius - 20).toNumber();
        dc.setPenWidth(2);
        dc.setColor(COLOR_HAND_SEC, Graphics.COLOR_TRANSPARENT);
        dc.drawLine(centerX - (22 * cosS).toNumber(), centerY - (22 * sinS).toNumber(),
                    centerX + (sLen * cosS).toNumber(), centerY + (sLen * sinS).toNumber());
        dc.fillCircle(centerX - (14 * cosS).toNumber(), centerY - (14 * sinS).toNumber(), 3);

        // Centre pin
        dc.setColor(COLOR_PIN, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(centerX, centerY, 5);
        dc.setColor(COLOR_BG, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(centerX, centerY, 2);
    }
}