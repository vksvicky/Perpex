with open("source/UIDrawer.mc", "r") as f:
    content = f.read()

replacement1 = """
            if (customFont != null) {
                var textW = dc.getTextWidthInPixels(battText, fontValue);
                dc.drawText(posX - textW / 2, posY + (3 * s).toNumber(), fontValue, battText, Graphics.TEXT_JUSTIFY_LEFT);
            } else {
                dc.drawText(posX, posY + (9 * s).toNumber(), fontValue, battText, Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
            }
"""

replacement2 = """
        var valColor = isLowPower ? 0x888888 : Graphics.COLOR_WHITE;
        dc.setColor(valColor, Graphics.COLOR_TRANSPARENT);
        if (customFont != null) {
            var textW = dc.getTextWidthInPixels(valStr, fontValue);
            dc.drawText(posX - textW / 2, posY + (3 * s).toNumber(), fontValue, valStr, Graphics.TEXT_JUSTIFY_LEFT);
        } else {
            dc.drawText(posX, posY + (9 * s).toNumber(), fontValue, valStr, Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);
        }
"""

content = content.replace("            dc.drawText(posX, posY + (9 * s).toNumber(), fontValue, battText, Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);", replacement1.strip())
content = content.replace("""        var valColor = isLowPower ? 0x888888 : Graphics.COLOR_WHITE;
        dc.setColor(valColor, Graphics.COLOR_TRANSPARENT);
        dc.drawText(posX, posY + (9 * s).toNumber(), fontValue, valStr, Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER);""", replacement2.strip())

with open("source/UIDrawer.mc", "w") as f:
    f.write(content)
