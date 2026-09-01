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


def _result_row(result):
    """Renders one test pass as an HTML row."""
    badge = _val_badge(result.get("passed"))
    curr_img_tag = _img_tag(result.get("current_img"), "Current screenshot")
    zones_img_tag = _img_tag(result.get("zones_img"), "Annotated zones")
    
    slots_html = "".join(f"<li>{s}</li>" for s in result.get("slots", []))
    
    issues_html = ""
    if result.get("issues"):
        issues_html = "<strong>Issues:</strong><ul class='issues-list'>" + "".join(f"<li>{issue}</li>" for issue in result["issues"]) + "</ul>"

    return f"""
      <tr>
        <td class="pass-name">
          <strong>{result['pass_name']}</strong><br>
          <small>{result['description']}</small><br>
          {badge}
          <ul class="slot-list">{slots_html}</ul>
          {issues_html}
        </td>
        <td class="img-cell">{curr_img_tag}</td>
        <td class="img-cell">{zones_img_tag}</td>
      </tr>"""


def generate_report(all_results: list, branch: str):
    os.makedirs("test_output", exist_ok=True)

    mode_label = f"Branch: <code>{branch}</code>"
    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    device_sections = ""
    for dev_id, res_info, dev_name, results in all_results:
        pass_rows = "".join(_result_row(r) for r in results)
        total = len(results)
        passed = sum(1 for r in results if r.get("passed"))
        failed = total - passed

        device_sections += f"""
    <section class="device-section">
      <div class="device-header">
        <h2>{dev_name}</h2>
        <span class="badge-res">{res_info}</span>
        <span class="stat">✓ {passed} passed</span>
        <span class="stat warn">❌ {failed} failed</span>
      </div>
      <table class="result-table">
        <thead><tr><th>Pass</th><th>Screenshot</th><th>Zones & Issues</th></tr></thead>
        <tbody>{pass_rows}</tbody>
      </table>
    </section>"""

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
    branch = get_current_branch()
    safe_branch = sanitise_branch(branch)

    output_dir = f"test_output/{safe_branch}"
    os.makedirs(output_dir, exist_ok=True)

    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  🎨  PERPEX LAYOUT VALIDATION TEST HARNESS                      ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"  Branch  : {branch}")
    print(f"  Mode    : LAYOUT VALIDATION")
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

            perm_results  = run_permutation_tests(dev_id, dev_name, res_info, output_dir)
            theme_results = run_theme_tests(dev_id, dev_name, res_info, output_dir)

            all_results.append((dev_id, res_info, dev_name, perm_results + theme_results))
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
