#!/usr/bin/env python3
"""
Integrate OS — Research Graph & Visualization Generator
Generates publication-quality SVG charts comparing FIFO, LRU, Optimal, Second Chance, and Clock
under Temporal, Spatial, Sequential, Random, and Mixed Locality.
"""

import os
import math

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "integrate-os", "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

# 1. Generate Multi-Algorithm Page Fault Comparison by Workload (Bar Chart)
def generate_workload_bar_chart():
    # Data: Page faults for 3 frames across 5 workloads (20 references total)
    # Workloads: Temporal, Spatial, Sequential, Random, Mixed
    algorithms = ["Optimal", "LRU", "Second Chance", "Clock", "FIFO"]
    colors = ["#22c55e", "#3b82f6", "#a855f7", "#eab308", "#ef4444"]
    
    # Faults with 3 frames
    data = {
        "Optimal":       [3,  12, 20, 16, 12],
        "LRU":           [3,  12, 20, 19, 18],
        "Second Chance": [3,  12, 20, 19, 18],
        "Clock":         [3,  12, 20, 19, 18],
        "FIFO":          [3,  12, 20, 19, 18],
    }
    workloads = ["Temporal", "Spatial", "Sequential", "Random", "Mixed"]
    
    width = 800
    height = 420
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg.append('<rect width="100%" height="100%" fill="#181825"/>')
    svg.append('<text x="400" y="32" font-family="Segoe UI, sans-serif" font-size="18" font-weight="bold" fill="#cdd6f4" text-anchor="middle">Page Fault Count by Memory Locality Pattern (3 Frames, 20 Refs)</text>')
    
    # Legend
    leg_x = 180
    for i, algo in enumerate(algorithms):
        lx = leg_x + (i * 105)
        svg.append(f'<rect x="{lx}" y="50" width="12" height="12" rx="2" fill="{colors[i]}"/>')
        svg.append(f'<text x="{lx+18}" y="61" font-family="Segoe UI, sans-serif" font-size="11" fill="#a6adc8">{algo}</text>')

    # Chart Area
    origin_x = 70
    origin_y = 340
    plot_w = 680
    plot_h = 240
    
    # Y Axis Grid (0 to 20 faults)
    for f in range(0, 25, 5):
        y = origin_y - (f * (plot_h / 20))
        svg.append(f'<line x1="{origin_x}" y1="{y}" x2="{origin_x + plot_w}" y2="{y}" stroke="#313244" stroke-width="1"/>')
        svg.append(f'<text x="{origin_x - 10}" y="{y + 4}" font-family="Segoe UI, sans-serif" font-size="11" fill="#6c7086" text-anchor="end">{f}</text>')

    # Bars
    group_width = plot_w / len(workloads)
    bar_w = 14
    for w_idx, w_name in enumerate(workloads):
        gx = origin_x + (w_idx * group_width) + (group_width - (len(algorithms) * bar_w + 4 * 4)) / 2
        for a_idx, algo in enumerate(algorithms):
            faults = data[algo][w_idx]
            bx = gx + (a_idx * (bar_w + 4))
            bh = faults * (plot_h / 20)
            by = origin_y - bh
            svg.append(f'<rect x="{bx}" y="{by}" width="{bar_w}" height="{bh}" rx="2" fill="{colors[a_idx]}"/>')
            svg.append(f'<text x="{bx + bar_w/2}" y="{by - 4}" font-family="Segoe UI, sans-serif" font-size="9" fill="#cdd6f4" text-anchor="middle">{faults}</text>')
        
        # Workload Label
        svg.append(f'<text x="{origin_x + (w_idx * group_width) + group_width/2}" y="{origin_y + 25}" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#89b4fa" text-anchor="middle">{w_name}</text>')

    svg.append(f'<text x="20" y="210" font-family="Segoe UI, sans-serif" font-size="12" fill="#a6adc8" transform="rotate(-90, 20, 210)" text-anchor="middle">Number of Page Faults (Lower is Better)</text>')
    svg.append('</svg>')
    
    out_path = os.path.join(DOCS_DIR, "page_fault_by_locality.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"[+] Generated: {out_path}")

# 2. Generate Frame Capacity Scaling Curves (3, 4, 5 Frames) for Mixed Locality
def generate_frame_scaling_chart():
    width = 750
    height = 400
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg.append('<rect width="100%" height="100%" fill="#181825"/>')
    svg.append('<text x="375" y="32" font-family="Segoe UI, sans-serif" font-size="18" font-weight="bold" fill="#cdd6f4" text-anchor="middle">Frame Allocation Scaling Effect on Page Faults (Mixed Workload)</text>')

    # Legend
    algorithms = ["Optimal", "LRU", "Second Chance", "Clock", "FIFO"]
    colors = ["#22c55e", "#3b82f6", "#a855f7", "#eab308", "#ef4444"]
    leg_x = 160
    for i, algo in enumerate(algorithms):
        lx = leg_x + (i * 105)
        svg.append(f'<circle cx="{lx+5}" cy="56" r="5" fill="{colors[i]}"/>')
        svg.append(f'<text x="{lx+16}" y="60" font-family="Segoe UI, sans-serif" font-size="11" fill="#a6adc8">{algo}</text>')

    # Data for Mixed Locality [3, 4, 5 frames]
    data = {
        "Optimal":       [12, 10, 10],
        "LRU":           [18, 16, 11],
        "Second Chance": [18, 15, 11],
        "Clock":         [18, 16, 13],
        "FIFO":          [18, 16, 13],
    }
    
    origin_x = 90
    origin_y = 330
    plot_w = 580
    plot_h = 230
    
    # Y Axis Grid (Faults 8 to 20)
    for f in range(8, 22, 2):
        y = origin_y - ((f - 8) * (plot_h / 12))
        svg.append(f'<line x1="{origin_x}" y1="{y}" x2="{origin_x + plot_w}" y2="{y}" stroke="#313244" stroke-width="1"/>')
        svg.append(f'<text x="{origin_x - 12}" y="{y + 4}" font-family="Segoe UI, sans-serif" font-size="11" fill="#6c7086" text-anchor="end">{f}</text>')

    # X Axis points for 3, 4, 5 frames
    frame_coords = [origin_x + 60, origin_x + plot_w/2, origin_x + plot_w - 60]
    frame_labels = ["3 Frames", "4 Frames", "5 Frames"]
    for i, fx in enumerate(frame_coords):
        svg.append(f'<line x1="{fx}" y1="{origin_y}" x2="{fx}" y2="{origin_y - plot_h}" stroke="#313244" stroke-dasharray="3,3"/>')
        svg.append(f'<text x="{fx}" y="{origin_y + 24}" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#89b4fa" text-anchor="middle">{frame_labels[i]}</text>')

    # Plot Lines
    for a_idx, algo in enumerate(algorithms):
        pts = []
        for f_idx, val in enumerate(data[algo]):
            px = frame_coords[f_idx]
            py = origin_y - ((val - 8) * (plot_h / 12))
            pts.append((px, py, val))
        
        # Draw polyline
        path_d = f"M {pts[0][0]} {pts[0][1]} L {pts[1][0]} {pts[1][1]} L {pts[2][0]} {pts[2][1]}"
        svg.append(f'<path d="{path_d}" fill="none" stroke="{colors[a_idx]}" stroke-width="3"/>')
        for px, py, val in pts:
            svg.append(f'<circle cx="{px}" cy="{py}" r="5" fill="{colors[a_idx]}" stroke="#181825" stroke-width="2"/>')
            svg.append(f'<text x="{px + (12 if a_idx%2==0 else -12)}" y="{py - 8}" font-family="Segoe UI, sans-serif" font-size="10" font-weight="bold" fill="{colors[a_idx]}" text-anchor="middle">{val}</text>')

    svg.append(f'<text x="25" y="210" font-family="Segoe UI, sans-serif" font-size="12" fill="#a6adc8" transform="rotate(-90, 25, 210)" text-anchor="middle">Page Faults (Lower is Better)</text>')
    svg.append('</svg>')
    
    out_path = os.path.join(DOCS_DIR, "frame_scaling_effect.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"[+] Generated: {out_path}")

# 3. Generate Belady's Anomaly Curve
def generate_belady_chart():
    width = 650
    height = 360
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">')
    svg.append('<rect width="100%" height="100%" fill="#181825"/>')
    svg.append('<text x="325" y="32" font-family="Segoe UI, sans-serif" font-size="17" font-weight="bold" fill="#f38ba8" text-anchor="middle">Belady\'s Anomaly Demonstration (FIFO vs LRU)</text>')
    svg.append('<text x="325" y="52" font-family="Segoe UI, sans-serif" font-size="11" fill="#a6adc8" text-anchor="middle">Reference Trace: [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]</text>')

    origin_x = 90
    origin_y = 290
    plot_w = 480
    plot_h = 200

    # Grid (Faults 6 to 12)
    for f in range(6, 13):
        y = origin_y - ((f - 6) * (plot_h / 6))
        svg.append(f'<line x1="{origin_x}" y1="{y}" x2="{origin_x + plot_w}" y2="{y}" stroke="#313244" stroke-width="1"/>')
        svg.append(f'<text x="{origin_x - 10}" y="{y + 4}" font-family="Segoe UI, sans-serif" font-size="11" fill="#6c7086" text-anchor="end">{f}</text>')

    x_3 = origin_x + 120
    x_4 = origin_x + plot_w - 120

    svg.append(f'<line x1="{x_3}" y1="{origin_y}" x2="{x_3}" y2="{origin_y - plot_h}" stroke="#313244" stroke-dasharray="3,3"/>')
    svg.append(f'<line x1="{x_4}" y1="{origin_y}" x2="{x_4}" y2="{origin_y - plot_h}" stroke="#313244" stroke-dasharray="3,3"/>')
    svg.append(f'<text x="{x_3}" y="{origin_y + 24}" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#89b4fa" text-anchor="middle">3 Frames</text>')
    svg.append(f'<text x="{x_4}" y="{origin_y + 24}" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#89b4fa" text-anchor="middle">4 Frames</text>')

    # FIFO: 3 frames = 9, 4 frames = 10 (Increases!)
    y_fifo_3 = origin_y - ((9 - 6) * (plot_h / 6))
    y_fifo_4 = origin_y - ((10 - 6) * (plot_h / 6))
    svg.append(f'<line x1="{x_3}" y1="{y_fifo_3}" x2="{x_4}" y2="{y_fifo_4}" stroke="#ef4444" stroke-width="4"/>')
    svg.append(f'<circle cx="{x_3}" cy="{y_fifo_3}" r="6" fill="#ef4444"/>')
    svg.append(f'<circle cx="{x_4}" cy="{y_fifo_4}" r="6" fill="#ef4444"/>')
    svg.append(f'<text x="{x_3 - 25}" y="{y_fifo_3 + 4}" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#ef4444">9 Faults</text>')
    svg.append(f'<text x="{x_4 + 25}" y="{y_fifo_4 + 4}" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#ef4444">10 Faults ⚠️</text>')
    svg.append(f'<text x="{(x_3+x_4)/2}" y="{(y_fifo_3+y_fifo_4)/2 - 14}" font-family="Segoe UI, sans-serif" font-size="11" font-weight="bold" fill="#ef4444" text-anchor="middle">FIFO Anomaly: +1 Fault</text>')

    # LRU: 3 frames = 10, 4 frames = 8 (Decreases!)
    y_lru_3 = origin_y - ((10 - 6) * (plot_h / 6))
    y_lru_4 = origin_y - ((8 - 6) * (plot_h / 6))
    svg.append(f'<line x1="{x_3}" y1="{y_lru_3}" x2="{x_4}" y2="{y_lru_4}" stroke="#3b82f6" stroke-width="4"/>')
    svg.append(f'<circle cx="{x_3}" cy="{y_lru_3}" r="6" fill="#3b82f6"/>')
    svg.append(f'<circle cx="{x_4}" cy="{y_lru_4}" r="6" fill="#3b82f6"/>')
    svg.append(f'<text x="{x_3 - 25}" y="{y_lru_3 + 4}" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#3b82f6">10 Faults</text>')
    svg.append(f'<text x="{x_4 + 25}" y="{y_lru_4 + 4}" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#3b82f6">8 Faults</text>')
    svg.append(f'<text x="{(x_3+x_4)/2}" y="{(y_lru_3+y_lru_4)/2 + 20}" font-family="Segoe UI, sans-serif" font-size="11" font-weight="bold" fill="#3b82f6" text-anchor="middle">LRU (Stack Algo): -2 Faults</text>')

    svg.append('</svg>')
    out_path = os.path.join(DOCS_DIR, "belady_anomaly_chart.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"[+] Generated: {out_path}")

if __name__ == "__main__":
    generate_workload_bar_chart()
    generate_frame_scaling_chart()
    generate_belady_chart()
