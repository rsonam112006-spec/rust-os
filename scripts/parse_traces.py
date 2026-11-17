#!/usr/bin/env python3
"""
scripts/parse_traces.py
CA-6 Trace Parser: Reads the VirtualBox serial log (or console log)
and extracts structured OS events, scheduling timelines, and performance data.
"""

import re
import json
import os
import sys

# Regex pattern for structured kernel log line:
# [TICK:00012] [INFO ] [SCHEDULER ] Task 2 ('NetPacket') dispatched to RUNNING
LOG_PATTERN = re.compile(
    r"\[TICK:(?P<tick>\d+)\]\s+\[(?P<level>[A-Z\s]+)\]\s+\[(?P<subsystem>[^\]]+)\]\s+(?P<message>.*)"
)

def parse_log_file(filepath):
    if not os.path.exists(filepath):
        print(f"Error: Log file not found at {filepath}")
        return None

    timeline = []
    task_events = []
    preemptions = 0
    dispatches = 0
    completions = 0
    task_stats = {}

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            match = LOG_PATTERN.search(line)
            if match:
                tick = int(match.group("tick"))
                level = match.group("level").strip()
                subsystem = match.group("subsystem").strip()
                message = match.group("message").strip()

                entry = {
                    "tick": tick,
                    "level": level,
                    "subsystem": subsystem,
                    "message": message,
                }
                timeline.append(entry)

                # Parse scheduler specific events
                if subsystem in ("SCHEDULER", "PRIO_SCHED", "AGING"):
                    if "PREEMPTION" in message or "preempted" in message:
                        preemptions += 1
                    if "Dispatched" in message or "dispatched" in message:
                        dispatches += 1
                    if "TERMINATED" in message or "completed" in message:
                        completions += 1

                    # Extract Task ID if mentioned
                    task_match = re.search(r"Task\s+(\d+)", message)
                    if task_match:
                        tid = int(task_match.group(1))
                        if tid not in task_stats:
                            task_stats[tid] = {"id": tid, "events": []}
                        task_stats[tid]["events"].append({"tick": tick, "event": message})

    metrics = {
        "total_parsed_lines": len(timeline),
        "total_ticks": timeline[-1]["tick"] if timeline else 0,
        "preemptions": preemptions,
        "dispatches": dispatches,
        "completions": completions,
        "monitored_tasks": list(task_stats.keys()),
    }

    return {"metrics": metrics, "task_stats": task_stats, "timeline": timeline}

def main():
    log_file = sys.argv[1] if len(sys.argv) > 1 else "traces/virtualbox_serial.log"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "results/metrics_summary.json"

    print(f"Parsing serial log: {log_file}")
    data = parse_log_file(log_file)

    if data:
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Metrics extracted successfully. Saved to {out_file}")
        print(f"Summary: Ticks={data['metrics']['total_ticks']}, Preemptions={data['metrics']['preemptions']}, Dispatches={data['metrics']['dispatches']}")

if __name__ == "__main__":
    main()
