using Toybox.Application;
using Toybox.WatchUi;

class GarminBasicWatchFaceApp extends Application.AppBase {

    function initialize() {
        AppBase.initialize();
    }

    // onStart() is called on application start up
    function onStart(state) {
    }

    // onStop() is called when your application is exiting
    function onStop(state) {
    }

    // Return the initial view of your application here
    function getInitialView() {
        return [ new GarminBasicWatchFaceView() ];
    }

    function onSettingsChanged() {
        WatchUi.requestUpdate();
    }

    // On-Device Settings Menu (CIQ 3.2+)
    function getSettingsView() {
        var menu = new WatchUi.Menu2({:title=>"Watch Face Settings"});
        
        var themeVal = 1;
        try {
            if (Application has :Properties) {
                var v = Application.Properties.getValue("ThemeColor");
                if (v != null) { themeVal = v; }
            }
        } catch (e) {}

        var themeNames = ["Vibrant Red", "Teal / Cyan", "Warm Orange", "Electric Green", "Gold / Yellow", "Pure White"];
        var currentThemeName = (themeVal >= 1 && themeVal <= 6) ? themeNames[themeVal - 1] : themeNames[0];
        
        menu.addItem(new WatchUi.MenuItem("Accent Color", currentThemeName, "ThemeColor", {}));
        
        return [ menu, new GarminSettingsDelegate() ];
    }
}

class GarminSettingsDelegate extends WatchUi.Menu2InputDelegate {
    function initialize() {
        Menu2InputDelegate.initialize();
    }

    function onSelect(item) {
        var id = item.getId();
        if (id.equals("ThemeColor")) {
            var current = 1;
            try {
                if (Application has :Properties) {
                    var v = Application.Properties.getValue("ThemeColor");
                    if (v != null) { current = v; }
                }
            } catch (e) {}
            
            current = (current % 6) + 1;
            try {
                if (Application has :Properties) {
                    Application.Properties.setValue("ThemeColor", current);
                }
            } catch (e) {}
            
            var themeNames = ["Vibrant Red", "Teal / Cyan", "Warm Orange", "Electric Green", "Gold / Yellow", "Pure White"];
            item.setSubLabel(themeNames[current - 1]);
            WatchUi.requestUpdate();
        }
    }
}