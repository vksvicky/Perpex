# Dynamic Ring Colors in Connect IQ

When building a watch face with settings that allow the user to dynamically change the colors of individual rings, we face specific technical constraints in the Garmin Connect IQ (CIQ) environment.

## The Problem with Static Images
In our recent prototypes, we generated the rings as **full-screen static PNG images**. 
- **Can we change their color dynamically via settings?** Practically, **No**. 
- Garmin's graphics engine does not support dynamically tinting or recoloring full-color PNG images at runtime. 
- The only way to support different colors with static images is to generate multiple versions of the images (e.g., one set of red rings, one set of blue rings) and load them based on the setting. This drastically increases the app's file size and memory footprint, making it incompatible with most Garmin watches.

*(Note: CIQ 4.0+ does support indexed palette swapping, but this limits compatibility and is extremely complex to manage for anti-aliased text).*

## The Solution: Custom Fonts (Vector Drawing)
To allow infinite, dynamic color customization for each ring without inflating memory, the text **must be drawn dynamically using a Custom Font** rather than static full-screen images.

- **How it works**: We compile the numbers/text into a Garmin Font Resource (`.fnt`). Because fonts in Garmin act as transparent masks, we can apply *any* color to them instantly at runtime.
- **The Code**: `dc.setColor(userRingColor, Graphics.COLOR_TRANSPARENT);` followed by `dc.drawText(...)`.
- **Quality**: We can achieve the exact same ultra-high-quality, non-jagged look as the static images by using a tool like BMFont to generate a high-resolution, anti-aliased custom font specifically for this watch face's curved layout.

## Recommendation for this Project
If dynamic color customization via settings is a hard requirement, **we cannot use the 3 static PNG rings we just generated.** 

Instead, we must:
1. Revert to the dynamic `drawCurvedLabel` approach in the code.
2. Ensure the `CurvedFonts` system is built with high-quality, anti-aliased font assets so it matches the visual crispness of the mockups.
3. Hook up the `dc.setColor()` calls to the user's settings.
