using Toybox.Application;
using Toybox.WatchUi;
using Toybox.Graphics;

class GarminBasicWatchFaceApp extends Application.AppBase {

    function initialize() {
        AppBase.initialize();
    }

    function onStart(state) {}
    function onStop(state) {}

    function getInitialView() {
        return [ new GarminBasicWatchFaceView() ];
    }

    function onSettingsChanged() {
        WatchUi.requestUpdate();
    }

    // ─────────────────────────────────────────────────────────────────────
    // ON-WATCH CUSTOM SETTINGS VIEW (VECTOR ARROWS & PERFECT SPACING)
    // ─────────────────────────────────────────────────────────────────────
    function getSettingsView() {
        var view = new GarminSettingsCustomView();
        return [ view, new GarminSettingsCustomDelegate(view) ];
    }
}

class GarminSettingsCustomView extends WatchUi.View {
    private var currentIndex = 0;
    private var menuItems = [
        ["Theme Color", "ThemeColor"],
        ["Top Field", "Slot1Metric"],
        ["Left Field", "Slot2Metric"],
        ["Center Badge", "Slot3Metric"],
        ["Right Field", "Slot4Metric"],
        ["Bottom Field", "Slot5Metric"],
        ["Reset Defaults", "ResetDefaults"]
    ];

    function initialize() {
        View.initialize();
    }

    function getSelectedIndex() { return currentIndex; }
    function setSelectedIndex(idx) { currentIndex = idx; }
    function getMenuItems() { return menuItems; }

    function onUpdate(dc) {
        var w = dc.getWidth();
        var h = dc.getHeight();
        var cx = w / 2;
        var cy = h / 2;
        var scale = w / 260.0;
        var gap   = (22 * scale).toNumber();
        var arrowH = (6 * scale).toNumber();
        var sz    = (6 * scale).toNumber();

        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_BLACK);
        dc.clear();

        // Resolve strings & colors
        var itemKey   = menuItems[currentIndex][1];
        var itemTitle = menuItems[currentIndex][0];
        var headerText = "SETTINGS  " + (currentIndex + 1) + " / " + menuItems.size();
        var subText   = "";
        var subColor  = Graphics.COLOR_WHITE;

        if (itemKey.equals("ThemeColor")) {
            var themeVal = getPropVal("ThemeColor", 1);
            var themeNames = ["Vibrant Red", "Teal / Cyan", "Warm Orange", "Electric Green", "Gold / Yellow", "Pure White"];
            subText = (themeVal >= 1 && themeVal <= 6) ? themeNames[themeVal - 1] : themeNames[0];
            subColor = getThemeAccentHex(themeVal);
        } else if (itemKey.equals("ResetDefaults")) {
            subText = "Press SELECT to Reset";
            subColor = 0xFF4444;
        } else {
            var metricId = getPropVal(itemKey, 1);
            subText = getMetricNameLabel(metricId);
            subColor = getThemeAccentHex(getPropVal("ThemeColor", 1));
        }

        // Measure exact font heights using system text metrics
        var dimTitle  = dc.getTextDimensions(itemTitle, Graphics.FONT_MEDIUM);
        var dimSub    = dc.getTextDimensions(subText, Graphics.FONT_SMALL);
        var dimHeader = dc.getTextDimensions(headerText, Graphics.FONT_XTINY);
        var dimFoot1  = dc.getTextDimensions("SELECT : Change", Graphics.FONT_XTINY);

        var hTitle  = dimTitle[1];
        var hSub    = dimSub[1];
        var hHeader = dimHeader[1];
        var hFoot1  = dimFoot1[1];

        // Central Text Block (Title & Sublabel centered symmetrically around cy)
        var innerGap = (8 * scale).toNumber();
        var yTitle = cy - (hTitle / 2) - (innerGap / 2);
        var ySub   = yTitle + hTitle + innerGap;

        // 1. Current Item Title & Sublabel
        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, yTitle, Graphics.FONT_MEDIUM, itemTitle, Graphics.TEXT_JUSTIFY_CENTER);

        dc.setColor(subColor, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, ySub, Graphics.FONT_SMALL, subText, Graphics.TEXT_JUSTIFY_CENTER);

        // 2. Top Arrow Chevron ▲ (EXACTLY gap = 22px above yTitle)
        var pyUp = yTitle - gap;
        dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.fillPolygon([
            [cx - sz, pyUp],
            [cx + sz, pyUp],
            [cx, pyUp - arrowH]
        ]);

        // 3. Top Header SETTINGS (EXACTLY gap = 22px above Top Arrow tip)
        var yHeader = pyUp - arrowH - gap - (hHeader / 2);
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, yHeader, Graphics.FONT_XTINY, headerText, Graphics.TEXT_JUSTIFY_CENTER);

        // 4. Bottom Arrow Chevron ▼ (EXACTLY gap = 22px below ySub + hSub)
        var pyDown = ySub + hSub + gap;
        dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.fillPolygon([
            [cx - sz, pyDown],
            [cx + sz, pyDown],
            [cx, pyDown + arrowH]
        ]);

        // 5. Footer Line 1 & Line 2 (EXACTLY gap = 22px below Bottom Arrow tip)
        var yFoot1 = pyDown + arrowH + gap;
        var yFoot2 = yFoot1 + hFoot1 + (2 * scale).toNumber();
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, yFoot1, Graphics.FONT_XTINY, "SELECT : Change", Graphics.TEXT_JUSTIFY_CENTER);
        dc.drawText(cx, yFoot2, Graphics.FONT_XTINY, "BACK : Save", Graphics.TEXT_JUSTIFY_CENTER);

        // 7. Right Edge Page Indicator Dots
        var dotX = w - (14 * scale).toNumber();
        var startY = cy - (24 * scale).toNumber();
        var dotSpacing = (8 * scale).toNumber();
        for (var i = 0; i < menuItems.size(); i++) {
            var dotY = startY + i * dotSpacing;
            if (i == currentIndex) {
                dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
                dc.fillCircle(dotX, dotY, (2.5 * scale).toNumber());
            } else {
                dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
                dc.fillCircle(dotX, dotY, (1.5 * scale).toNumber());
            }
        }
    }

    function getThemeAccentHex(val) {
        if (val == 1) { return 0xFF3333; } // Red
        if (val == 2) { return 0x00CCCC; } // Teal
        if (val == 3) { return 0xFF8800; } // Orange
        if (val == 4) { return 0x00FF66; } // Green
        if (val == 5) { return 0xFFCC00; } // Gold
        if (val == 6) { return 0xFFFFFF; } // White
        return 0xFF3333;
    }

    function getPropVal(key, defaultVal) {
        try {
            if (Application has :Properties) {
                var v = Application.Properties.getValue(key);
                if (v != null) { return v; }
            }
        } catch (e) {}
        return defaultVal;
    }

    function getMetricNameLabel(id) {
        var names = [
            "Hidden", "Battery", "Heart Rate", "Steps", "Step Goal",
            "Calories", "Distance", "Floors", "Active Mins", "Stress",
            "Digital Clock", "Notifications", "Altitude", "Barometer"
        ];
        if (id >= 0 && id < names.size()) { return names[id]; }
        return "Hidden";
    }
}

class GarminSettingsCustomDelegate extends WatchUi.BehaviorDelegate {
    private var customView;

    function initialize(view) {
        BehaviorDelegate.initialize();
        customView = view;
    }

    function onNextPage() { return cycleDown(); }
    function onPreviousPage() { return cycleUp(); }

    function cycleDown() {
        var idx = customView.getSelectedIndex();
        var items = customView.getMenuItems();
        customView.setSelectedIndex((idx + 1) % items.size());
        WatchUi.requestUpdate();
        return true;
    }

    function cycleUp() {
        var idx = customView.getSelectedIndex();
        var items = customView.getMenuItems();
        customView.setSelectedIndex((idx - 1 + items.size()) % items.size());
        WatchUi.requestUpdate();
        return true;
    }

    function onSelect() {
        var idx = customView.getSelectedIndex();
        var items = customView.getMenuItems();
        var itemKey = items[idx][1];

        if (itemKey.equals("ThemeColor")) {
            var current = getPropVal("ThemeColor", 1);
            current = (current % 6) + 1;
            setPropVal("ThemeColor", current);
        } else if (itemKey.equals("ResetDefaults")) {
            setPropVal("ThemeColor", 1);
            setPropVal("Slot1Metric", 1);
            setPropVal("Slot2Metric", 2);
            setPropVal("Slot3Metric", 11);
            setPropVal("Slot4Metric", 3);
            setPropVal("Slot5Metric", 5);
        } else {
            var current = getPropVal(itemKey, 0);
            current = (current + 1) % 14;
            setPropVal(itemKey, current);
        }

        WatchUi.requestUpdate();
        return true;
    }

    function onBack() {
        WatchUi.popView(WatchUi.SLIDE_IMMEDIATE);
        return true;
    }

    function getPropVal(key, defaultVal) {
        try {
            if (Application has :Properties) {
                var v = Application.Properties.getValue(key);
                if (v != null) { return v; }
            }
        } catch (e) {}
        return defaultVal;
    }

    function setPropVal(key, val) {
        try {
            if (Application has :Properties) {
                Application.Properties.setValue(key, val);
            }
        } catch (e) {}
    }
}