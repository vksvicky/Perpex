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
    // ─────────────────────────────────────────────────────────────────────
    // ANALOG HANDS (3D Metallic Heavy-Duty Industrial Hands)
    // ─────────────────────────────────────────────────────────────────────
    function drawRotatedPolygon(dc, cx, cy, cosA, sinA, pts, color) {
        var count = pts.size();
        var result = new [count];
        for (var i = 0; i < count; i++) {
            var p = pts[i];
            var perp = p[0];
            var along = p[1];
            var px = (cx + along * cosA - perp * sinA).toNumber();
            var py = (cy + along * sinA + perp * cosA).toNumber();
            result[i] = [px, py];
        }
        dc.setColor(color, Graphics.COLOR_TRANSPARENT);
        dc.fillPolygon(result);
    }

    function drawHands(dc, hour, min, sec) {
        var TWO_PI  = Math.PI * 2.0;
        var OFFSET  = Math.PI / 2.0;

        var w = dc.getWidth();
        var scale = w / 260.0;
        var s = scale;

        var minFrac   = min / 60.0;
        var hourAngle = (((hour % 12) / 12.0) + (minFrac / 12.0)) * TWO_PI - OFFSET;
        var minAngle  = minFrac * TWO_PI - OFFSET;
        var secAngle  = (sec / 60.0) * TWO_PI - OFFSET;

        var cosH = Math.cos(hourAngle); var sinH = Math.sin(hourAngle);
        var cosM = Math.cos(minAngle);  var sinM = Math.sin(minAngle);
        var cosS = Math.cos(secAngle);  var sinS = Math.sin(secAngle);

        var COLOR_STEEL_DARK  = 0x444444;
        var COLOR_STEEL_LIGHT = 0x888888;
        var COLOR_WHITE_LUME  = 0xFFFFFF;
        var COLOR_RED_ACCENT  = 0xFF2222;

        // ── HOUR HAND (Heavy-Duty 3D Metallic Fork Hand) ───────────────────
        // 1. 3D Metallic V-Fork Base (Left Dark / Right Light)
        var ptsHourForkL = [
            [0.0,     -10.0*s],
            [-5.5*s,  0.0],
            [-4.5*s,  28.0*s],
            [0.0,     28.0*s]
        ];
        var ptsHourForkR = [
            [0.0,     -10.0*s],
            [5.5*s,   0.0],
            [4.5*s,   28.0*s],
            [0.0,     28.0*s]
        ];
        var ptsHourForkSlot = [
            [-2.0*s, -2.0*s],
            [-2.2*s, 24.0*s],
            [2.2*s,  24.0*s],
            [2.0*s,  -2.0*s]
        ];
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourForkL, COLOR_STEEL_DARK);
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourForkR, COLOR_STEEL_LIGHT);
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourForkSlot, COLOR_BG);

        // 2. White Lume Main Body with Dark Bevel
        var ptsHourBodyOuter = [
            [-5.0*s, 24.0*s],
            [-4.2*s, 56.0*s],
            [0.0,    62.0*s],
            [4.2*s,  56.0*s],
            [5.0*s,  24.0*s]
        ];
        var ptsHourBodyInner = [
            [-2.4*s, 30.0*s],
            [-2.0*s, 50.0*s],
            [0.0,    55.0*s],
            [2.0*s,  50.0*s],
            [2.4*s,  30.0*s]
        ];
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourBodyOuter, COLOR_WHITE_LUME);
        drawRotatedPolygon(dc, centerX, centerY, cosH, sinH, ptsHourBodyInner, COLOR_BG);

        // ── MINUTE HAND (Heavy-Duty 3D Metallic Fork Hand) ─────────────────
        // 1. 3D Metallic V-Fork Base (Left Dark / Right Light)
        var ptsMinForkL = [
            [0.0,     -10.0*s],
            [-5.0*s,  0.0],
            [-4.0*s,  32.0*s],
            [0.0,     32.0*s]
        ];
        var ptsMinForkR = [
            [0.0,     -10.0*s],
            [5.0*s,   0.0],
            [4.0*s,   32.0*s],
            [0.0,     32.0*s]
        ];
        var ptsMinForkSlot = [
            [-1.8*s, -2.0*s],
            [-2.0*s, 28.0*s],
            [2.0*s,  28.0*s],
            [1.8*s,  -2.0*s]
        ];
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinForkL, COLOR_STEEL_DARK);
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinForkR, COLOR_STEEL_LIGHT);
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinForkSlot, COLOR_BG);

        // 2. White Lume Main Body
        var ptsMinBodyOuter = [
            [-4.5*s, 28.0*s],
            [-3.5*s, 86.0*s],
            [0.0,    92.0*s],
            [3.5*s,  86.0*s],
            [4.5*s,  28.0*s]
        ];
        var ptsMinBodyInner = [
            [-2.2*s, 34.0*s],
            [-1.6*s, 80.0*s],
            [0.0,    85.0*s],
            [1.6*s,  80.0*s],
            [2.2*s,  34.0*s]
        ];
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinBodyOuter, COLOR_WHITE_LUME);
        drawRotatedPolygon(dc, centerX, centerY, cosM, sinM, ptsMinBodyInner, COLOR_BG);

        // ── SECOND HAND (Metallic Needle + Red Arrow Tip) ──────────────────
        dc.setPenWidth((2.5 * s).toNumber());
        dc.setColor(COLOR_STEEL_DARK, Graphics.COLOR_TRANSPARENT);

        var tailX = (centerX - 24.0 * s * cosS).toNumber();
        var tailY = (centerY - 24.0 * s * sinS).toNumber();
        var stemX = (centerX + 85.0 * s * cosS).toNumber();
        var stemY = (centerY + 85.0 * s * sinS).toNumber();
        dc.drawLine(tailX, tailY, stemX, stemY);

        // Counterweight (Heavy steel rectangle)
        var ptsSecCounter = [
            [-3.5*s, -24.0*s],
            [-3.5*s, -12.0*s],
            [3.5*s,  -12.0*s],
            [3.5*s,  -24.0*s]
        ];
        drawRotatedPolygon(dc, centerX, centerY, cosS, sinS, ptsSecCounter, COLOR_STEEL_LIGHT);

        // Red Arrow Tip with White Outline Frame
        var ptsSecWhiteFrame = [
            [-4.0*s, 84.0*s],
            [0.0,    112.0*s],
            [4.0*s,  84.0*s],
            [0.0,    90.0*s]
        ];
        var ptsSecRedFill = [
            [-2.5*s, 87.0*s],
            [0.0,    108.0*s],
            [2.5*s,  87.0*s],
            [0.0,    92.0*s]
        ];
        drawRotatedPolygon(dc, centerX, centerY, cosS, sinS, ptsSecWhiteFrame, COLOR_WHITE_LUME);
        drawRotatedPolygon(dc, centerX, centerY, cosS, sinS, ptsSecRedFill, COLOR_RED_ACCENT);

        // ── CENTER PIN HUB (Proportional Metallic Brushed Cap) ────────────
        dc.setColor(COLOR_STEEL_DARK, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(centerX, centerY, (9.0 * s).toNumber());
        dc.setColor(0xE0E0E0, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(centerX, centerY, (7.0 * s).toNumber());
        dc.setColor(COLOR_STEEL_LIGHT, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(centerX, centerY, (4.5 * s).toNumber());
        dc.setColor(COLOR_BG, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(centerX, centerY, (2.0 * s).toNumber());
    }
}