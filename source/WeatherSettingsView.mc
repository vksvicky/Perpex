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
        if (item == :updateInterval) {
            Settings.setWeatherUpdateInterval(updateIntervals[selectedInterval]);
        } else if (item == :tempUnit) {
            Settings.setTempUnit(selectedUnit);
        } else if (item == :timeFormat) {
            Settings.setTimeFormat(selectedTimeFormat);
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
        if (id == :updateInterval) {
            var menu = new WatchUi.Menu2({:title=>"Update Interval"});
            menu.addItem(new WatchUi.MenuItem("5 min", null, 5, null));
            menu.addItem(new WatchUi.MenuItem("15 min", null, 15, null));
            menu.addItem(new WatchUi.MenuItem("30 min", null, 30, null));
            menu.addItem(new WatchUi.MenuItem("60 min", null, 60, null));
            WatchUi.pushView(menu, new IntervalMenuDelegate(), WatchUi.SLIDE_UP);
        } else if (id == :tempUnit) {
            var menu = new WatchUi.Menu2({:title=>"Temperature Unit"});
            menu.addItem(new WatchUi.MenuItem("Celsius", null, Settings.TEMP_CELSIUS, null));
            menu.addItem(new WatchUi.MenuItem("Fahrenheit", null, Settings.TEMP_FAHRENHEIT, null));
            WatchUi.pushView(menu, new TempUnitMenuDelegate(), WatchUi.SLIDE_UP);
        } else if (id == :timeFormat) {
            var menu = new WatchUi.Menu2({:title=>"Time Format"});
            menu.addItem(new WatchUi.MenuItem("24 Hour", null, Settings.TIME_FORMAT_24, null));
            menu.addItem(new WatchUi.MenuItem("12 Hour (AM/PM)", null, Settings.TIME_FORMAT_12, null));
            WatchUi.pushView(menu, new TimeFormatMenuDelegate(), WatchUi.SLIDE_UP);
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