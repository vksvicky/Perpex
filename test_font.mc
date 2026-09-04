import Toybox.System;

class TestApp {
    function run() {
        var w = 454;
        var m = { 454 => "test" };
        System.println("w == 454? " + (w == 454));
        System.println("hasKey? " + m.hasKey(w));
    }
}
