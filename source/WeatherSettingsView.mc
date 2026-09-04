using Toybox.WatchUi;
using Toybox.Graphics;

class WeatherSettingsView extends WatchUi.Menu2 {
    private var updateIntervals = [15, 30, 60];  // Minutes
    private var selectedInterval = 0;
    private var selectedUnit = 0;
    private var selectedTimeFormat = 0;

    function initialize() {
        Menu2.initialize({:title=>"Settings"});
        
        // Initialize with current settings
        selectedUnit = Settings.getTempUnit();
        selectedTimeFormat = Settings.getTimeFormat();
        var currentInterval = Settings.getWeatherUpdateInterval();
        
        // Find matching interval index
        for (var i = 0; i < updateIntervals.size(); i++) {
            if (updateIntervals[i] == currentInterval) {
                selectedInterval = i;
                break;
            }
        }

        // Add menu items
        addItem(new WatchUi.MenuItem(
            "Update Interval",
            "Minutes: " + updateIntervals[selectedInterval],
            :updateInterval,
            {}
        ));

        addItem(new WatchUi.MenuItem(
            "Temperature Unit",
            selectedUnit == Settings.TEMP_CELSIUS ? "Celsius" : "Fahrenheit",
            :tempUnit,
            {}
        ));

        addItem(new WatchUi.MenuItem(
            "Time Format",
            selectedTimeFormat == Settings.TIME_FORMAT_24 ? "24 Hour" : "12 Hour",
            :timeFormat,
            {}
        ));
    }

    function onSelect(item) {
        switch (item) {
            case :updateInterval:
                Settings.setWeatherUpdateInterval(updateIntervals[selectedInterval]);
                break;
            case :tempUnit:
                Settings.setTempUnit(selectedUnit);
                break;
            case :timeFormat:
                Settings.setTimeFormat(selectedTimeFormat);
                break;
        }
        WatchUi.popView(WatchUi.SLIDE_DOWN);
    }
}

class WeatherSettingsDelegate extends WatchUi.Menu2InputDelegate {
    function initialize() {
        Menu2InputDelegate.initialize();
    }
    
    function onSelect(item) {
        var id = item.getId();
        switch (id) {
            case :updateInterval:
                var menu1 = new WatchUi.Menu2({:title=>"Update Interval"});
                menu1.addItem(new WatchUi.MenuItem("5 min", null, 5, null));
                menu1.addItem(new WatchUi.MenuItem("15 min", null, 15, null));
                menu1.addItem(new WatchUi.MenuItem("30 min", null, 30, null));
                menu1.addItem(new WatchUi.MenuItem("60 min", null, 60, null));
                WatchUi.pushView(menu1, new IntervalMenuDelegate(), WatchUi.SLIDE_UP);
                break;
            case :tempUnit:
                var menu2 = new WatchUi.Menu2({:title=>"Temperature Unit"});
                menu2.addItem(new WatchUi.MenuItem("Celsius", null, Settings.TEMP_CELSIUS, null));
                menu2.addItem(new WatchUi.MenuItem("Fahrenheit", null, Settings.TEMP_FAHRENHEIT, null));
                WatchUi.pushView(menu2, new TempUnitMenuDelegate(), WatchUi.SLIDE_UP);
                break;
            case :timeFormat:
                var menu3 = new WatchUi.Menu2({:title=>"Time Format"});
                menu3.addItem(new WatchUi.MenuItem("24 Hour", null, Settings.TIME_FORMAT_24, null));
                menu3.addItem(new WatchUi.MenuItem("12 Hour (AM/PM)", null, Settings.TIME_FORMAT_12, null));
                WatchUi.pushView(menu3, new TimeFormatMenuDelegate(), WatchUi.SLIDE_UP);
                break;
        }
    }
}

class IntervalMenuDelegate extends WatchUi.Menu2InputDelegate {
    function initialize() {
        Menu2InputDelegate.initialize();
    }
    
    function onSelect(item) {
        var interval = item.getId();
        Settings.setWeatherUpdateInterval(interval);
        WatchUi.popView(WatchUi.SLIDE_DOWN);
    }
}

class TempUnitMenuDelegate extends WatchUi.Menu2InputDelegate {
    function initialize() {
        Menu2InputDelegate.initialize();
    }
    
    function onSelect(item) {
        Settings.setTempUnit(item.getId());
        WatchUi.popView(WatchUi.SLIDE_DOWN);
    }
}

class TimeFormatMenuDelegate extends WatchUi.Menu2InputDelegate {
    function initialize() {
        Menu2InputDelegate.initialize();
    }

    function onSelect(item) {
        Settings.setTimeFormat(item.getId());
        WatchUi.popView(WatchUi.SLIDE_DOWN);
    }
}