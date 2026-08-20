using Toybox.Position;
using Toybox.Activity;
using Toybox.Weather;
using Toybox.System;

class LocationHelper {
    static function getBestLocation() {
        var pos = null;
        
        if (Toybox has :Position) {
            var posInfo = Toybox.Position.getInfo();
            if (posInfo != null && posInfo.position != null) { 
                pos = posInfo.position;
            }
        }
        
        if (pos == null && Toybox has :Activity) {
            var actInfo = Activity.getActivityInfo();
            if (actInfo != null && actInfo.currentLocation != null) { 
                pos = actInfo.currentLocation; 
            }
        }
        
        if (pos == null && Toybox has :Weather && Weather has :getCurrentConditions) {
            var cond = Weather.getCurrentConditions();
            if (cond != null && cond.observationLocationPosition != null) { 
                pos = cond.observationLocationPosition; 
            }
        }
        
        return pos;
    }
}
