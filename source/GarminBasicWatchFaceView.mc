using Toybox.WatchUi;
using Toybox.Graphics;
using Toybox.System;
using Toybox.Time;
using Toybox.Time.Gregorian;

class GarminBasicWatchFaceView extends WatchUi.WatchFace {
    private var centerX, centerY;
    private var radius;
    private const COLOR_BG = Graphics.COLOR_BLACK;

    var dialBg;
    var customFont = null;
    var customFontSmall = null;

    private var isLowPower = false;

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

        var fontMap = {
            320 => Rez.Fonts.SystemLike_14
        };

        if (fontMap.hasKey(w)) {
            customFont = WatchUi.loadResource(fontMap[w]);
        } else {
            customFont = null;
        }
    }

    function onShow() {}

    function onEnterSleep() {
        isLowPower = true;
        WatchUi.requestUpdate();
    }

    function onExitSleep() {
        isLowPower = false;
        WatchUi.requestUpdate();
    }

    function onUpdate(dc) {
        var now       = Gregorian.info(Time.now(), Time.FORMAT_SHORT);
        var clockTime = System.getClockTime();

        var w = dc.getWidth();
        var h = dc.getHeight();
        centerX = w / 2;
        centerY = h / 2;
        
        var aodOffsetX = 0;
        var aodOffsetY = 0;
        
        if (isLowPower) {
            var shiftState = clockTime.min % 4; // 0, 1, 2, 3
            if (shiftState == 0) { aodOffsetX = -2; aodOffsetY = -2; }
            else if (shiftState == 1) { aodOffsetX = 2; aodOffsetY = -2; }
            else if (shiftState == 2) { aodOffsetX = 2; aodOffsetY = 2; }
            else if (shiftState == 3) { aodOffsetX = -2; aodOffsetY = 2; }
            
            centerX += aodOffsetX;
            centerY += aodOffsetY;
        }

        dc.setColor(COLOR_BG, COLOR_BG);
        dc.clear();

        UIDrawer.drawConcentricRings(dc, now, dialBg, isLowPower, centerX, centerY);
        UIDrawer.drawDataSlots(dc, aodOffsetX, aodOffsetY, customFont, isLowPower);
        UIDrawer.drawHands(dc, clockTime.hour, clockTime.min, clockTime.sec, isLowPower, centerX, centerY);
    }
}