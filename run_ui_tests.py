#!/usr/bin/env python3
"""
Perpex UI Layout Validation Test Harness
========================================
Usage:
  python3 run_ui_tests.py
"""
import os
import re
import subprocess
import sys
import time
from datetime import datetime

# ── Paths ─────────────────────────────────────────────────────────────────────
SDK_PATH     = os.path.expanduser("~/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2")
KEY_PATH     = "developer_key.der"
REPORT_PATH  = "test_output/visual_report.html"

# ── Devices ───────────────────────────────────────────────────────────────────
DEVICES = [
    ("fenix7s",      "240×240 MIP",        "Fenix 7S / 7S Pro"),
    ("fenix7",       "260×260 MIP Solar",  "Fenix 7 / Fenix 9 Pro Solar 47mm"),
    ("fr255",        "260×260 MIP Running","Forerunner 255 / 255 Music"),
    ("enduro3",      "280×280 MIP Solar",  "Enduro 3 / Fenix 7X / Fenix 8 Solar 51mm"),
    ("venu2s",       "360×360 AMOLED",     "Venu 2S"),
    ("epix2pro42mm", "390×390 AMOLED",     "Epix 2 Pro 42mm / Venu 3S"),
    ("venu2",        "416×416 AMOLED",     "Venu 2 / Venu 2 Plus / Epix Gen 2"),
    ("venu3",        "454×454 AMOLED",     "Venu 3 / Forerunner 965 / Fenix 8 47mm"),
    ("venusq2",      "320×360 AMOLED",     "Venu Sq 2"),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_current_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def sanitise_branch(branch: str) -> str:
    """Make branch name safe for use as a directory component."""
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", branch)


# ── HTML report ───────────────────────────────────────────────────────────────

def _val_badge(passed):
    if passed:
        return '<span class="badge badge-pass">✅ PASS</span>'
    return '<span class="badge badge-fail">❌ FAIL</span>'


def _img_tag(path, alt=""):
    if path and os.path.exists(path):
        rel = os.path.relpath(path, "test_output")
        return f'<img src="{rel}" alt="{alt}" loading="lazy">'
    return '<div class="no-img">No image</div>'


def generate_report(all_results, branch):
    """
    all_results: list of (dev_id, res_info, dev_name, list_of_pass_results)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    mode_label = f"branch: <code>{branch}</code>"

    device_sections = ""
    for dev_id, res_info, dev_name, results in all_results:
        passed = sum(1 for r in results if r.get("passed"))
        failed = len(results) - passed
        warn_cls = " warn" if failed > 0 else ""

        rows = ""
        for r in results:
            pass_name = r.get("pass_name") or r.get("name") or r.get("id", "")
            desc = r.get("description", "")
            img_path = r.get("current_img") or r.get("img_path", "")
            zones_path = r.get("zones_img") or r.get("annotated_path", "")
            val_passed = r.get("passed", False)
            issues = r.get("issues", [])

            slots_html = ""
            if "slots" in r:
                items = "".join(f"<li>{s}</li>" for s in r["slots"])
                slots_html = f'<ul class="slot-list">{items}</ul>'

            issues_html = ""
            if issues:
                items = "".join(f"<li>⚠️ {iss}</li>" for iss in issues)
                issues_html = f'<ul class="issues-list">{items}</ul>'

            rows += f"""
        <tr>
          <td class="pass-name">
            <strong>{pass_name}</strong><br>
            <small>{desc}</small><br>
            {_val_badge(val_passed)}
            {slots_html}
            {issues_html}
          </td>
          <td class="img-cell">
            {_img_tag(img_path, pass_name)}
          </td>
          <td class="img-cell">
            {_img_tag(zones_path, pass_name + ' Zones')}
          </td>
        </tr>"""

        device_sections += f"""
    <div class="device-section">
      <div class="device-header">
        <h2>{dev_name}</h2>
        <span class="badge-res">{res_info}</span>
        <span class="stat">✅ {passed} passed</span>
        {f'<span class="stat{warn_cls}">❌ {failed} failed</span>' if failed else ''}
      </div>
      <table class="result-table">
        <thead>
          <tr>
            <th>Pass & Assertions</th>
            <th>Watch Face Screenshot</th>
            <th>Layout Zones & Clearance</th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Perpex Layout Validation Report</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a; color: #f1f5f9; margin: 0; padding: 24px; }}
    h1   {{ text-align:center; color: #38bdf8; margin-bottom: 4px; font-size: 1.8rem; }}
    .meta {{ text-align:center; color:#94a3b8; margin-bottom:28px; font-size:.9rem; }}
    .meta code {{ background:#1e293b; padding:2px 6px; border-radius:4px; color:#7dd3fc; }}

    .device-section {{ background:#1e293b; border-radius:12px; border:1px solid #334155;
                        margin-bottom:32px; overflow:hidden; }}
    .device-header  {{ padding:16px 20px; background:#162032; display:flex;
                        align-items:center; gap:14px; flex-wrap:wrap; }}
    .device-header h2 {{ margin:0; color:#e2e8f0; font-size:1.1rem; }}
    .badge-res {{ background:#0284c7; color:#fff; padding:3px 10px;
                   border-radius:20px; font-size:.8rem; font-weight:700; }}
    .stat      {{ font-size:.82rem; color:#4ade80; }}
    .stat.warn {{ color:#f87171; }}

    .result-table {{ width:100%; border-collapse:collapse; }}
    .result-table th {{ background:#0f172a; color:#7dd3fc; text-align:left;
                         padding:10px 16px; font-size:.8rem; text-transform:uppercase;
                         letter-spacing:.05em; }}
    .result-table td {{ padding:12px 16px; border-top:1px solid #1e293b; vertical-align:top; }}
    .result-table tr:hover td {{ background:#162032; }}
    .pass-name  {{ width:280px; min-width:220px; }}
    .pass-name strong {{ color:#e2e8f0; font-size:.9rem; }}
    .pass-name small  {{ color:#94a3b8; font-size:.78rem; }}
    .img-cell  {{ }}
    .img-cell img {{ max-width:100%; border-radius:6px; border:1px solid #334155; }}
    .no-img {{ color:#475569; font-size:.8rem; padding:20px; text-align:center; }}

    .slot-list {{ margin:6px 0 0 0; padding-left:16px; font-size:.75rem; color:#94a3b8; }}
    .slot-list li {{ margin-bottom:2px; }}
    
    .issues-list {{ margin:6px 0 0 0; padding-left:16px; font-size:.75rem; color:#f87171; font-weight: bold; }}

    .badge {{ display:inline-block; padding:2px 8px; border-radius:12px;
               font-size:.75rem; font-weight:700; margin-top:6px; }}
    .badge-pass   {{ background:#14532d; color:#4ade80; }}
    .badge-fail   {{ background:#7f1d1d; color:#f87171; }}
  </style>
</head>
<body>
  <h1>🎨 Perpex Layout Validation Report</h1>
  <p class="meta">
    {mode_label} &nbsp;·&nbsp; {timestamp} &nbsp;·&nbsp;
    {len(all_results)} devices
  </p>
  {device_sections}
</body>
</html>"""

    with open(REPORT_PATH, "w") as f:
        f.write(html)
    print(f"\n  📄 Report → {REPORT_PATH}")


# ── Focused 48-Pass Resolution Matrix ─────────────────────────────────────────

THEME_DISTRIBUTION = {
    "fenix7":       ["theme1"],           # Vibrant Red (Default)
    "venu2":        ["theme2", "low_power"], # Teal / Cyan + AOD Mode
    "enduro3":      ["theme3"],           # Warm Orange
    "venu3":        ["theme4", "low_power"], # Electric Green + AOD Mode
    "fr255":        ["theme5"],           # Gold / Yellow
    "epix2pro42mm": ["theme6", "low_power"], # Pure White + AOD Mode
    "fenix7s":      ["night_red"],        # Night Mode: Tactical Red
    "venu2s":       ["night_amber"],      # Night Mode: Night Amber
    "venusq2":      ["night_green", "low_power"], # Night Mode: Stealth Green + AOD Mode
}

WEATHER_DISTRIBUTION = {
    "fenix7":       ["weather_rain"],          # Raindrop 27%
    "enduro3":      ["weather_sunny"],         # Clear / Sunny 22°C
    "fr255":        ["weather_partly_cloudy"],  # Partly Cloudy 20°C
    "venu2":        ["weather_cloudy"],        # Cloudy 18°C
    "venu3":        ["weather_showers"],       # Showers 85%
    "epix2pro42mm": ["weather_thunderstorm"],  # Thunderstorm 90%
    "fenix7s":      ["weather_snow"],          # Snow -1°C
    "venusq2":      ["weather_wind"],          # High Wind 12kt
}


def run_device_passes(dev_id, dev_name, res_info, output_dir, full_mode=False):
    from test_ui.test_permutations import run_permutation_tests
    from test_ui.test_themes import run_theme_tests, THEME_PASSES, LOW_POWER_PASS
    from test_ui.test_weather import run_weather_tests, WEATHER_PASSES
    from test_ui.simulator_driver import build_app, launch_simulator_and_screenshot
    from test_ui.layout_validator import validate_layout
    from test_ui.config_manager import set_properties

    # 1. Permutations: always run all 3 zero-duplicate passes (Metrics 1-21)
    results = run_permutation_tests(dev_id, dev_name, res_info, output_dir)

    # 2. Themes: run full or targeted distribution
    if full_mode:
        results += run_theme_tests(dev_id, dev_name, res_info, output_dir)
        results += run_weather_tests(dev_id, dev_name, res_info, output_dir)
    else:
        # Targeted Theme passes
        theme_ids = THEME_DISTRIBUTION.get(dev_id, [])
        all_theme_passes = THEME_PASSES + [LOW_POWER_PASS]
        for p in all_theme_passes:
            if p["id"] in theme_ids:
                print(f"  🎨 [{p['id']}] {p['name']}")
                set_properties(p["props"])
                prg_path = f"bin/Theme_{dev_id}_{p['id']}.prg"
                img_path = os.path.join(output_dir, f"{dev_id}_{p['id']}.png")
                built = build_app(dev_id, prg_path)
                captured = False
                val_result = {"pass": False, "issues": ["Build failed"]}
                if built:
                    captured = launch_simulator_and_screenshot(dev_id, prg_path, img_path, res_info)
                    if captured:
                        val_result = validate_layout(img_path, [1, 2, 3, 4, 5, 6])
                res = dict(p)
                res["pass_name"] = p["name"]
                res["current_img"] = img_path if captured else None
                res["zones_img"] = val_result["annotated_path"] if captured else None
                res["passed"] = val_result["pass"]
                res["issues"] = val_result["issues"]
                results.append(res)

        # Targeted Weather passes
        weather_ids = WEATHER_DISTRIBUTION.get(dev_id, [])
        for w in WEATHER_PASSES:
            if w["id"] in weather_ids:
                print(f"  🌦️ [{w['id']}] {w['name']} -> {w['condition_text']}")
                weather_props = {
                    "NightMode": 0, "TestHideHands": 1,
                    "Slot1Metric": 15, "Slot2Metric": 2, "Slot3Metric": 3,
                    "Slot4Metric": 4, "Slot5Metric": 5, "Slot6Metric": 6,
                    "TestWeatherOverride": w["override"],
                }
                set_properties(weather_props)
                prg_path = f"bin/Weather_{dev_id}_{w['id']}.prg"
                img_path = os.path.join(output_dir, f"{dev_id}_{w['id']}.png")
                built = build_app(dev_id, prg_path)
                captured = False
                val_result = {"pass": False, "issues": ["Build failed"], "annotated_path": None}
                if built:
                    val_result["issues"] = ["Simulator capture timed out"]
                    captured = launch_simulator_and_screenshot(dev_id, prg_path, img_path, res_info)
                    if captured:
                        val_result = validate_layout(img_path, [1, 2, 3, 4, 5, 6])
                res = dict(w)
                res["pass_name"] = w["name"]
                res["current_img"] = img_path if captured else None
                res["zones_img"] = val_result["annotated_path"] if captured else None
                res["passed"] = val_result["pass"]
                res["issues"] = val_result["issues"]
                results.append(res)

    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Perpex Layout Validation Test Harness")
    parser.add_argument("--device", help="Run only on a specific device (e.g. fenix7, venu2, venusq2)")
    parser.add_argument("--full", action="store_true", help="Run full 21 passes on every device instead of 48-pass matrix")
    args = parser.parse_args()

    branch = get_current_branch()
    safe_branch = sanitise_branch(branch)
    output_dir = f"test_output/{safe_branch}"
    os.makedirs(output_dir, exist_ok=True)

    target_devices = DEVICES
    if args.device:
        target_devices = [d for d in DEVICES if d[0] == args.device]
        if not target_devices:
            print(f"❌ Unknown device '{args.device}'. Choose from: {[d[0] for d in DEVICES]}")
            return

    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  🎨  PERPEX FOCUSED LAYOUT VALIDATION MATRIX                     ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"  Branch  : {branch}")
    print(f"  Output  : {output_dir}")
    print(f"  Devices : {len(target_devices)} ({', '.join(d[0] for d in target_devices)})")
    if args.full:
        print(f"  Mode    : FULL EXHAUSTIVE (21 passes per device)")
    else:
        print(f"  Mode    : FOCUSED RESOLUTION MATRIX (~48 total passes across all devices)")
    print()

    from test_ui.config_manager import backup_properties, restore_properties
    backup_properties()
    all_results = []

    try:
        for dev_id, res_info, dev_name in target_devices:
            print(f"\n📱 {dev_name} ({res_info})")
            dev_results = run_device_passes(dev_id, dev_name, res_info, output_dir, full_mode=args.full)
            all_results.append((dev_id, res_info, dev_name, dev_results))
    finally:
        restore_properties()

    generate_report(all_results, branch)

    # Summary
    total  = sum(len(r[3]) for r in all_results)
    passed = sum(
        1 for _, _, _, results in all_results
        for r in results if r.get("passed")
    )
    failed = total - passed

    print()
    print("╔════════════════════════════════════════════════════════════════════════════════╗")
    print(f"║  ✅ {passed}/{total} passed   ❌ {failed} failed")
    print(f"║  Report → {REPORT_PATH}")
    print("╚════════════════════════════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
