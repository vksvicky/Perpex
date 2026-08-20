using Toybox.Math as Math;
using Toybox.Time as Time;
using Toybox.Position as Pos;

class SunCalc {

    hidden const PI   = Math.PI,
        RAD  = Math.PI / 180.0d,
        PI2  = Math.PI * 2.0d,
        DAYS = 86400.0d,
        J1989 = 2447892.0d,
        J2000 = 2451545.0d,
        J0 = 0.0009d;

    hidden const TIMES = [
        -18.0d * RAD,    // ASTRO_DAWN
        -12.0d * RAD,    // NAUTIC_DAWN
        -6.0d * RAD,     // DAWN
        -4.0d * RAD,     // BLUE_HOUR
        -0.833d * RAD, // SUNRISE
        -0.3d * RAD,   // SUNRISE_END
        6.0d * RAD,      // GOLDEN_HOUR_AM
        null,         // NOON
        6.0d * RAD,
        -0.3d * RAD,
        -0.833d * RAD,
        -4.0d * RAD,
        -6.0d * RAD,
        -12.0d * RAD,
        -18.0d * RAD
        ];

    var lastD, lastLng;
    var	n, ds, M, sinM, C, L, sin2L, dec, Jnoon;

    function initialize() {
        lastD = null;
        lastLng = null;
    }

    function fromJulian(j) {
        return new Time.Moment(((j + 0.5d - J1989) * DAYS).toNumber());
    }

    function round(a) {
        if (a > 0) {
            return (a + 0.5d).toNumber().toDouble();
        } else {
            return (a - 0.5d).toNumber().toDouble();
        }
    }

    // lat and lng in radians
    function calculate(moment, pos, what) {
        var lat = pos[0].toDouble();
        var lng = pos[1].toDouble();

        var d = moment.value().toDouble() / DAYS - 0.5d + J1989 - J2000;
        if (lastD != d || lastLng != lng) {
            n = round(d - J0 + lng / PI2);
//			ds = J0 - lng / PI2 + n;
            ds = J0 - lng / PI2 + n - 0.000787d; // 1.1574e-5 * 68
            M = 6.240059967d + 0.0172019715d * ds;
            sinM = Math.sin(M);
            C = (1.9148d * sinM + 0.02d * Math.sin(2 * M) + 0.0003d * Math.sin(3 * M)) * RAD;
            L = M + C + 1.796593063d + PI;
            sin2L = Math.sin(2 * L);
            dec = Math.asin( 0.397783703d * Math.sin(L) );
            Jnoon = J2000 + ds + 0.0053d * sinM - 0.0069d * sin2L;
            lastD = d;
            lastLng = lng;
        }

        if (what == NOON) {
            return fromJulian(Jnoon);
        }

        var x = (Math.sin(TIMES[what]) - Math.sin(lat) * Math.sin(dec)) / (Math.cos(lat) * Math.cos(dec));

        if (x > 1.0 || x < -1.0) {
            return null;
        }

        var ds_set = J0 + (Math.acos(x) - lng) / PI2 + n - 0.000787d;

        var Jset = J2000 + ds_set + 0.0053d * sinM - 0.0069d * sin2L;
        if (what > 7) { // 7 is NOON
            return fromJulian(Jset);
        }

        var Jrise = Jnoon - (Jset - Jnoon);

        return fromJulian(Jrise);
    }

    function momentToString(moment, is24Hour) {

        if (moment == null) {
            return "--:--";
        }

        var tinfo = Time.Gregorian.info(new Time.Moment(moment.value() + 30), Time.FORMAT_SHORT);
        var text;
        if (is24Hour) {
            text = tinfo.hour.format("%02d") + ":" + tinfo.min.format("%02d");
        } else {
            var hour = tinfo.hour % 12;
            if (hour == 0) {
                hour = 12;
            }
            text = hour.format("%02d") + ":" + tinfo.min.format("%02d");
            // wtf... get used to 24 hour format...
            if (tinfo.hour < 12 || tinfo.hour == 24) {
                text = text + " AM";
            } else {
                text = text + " PM";
            }
        }
        var today = Time.today();
        var days = ((moment.value() - today.value()) / Time.Gregorian.SECONDS_PER_DAY).toNumber();

        if (moment.value() > today.value() ) {
            if (days > 0) {
                text = text + " +" + days;
            }
        } else {
            days = days - 1;
            text = text + " " + days;
        }
        return text;
    }

    static function printMoment(moment) {
        var info = Time.Gregorian.info(moment, Time.FORMAT_SHORT);
        return info.day.format("%02d") + "." + info.month.format("%02d") + "." + info.year.toString()
            + " " + info.hour.format("%02d") + ":" + info.min.format("%02d") + ":" + info.sec.format("%02d");
    }

    (:test) static function testCalc(logger) {

        var testMatrix = [
            [ 1496310905, 48.1009616, 11.759784, NOON, 1496315468 ],
            [ 1496310905, 70.6632359, 23.681726, NOON, 1496312606 ],
            [ 1496310905, 70.6632359, 23.681726, SUNSET, null ],
            [ 1496310905, 70.6632359, 23.681726, SUNRISE, null ],
            [ 1496310905, 70.6632359, 23.681726, ASTRO_DAWN, null ],
            [ 1496310905, 70.6632359, 23.681726, NAUTIC_DAWN, null ],
            [ 1496310905, 70.6632359, 23.681726, DAWN, null ],
            [ 1483225200, 70.6632359, 23.681726, SUNRISE, null ],
            [ 1483225200, 70.6632359, 23.681726, NOON, 1483266532 ],
            [ 1483225200, 70.6632359, 23.681726, ASTRO_DAWN, 1483247635 ],
            [ 1483225200, 70.6632359, 23.681726, NAUTIC_DAWN, 1483252565 ],
            [ 1483225200, 70.6632359, 23.681726, DAWN, 1483259336 ]
            ];

        var sc = new SunCalc();
        var moment;

        for (var i = 0; i < testMatrix.size(); i++) {
            moment = sc.calculate(new Time.Moment(testMatrix[i][0]),
                                  new Pos.Location(
                                      { :latitude => testMatrix[i][1], :longitude => testMatrix[i][2], :format => :degrees }
                                      ).toRadians(),
                                  testMatrix[i][3]);

            if (   (moment == null  && testMatrix[i][4] != moment)
                   || (moment != null && moment.value().toLong() != testMatrix[i][4])) {
                var val;

                if (moment == null) {
                    val = "null";
                } else {
                    val = (moment as Time.Moment).value().toLong();
                }

                logger.debug("Expected " + testMatrix[i][4] + " but got: " + val);
                logger.debug(printMoment(moment));
                return false;
            }
        }

        return true;
    }
}
