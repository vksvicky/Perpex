#!/usr/bin/env python3
"""
Perpex UI Layout Validation & Visual Regression Test Harness
=============================================================
Usage:
  python3 run_ui_tests.py                    # Run tests against baselines
  python3 run_ui_tests.py --update-baselines # Capture and update baseline images
  python3 run_ui_tests.py --device venu2s    # Test specific device
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime

# ── Paths ─────────────────────────────────────────────────────────────────────
SDK_PATH      = os.path.expanduser("~/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2")
KEY_PATH      = "developer_key.der"
REPORT_PATH   = "test_output/visual_report.html"
BASELINES_DIR = "test_output/baselines"
DIFFS_DIR     = "test_output/diffs"

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
    ("fenix9pro51mm","466×466 AMOLED",     "Fenix 9 Pro 51mm"),
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


def process_result_baseline(r, dev_id, update_baselines=False):
    pass_id = r.get("id", "")
    img_path = r.get("current_img")
    base_path = os.path.join(BASELINES_DIR, f"{dev_id}_{pass_id}.png")
    diff_path = os.path.join(DIFFS_DIR, f"{dev_id}_{pass_id}.png")

    if update_baselines:
        if img_path and os.path.exists(img_path) and r.get("passed", False):
            os.makedirs(BASELINES_DIR, exist_ok=True)
            shutil.copy2(img_path, base_path)
            print(f"    📸 [BASELINE SAVED] {base_path}")
            r["has_baseline"] = True
            r["baseline_img"] = base_path
            r["diff_img"] = None
            r["diff_pct"] = 0.0
            r["passed"] = True
        else:
            reasons = ", ".join(r.get("issues", [])) or "No valid screenshot captured"
            print(f"    ❌ [BASELINE FAILED] {dev_id}_{pass_id}: {reasons}")
            r["has_baseline"] = False
            r["baseline_img"] = None
            r["diff_img"] = None
            r["diff_pct"] = None
            r["passed"] = False
            if "issues" not in r or r["issues"] is None:
                r["issues"] = []
            if not any("CAPTURE FAILED" in iss for iss in r["issues"]):
                r["issues"].append(f"CAPTURE FAILED: {reasons}")
        return r

    has_baseline = os.path.exists(base_path)
    r["has_baseline"] = has_baseline
    r["baseline_img"] = base_path if has_baseline else None

    if "issues" not in r or r["issues"] is None:
        r["issues"] = []

    if not has_baseline:
        print(f"    ⚠️  MISSING BASELINE: {base_path} not found!")
        r["issues"].insert(0, f"MISSING BASELINE: No reference baseline found at '{base_path}'. Run './run_tests.sh ui --update-baselines' to generate.")
        r["passed"] = False
        r["diff_img"] = None
        r["diff_pct"] = None
    else:
        if img_path and os.path.exists(img_path):
            from test_ui.image_utils import make_3panel_diff
            os.makedirs(DIFFS_DIR, exist_ok=True)
            diff_res = make_3panel_diff(base_path, img_path, diff_path)
            r["diff_img"] = diff_res.get("composite_path")
            r["diff_pct"] = diff_res.get("diff_pct")
            if diff_res.get("diff_pct") is not None and diff_res["diff_pct"] > 5.0:
                r["issues"].append(f"VISUAL REGRESSION: {diff_res['diff_pct']:.2f}% pixel variance from baseline.")
                r["passed"] = False
    return r


# ── HTML report ───────────────────────────────────────────────────────────────

def _val_badge(r, update_baselines=False):
    if update_baselines:
        return '<span class="badge badge-pass">BASELINE UPDATED</span>'
    if not r.get("has_baseline", False):
        return '<span class="badge badge-nobase">⚠️ NO BASELINE</span>'
    if r.get("passed", False):
        return '<span class="badge badge-pass">✅ PASS</span>'
    return '<span class="badge badge-fail">❌ FAIL</span>'


def _img_tag(path, alt=""):
    if path and os.path.exists(path):
        rel = os.path.relpath(path, "test_output")
        return f'<img src="{rel}" alt="{alt}" loading="lazy">'
    return '<div class="no-img">No image</div>'


def _diff_cell(r):
    if not r.get("has_baseline"):
        return '<div class="no-img" style="color:#fef08a; background:#291e0a; border:1px dashed #854d0e; padding:16px; border-radius:6px;">⚠️ No Baseline<br><small style="color:#94a3b8">Run with --update-baselines</small></div>'
    if r.get("diff_img") and os.path.exists(r["diff_img"]):
        diff_badge = ""
        if r.get("diff_pct") is not None:
            cls = "badge-pass" if r["diff_pct"] <= 5.0 else "badge-fail"
            diff_badge = f'<div style="margin-top:4px;"><span class="badge {cls}">{r["diff_pct"]:.2f}% diff</span></div>'
        return _img_tag(r["diff_img"], "Diff") + diff_badge
    elif r.get("baseline_img") and os.path.exists(r["baseline_img"]):
        return _img_tag(r["baseline_img"], "Baseline")
    return '<div class="no-img">No diff</div>'


def generate_report(all_results, branch, update_baselines=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    mode_label = f"branch: <code>{branch}</code>"
    if update_baselines:
        mode_label += " &nbsp;·&nbsp; <strong>BASELINE CAPTURE MODE</strong>"

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
            {_val_badge(r, update_baselines)}
            {slots_html}
            {issues_html}
          </td>
          <td class="img-cell">
            {_img_tag(img_path, pass_name)}
          </td>
          <td class="img-cell">
            {_img_tag(zones_path, pass_name + ' Zones')}
          </td>
          <td class="img-cell">
            {_diff_cell(r)}
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
            <th>Baseline Comparison (Diff)</th>
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
  <title>Perpex Visual Regression & Layout Validation Report</title>
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
    .pass-name  {{ width:260px; min-width:200px; }}
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
    .badge-nobase {{ background:#854d0e; color:#fef08a; }}
  </style>
</head>
<body>
  <h1>🎨 Perpex Visual Regression & Layout Report</h1>
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


# ── Device Test Matrix ────────────────────────────────────────────────────────

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


def run_device_passes(dev_id, dev_name, res_info, output_dir, full_mode=False, update_baselines=False):
    from test_ui.test_permutations import run_permutation_tests
    from test_ui.test_themes import run_theme_tests, THEME_PASSES, LOW_POWER_PASS
    from test_ui.test_weather import run_weather_tests, WEATHER_PASSES
    from test_ui.simulator_driver import build_app, launch_simulator_and_screenshot
    from test_ui.layout_validator import validate_layout
    from test_ui.config_manager import set_properties

    results = []

    # 1. Permutations: always run all 3 zero-duplicate passes (Metrics 1-21)
    raw_perms = run_permutation_tests(dev_id, dev_name, res_info, output_dir)
    for p in raw_perms:
        results.append(process_result_baseline(p, dev_id, update_baselines=update_baselines))

    # 2. Themes: run full or targeted distribution
    if full_mode:
        raw_themes = run_theme_tests(dev_id, dev_name, res_info, output_dir)
        for t in raw_themes:
            results.append(process_result_baseline(t, dev_id, update_baselines=update_baselines))
        raw_weathers = run_weather_tests(dev_id, dev_name, res_info, output_dir)
        for w in raw_weathers:
            results.append(process_result_baseline(w, dev_id, update_baselines=update_baselines))
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
                val_result = {"pass": False, "issues": ["Build failed"], "annotated_path": None}
                if built:
                    captured = launch_simulator_and_screenshot(dev_id, prg_path, img_path, res_info)
                    if captured:
                        val_result = validate_layout(img_path, [1, 2, 3, 4, 5, 6])
                res = dict(p)
                res["pass_name"] = p["name"]
                res["current_img"] = img_path if captured else None
                res["zones_img"] = val_result.get("annotated_path") if captured else None
                res["passed"] = val_result.get("pass", False)
                res["issues"] = list(val_result.get("issues", []))
                results.append(process_result_baseline(res, dev_id, update_baselines=update_baselines))

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
                res["zones_img"] = val_result.get("annotated_path") if captured else None
                res["passed"] = val_result.get("pass", False)
                res["issues"] = list(val_result.get("issues", []))
                results.append(process_result_baseline(res, dev_id, update_baselines=update_baselines))

    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Perpex UI Layout Validation & Visual Regression Test Harness")
    parser.add_argument("--device", help="Run only on a specific device (e.g. fenix7, venu2s, venusq2)")
    parser.add_argument("--full", action="store_true", help="Run full 21 passes on every device instead of 48-pass matrix")
    parser.add_argument("--update-baselines", action="store_true", help="Capture and save baseline images into test_output/baselines")
    args = parser.parse_args()

    branch = get_current_branch()
    safe_branch = sanitise_branch(branch)
    output_dir = f"test_output/{safe_branch}"
    os.makedirs(output_dir, exist_ok=True)

    if args.update_baselines:
        print()
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║  📸  UPDATING VISUAL REFERENCE BASELINES                         ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        if branch != "main":
            print(f"  ℹ️  Capturing baseline references on current branch: '{branch}'")
        if os.path.isdir(BASELINES_DIR) and len(os.listdir(BASELINES_DIR)) > 0:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"test_output/baselines_backup_{ts}"
            shutil.copytree(BASELINES_DIR, backup_dir)
            print(f"  📦 Existing baselines automatically backed up → {backup_dir}")
        os.makedirs(BASELINES_DIR, exist_ok=True)

    target_devices = DEVICES
    if args.device:
        target_devices = [d for d in DEVICES if d[0] == args.device]
        if not target_devices:
            print(f"❌ Unknown device '{args.device}'. Choose from: {[d[0] for d in DEVICES]}")
            return

    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  🎨  PERPEX VISUAL VALIDATION MATRIX                             ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"  Branch  : {branch}")
    print(f"  Output  : {output_dir}")
    print(f"  Devices : {len(target_devices)} ({', '.join(d[0] for d in target_devices)})")
    if args.update_baselines:
        print(f"  Action  : CAPTURE BASELINES → {BASELINES_DIR}")
    elif args.full:
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
            dev_results = run_device_passes(
                dev_id, dev_name, res_info, output_dir,
                full_mode=args.full, update_baselines=args.update_baselines
            )
            all_results.append((dev_id, res_info, dev_name, dev_results))
    finally:
        restore_properties()

    generate_report(all_results, branch, update_baselines=args.update_baselines)

    # Summary
    total  = sum(len(r[3]) for r in all_results)
    passed = sum(
        1 for _, _, _, results in all_results
        for r in results if r.get("passed")
    )
    failed = total - passed

    print()
    print("╔════════════════════════════════════════════════════════════════════════════════╗")
    if args.update_baselines:
        print(f"║  🎉 {total} reference baselines captured & updated successfully!")
    else:
        print(f"║  {'✅' if failed == 0 else '❌'} {passed}/{total} passed   {f'❌ {failed} failed' if failed else '0 failed'}")
    print(f"║  Report → {REPORT_PATH}")
    print("╚════════════════════════════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
