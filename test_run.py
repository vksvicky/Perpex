import subprocess
import time
import socket

print("Starting simulator...")
p = subprocess.Popen(["/Users/vivek/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2/bin/monkeydo", "bin/Visual_fenix7_theme2.prg", "fenix7", "-t"])

print("Waiting 10s...")
time.sleep(10)
p.kill()
