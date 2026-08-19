using Toybox.Application.Properties;

class Settings {
    static function getTempUnit() {
        return Properties.getValue("tempUnit") != null ? 
            Properties.getValue("tempUnit") : TEMP_CELSIUS;
    }

    static function setTempUnit(unit) {
        Properties.setValue("tempUnit", unit);
    }

    static function getWeatherUpdateInterval() {
        return Properties.getValue("weatherUpdateInterval") != null ? 
            Properties.getValue("weatherUpdateInterval") : 15;
    }

    static function setWeatherUpdateInterval(interval) {
        Properties.setValue("weatherUpdateInterval", interval);
    }

    static const TEMP_CELSIUS = 0;
    static const TEMP_FAHRENHEIT = 1;
}