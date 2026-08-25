# Garmin Watch Face (Perpex)

This is a custom Connect IQ watch face for Garmin devices featuring a heavily customizable data-rich layout.

## Testing & Compliance

### Always-On Display (AOD) Burn-In Protection
Garmin AMOLED devices require watch faces to adhere to strict burn-in protection guidelines in Low Power mode. Specifically, the watch face must use less than 10% active pixels and no single pixel can remain static for more than 3 minutes. 

To ensure compliance, the watch face utilizes a global coordinate shift `(-2 to +2 pixels)` every minute.

**How to verify in the Connect IQ Simulator:**
1. Run the simulator for an AMOLED device (e.g., `epix2`).
2. Navigate to **Settings > Low Power Mode**.
3. Navigate to **File > View Heat Map**.
4. Use **Simulation > Time > Fast Forward** to let the simulation run for an extended period.

**Latest Test Results (Epix 2):**
- 24-Hour simulation finished, no screen burn-in detected.
- Peak Luminance Usage: **1.27%** (Well below the 10% limit).
