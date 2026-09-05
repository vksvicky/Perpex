using Toybox.Application;
using Toybox.WatchUi;
using Toybox.Graphics;

(:background)
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
        ThemeManager.invalidateCache();
        WatchUi.requestUpdate();
    }

    // ─────────────────────────────────────────────────────────────────────
    // ON-WATCH CUSTOM SETTINGS VIEW (DYNAMIC FONT HEIGHT EVEN FORMULA)
    // ─────────────────────────────────────────────────────────────────────
    function getSettingsView() {
        if (WatchUi has :WatchFaceDelegate) {
            var view = new GarminSettingsCustomView();
            return [ view, new GarminSettingsCustomDelegate(view) ];
        }
        return null;
    }
}

(:typecheck(false))
class GarminSettingsCustomView extends WatchUi.View {
    private var currentIndex = 0;
    private var menuItems = [
        ["Theme Color", "ThemeColor"],
        ["Temp Unit", "TemperatureUnit"],
        ["Time Format", "TimeFormat"],
        ["Night Mode", "NightMode"],
        ["Night Color", "NightModeColor"],
        ["Top Field", "Slot1Metric"],
        ["Upper-Left Field", "Slot2Metric"],
        ["Upper-Right Field", "Slot3Metric"],
        ["Lower-Left Field", "Slot4Metric"],
        ["Lower-Right Field", "Slot5Metric"],
        ["Bottom Field", "Slot6Metric"],
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
        var scale  = w / 260.0;
        var sz     = (4.5 * scale).toNumber();
        var arrowH = (4.5 * scale).toNumber();

        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_BLACK);
        dc.clear();

        // 1. Resolve strings & colors
        var itemKey    = menuItems[currentIndex][1];
        var itemTitle  = menuItems[currentIndex][0];
        var headerText = "SETTING " + (currentIndex + 1) + " OF " + menuItems.size();
        var subText    = "";
        var subColor   = Graphics.COLOR_WHITE;

        switch (itemKey) {
            case "ThemeColor":
                var themeVal = getPropVal("ThemeColor", 1);
                var themeNames = ["Vibrant Red", "Teal / Cyan", "Warm Orange", "Electric Green", "Gold / Yellow", "Pure White"];
                subText = (themeVal >= 1 && themeVal <= 6) ? themeNames[themeVal - 1] : themeNames[0];
                subColor = getThemeAccentHex(themeVal);
                break;
            case "TemperatureUnit":
                var unitVal = getPropVal("TemperatureUnit", 0);
                subText = (unitVal == 1) ? "Fahrenheit (°F)" : "Celsius (°C)";
                subColor = getThemeAccentHex(getPropVal("ThemeColor", 1));
                break;
            case "TimeFormat":
                var tfVal = getPropVal("TimeFormat", 0);
                subText = (tfVal == 1) ? "12 Hour (AM/PM)" : "24 Hour";
                subColor = getThemeAccentHex(getPropVal("ThemeColor", 1));
                break;
            case "NightMode":
                var nVal = getPropVal("NightMode", 1);
                var nNames = ["Disabled / Off", "Auto (Sun)", "Scheduled", "Always On"];
                subText = (nVal >= 0 && nVal <= 3) ? nNames[nVal] : nNames[1];
                subColor = getThemeAccentHex(getPropVal("ThemeColor", 1));
                break;
            case "NightModeColor":
                var ncVal = getPropVal("NightModeColor", 0);
                var ncNames = ["Tactical Red", "Night Amber", "Stealth Green"];
                var ncColors = [0xFF0000, 0xFF8800, 0x00FF00];
                subText = (ncVal >= 0 && ncVal <= 2) ? ncNames[ncVal] : ncNames[0];
                subColor = (ncVal >= 0 && ncVal <= 2) ? ncColors[ncVal] : 0xFF0000;
                break;
            case "ResetDefaults":
                subText = "Tap to Reset All";
                subColor = 0xFF4444;
                break;
            default:
                var metricId = getPropVal(itemKey, 1);
                subText = getMetricNameLabel(metricId);
                subColor = getThemeAccentHex(getPropVal("ThemeColor", 1));
                break;
        }

        // 2. Exact Font Height Metrics & Even Gap Formula
        var fontHeader = Graphics.FONT_XTINY;
        var fontTitle  = Graphics.FONT_SMALL;
        var fontSub    = Graphics.FONT_TINY;

        var hHeader = dc.getFontHeight(fontHeader);
        var hTitle  = dc.getFontHeight(fontTitle);
        var hSub    = dc.getFontHeight(fontSub);

        var uniformGap = (16 * scale).toNumber();
        var itemGap    = (4 * scale).toNumber();

        // Total central block height (title + gap + sublabel)
        var totalTextH = hTitle + itemGap + hSub;

        // Title Top Y (Centered at cy)
        var titleY = cy - (totalTextH / 2);
        var subY   = titleY + hTitle + itemGap;

        // Top Chevron Y (Base placed uniformGap above titleY)
        var pyUp = titleY - uniformGap;

        // Bottom Chevron Y (Base placed uniformGap below subY + hSub)
        var pyDown = subY + hSub + uniformGap;

        // Header Text Y (Placed uniformGap above top chevron tip)
        var headerY = (pyUp - arrowH) - uniformGap - hHeader;

        // 3. Draw Header
        dc.setColor(Graphics.COLOR_DK_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, headerY, fontHeader, headerText, Graphics.TEXT_JUSTIFY_CENTER);

        // 4. Draw Top Vector Chevron ▲
        dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.fillPolygon([
            [cx - sz, pyUp],
            [cx + sz, pyUp],
            [cx, pyUp - arrowH]
        ]);

        // 5. Draw Title
        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, titleY, fontTitle, itemTitle, Graphics.TEXT_JUSTIFY_CENTER);

        // 6. Draw Sublabel Value
        dc.setColor(subColor, Graphics.COLOR_TRANSPARENT);
        dc.drawText(cx, subY, fontSub, subText, Graphics.TEXT_JUSTIFY_CENTER);

        // 7. Draw Bottom Vector Chevron ▼
        dc.setColor(Graphics.COLOR_LT_GRAY, Graphics.COLOR_TRANSPARENT);
        dc.fillPolygon([
            [cx - sz, pyDown],
            [cx + sz, pyDown],
            [cx, pyDown + arrowH]
        ]);

        // 8. Right Edge Page Indicator Dots
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
            "Unused", "Notifications", "Altitude", "Barometer",
            "Weather Temp", "Weather Condition", "Sunrise / Sunset", "Body Battery",
            "Sunrise Only", "Sunset Only", "Recovery Time", "VO2 Max"
        ];
        if (id >= 0 && id < names.size()) { return names[id]; }
        return "Hidden";
    }
}

(:typecheck(false))
class GarminSettingsCustomDelegate extends WatchUi.BehaviorDelegate {
    private var customView;

    function initialize(view) {
        BehaviorDelegate.initialize();
        customView = view;
    }

    function onNextPage() { return cycleDown(); }
    function onPreviousPage() { return cycleUp(); }

    function onKey(evt) {
        var key = evt.getKey();
        if (key == WatchUi.KEY_DOWN) {
            return cycleDown();
        } else if (key == WatchUi.KEY_UP) {
            return cycleUp();
        } else if (key == WatchUi.KEY_ENTER || key == WatchUi.KEY_START) {
            return changeCurrentValue();
        }
        return false;
    }

    function onSwipe(evt) {
        var dir = evt.getDirection();
        if (dir == WatchUi.SWIPE_DOWN) {
            return cycleDown();
        } else if (dir == WatchUi.SWIPE_UP) {
            return cycleUp();
        }
        return false;
    }

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

    function onTap(evt) {
        var xy = evt.getCoordinates();
        var y = xy[1];
        var screenH = System.getDeviceSettings().screenHeight;
        var cy = screenH / 2;

        if (y < cy - 15) {
            return cycleUp();
        } else if (y > cy + 15) {
            return cycleDown();
        } else {
            return changeCurrentValue();
        }
    }

    function changeCurrentValue() {
        var idx = customView.getSelectedIndex();
        var items = customView.getMenuItems();
        var itemKey = items[idx][1];

        switch (itemKey) {
            case "ThemeColor":
                var current = getPropVal("ThemeColor", 1);
                current = (current % 6) + 1;
                setPropVal("ThemeColor", current);
                break;
            case "TemperatureUnit":
                var currentUnit = getPropVal("TemperatureUnit", 0);
                currentUnit = (currentUnit + 1) % 2;
                setPropVal("TemperatureUnit", currentUnit);
                break;
            case "TimeFormat":
                var currentTF = getPropVal("TimeFormat", 0);
                currentTF = (currentTF + 1) % 2;
                setPropVal("TimeFormat", currentTF);
                break;
            case "NightMode":
                var currentNM = getPropVal("NightMode", 1);
                currentNM = (currentNM + 1) % 4;
                setPropVal("NightMode", currentNM);
                break;
            case "NightModeColor":
                var currentNMC = getPropVal("NightModeColor", 0);
                currentNMC = (currentNMC + 1) % 3;
                setPropVal("NightModeColor", currentNMC);
                break;
            case "ResetDefaults":
                setPropVal("ThemeColor", 1);
                setPropVal("TemperatureUnit", 0);
                setPropVal("NightMode", 1);
                setPropVal("NightModeColor", 0);
                setPropVal("Slot1Metric", 1);  // Top: Battery
                setPropVal("Slot2Metric", 2);  // Upper-Left: Heart Rate
                setPropVal("Slot3Metric", 3);  // Upper-Right: Steps
                setPropVal("Slot4Metric", 5);  // Lower-Left: Calories
                setPropVal("Slot5Metric", 6);  // Lower-Right: Distance
                setPropVal("Slot6Metric", 14); // Bottom: Weather Temp
                break;
            default:
                var currentVal = getPropVal(itemKey, 0);
                currentVal = (currentVal + 1) % 20;
                setPropVal(itemKey, currentVal);
                break;
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