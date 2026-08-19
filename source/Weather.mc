using Toybox.Weather;
using Toybox.Time;
using Toybox.Position;

class WeatherProvider {
    private var lastUpdate = 0;
    private var currentTemp = null;
    
    function initialize() {
        requestUpdate();
    }
    
    function requestUpdate() {
        var current = Weather.getCurrentConditions();
        if (current != null && current.temperature != null) {
            currentTemp = current.temperature;
        }
        lastUpdate = Time.now().value();
    }
    
    function getTemperature() {
        return currentTemp;
    }
    
    function needsUpdate() {
        var now = Time.now().value();
        var interval = Settings.getWeatherUpdateInterval() * 60; // Convert minutes to seconds
        return (now - lastUpdate) >= interval;
    }
}