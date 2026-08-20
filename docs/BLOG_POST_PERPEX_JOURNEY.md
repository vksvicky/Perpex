---
title: "Stuck in SDK Beta for a Year: Building & Launching Perpex for Garmin Connect IQ"
date: 2026-08-20
author: Vivek
summary: "The 12-month journey of building Perpex—from hitting memory ceilings on SDK 8.0.0 Beta to mastering Connect IQ SDK 9.2.0, resolution qualifiers, multi-device builds, and the quirks of physical watch testing."
slug: perpex-garmin-watchface-journey
status: draft
tags: [garmin, connect-iq, monkeyc, watchface, embedded, architecture, release]
categories: [code, engineering]
---

Building software for resource-constrained hardware is a humbling experience. Unlike modern web browsers or high-powered desktop operating systems where megabytes of memory are cheap, embedded systems force software engineers to count every single kilobyte.

For the past year, my side project—a high-end, mechanical-style perpetual calendar watch face named **Perpex** for Garmin smartwatches—sat completely frozen. 

What started as an exciting side project ground to a halt due to a fundamental lack of understanding of how the Garmin Connect IQ SDK handles memory, graphics primitives, resolution qualifiers, and device hardware tiers. 

Here is the story of how I spent 12 months stuck on **Connect IQ SDK 8.0.0 Beta**, how upgrading to **SDK 9.2.0** unlocked the project, the hard architectural decisions we made along the way, and the lessons learned preparing a multi-device binary for the Garmin Store.

---

### The 1-Year Hiatus: Stuck in SDK 8.0.0 Beta & The 32KB Memory Ceiling

When I first envisioned **Perpex**, I wanted to bring the intricate elegance of a multi-thousand dollar Swiss perpetual calendar watch to a Garmin wrist display. I designed concentric inner dial rings tracking the Month, Day of the Month, and Day of the Week, flanked by 7 customizable metric slots and tactical night modes.

However, during early development, I made two critical mistakes:

1. **Relying on SDK 8.0.0 Beta**: I was building against an early SDK release without understanding the underlying API changes, resource qualifier resolution, or memory model shifts.
2. **The System 3 Memory Trap (Fenix 6S)**: I tried forcing the entire watch face—including heavy bitmap drawables and concentric ring calculations—to run on older System 3 devices like the **Fenix 6S** (240x240 display). 

In Garmin Connect IQ, System 3 watch faces are allocated a strict, unforgiving **32KB RAM memory budget**. The moment you load a couple of uncompressed bitmaps or attempt dynamic vector operations, the system throws an Out-Of-Memory (`OOM`) error and crashes the watch face. 

Stuck without a clear path forward and frustrated by memory crashes, the project sat untouched for a full year.

---

### The Breakthrough: Upgrading to SDK 9.2.0 & The Vector-to-Asset Architectural Pivot

Recently, I decided to revisit the project with a fresh architectural perspective. The breakthrough came down to three major changes:

#### 1. Upgrading to Connect IQ SDK 9.2.0
We upgraded the toolchain to **SDK 9.2.0** and re-anchored our application to **Connect IQ System 4+ (SDK 4.0.0+)**. System 4+ devices (like the Fenix 7, Fenix 8, Enduro 3, Epix Gen 2, and Venu 3) provide **128KB to 512KB of RAM**—giving us the breathing room required for high-density watch faces.

#### 2. Cutting Legacy Resolution Anchor (Dropping 240x240 Fenix 6S)
We made a conscious decision to drop System 3 (240x240) devices from our target product list. Trying to support legacy 32KB hardware was breaking modern System 4 code. By establishing a strict **260px minimum resolution baseline**, we preserved code cleanliness and rock-solid stability.

#### 3. Moving from Procedural Primitive Vectors to Pre-Rendered Resolution Assets
Instead of forcing the watch CPU to compute complex, anti-aliased concentric ring graphics on every screen refresh (which destroys battery life), we pivoted to pre-rendering high-precision PNG assets organized into resolution qualifier folders:
- `resources-round-260x260` *(Fenix 7, Forerunner 255)*
- `resources-round-280x280` *(Enduro 3, Fenix 7X)*
- `resources-round-390x390` *(Epix 2 Pro 42mm, Venu 2S)*
- `resources-round-416x416` *(Epix Gen 2 47mm, Venu 2/3)*
- `resources-round-454x454` *(Fenix 8 47mm/51mm, Epix Pro 51mm)*

By letting Garmin's `monkeyc` resource compiler pick the exact bitmap per screen density, runtime memory overhead dropped by 60% and battery draw remained minimal.

---

### Preparing the Store Package: Resolving Multi-Device Build Errors

When building a single device target in the simulator (e.g., `./build.sh epix2`), everything can look completely flawless. But exporting a production store package (`.iq` file via `./export_iq.sh`) is a different beast entirely.

`export_iq.sh` compiles your code against **all 44 target devices** listed in `manifest.xml`. 

During our initial export run, the build abruptly failed with:
```text
ERROR: fenix7s: Undefined symbol ':dial_bg' detected.
ERROR: Failed to export application for device id: 'fenix7s'.
```

#### The Root Cause & Fix
While our resolution folders covered 260px through 454px, devices like the **Fenix 7S** use a 240x240 MIP display under System 4. When `monkeyc` tried to build `fenix7s`, it looked for `:dial_bg` in a `resources-round-240x240` folder that didn't exist, and failed because there was no global fallback.

We solved this by adding a global fallback bitmap in the root `resources/drawables/drawables.xml`:
```xml
<drawables>
    <bitmap id="LauncherIcon" filename="images/launcher_icon.png" />
    <bitmap id="dial_bg" filename="../../resources-round-260x260/drawables/dial_bg.png" />
    ...
</drawables>
```
With this fallback in place, `monkeyc` cleanly compiled all 44 device targets, generating a production-ready **3.0 MB `PerpexTacticalWatchFace.iq`** binary!

---

### The Testing Dilemma: Watch Simulator vs. Physical Mobile Phone App Settings

One of the most fascinating engineering challenges of Garmin Connect IQ development is how testing works across hardware vs. software.

#### 1. The Power of the Watch Simulator
Garmin's `ConnectIQ.app` simulator on Mac is exceptional. It allows developers to instantly test layout rendering, low-power AMOLED Always-On Display (AOD) burn-in protection, and native on-watch settings (`UP/MENU`) across 44 different screen sizes without owning 44 physical watches.

#### 2. The Mobile App Settings Paradox
However, **mobile phone settings cannot be tested via USB side-loading**. 

If you copy a `.prg` file via USB directly onto a physical watch (like my personal Fenix 6S), the watch face runs fine on the watch hardware, but the **Garmin Connect IQ Mobile App on your phone will NOT show a Settings button**. 

Why? Because side-loaded `.prg` files lack the server-side registration GUID that binds mobile setting forms (`resources/settings/settings.xml`) to Garmin's cloud servers. 

#### How Developers Work Around This:
- **Simulator App Settings Tool**: In the simulator, clicking **Settings ➔ Trigger App Settings** (`Cmd + Shift + S`) renders the exact mobile settings form on your Mac.
- **Private Draft Uploads**: Uploading a `.iq` package to the Garmin Developer Dashboard as an **Unlisted / Private Draft** allows your phone's Connect IQ app to recognize the app on a paired watch and open the live phone settings screen.
- **Relying on User Testing & Community Feedback**: Until an app is published or deployed as a private beta link, mobile settings UI relies heavily on simulator validation and community feedback.

---

### The Final Result: Verification & Store Upload

After optimizing every asset, tuning metric vertical offsets, and removing all emojis from text fields to satisfy Garmin's strict validator rules, we uploaded the release package to the Garmin Developer Dashboard.

The results:
- **Manifest App ID**: `bd57c3bccf764485b28dd4fcc24a9f02`
- **Status**: **Verified**
- **Signature**: **Verified**
- **Version**: **1.0.0**
- **Assets**: 1440x720 Hero Banner, 500x500 Cover Image, and 8 Real-Device Screenshots (all strictly under size limits).

**Perpex** is now officially submitted and undergoing final review on the Garmin Connect IQ Store!

---

### Key Takeaways for Embedded & Wearable Developers

1. **Know Your Memory Ceilings Early**: Don't force modern features onto legacy hardware tiers. Define your minimum SDK and hardware specs early.
2. **Pre-Render Over Procedural**: On wearable CPUs, pre-rendered resolution-qualified assets beat runtime canvas math for battery life and frame rates.
3. **Always Test Multi-Device Builds**: Single-device builds lie; multi-device store package exports (`.iq`) will reveal missing resource fallbacks.
4. **Embrace the Ecosystem Quirks**: Understand what the simulator can test (watch UI, AOD, on-watch menus) versus what requires server-side draft uploads (mobile app settings).

Building **Perpex** was a masterclass in perseverance, asset optimization, and understanding embedded hardware constraints. I can't wait to see it running on Garmin wrists around the world!
