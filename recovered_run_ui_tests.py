#!/usr/bin/env python3
import os
import subprocess
import time
from test_ui.config_manager import backup_properties, restore_properties, set_properties
from test_ui.simulator_driver import SDK_PATH, OUTPUT_DIR
from test_ui.test_permutations import run_permutation_tests
from test_ui.test_themes import run_theme_tests

REPORT_PATH = "test_output/visual_report.html"

DEVICES = [
    ("fenix7", "260x260 MIP", "Fenix 7 / FR255"),
    ("enduro3", "280x280 MIP", "Enduro 3 / Fenix 7X"),
    ("epix2pro42mm", "390x390 AMOLED", "Epix 2 Pro 42mm"),
    ("epix2", "416x416 AMOLED", "Epix Gen 2 47mm"),
    ("fenix847mm", "454x454 AMOLED", "Fenix 8 47mm"),
    ("venusq2", "320x360 AMOLED", "Venu Sq 2")
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("========================================================")
print("🎨 PERPEX VISUAL UI MODULAR TEST HARNESS")
print("========================================================")
print("Verifying UI permutations across 6 Device Resolutions...")
print("========================================================")

print("Starting Connect IQ Simulator...")
subprocess.run(["open", os.path.join(SDK_PATH, "bin", "ConnectIQ.app")])
time.sleep(10) # Give simulator time to boot up initially

report_rows = []

try:
    for dev_id, res_info, dev_name in DEVICES:
        print(f"\n📱 Generating Visual UI Snapshots for: {dev_name} ({dev_id})...")
        
        # We run the permutation passes and the theme passes
        perm_results = run_permutation_tests(dev_id, dev_name)
        theme_results = run_theme_tests(dev_id, dev_name)
        
        all_results = perm_results + theme_results
        
        # Generate HTML snippet for this device
        img_tags = ""
        for res in all_results:
            img_tags += f'''
            <div style="margin-bottom: 10px;">
                <p style="color: #94a3b8; font-size: 0.8rem; margin: 0 0 5px 0;">{res["pass_name"]}</p>
                <img src="{res["image"]}" alt="{res["pass_name"]}">
            </div>
            '''

        report_rows.append(f"""
        <div class="card">
            <h3>{dev_name}</h3>
            <p class="badge">{res_info}</p>
            <div class="img-wrapper" style="flex-direction: column; max-height: 800px; overflow-y: auto;">
                {img_tags}
            </div>
        </div>
        """)

finally:
    # Always restore original properties
    restore_properties()


# Generate HTML Visual Report
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Perpex Visual UI Testing Gallery Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 30px; margin: 0; }}
        h1 {{ text-align: center; color: #38bdf8; margin-bottom: 5px; }}
        p.sub {{ text-align: center; color: #94a3b8; margin-bottom: 30px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 25px; max-width: 1600px; margin: 0 auto; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); text-align: center; }}
        .badge {{ display: inline-block; background: #0284c7; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; margin-bottom: 15px; }}
        .img-wrapper {{ background: #000; border-radius: 8px; padding: 10px; display: flex; justify-content: flex-start; align-items: center; min-height: 250px; border: 1px solid #475569; }}
        img {{ max-width: 100%; height: auto; border-radius: 4px; display: block; margin: 0 auto; }}
    </style>
</head>
<body>
    <h1>🎨 Perpex Multi-Device Visual UI Test Gallery</h1>
    <p class="sub">Generated Visual Snapshots across Permutations & Themes on MIP & AMOLED Resolution Classes</p>
    <div class="grid">
        {"".join(report_rows)}
    </div>
</body>
</html>
"""

with open(REPORT_PATH, "w") as f:
    f.write(html_content)

print("\n========================================================")
print(f"🎉 MODULAR VISUAL UI TEST REPORT GENERATED!")
print(f"Report Location: {REPORT_PATH}")
print(f"Screenshots Directory: {OUTPUT_DIR}/")
print("========================================================")
