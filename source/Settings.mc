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

    static function getTimeFormat() {
        return Properties.getValue("TimeFormat") != null ?
            Properties.getValue("TimeFormat") : 0;
    }

    static function setTimeFormat(format) {
        Properties.setValue("TimeFormat", format);
    }

    static const TEMP_CELSIUS = 0;
    static const TEMP_FAHRENHEIT = 1;

    static const TIME_FORMAT_24 = 0;
    static const TIME_FORMAT_12 = 1;
}