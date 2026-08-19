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

    var dialBg;

    function initialize() {
        WatchFace.initialize();
    }

    function onLayout(dc) {
        var w = dc.getWidth();
        var h = dc.getHeight();
        centerX = w / 2;
        centerY = h / 2;
        radius  = (w < h ? w : h) / 2;
        
        dialBg = WatchUi.loadResource(Rez.Drawables.dial_bg);
    }

    function onShow() {}

    function onUpdate(dc) {
        var now       = Gregorian.info(Time.now(), Time.FORMAT_SHORT);
        var clockTime = System.getClockTime();

        dc.setColor(COLOR_BG, COLOR_BG);
        dc.clear();

        drawConcentricRings(dc, now);
        
        // Leaving the center clean and empty
        
        drawHands(dc, clockTime.hour, clockTime.min, clockTime.sec);
    }

    // ─────────────────────────────────────────────────────────────────────
    // CONCENTRIC RINGS
    // ─────────────────────────────────────────────────────────────────────
    function drawConcentricRings(dc, now) {
        var TWO_PI  = Math.PI * 2.0;
        var HALF_PI = Math.PI / 2.0;
        
        // Calculate scale factor based on 260px base width
        var w = dc.getWidth();
        var scale = w / 260.0;

        // Draw the static opaque background dial
        if (dialBg != null) { dc.drawBitmap(0, 0, dialBg); }

        dc.setPenWidth(4);

        // ── Highlight: Days ──────────────────────────────────
        var r1       = (96 * scale).toNumber(); // radius from script
        var dayStep  = TWO_PI / 31.0;
        var d = now.day;
        var angle1 = (d - 1) * dayStep - HALF_PI;
        var degCenter1 = ((- (angle1 * 180.0 / Math.PI)).toNumber() % 360 + 360) % 360;
        
        // Arc below text
        dc.setColor(COLOR_HAND_SEC, Graphics.COLOR_TRANSPARENT);
        var r1_arc = r1 - (5 * scale).toNumber();
        dc.drawArc(centerX, centerY, r1_arc, Graphics.ARC_COUNTER_CLOCKWISE, (degCenter1 - 4 + 360) % 360, (degCenter1 + 4 + 360) % 360);

        // ── Highlight: Months ───────────────────────────────────────
        var r2       = (117 * scale).toNumber(); // radius from script
        var m = now.month;
        var monStep  = TWO_PI / 12.0;
        var angle2 = (m - 1) * monStep - HALF_PI;
        var degCenter2 = ((- (angle2 * 180.0 / Math.PI)).toNumber() % 360 + 360) % 360;
        
        // Arc below text
        var r2_arc = r2 - (5 * scale).toNumber();
        dc.drawArc(centerX, centerY, r2_arc, Graphics.ARC_COUNTER_CLOCKWISE, (degCenter2 - 10 + 360) % 360, (degCenter2 + 10 + 360) % 360);

        // ── Highlight: Weekdays ───────────────────────────────────────
        var r3       = (75 * scale).toNumber(); // radius from script
        var wkStep  = TWO_PI / 7.0;
        var w_day = now.day_of_week;
        var angle3 = (w_day - 1) * wkStep - HALF_PI;
        var degCenter3 = ((- (angle3 * 180.0 / Math.PI)).toNumber() % 360 + 360) % 360;
        
        // Arc below text
        var r3_arc = r3 - (5 * scale).toNumber();
        dc.drawArc(centerX, centerY, r3_arc, Graphics.ARC_COUNTER_CLOCKWISE, (degCenter3 - 16 + 360) % 360, (degCenter3 + 16 + 360) % 360);
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