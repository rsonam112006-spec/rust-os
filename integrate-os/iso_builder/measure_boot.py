#!/usr/bin/env python3
"""
Integrate OS — Automated Boot Time Measurement Tool
Extracts real, uninvented startup timing across all kernel and systemd layers.
"""

import subprocess
import json
import re

def get_boot_metrics():
    metrics = {}
    
    # 1. Systemd Analyze Summary
    try:
        res = subprocess.check_output(["systemd-analyze"], text=True)
        # Typical output: "Startup finished in 1.525s (userspace)"
        match = re.search(r"Startup finished in ([0-9.]+s)?\s*\(?([a-z]+)?\)?\s*\+?\s*([0-9.]+s)?\s*\(?([a-z]+)?\)?", res)
        metrics["systemd_summary"] = res.strip()
    except Exception as e:
        metrics["systemd_summary"] = str(e)

    # 2. Top Blame Services
    try:
        blame_res = subprocess.check_output(["systemd-analyze", "blame"], text=True)
        top_services = [line.strip() for line in blame_res.strip().split("\n")[:10]]
        metrics["top_services"] = top_services
    except Exception as e:
        metrics["top_services"] = []

    # 3. Kernel handoff timestamp from dmesg
    try:
        dmesg_res = subprocess.check_output(["dmesg"], text=True)
        for line in dmesg_res.split("\n"):
            if "Run /init as init process" in line or "Freeing unused kernel image" in line:
                match = re.search(r"\[\s*([0-9.]+)\]", line)
                if match:
                    metrics["kernel_init_time_sec"] = float(match.group(1))
                    break
    except Exception as e:
        metrics["kernel_init_time_sec"] = None

    return metrics

if __name__ == "__main__":
    print("==========================================================")
    print("      INTEGRATE OS — BOOT TIME TELEMETRY COLLECTOR        ")
    print("==========================================================")
    data = get_boot_metrics()
    print(f"[*] Kernel Initialization Time : {data.get('kernel_init_time_sec', 'N/A')} seconds")
    print(f"[*] Userspace Startup Metric   : {data.get('systemd_summary')}")
    print("\n[*] Top Startup Services:")
    for svc in data.get("top_services", []):
        print(f"    - {svc}")
    print("==========================================================")
