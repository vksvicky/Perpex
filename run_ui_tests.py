#!/usr/bin/env python3
"""
Perpex Visual Regression Test Harness
======================================
Usage:
  python3 run_ui_tests.py                    # Run tests on current branch
  python3 run_ui_tests.py --update-baselines # Capture new baselines (main branch only)
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
SDK_PATH     = os.path.expanduser("~/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2")
KEY_PATH     = "developer_key.der"
BASELINES_DIR = "test_output/baselines"
DIFFS_DIR     = "test_output/diffs"
REPORT_PATH   = "test_output/visual_report.html"

# ── Devices ───────────────────────────────────────────────────────────────────
DEVICES = [
    ("fenix7",      "260×260 MIP Solar",  "Fenix 7 / Fenix 9 Pro Solar 47mm"),
    ("enduro3",     "280×280 MIP Solar",  "Enduro 3 / Fenix 9 Pro Solar 51mm"),
    ("epix2pro42mm","390×390 AMOLED",     "Epix 2 Pro 42mm"),
    ("epix2",       "416×416 AMOLED",     "Epix Gen 2 47mm"),
    ("fenix847mm",  "454×454 AMOLED",     "Fenix 8 / Fenix 9 Pro 47mm"),
    ("venusq2",     "320×360 AMOLED",     "Venu Sq 2"),
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


def get_simulator_window_bounds():
    for _ in range(15):
        try:
            script = ('tell application "System Events" to tell process "simulator" '
                      'to get {position, size} of window 1')
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                parts = [int(x.strip()) for x in res.stdout.strip().split(",")]
                return parts[0], parts[1], parts[2], parts[3]
        except Exception:
            pass
        time.sleep(2)
    return None


def capture_screenshot(dev_id: str, img_path: str):
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    bounds = get_simulator_window_bounds()
    if bounds:
        x, y, w, h = bounds
        subprocess.run(["screencapture", "-R", f"{x},{y},{w},{h}", img_path])
    else:
        subprocess.run(["screencapture", "-x", "-m", img_path])


def build_and_run(dev_id: str, prg_path: str, img_path: str):
    """Compile, launch in simulator, and screenshot. Returns True on success."""
    os.makedirs("bin", exist_ok=True)
    cmd_build = [
        os.path.join(SDK_PATH, "bin/monkeyc"),
        "-f", "monkey.jungle",
        "-o", prg_path,
        "-d", dev_id,
        "-y", KEY_PATH,
    ]
    res = subprocess.run(cmd_build, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"    ❌ Build failed: {res.stderr[:200]}")
        return False

    subprocess.Popen(
        [os.path.join(SDK_PATH, "bin/monkeydo"), prg_path, dev_id],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(8)
    subprocess.run([
        "osascript", "-e",
        'tell application "System Events" to set frontmost of '
        '(first process whose name is "simulator") to true'
    ])
    time.sleep(1)
    capture_screenshot(dev_id, img_path)
    return True


# ── Baseline safety ───────────────────────────────────────────────────────────

def validate_and_confirm_baseline_update() -> bool:
    """
    Enforces the baseline update safety rules:
      1. Current branch must be 'main'
      2. User must explicitly confirm
      3. Auto-backup of existing baselines is taken regardless
    Returns True if the user confirmed and it's safe to proceed.
    """
    branch = get_current_branch()
    if branch != "main":
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  ❌  BASELINE UPDATE REJECTED                                ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print(f"║  Current branch: '{branch}'                        ")
        print("║  Baselines can only be updated from the 'main' branch.      ║")
        print("║  Switch to main and try again.                              ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        return False

    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  ⚠️   BASELINE UPDATE — MAIN BRANCH DETECTED                    ║")
    print("╠══════════════════════════════════════════════════════════════════╣")
    print("║  This will overwrite all baseline images in test_output/baselines/")
    print("║  A backup will be taken automatically before any changes.        ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    answer = input("  Are you sure you want to update the baseline images? [y/N]: ").strip().lower()
    if answer not in ("y", "yes"):
        print("  Cancelled. No baselines were modified.")
        return False

    # Auto-backup regardless
    if os.path.isdir(BASELINES_DIR):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"test_output/baselines_backup_{ts}"
        shutil.copytree(BASELINES_DIR, backup_dir)
        print(f"  ✅ Backup saved → {backup_dir}")
    else:
        print("  ℹ️  No existing baselines to back up — creating fresh.")

    return True


# ── HTML report ───────────────────────────────────────────────────────────────

def _diff_badge(diff_pct):
    if diff_pct is None:
        return '<span class="badge badge-nobase">NO BASELINE</span>'
    if diff_pct == 0.0:
        return '<span class="badge badge-pass">✓ 0% DIFF</span>'
    if diff_pct < 2.0:
        return f'<span class="badge badge-warn">⚠ {diff_pct:.1f}% DIFF</span>'
    return f'<span class="badge badge-fail">✗ {diff_pct:.1f}% DIFF</span>'


def _img_tag(path, alt=""):
    if path and os.path.exists(path):
        rel = os.path.relpath(path, "test_output")
        return f'<img src="{rel}" alt="{alt}" loading="lazy">'
    return '<div class="no-img">No image</div>'


def _result_row(result, output_dir):
    """Renders one test pass as an HTML row."""
    badge = _diff_badge(result.get("diff_pct"))
    diff_img_tag = _img_tag(result.get("diff_img"), "3-panel diff")
    slots_html = "".join(f"<li>{s}</li>" for s in result.get("slots", []))
    return f"""
      <tr>
        <td class="pass-name">
          <strong>{result['pass_name']}</strong><br>
          <small>{result['description']}</small><br>
          {badge}
          <ul class="slot-list">{slots_html}</ul>
        </td>
        <td class="diff-cell">{diff_img_tag}</td>
      </tr>"""


def generate_report(all_results: list, branch: str, update_baselines: bool):
    os.makedirs("test_output", exist_ok=True)

    mode_label = "BASELINE CAPTURE (main)" if update_baselines else f"Branch: <code>{branch}</code>"
    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    device_sections = ""
    for dev_id, res_info, dev_name, results in all_results:
        pass_rows = "".join(_result_row(r, "") for r in results)
        total = len(results)
        passed = sum(1 for r in results if r.get("diff_pct") is not None and r["diff_pct"] == 0.0)
        changed = sum(1 for r in results if r.get("diff_pct") is not None and r["diff_pct"] > 0)
        no_base = sum(1 for r in results if r.get("diff_pct") is None)

        device_sections += f"""
    <section class="device-section">
      <div class="device-header">
        <h2>{dev_name}</h2>
        <span class="badge-res">{res_info}</span>
        <span class="stat">✓ {passed} identical</span>
        <span class="stat warn">{changed} changed</span>
        <span class="stat muted">{no_base} no baseline</span>
      </div>
      <table class="result-table">
        <thead><tr><th>Pass</th><th>Diff (Baseline | Current | Diff)</th></tr></thead>
        <tbody>{pass_rows}</tbody>
      </table>
    </section>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Perpex Visual Regression Report</title>
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
    .stat.warn {{ color:#fbbf24; }}
    .stat.muted{{ color:#64748b; }}

    .result-table {{ width:100%; border-collapse:collapse; }}
    .result-table th {{ background:#0f172a; color:#7dd3fc; text-align:left;
                         padding:10px 16px; font-size:.8rem; text-transform:uppercase;
                         letter-spacing:.05em; }}
    .result-table td {{ padding:12px 16px; border-top:1px solid #1e293b; vertical-align:top; }}
    .result-table tr:hover td {{ background:#162032; }}
    .pass-name  {{ width:280px; min-width:220px; }}
    .pass-name strong {{ color:#e2e8f0; font-size:.9rem; }}
    .pass-name small  {{ color:#94a3b8; font-size:.78rem; }}
    .diff-cell  {{ }}
    .diff-cell img {{ max-width:100%; border-radius:6px; border:1px solid #334155; }}
    .no-img {{ color:#475569; font-size:.8rem; padding:20px; text-align:center; }}

    .slot-list {{ margin:6px 0 0 0; padding-left:16px; font-size:.75rem; color:#94a3b8; }}
    .slot-list li {{ margin-bottom:2px; }}

    .badge {{ display:inline-block; padding:2px 8px; border-radius:12px;
               font-size:.75rem; font-weight:700; margin-top:6px; }}
    .badge-pass   {{ background:#14532d; color:#4ade80; }}
    .badge-warn   {{ background:#713f12; color:#fbbf24; }}
    .badge-fail   {{ background:#7f1d1d; color:#f87171; }}
    .badge-nobase {{ background:#1e3a5f; color:#93c5fd; }}
  </style>
</head>
<body>
  <h1>🎨 Perpex Visual Regression Report</h1>
  <p class="meta">
    {mode_label} &nbsp;·&nbsp; {timestamp} &nbsp;·&nbsp;
    {len(all_results)} devices &nbsp;·&nbsp;
    {sum(len(r[3]) for r in all_results)} total passes
  </p>
  {device_sections}
</body>
</html>"""

    with open(REPORT_PATH, "w") as f:
        f.write(html)
    print(f"\n  📄 Report → {REPORT_PATH}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Perpex Visual Regression Test Harness")
    parser.add_argument(
        "--update-baselines", action="store_true",
        help="Capture new baselines from current branch (must be main)."
    )
    args = parser.parse_args()

    branch = get_current_branch()
    safe_branch = sanitise_branch(branch)

    update_baselines = args.update_baselines

    if update_baselines:
        if not validate_and_confirm_baseline_update():
            sys.exit(1)
        output_dir = BASELINES_DIR   # write directly into baselines
    else:
        output_dir = f"test_output/{safe_branch}"

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(DIFFS_DIR,  exist_ok=True)

    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  🎨  PERPEX VISUAL REGRESSION TEST HARNESS                      ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"  Branch  : {branch}")
    print(f"  Mode    : {'BASELINE CAPTURE' if update_baselines else 'REGRESSION TEST'}")
    print(f"  Output  : {output_dir}")
    print(f"  Devices : {len(DEVICES)}")
    print(f"  Passes  : 3 metric permutations + 3 themes + 1 low-power = 7 per device")
    print()

    # Lazy imports after sys.path is set (module runs from project root)
    from test_ui.config_manager import backup_properties, restore_properties
    from test_ui.test_permutations import run_permutation_tests
    from test_ui.test_themes import run_theme_tests

    backup_properties()
    all_results = []

    try:
        for dev_id, res_info, dev_name in DEVICES:
            print(f"\n📱 {dev_name} ({res_info})")

            perm_results  = run_permutation_tests(
                dev_id, dev_name, output_dir, BASELINES_DIR, DIFFS_DIR
            )
            theme_results = run_theme_tests(
                dev_id, dev_name, output_dir, BASELINES_DIR, DIFFS_DIR
            )

            all_results.append((dev_id, res_info, dev_name, perm_results + theme_results))
    finally:
        restore_properties()

    generate_report(all_results, branch, update_baselines)

    # Summary
    total  = sum(len(r[3]) for r in all_results)
    passed = sum(
        1 for _, _, _, results in all_results
        for r in results if r.get("diff_pct") == 0.0
    )
    changed = sum(
        1 for _, _, _, results in all_results
        for r in results if r.get("diff_pct") is not None and r["diff_pct"] > 0
    )
    no_base = sum(
        1 for _, _, _, results in all_results
        for r in results if r.get("diff_pct") is None
    )

    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print(f"║  ✅  {passed}/{total} passes identical   "
          f"⚠ {changed} changed   ℹ {no_base} no baseline")
    print(f"║  Report → {REPORT_PATH}")
    print("╚══════════════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
