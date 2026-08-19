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
    // ON-WATCH NATIVE MENU (WatchUi.Menu2) - SHORT TITLES & RESET DEFAULTS
    // ─────────────────────────────────────────────────────────────────────
    function getSettingsView() {
        var menu = new WatchUi.Menu2({:title=>"Watch Face"});

        var themeVal = getPropVal("ThemeColor", 1);
        var slot1Val = getPropVal("Slot1Metric", 1);
        var slot2Val = getPropVal("Slot2Metric", 2);
        var slot3Val = getPropVal("Slot3Metric", 11);
        var slot4Val = getPropVal("Slot4Metric", 3);
        var slot5Val = getPropVal("Slot5Metric", 5);

        var themeNames = ["Vibrant Red", "Teal / Cyan", "Warm Orange", "Electric Green", "Gold / Yellow", "Pure White"];
        var currentThemeName = (themeVal >= 1 && themeVal <= 6) ? themeNames[themeVal - 1] : themeNames[0];

        menu.addItem(new WatchUi.MenuItem("Theme Color", currentThemeName, "ThemeColor", {}));
        menu.addItem(new WatchUi.MenuItem("Top Field", getMetricNameLabel(slot1Val), "Slot1Metric", {}));
        menu.addItem(new WatchUi.MenuItem("Left Field", getMetricNameLabel(slot2Val), "Slot2Metric", {}));
        menu.addItem(new WatchUi.MenuItem("Center Badge", getMetricNameLabel(slot3Val), "Slot3Metric", {}));
        menu.addItem(new WatchUi.MenuItem("Right Field", getMetricNameLabel(slot4Val), "Slot4Metric", {}));
        menu.addItem(new WatchUi.MenuItem("Bottom Field", getMetricNameLabel(slot5Val), "Slot5Metric", {}));
        menu.addItem(new WatchUi.MenuItem("Reset Defaults", "Restore Original", "ResetDefaults", {}));

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
            "Hidden",        // 0
            "Battery",       // 1
            "Heart Rate",    // 2
            "Steps",         // 3
            "Step Goal",     // 4
            "Calories",      // 5
            "Distance",      // 6
            "Floors",        // 7
            "Active Mins",   // 8
            "Stress",        // 9
            "Digital Clock", // 10
            "Notifications", // 11
            "Altitude",      // 12
            "Barometer"      // 13
        ];
        if (id >= 0 && id < names.size()) {
            return names[id];
        }
        return "Hidden";
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

        } else if (id.equals("ResetDefaults")) {
            setPropVal("ThemeColor", 1);
            setPropVal("Slot1Metric", 1);
            setPropVal("Slot2Metric", 2);
            setPropVal("Slot3Metric", 11);
            setPropVal("Slot4Metric", 3);
            setPropVal("Slot5Metric", 5);

            item.setSubLabel("Reset Done!");
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
            "Hidden",        // 0
            "Battery",       // 1
            "Heart Rate",    // 2
            "Steps",         // 3
            "Step Goal",     // 4
            "Calories",      // 5
            "Distance",      // 6
            "Floors",        // 7
            "Active Mins",   // 8
            "Stress",        // 9
            "Digital Clock", // 10
            "Notifications", // 11
            "Altitude",      // 12
            "Barometer"      // 13
        ];
        if (id >= 0 && id < names.size()) {
            return names[id];
        }
        return "Hidden";
    }
}