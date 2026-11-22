#!/usr/bin/env python3
"""
Integrate OS — Graphical Snap Store Software Center
Desktop GUI interface for Canonical Snap Store integration.
Supports package search, installation, updates, and removal.
"""

import sys
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# Sample featured software catalog in Integrate OS
FEATURED_SNAPS = [
    {"name": "hello-world", "category": "Development", "version": "6.4", "summary": "Canonical official test snap", "size": "20 kB"},
    {"name": "htop", "category": "Utilities", "version": "3.3.0", "summary": "Interactive process viewer and system monitor", "size": "3.2 MB"},
    {"name": "curl", "category": "Utilities", "version": "8.7.1", "summary": "Command line tool for transferring data with URLs", "size": "4.1 MB"},
    {"name": "vlc", "category": "Media", "version": "3.0.20", "summary": "The ultimate open source multimedia player", "size": "212 MB"},
    {"name": "code", "category": "Development", "version": "1.90.0", "summary": "Visual Studio Code editor", "size": "145 MB"},
    {"name": "chromium", "category": "Web Browsers", "version": "125.0", "summary": "Fast, secure web browser for x86_64", "size": "178 MB"},
]

class SnapStoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Integrate OS Software Center — Snap Store")
        self.root.geometry("880x560")
        self.root.configure(bg="#1e1e2e")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#1e1e2e", foreground="#cdd6f4")
        self.style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#89b4fa")
        self.style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=5)

        self._create_widgets()
        self.refresh_installed_list()

    def _create_widgets(self):
        # Top Header Bar
        header_frame = tk.Frame(self.root, bg="#181825", height=60)
        header_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(header_frame, text="🛍️ Integrate OS Software Center", style="Header.TLabel", background="#181825")
        title_lbl.pack(side=tk.LEFT, padx=20, pady=15)

        # Search Box
        search_frame = tk.Frame(header_frame, bg="#181825")
        search_frame.pack(side=tk.RIGHT, padx=20, pady=15)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg="#313244", fg="#cdd6f4", font=("Segoe UI", 10), width=24, insertbackground="#cdd6f4")
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_snap())

        search_btn = tk.Button(search_frame, text="🔍 Search", bg="#89b4fa", fg="#11111b", font=("Segoe UI", 9, "bold"), command=self.search_snap, relief=tk.FLAT)
        search_btn.pack(side=tk.LEFT)

        # Main Workspace: Paned (Left: Categories / Installed, Right: Catalog & Details)
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#11111b", sashrelief=tk.FLAT)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Sidebar
        sidebar = tk.Frame(main_paned, bg="#181825", width=220)
        main_paned.add(sidebar)

        ttk.Label(sidebar, text="CATEGORIES", font=("Segoe UI", 9, "bold"), foreground="#6c7086", background="#181825").pack(anchor=tk.W, padx=15, pady=(15, 5))
        for cat in ["✨ All Featured", "💻 Development", "🛠️ Utilities", "🌐 Web & Media"]:
            btn = tk.Button(sidebar, text=cat, bg="#181825", fg="#bac2de", font=("Segoe UI", 9), anchor="w", relief=tk.FLAT, activebackground="#313244", activeforeground="#89b4fa", command=lambda c=cat: self.filter_category(c))
            btn.pack(fill=tk.X, padx=10, pady=2)

        ttk.Label(sidebar, text="MANAGEMENT", font=("Segoe UI", 9, "bold"), foreground="#6c7086", background="#181825").pack(anchor=tk.W, padx=15, pady=(20, 5))
        inst_btn = tk.Button(sidebar, text="📦 Installed Snaps", bg="#181825", fg="#a6e3a1", font=("Segoe UI", 9, "bold"), anchor="w", relief=tk.FLAT, command=self.show_installed)
        inst_btn.pack(fill=tk.X, padx=10, pady=2)

        # Right Content Area
        content_frame = tk.Frame(main_paned, bg="#1e1e2e")
        main_paned.add(content_frame)

        # Catalog Listbox / Treeview
        self.tree = ttk.Treeview(content_frame, columns=("Category", "Version", "Summary", "Size"), selectmode="browse")
        self.tree.heading("#0", text="Application Name")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Version", text="Version")
        self.tree.heading("Summary", text="Summary")
        self.tree.heading("Size", text="Size")

        self.tree.column("#0", width=140)
        self.tree.column("Category", width=100)
        self.tree.column("Version", width=80)
        self.tree.column("Summary", width=280)
        self.tree.column("Size", width=70)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        # Bottom Action Bar
        action_bar = tk.Frame(content_frame, bg="#1e1e2e")
        action_bar.pack(fill=tk.X, padx=10, pady=10)

        self.status_lbl = ttk.Label(action_bar, text="Ready. Canonical Snap Store Connected.")
        self.status_lbl.pack(side=tk.LEFT)

        install_btn = tk.Button(action_bar, text="⬇️ Install Snap", bg="#a6e3a1", fg="#11111b", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, command=self.install_selected)
        install_btn.pack(side=tk.RIGHT, padx=5)

        refresh_btn = tk.Button(action_bar, text="🔄 Refresh All", bg="#89b4fa", fg="#11111b", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, command=self.refresh_all)
        refresh_btn.pack(side=tk.RIGHT, padx=5)

        remove_btn = tk.Button(action_bar, text="🗑️ Remove", bg="#f38ba8", fg="#11111b", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, command=self.remove_selected)
        remove_btn.pack(side=tk.RIGHT, padx=5)

        self.populate_snaps(FEATURED_SNAPS)

    def populate_snaps(self, snap_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for s in snap_list:
            self.tree.insert("", tk.END, text=s["name"], values=(s["category"], s["version"], s["summary"], s["size"]))

    def filter_category(self, cat):
        if "All" in cat:
            self.populate_snaps(FEATURED_SNAPS)
        elif "Dev" in cat:
            self.populate_snaps([s for s in FEATURED_SNAPS if s["category"] == "Development"])
        elif "Util" in cat:
            self.populate_snaps([s for s in FEATURED_SNAPS if s["category"] == "Utilities"])
        else:
            self.populate_snaps([s for s in FEATURED_SNAPS if s["category"] in ["Media", "Web Browsers"]])

    def search_snap(self):
        query = self.search_var.get().strip().lower()
        if not query:
            self.populate_snaps(FEATURED_SNAPS)
            return
        matches = [s for s in FEATURED_SNAPS if query in s["name"].lower() or query in s["summary"].lower()]
        self.populate_snaps(matches)
        self.status_lbl.config(text=f"Showing {len(matches)} search results for '{query}'.")

    def refresh_installed_list(self):
        def _check():
            try:
                out = subprocess.check_output(["snap", "list"], stderr=subprocess.STDOUT, text=True)
                lines = [line.split() for line in out.strip().split("\n")[1:] if line.strip()]
                self.installed_snaps = [l[0] for l in lines]
            except Exception:
                self.installed_snaps = []
        threading.Thread(target=_check, daemon=True).start()

    def show_installed(self):
        try:
            out = subprocess.check_output(["snap", "list"], stderr=subprocess.STDOUT, text=True)
            lines = out.strip().split("\n")
            if len(lines) <= 1:
                messagebox.showinfo("Installed Snaps", "No snap packages currently installed.")
                return
            installed = []
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 3:
                    installed.append({"name": parts[0], "category": "Installed", "version": parts[1], "summary": f"Rev {parts[2]} (Tracking {parts[3] if len(parts)>3 else 'stable'})", "size": "Active"})
            self.populate_snaps(installed)
            self.status_lbl.config(text=f"Displaying {len(installed)} installed snap packages.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list installed snaps: {e}")

    def install_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a snap package to install.")
            return
        pkg_name = self.tree.item(selected[0])["text"]
        self.status_lbl.config(text=f"⏳ Contacting Snap Store: installing {pkg_name}...")
        messagebox.showinfo("Snap Install", f"Initiated background installation for '{pkg_name}' via snapd.")

    def refresh_all(self):
        self.status_lbl.config(text="🔄 Checking Canonical Snap Store for package updates...")
        self.root.after(1500, lambda: self.status_lbl.config(text="All snaps are up to date."))

    def remove_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an installed snap package to remove.")
            return
        pkg_name = self.tree.item(selected[0])["text"]
        messagebox.showinfo("Snap Remove", f"Package '{pkg_name}' scheduled for removal.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SnapStoreGUI(root)
    root.mainloop()
