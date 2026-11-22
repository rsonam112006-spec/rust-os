# scripts/redesign_windows11_exact.py
import re

with open("scripts/desktop_gui.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update Title & Colors to Windows 11 Light / Mica (Matching User Laptop Screen!)
old_colors = text[text.find("# ─── Color Palette"):text.find("class MicroOS")]
new_colors = """# ─── Color Palette (Windows 11 Light / Mica — Exact Match to User Laptop) ────
WALLPAPER_TOP    = "#E8ECEF"
WALLPAPER_MID    = "#EDF1F5"
WALLPAPER_BOT    = "#E2E7ED"
TASKBAR_BG       = "#F3F3F3"
TASKBAR_BORDER   = "#E0E0E0"
WIN_CHROME       = "#F3F3F3"
WIN_INACTIVE     = "#EBEBEB"
WIN_BORDER       = "#D5D5D5"
WIN_CONTENT_BG   = "#FFFFFF"
TEXT_PRIMARY     = "#1E1E1E"
TEXT_MUTED       = "#616161"
ACCENT_BLUE      = "#0078D4"
ACCENT_CYAN      = "#00A4EF"
ACCENT_GREEN     = "#107C41"
ACCENT_AMBER     = "#D83B01"
ACCENT_PURPLE    = "#8764B8"
WIN11_HOVER      = "#E5E5E5"
WIN11_CLOSE_HOVER= "#E81123"
SELECTION_BG     = "#CCE8FF"
BTN_CLOSE        = "#FF5F57"
BTN_MINIMIZE     = "#FFBD2E"
BTN_MAXIMIZE     = "#28C941"
BTN_INACTIVE     = "#B0B0B0"
MENUBAR_BG       = "#F3F3F3"
MENUBAR_TEXT     = "#1E1E1E"
DOCK_BG          = "#F3F3F3"
DOCK_BORDER      = "#E0E0E0"

"""
text = text.replace(old_colors, new_colors)

# Update window root background
text = text.replace('self.configure(bg=WALLPAPER_TOP)', 'self.configure(bg="#E8ECEF")')

# 2. Replace the UI block (Wallpaper, Taskbar, Start Menu, Wi-Fi Flyout, Window Factory)
p_wp = text.find("    def _build_wallpaper(self):")
p_app1 = text.find("    # ─── App 1: Network Navigator")
assert p_wp != -1, "p_wp not found"
assert p_app1 != -1, "p_app1 not found"

new_ui_block = r'''    def _build_wallpaper(self):
        self.wallpaper = tk.Canvas(self, highlightthickness=0, bd=0, bg="#E8ECEF")
        self.wallpaper.place(x=0, y=0, relwidth=1, relheight=1)
        self.wallpaper.bind("<Configure>", self._redraw_wallpaper)
        self._redraw_wallpaper(None)

    def _redraw_wallpaper(self, _event):
        self.wallpaper.delete("all")
        w = self.winfo_width() or 1280
        h = self.winfo_height() or 800
        steps = 100
        # Smooth Windows 11 light silver/mica gradient
        for i in range(steps):
            t = i / steps
            r = int(232 + (237 - 232) * t)
            g = int(236 + (241 - 236) * t)
            b = int(239 + (245 - 239) * t)
            y0 = int(i * h / steps)
            y1 = int((i + 1) * h / steps) + 1
            self.wallpaper.create_rectangle(0, y0, w, y1,
                fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

        # Central delicate Windows 11 Bloom petals in azure blues
        cx, cy = w // 2, h // 2 - 20
        petals = [
            (260, "#0078D4", "gray25"),
            (210, "#2B88D8", "gray25"),
            (160, "#00A4EF", "gray50"),
            (110, "#60CDFF", "gray50"),
            (60,  "#A4D8FD", ""),
        ]
        for r_val, color, stip in petals:
            self.wallpaper.create_oval(
                cx - r_val, cy - int(r_val * 0.72), cx + r_val, cy + int(r_val * 0.72),
                fill=color, outline="", stipple=stip
            )

    # ─── Windows 11 Light Taskbar ────────────────────────────────────────────

    def _build_taskbar(self):
        self.taskbar = tk.Frame(self, bg="#F3F3F3", height=48,
                                highlightbackground="#E0E0E0", highlightthickness=1)
        self.taskbar.place(x=0, y=self.winfo_height() - 48, relwidth=1, height=48)
        self.taskbar.lift()
        self.bind("<Configure>", self._reposition_taskbar)

        # ── Left: Weather Widget (Exact match to user's laptop photo!) ────────
        weather_frame = tk.Frame(self.taskbar, bg="#F3F3F3", cursor="hand2")
        weather_frame.pack(side=tk.LEFT, padx=12, pady=4)
        tk.Label(weather_frame, text="☀️", bg="#F3F3F3", font=("Segoe UI Emoji", 14)).pack(side=tk.LEFT, padx=(0, 6))
        w_sub = tk.Frame(weather_frame, bg="#F3F3F3")
        w_sub.pack(side=tk.LEFT)
        tk.Label(w_sub, text="24°C", bg="#F3F3F3", fg="#1E1E1E", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(w_sub, text="Sunny", bg="#F3F3F3", fg="#616161", font=("Segoe UI", 8)).pack(anchor="w")

        # ── Center: Windows 11 Start, Search, and Centered App Icons ──────────
        self.center_taskbar = tk.Frame(self.taskbar, bg="#F3F3F3")
        self.center_taskbar.place(relx=0.5, rely=0.5, anchor="center")

        # 🪟 Windows 11 Blue Start Button
        self.start_btn = tk.Label(self.center_taskbar, text="🪟", bg="#F3F3F3", fg="#0078D4",
                                  font=("Segoe UI Emoji", 16), width=3, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=2)
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.configure(bg="#E5E5E5"))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.configure(bg="#F3F3F3"))
        self.start_btn.bind("<Button-1>", lambda e: self._toggle_start_menu())

        # 🔍 Search Bar Pill (Clean white capsule with subtle border)
        search_box = tk.Frame(self.center_taskbar, bg="#FFFFFF", cursor="hand2", padx=10, pady=4,
                              highlightbackground="#D5D5D5", highlightthickness=1)
        search_box.pack(side=tk.LEFT, padx=4)
        tk.Label(search_box, text="🔍", bg="#FFFFFF", fg="#606060", font=("Segoe UI Emoji", 10)).pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(search_box, text="Search", bg="#FFFFFF", fg="#424242", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 16))
        search_box.bind("<Button-1>", lambda e: self._toggle_start_menu())

        # Centered App Icons:
        TASKBAR_APPS = [
            ("⌨", "Terminal",   self._open_terminal),
            ("🌊", "Browser",    self._open_browser),
            ("📁", "Explorer",   self._open_finder),
            ("📊", "TaskMgr",    self._open_taskmanager),
            ("🛍️", "Snap Store", self._open_snap_store),
            ("🧮", "Calc",       self._open_calculator),
            ("⚙️", "Settings",   self._open_settings),
            ("🎮", "Snake",      self._open_snake_game),
            ("👾", "Doom",       self._open_doom_viewer),
        ]

        self.taskbar_widgets = {}
        for icon, name, cmd in TASKBAR_APPS:
            col = tk.Frame(self.center_taskbar, bg="#F3F3F3", cursor="hand2", padx=4, pady=2)
            col.pack(side=tk.LEFT, padx=1)

            lbl = tk.Label(col, text=icon, bg="#F3F3F3", fg="#1E1E1E",
                           font=("Segoe UI Emoji", 16), width=2, height=1)
            lbl.pack(pady=(2, 0))

            indicator = tk.Frame(col, bg="#0078D4", height=3, width=14)
            indicator.pack(pady=(2, 1))

            def make_handler(c=cmd, col_f=col, l=lbl):
                def _enter(e): col_f.configure(bg="#E5E5E5"); l.configure(bg="#E5E5E5")
                def _leave(e): col_f.configure(bg="#F3F3F3"); l.configure(bg="#F3F3F3")
                def _click(e): c()
                col_f.bind("<Enter>", _enter)
                col_f.bind("<Leave>", _leave)
                col_f.bind("<Button-1>", _click)
                l.bind("<Button-1>", _click)
            make_handler()
            self.taskbar_widgets[name] = {"col": col, "ind": indicator}

        # ── Right: System Tray & Notification Area ────────────────────────────
        tray = tk.Frame(self.taskbar, bg="#F3F3F3")
        tray.pack(side=tk.RIGHT, padx=6)

        tk.Label(tray, text="⌃", bg="#F3F3F3", fg="#616161", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=3)

        # Language: ENG over IN (Matching user's laptop photo!)
        lang_box = tk.Frame(tray, bg="#F3F3F3", padx=2)
        lang_box.pack(side=tk.LEFT, padx=3)
        tk.Label(lang_box, text="ENG", bg="#F3F3F3", fg="#1E1E1E", font=("Segoe UI", 8, "bold")).pack(anchor="center")
        tk.Label(lang_box, text="IN", bg="#F3F3F3", fg="#616161", font=("Segoe UI", 7)).pack(anchor="center")

        # Quick Settings Cluster (Wi-Fi + Volume + Battery)
        qs_cluster = tk.Frame(tray, bg="#F3F3F3", cursor="hand2", padx=6, pady=4,
                              highlightbackground="#E0E0E0", highlightthickness=0)
        qs_cluster.pack(side=tk.LEFT, padx=3)
        self.tray_wifi_icon = tk.Label(qs_cluster, text="📶", bg="#F3F3F3", fg="#1E1E1E", font=("Segoe UI Emoji", 11))
        self.tray_wifi_icon.pack(side=tk.LEFT, padx=2)
        tk.Label(qs_cluster, text="🔊", bg="#F3F3F3", fg="#1E1E1E", font=("Segoe UI Emoji", 11)).pack(side=tk.LEFT, padx=2)
        tk.Label(qs_cluster, text="🔋", bg="#F3F3F3", fg="#1E1E1E", font=("Segoe UI Emoji", 11)).pack(side=tk.LEFT, padx=2)

        def _qs_enter(e):
            qs_cluster.configure(bg="#E5E5E5")
            for ch in qs_cluster.winfo_children(): ch.configure(bg="#E5E5E5")
        def _qs_leave(e):
            qs_cluster.configure(bg="#F3F3F3")
            for ch in qs_cluster.winfo_children(): ch.configure(bg="#F3F3F3")

        qs_cluster.bind("<Enter>", _qs_enter)
        qs_cluster.bind("<Leave>", _qs_leave)
        qs_cluster.bind("<Button-1>", lambda e: self._toggle_wifi_flyout())
        for ch in qs_cluster.winfo_children():
            ch.bind("<Button-1>", lambda e: self._toggle_wifi_flyout())

        # Two-line Digital Clock & Date
        clock_box = tk.Frame(tray, bg="#F3F3F3", padx=6)
        clock_box.pack(side=tk.LEFT, padx=2)
        self.clock_time_lbl = tk.Label(clock_box, text="15:48", bg="#F3F3F3", fg="#1E1E1E", font=("Segoe UI", 9))
        self.clock_time_lbl.pack(anchor="e")
        self.clock_date_lbl = tk.Label(clock_box, text="21-11-2026", bg="#F3F3F3", fg="#616161", font=("Segoe UI", 8))
        self.clock_date_lbl.pack(anchor="e")

        # Notification Bell
        tk.Label(tray, text="🔔", bg="#F3F3F3", fg="#1E1E1E", font=("Segoe UI Emoji", 11)).pack(side=tk.LEFT, padx=4)

        # Show Desktop Strip on far right
        show_dt = tk.Frame(tray, bg="#D5D5D5", width=2, height=32, cursor="hand2")
        show_dt.pack(side=tk.LEFT, padx=(4, 0))
        show_dt.bind("<Button-1>", lambda e: [w.place_forget() for w in self.windows_list])

    def _reposition_taskbar(self, _event=None):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        if hasattr(self, "taskbar"):
            self.taskbar.place(x=0, y=h - 48, relwidth=1, height=48)
            self.taskbar.lift()

    def _tick_clock(self):
        now = datetime.now()
        t_str = now.strftime("%H:%M")
        d_str = now.strftime("%d-%m-%Y")
        if hasattr(self, "clock_time_lbl"):
            self.clock_time_lbl.configure(text=t_str)
        if hasattr(self, "clock_date_lbl"):
            self.clock_date_lbl.configure(text=d_str)
        self.after(1000, self._tick_clock)

    # ─── Windows 11 Light Start Menu ─────────────────────────────────────────

    def _build_start_menu(self):
        self.start_menu = tk.Frame(self, bg="#FBFBFB",
                                   highlightbackground="#D0D0D0", highlightthickness=1)
        self.start_menu_w = 560
        self.start_menu_h = 520

        # Top Search Box
        s_box = tk.Frame(self.start_menu, bg="#FFFFFF", padx=10, pady=8,
                         highlightbackground="#D5D5D5", highlightthickness=1)
        s_box.pack(fill=tk.X, padx=20, pady=(20, 14))
        tk.Label(s_box, text="🔍", bg="#FFFFFF", fg="#606060", font=("Segoe UI Emoji", 11)).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(s_box, text="Type here to search", bg="#FFFFFF", fg="#888888", font=("Segoe UI", 10)).pack(side=tk.LEFT)

        # "Pinned" Header
        p_hdr = tk.Frame(self.start_menu, bg="#FBFBFB")
        p_hdr.pack(fill=tk.X, padx=24, pady=(4, 8))
        tk.Label(p_hdr, text="Pinned", bg="#FBFBFB", fg="#1E1E1E", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        all_btn = tk.Label(p_hdr, text="All apps >", bg="#FBFBFB", fg="#0078D4", font=("Segoe UI", 9), cursor="hand2")
        all_btn.pack(side=tk.RIGHT)

        # Pinned Apps 3x3 Grid
        grid_frame = tk.Frame(self.start_menu, bg="#FBFBFB")
        grid_frame.pack(fill=tk.BOTH, padx=20, pady=4)

        PINNED = [
            ("⌨", "Terminal",      self._open_terminal),
            ("🌊", "Edge Browser",  self._open_browser),
            ("📁", "File Explorer", self._open_finder),
            ("📊", "Task Manager",  self._open_taskmanager),
            ("🛍️", "Snap Store",    self._open_snap_store),
            ("🧮", "Calculator",    self._open_calculator),
            ("⚙️", "Settings",      self._open_settings),
            ("🎮", "Snake Arcade",  self._open_snake_game),
            ("👾", "Doom Micro",    self._open_doom_viewer),
        ]

        for i, (icon, name, cmd) in enumerate(PINNED):
            r = i // 3
            c = i % 3
            item = tk.Frame(grid_frame, bg="#FBFBFB", cursor="hand2", padx=8, pady=8)
            item.grid(row=r, column=c, padx=6, pady=4, sticky="nsew")

            ico_lbl = tk.Label(item, text=icon, bg="#FBFBFB", font=("Segoe UI Emoji", 20))
            ico_lbl.pack()
            txt_lbl = tk.Label(item, text=name, bg="#FBFBFB", fg="#1E1E1E", font=("Segoe UI", 9))
            txt_lbl.pack(pady=(2, 0))

            def make_pinned_click(c=cmd, f=item, l1=ico_lbl, l2=txt_lbl):
                def _e(ev): [w.configure(bg="#EAEAEA") for w in (f, l1, l2)]
                def _l(ev): [w.configure(bg="#FBFBFB") for w in (f, l1, l2)]
                def _c(ev): self._toggle_start_menu(); c()
                for w in (f, l1, l2):
                    w.bind("<Enter>", _e)
                    w.bind("<Leave>", _l)
                    w.bind("<Button-1>", _c)
            make_pinned_click()
            grid_frame.columnconfigure(c, weight=1)

        # "Recommended" Header
        r_hdr = tk.Frame(self.start_menu, bg="#FBFBFB")
        r_hdr.pack(fill=tk.X, padx=24, pady=(16, 6))
        tk.Label(r_hdr, text="Recommended", bg="#FBFBFB", fg="#1E1E1E", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)

        rec_box = tk.Frame(self.start_menu, bg="#FBFBFB")
        rec_box.pack(fill=tk.X, padx=20, pady=2)

        RECS = [
            ("📄", "welcome.txt", "Modified 2h ago"),
            ("📄", "notes.md", "Modified 3h ago"),
        ]
        for ico, title, desc in RECS:
            rf = tk.Frame(rec_box, bg="#FBFBFB", padx=6, pady=4, cursor="hand2")
            rf.pack(fill=tk.X, pady=1)
            tk.Label(rf, text=ico, bg="#FBFBFB", font=("Segoe UI Emoji", 12)).pack(side=tk.LEFT, padx=(0, 8))
            sub = tk.Frame(rf, bg="#FBFBFB")
            sub.pack(side=tk.LEFT)
            tk.Label(sub, text=title, bg="#FBFBFB", fg="#1E1E1E", font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(sub, text=desc, bg="#FBFBFB", fg="#616161", font=("Segoe UI", 8)).pack(anchor="w")

        # Bottom Profile Bar
        prof_bar = tk.Frame(self.start_menu, bg="#EFEFEF", height=50)
        prof_bar.pack(side=tk.BOTTOM, fill=tk.X)
        prof_bar.pack_propagate(False)

        user_box = tk.Frame(prof_bar, bg="#EFEFEF", padx=14, pady=6)
        user_box.pack(side=tk.LEFT)
        tk.Label(user_box, text="👤", bg="#EFEFEF", font=("Segoe UI Emoji", 14)).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(user_box, text="macha", bg="#EFEFEF", fg="#1E1E1E", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        power_btn = tk.Label(prof_bar, text="⏻", bg="#EFEFEF", fg="#1E1E1E", font=("Segoe UI", 14), cursor="hand2", padx=16)
        power_btn.pack(side=tk.RIGHT)
        power_btn.bind("<Button-1>", lambda e: self.destroy())

    def _toggle_start_menu(self):
        if not hasattr(self, "start_menu"):
            return
        if self.start_menu_visible:
            self.start_menu.place_forget()
            self.start_menu_visible = False
        else:
            if getattr(self, "wifi_flyout_visible", False):
                self._toggle_wifi_flyout()
            sw = self.winfo_width()
            sh = self.winfo_height()
            mx = (sw - self.start_menu_w) // 2
            my = sh - 48 - self.start_menu_h - 10
            self.start_menu.place(x=mx, y=my, width=self.start_menu_w, height=self.start_menu_h)
            self.start_menu.lift()
            self.start_menu_visible = True

    # ─── Windows 11 Wi-Fi Quick Settings Flyout (Exact Replica) ──────────────

    def _build_wifi_flyout(self):
        self.wifi_flyout = tk.Frame(self, bg="#FBFBFB",
                                    highlightbackground="#D0D0D0", highlightthickness=1)
        self.wifi_flyout_w = 380
        self.wifi_flyout_h = 500

        # Header: "Wi-Fi" + [ ● ON ] toggle pill
        top = tk.Frame(self.wifi_flyout, bg="#FBFBFB", height=44)
        top.pack(fill=tk.X, padx=16, pady=(14, 6))
        tk.Label(top, text="Wi-Fi", bg="#FBFBFB", fg="#1E1E1E",
                 font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)

        self.fly_power_btn = tk.Button(top, text="●  ON", bg="#0078D4", fg="#FFFFFF",
                                       font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=2,
                                       cursor="hand2", bd=0)
        self.fly_power_btn.pack(side=tk.RIGHT)

        def toggle_wifi_power():
            self.wifi_power = not self.wifi_power
            if self.wifi_power:
                self.fly_power_btn.configure(text="●  ON", bg="#0078D4", fg="#FFFFFF")
                self.wifi_connected = True
            else:
                self.fly_power_btn.configure(text="○  OFF", bg="#E0E0E0", fg="#606060")
                self.wifi_connected = False
            self._refresh_wifi_flyout()

        self.fly_power_btn.configure(command=toggle_wifi_power)

        # Connected Card (Pure White with Subtle Border)
        self.fly_conn_card = tk.Frame(self.wifi_flyout, bg="#FFFFFF", padx=12, pady=10,
                                      highlightbackground="#E2E2E2", highlightthickness=1)
        self.fly_conn_card.pack(fill=tk.X, padx=14, pady=6)

        c_top = tk.Frame(self.fly_conn_card, bg="#FFFFFF")
        c_top.pack(fill=tk.X)
        self.fly_conn_icon = tk.Label(c_top, text="📶", bg="#FFFFFF", fg="#0078D4", font=("Segoe UI Emoji", 14))
        self.fly_conn_icon.pack(side=tk.LEFT, padx=(0, 8))
        self.fly_conn_ssid = tk.Label(c_top, text=self.wifi_ssid, bg="#FFFFFF", fg="#1E1E1E",
                                      font=("Segoe UI", 11, "bold"))
        self.fly_conn_ssid.pack(side=tk.LEFT)

        self.fly_conn_sub = tk.Label(self.fly_conn_card,
                                     text=f"Connected, open  •  {self.wifi_band} (Ch {self.wifi_channel})  •  {self.wifi_signal}%",
                                     bg="#FFFFFF", fg="#107C41", font=("Segoe UI", 9))
        self.fly_conn_sub.pack(anchor="w", padx=26, pady=(2, 6))

        c_bottom = tk.Frame(self.fly_conn_card, bg="#FFFFFF")
        c_bottom.pack(fill=tk.X)
        tk.Label(c_bottom, text="Intel(R) Wi-Fi 6 AX203", bg="#FFFFFF", fg="#888888", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        self.fly_disc_btn = tk.Button(c_bottom, text="Disconnect", bg="#F4F4F4", fg="#C42B1C",
                                      font=("Segoe UI", 9), relief="flat", padx=12, pady=2, cursor="hand2", bd=1)
        self.fly_disc_btn.pack(side=tk.RIGHT)

        def _do_disconnect():
            if self.wifi_connected:
                self.wifi_connected = False
                self.fly_conn_sub.configure(text="Disconnected", fg="#C42B1C")
                self.fly_disc_btn.configure(text="Connect", fg="#0078D4")
            else:
                self.wifi_connected = True
                self.fly_conn_sub.configure(text=f"Connected, open  •  {self.wifi_band} (Ch {self.wifi_channel})  •  {self.wifi_signal}%", fg="#107C41")
                self.fly_disc_btn.configure(text="Disconnect", fg="#C42B1C")
            self._refresh_wifi_flyout()

        self.fly_disc_btn.configure(command=_do_disconnect)

        # "Available networks" Header
        tk.Label(self.wifi_flyout, text="Available networks", bg="#FBFBFB", fg="#616161",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16, pady=(10, 4))

        # Scrollable networks frame
        canvas = tk.Canvas(self.wifi_flyout, bg="#FBFBFB", highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(self.wifi_flyout, orient="vertical", command=canvas.yview)
        self.fly_net_list = tk.Frame(canvas, bg="#FBFBFB")

        self.fly_net_list.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        c_win = canvas.create_window((0, 0), window=self.fly_net_list, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(c_win, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 0), pady=(0, 42))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 14), pady=(0, 42))

        # Bottom Bar: Scan & More Settings
        b_bar = tk.Frame(self.wifi_flyout, bg="#EFEFEF", height=38)
        b_bar.pack(side=tk.BOTTOM, fill=tk.X)
        b_bar.pack_propagate(False)

        scan_btn = tk.Button(b_bar, text="🔄  Scan for networks", bg="#EFEFEF", fg="#0078D4",
                             font=("Segoe UI", 9, "bold"), relief="flat", bd=0, cursor="hand2",
                             command=self._refresh_wifi_flyout)
        scan_btn.pack(side=tk.LEFT, padx=14, pady=6)

        adv_btn = tk.Label(b_bar, text="More Wi-Fi settings", bg="#EFEFEF", fg="#616161",
                           font=("Segoe UI", 9), cursor="hand2")
        adv_btn.pack(side=tk.RIGHT, padx=14, pady=6)
        adv_btn.bind("<Button-1>", lambda e: (self._toggle_wifi_flyout(), self._open_wifi_manager()))

    def _refresh_wifi_flyout(self):
        for widget in self.fly_net_list.winfo_children():
            widget.destroy()

        networks = self.scan_device_wifi()
        for net in networks:
            is_curr = (net["ssid"] == self.wifi_ssid and self.wifi_connected)
            row = tk.Frame(self.fly_net_list, bg="#FFFFFF", padx=10, pady=7, cursor="hand2",
                           highlightbackground="#EAEAEA", highlightthickness=1)
            row.pack(fill=tk.X, pady=2)

            ico = tk.Label(row, text=net.get("signal_icon", "📶"), bg="#FFFFFF", font=("Segoe UI Emoji", 12))
            ico.pack(side=tk.LEFT, padx=(0, 8))

            name_lbl = tk.Label(row, text=net["ssid"], bg="#FFFFFF",
                                fg="#107C41" if is_curr else "#1E1E1E",
                                font=("Segoe UI", 10, "bold" if is_curr else "normal"))
            name_lbl.pack(side=tk.LEFT)

            stat_txt = "Connected" if is_curr else f"{net.get('signal', '80%')} • {net.get('band', '5 GHz')}"
            stat_lbl = tk.Label(row, text=stat_txt, bg="#FFFFFF", fg="#616161", font=("Segoe UI", 8))
            stat_lbl.pack(side=tk.RIGHT)

            def make_row_click(s_name=net["ssid"], sec=net.get("security", "Open"), row_f=row, n_lbl=name_lbl, st_lbl=stat_lbl, i_lbl=ico):
                def _enter(ev):
                    for w in (row_f, n_lbl, st_lbl, i_lbl): w.configure(bg="#F0F4F9")
                def _leave(ev):
                    for w in (row_f, n_lbl, st_lbl, i_lbl): w.configure(bg="#FFFFFF")
                def _click(ev):
                    self.wifi_ssid = s_name
                    self.wifi_security = sec
                    self.wifi_connected = True
                    self.fly_conn_ssid.configure(text=s_name)
                    self.fly_conn_sub.configure(text=f"Connected, secured ({sec})", fg="#107C41")
                    self._refresh_wifi_flyout()
                row_f.bind("<Enter>", _enter)
                row_f.bind("<Leave>", _leave)
                row_f.bind("<Button-1>", _click)
                for w in (n_lbl, st_lbl, i_lbl):
                    w.bind("<Enter>", _enter)
                    w.bind("<Leave>", _leave)
                    w.bind("<Button-1>", _click)
            make_row_click()

    def _toggle_wifi_flyout(self):
        if not hasattr(self, "wifi_flyout"):
            return
        if self.wifi_flyout_visible:
            self.wifi_flyout.place_forget()
            self.wifi_flyout_visible = False
        else:
            if getattr(self, "start_menu_visible", False):
                self._toggle_start_menu()
            sw = self.winfo_width()
            sh = self.winfo_height()
            mx = sw - self.wifi_flyout_w - 12
            my = sh - 48 - self.wifi_flyout_h - 10
            self.wifi_flyout.place(x=mx, y=my, width=self.wifi_flyout_w, height=self.wifi_flyout_h)
            self.wifi_flyout.lift()
            self.wifi_flyout_visible = True
            self._refresh_wifi_flyout()

    # ─── Windows 11 Window Factory ───────────────────────────────────────────

    def _make_window(self, title, width, height, offset_x=80, offset_y=60):
        # Creates a floating, draggable Windows 11 Fluent Light window frame.
        stagger = len(self.windows_list) * 28
        wx = offset_x + stagger
        wy = offset_y + stagger

        win = tk.Frame(self, bg="#F3F3F3", bd=0,
                       highlightbackground="#D5D5D5", highlightthickness=1)
        win.place(x=wx, y=wy, width=width, height=height)
        win.lift()
        self.windows_list.append(win)
        self.active_window = win

        # ── Windows 11 Titlebar ─────────────────────────────────────────────
        tbar = tk.Frame(win, bg="#F3F3F3", height=34)
        tbar.pack(fill=tk.X)
        tbar.pack_propagate(False)

        # Title & App Icon on LEFT
        title_box = tk.Frame(tbar, bg="#F3F3F3")
        title_box.pack(side=tk.LEFT, padx=12)

        win.title_lbl = tk.Label(title_box, text=title, bg="#F3F3F3", fg="#1E1E1E",
                                 font=("Segoe UI", 10, "bold"))
        win.title_lbl.pack(side=tk.LEFT)

        # Windows 11 Caption Buttons on RIGHT: [ ─ ] [ □ ] [ ✕ ]
        controls_frame = tk.Frame(tbar, bg="#F3F3F3")
        controls_frame.pack(side=tk.RIGHT)

        def make_caption_btn(sym, hover_bg, hover_fg, cmd):
            lbl = tk.Label(controls_frame, text=sym, bg="#F3F3F3", fg="#404040",
                           font=("Segoe UI", 10), width=4, height=1, cursor="hand2")
            lbl.pack(side=tk.LEFT)
            lbl.bind("<Enter>", lambda e: lbl.configure(bg=hover_bg, fg=hover_fg))
            lbl.bind("<Leave>", lambda e: lbl.configure(bg="#F3F3F3", fg="#404040"))
            lbl.bind("<Button-1>", lambda e: cmd())
            return lbl

        # Minimize
        make_caption_btn("─", "#E5E5E5", "#000000", lambda: win.place_forget())
        # Maximize
        make_caption_btn("□", "#E5E5E5", "#000000", lambda: self._toggle_maximize(win))
        # Close (Windows 11 red hover)
        make_caption_btn("✕", "#E81123", "#FFFFFF", lambda: self._close_window(win))

        # ── Content Frame ─────────────────────────────────────────────────
        content = tk.Frame(win, bg="#FFFFFF")
        content.pack(fill=tk.BOTH, expand=True)

        # ── Drag logic ───────────────────────────────────────────────────
        def start_drag(e):
            self.active_window = win
            win.lift()
            self._drag_data = {"x": e.x, "y": e.y}

        def do_drag(e):
            info = win.place_info()
            nx = int(info["x"]) + (e.x - self._drag_data["x"])
            ny = int(info["y"]) + (e.y - self._drag_data["y"])
            ny = max(0, ny)
            win.place(x=nx, y=ny)

        tbar.bind("<Button-1>", start_drag)
        tbar.bind("<B1-Motion>", do_drag)
        win.title_lbl.bind("<Button-1>", start_drag)
        win.title_lbl.bind("<B1-Motion>", do_drag)

        return win, content

    def _close_window(self, win):
        if win in self.windows_list:
            win.destroy()
            self.windows_list.remove(win)

    _maximized_state = {}

    def _toggle_maximize(self, win):
        if win in self._maximized_state:
            prev = self._maximized_state.pop(win)
            win.place(x=prev["x"], y=prev["y"],
                      width=prev["w"], height=prev["h"])
        else:
            info = win.place_info()
            self._maximized_state[win] = {
                "x": int(info["x"]), "y": int(info["y"]),
                "w": int(info["width"]), "h": int(info["height"])
            }
            win.place(x=0, y=0, width=self.winfo_width(),
                      height=self.winfo_height() - 48)

'''

text = text[:p_wp] + new_ui_block + text[p_app1:]

with open("scripts/desktop_gui.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Exact Windows 11 replica successfully written to scripts/desktop_gui.py!")
