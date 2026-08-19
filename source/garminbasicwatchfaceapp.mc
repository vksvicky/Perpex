using Toybox.Application;
using Toybox.WatchUi;

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
    // ON-WATCH NATIVE MENU (WatchUi.Menu2) - FULL 6-SETTING PICKER
    // ─────────────────────────────────────────────────────────────────────
    function getSettingsView() {
        var menu = new WatchUi.Menu2({:title=>"Watch Face Settings"});

        var themeVal = getPropVal("ThemeColor", 1);
        var slot1Val = getPropVal("Slot1Metric", 1);
        var slot2Val = getPropVal("Slot2Metric", 2);
        var slot3Val = getPropVal("Slot3Metric", 11);
        var slot4Val = getPropVal("Slot4Metric", 3);
        var slot5Val = getPropVal("Slot5Metric", 5);

        var themeNames = ["Vibrant Red", "Teal / Cyan", "Warm Orange", "Electric Green", "Gold / Yellow", "Pure White"];
        var currentThemeName = (themeVal >= 1 && themeVal <= 6) ? themeNames[themeVal - 1] : themeNames[0];

        menu.addItem(new WatchUi.MenuItem("Accent Theme Color", currentThemeName, "ThemeColor", {}));
        menu.addItem(new WatchUi.MenuItem("Top Slot Metric", getMetricNameLabel(slot1Val), "Slot1Metric", {}));
        menu.addItem(new WatchUi.MenuItem("Left Slot Metric", getMetricNameLabel(slot2Val), "Slot2Metric", {}));
        menu.addItem(new WatchUi.MenuItem("Center Badge Metric", getMetricNameLabel(slot3Val), "Slot3Metric", {}));
        menu.addItem(new WatchUi.MenuItem("Right Slot Metric", getMetricNameLabel(slot4Val), "Slot4Metric", {}));
        menu.addItem(new WatchUi.MenuItem("Bottom Slot Metric", getMetricNameLabel(slot5Val), "Slot5Metric", {}));

        return [ menu, new GarminSettingsDelegate() ];
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
            "None (Hidden)",          // 0
            "Battery Level (%)",      // 1
            "Heart Rate (BPM)",       // 2
            "Step Count",             // 3
            "Step Goal Progress (%)", // 4
            "Active Calories (kCal)", // 5
            "Distance Walked",        // 6
            "Floors Climbed",         // 7
            "Active Minutes",         // 8
            "Stress Level",           // 9
            "Digital Clock",          // 10
            "Unread Notifications",   // 11
            "Altitude / Elevation",   // 12
            "Barometer"               // 13
        ];
        if (id >= 0 && id < names.size()) {
            return names[id];
        }
        return "None (Hidden)";
    }
}

class GarminSettingsDelegate extends WatchUi.Menu2InputDelegate {
    function initialize() {
        Menu2InputDelegate.initialize();
    }

    function onSelect(item) {
        var id = item.getId();
        if (id.equals("ThemeColor")) {
            var current = getPropVal("ThemeColor", 1);
            current = (current % 6) + 1;
            setPropVal("ThemeColor", current);

            var themeNames = ["Vibrant Red", "Teal / Cyan", "Warm Orange", "Electric Green", "Gold / Yellow", "Pure White"];
            item.setSubLabel(themeNames[current - 1]);
        } else if (id.equals("Slot1Metric") || id.equals("Slot2Metric") || id.equals("Slot3Metric") || id.equals("Slot4Metric") || id.equals("Slot5Metric")) {
            var current = getPropVal(id, 0);
            current = (current + 1) % 14;
            setPropVal(id, current);

            item.setSubLabel(getMetricNameLabel(current));
        }
        WatchUi.requestUpdate();
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

    function getMetricNameLabel(id) {
        var names = [
            "None (Hidden)",          // 0
            "Battery Level (%)",      // 1
            "Heart Rate (BPM)",       // 2
            "Step Count",             // 3
            "Step Goal Progress (%)", // 4
            "Active Calories (kCal)", // 5
            "Distance Walked",        // 6
            "Floors Climbed",         // 7
            "Active Minutes",         // 8
            "Stress Level",           // 9
            "Digital Clock",          // 10
            "Unread Notifications",   // 11
            "Altitude / Elevation",   // 12
            "Barometer"               // 13
        ];
        if (id >= 0 && id < names.size()) {
            return names[id];
        }
        return "None (Hidden)";
    }
}