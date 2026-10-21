import customtkinter as ctk
import psutil
import json
import os
import subprocess
from tkinter import filedialog, messagebox
from pathlib import Path

# ---------- Config ----------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

RULES_FILE = Path(__file__).with_name("split_rules.json")
FORCEBIND_CANDIDATES = [
    Path(__file__).with_name("ForceBindIP64.exe"),
    Path(__file__).with_name("ForceBindIP.exe"),
    Path("ForceBindIP64.exe"),
    Path("ForceBindIP.exe"),
]

# Iran Sans font (make sure the font is installed on the system)
FONT_FAMILY = "IRANSans"
FONT_NORMAL = ctk.CTkFont(family=FONT_FAMILY, size=14)
FONT_BOLD = ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold")
FONT_TITLE = ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold")
FONT_HEADER = ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold")
FONT_SMALL = ctk.CTkFont(family=FONT_FAMILY, size=13)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("EnzoArena Split Tunneling")
        self.geometry("1000x660")
        self.minsize(920, 600)

        # Data
        self.rules = self.load_rules()
        self.interfaces = self.get_interfaces()
        self.forcebind = self.find_forcebind()

        # Layout - RTL (sidebar on the right)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_main()      # left side (main content)
        self.build_sidebar()   # right side

        self.refresh_rules_list()
        self.update_status()

    # ---------- Data helpers ----------
    def get_interfaces(self):
        result = []
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()

        for name, addr_list in addrs.items():
            if name not in stats or not stats[name].isup:
                continue
            for addr in addr_list:
                if addr.family.name == "AF_INET" and not addr.address.startswith("127."):
                    result.append((name, addr.address))
                    break
        return result

    def find_forcebind(self):
        for p in FORCEBIND_CANDIDATES:
            if p.exists():
                return str(p.resolve())
        return None

    def load_rules(self):
        if RULES_FILE.exists():
            try:
                with open(RULES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def save_rules(self):
        with open(RULES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.rules, f, indent=2, ensure_ascii=False)

    # ---------- UI ----------
    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=290, corner_radius=0)
        self.sidebar.grid(row=0, column=1, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            self.sidebar,
            text="قوانین تقسیم تونل",
            font=FONT_TITLE,
            anchor="e"
        ).grid(row=0, column=0, padx=20, pady=(25, 6), sticky="e")

        ctk.CTkLabel(
            self.sidebar,
            text="اتصال برنامه به اینترفیس مشخص",
            font=FONT_SMALL,
            text_color=("gray70", "gray60"),
            anchor="e"
        ).grid(row=1, column=0, padx=20, pady=(0, 15), sticky="e")

        self.rules_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            label_text="قوانین ذخیره‌شده",
            label_font=FONT_NORMAL
        )
        self.rules_frame.grid(row=2, column=0, padx=15, pady=10, sticky="nsew")
        self.rules_frame.grid_columnconfigure(0, weight=1)

        self.btn_refresh = ctk.CTkButton(
            self.sidebar,
            text="بروزرسانی اینترفیس‌ها",
            font=FONT_NORMAL,
            command=self.refresh_interfaces,
            height=38
        )
        self.btn_refresh.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(
            self.sidebar,
            text="",
            font=FONT_SMALL,
            text_color=("gray60", "gray50"),
            wraplength=250,
            justify="right",
            anchor="e"
        )
        self.status_label.grid(row=6, column=0, padx=20, pady=(5, 20), sticky="e")

    def build_main(self):
        self.main = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="ایجاد قانون جدید",
            font=FONT_HEADER,
            anchor="e"
        ).grid(row=0, column=0, sticky="e")

        # Card 1 - Select App
        card1 = ctk.CTkFrame(self.main, corner_radius=14)
        card1.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        card1.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card1,
            text="انتخاب برنامه",
            font=FONT_BOLD,
            anchor="e"
        ).grid(row=0, column=0, columnspan=3, padx=20, pady=(18, 8), sticky="e")

        self.app_path_var = ctk.StringVar(value="")
        self.app_entry = ctk.CTkEntry(
            card1,
            textvariable=self.app_path_var,
            height=40,
            font=FONT_NORMAL,
            placeholder_text="مسیر فایل .exe ...",
            justify="right"
        )
        self.app_entry.grid(row=1, column=0, columnspan=2, padx=(20, 10), pady=(0, 12), sticky="ew")

        ctk.CTkButton(
            card1,
            text="انتخاب فایل",
            font=FONT_NORMAL,
            width=110,
            height=40,
            command=self.browse_exe
        ).grid(row=1, column=2, padx=(0, 20), pady=(0, 12))

        ctk.CTkButton(
            card1,
            text="انتخاب از برنامه‌های در حال اجرا",
            font=FONT_NORMAL,
            height=38,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            command=self.pick_running
        ).grid(row=2, column=0, columnspan=3, padx=20, pady=(0, 18), sticky="ew")

        # Card 2 - Select Interface
        card2 = ctk.CTkFrame(self.main, corner_radius=14)
        card2.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        card2.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card2,
            text="اینترفیس شبکه",
            font=FONT_BOLD,
            anchor="e"
        ).grid(row=0, column=0, padx=20, pady=(18, 8), sticky="e")

        self.iface_var = ctk.StringVar()
        self.iface_menu = ctk.CTkOptionMenu(
            card2,
            variable=self.iface_var,
            height=40,
            font=FONT_NORMAL,
            dropdown_font=FONT_NORMAL,
            values=self._iface_display_list(),
            anchor="e"
        )
        self.iface_menu.grid(row=1, column=0, padx=20, pady=(0, 18), sticky="ew")

        # Action buttons
        actions = ctk.CTkFrame(self.main, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        actions.grid_columnconfigure((0, 1), weight=1)

        self.btn_add = ctk.CTkButton(
            actions,
            text="ذخیره قانون",
            font=FONT_BOLD,
            height=46,
            command=self.add_rule
        )
        self.btn_add.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        self.btn_launch = ctk.CTkButton(
            actions,
            text="اجرای فوری با اینترفیس",
            font=FONT_BOLD,
            height=46,
            fg_color="#1f6aa5",
            hover_color="#144870",
            command=self.launch_bound
        )
        self.btn_launch.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        # Info box
        info = ctk.CTkFrame(self.main, corner_radius=14, fg_color=("gray90", "gray17"))
        info.grid(row=4, column=0, sticky="ew", pady=(22, 0))

        ctk.CTkLabel(
            info,
            text="راهنما",
            font=FONT_BOLD,
            anchor="e"
        ).pack(anchor="e", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            info,
            text="• برنامه و اینترفیس را انتخاب کنید و «ذخیره قانون» را بزنید\n"
                 "• با دکمه «اجرای فوری» برنامه با اینترفیس انتخاب‌شده اجرا می‌شود\n"
                 "• بهترین عملکرد برای بازی‌ها، مرورگر و دانلودرها است\n"
                 "• برای مسیریابی مداوم برنامه‌های در حال اجرا به ابزارهای پیشرفته‌تر نیاز است",
            font=FONT_SMALL,
            justify="right",
            anchor="e",
            text_color=("gray40", "gray65")
        ).pack(anchor="e", padx=18, pady=(0, 16))

    def _iface_display_list(self):
        if not self.interfaces:
            return ["هیچ اینترفیس فعالی یافت نشد"]
        return [f"{name}  •  {ip}" for name, ip in self.interfaces]

    def refresh_interfaces(self):
        self.interfaces = self.get_interfaces()
        values = self._iface_display_list()
        self.iface_menu.configure(values=values)
        if values:
            self.iface_var.set(values[0])
        self.update_status()

    def update_status(self):
        if self.forcebind:
            txt = f"ForceBindIP پیدا شد\n{Path(self.forcebind).name}"
        else:
            txt = "ForceBindIP پیدا نشد\nفایل ForceBindIP64.exe را کنار برنامه قرار دهید"
        self.status_label.configure(text=txt)

    def refresh_rules_list(self):
        for w in self.rules_frame.winfo_children():
            w.destroy()

        if not self.rules:
            ctk.CTkLabel(
                self.rules_frame,
                text="هنوز قانونی ذخیره نشده",
                font=FONT_NORMAL,
                text_color="gray50",
                anchor="e"
            ).pack(pady=20, anchor="e")
            return

        for i, rule in enumerate(self.rules):
            row = ctk.CTkFrame(self.rules_frame, corner_radius=10)
            row.pack(fill="x", pady=5, padx=4)

            name = Path(rule["app"]).name
            iface = rule["interface_name"]
            ip = rule["ip"]

            ctk.CTkLabel(
                row,
                text=name,
                font=FONT_BOLD,
                anchor="e"
            ).pack(fill="x", padx=14, pady=(10, 2))

            ctk.CTkLabel(
                row,
                text=f"{iface}\n{ip}",
                font=FONT_SMALL,
                text_color="gray60",
                anchor="e",
                justify="right"
            ).pack(fill="x", padx=14, pady=(0, 6))

            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=(0, 10))

            ctk.CTkButton(
                btn_frame,
                text="اجرا",
                font=FONT_SMALL,
                width=75,
                height=30,
                command=lambda r=rule: self.launch_rule(r)
            ).pack(side="right", padx=3)

            ctk.CTkButton(
                btn_frame,
                text="حذف",
                font=FONT_SMALL,
                width=75,
                height=30,
                fg_color="#8B3A3A",
                hover_color="#6B2A2A",
                command=lambda idx=i: self.delete_rule(idx)
            ).pack(side="right", padx=3)

    # ---------- Actions ----------
    def browse_exe(self):
        path = filedialog.askopenfilename(
            title="انتخاب برنامه",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
        )
        if path:
            self.app_path_var.set(path)

    def pick_running(self):
        win = ctk.CTkToplevel(self)
        win.title("برنامه‌های در حال اجرا")
        win.geometry("540x500")
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="برنامه مورد نظر را انتخاب کنید",
            font=FONT_BOLD
        ).pack(pady=14)

        frame = ctk.CTkScrollableFrame(win)
        frame.pack(fill="both", expand=True, padx=15, pady=5)

        processes = []
        for p in psutil.process_iter(["pid", "name", "exe"]):
            try:
                if p.info["exe"] and p.info["name"].lower().endswith(".exe"):
                    processes.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda x: x["name"].lower())

        selected = {"path": None}

        def on_select(exe_path):
            selected["path"] = exe_path
            win.destroy()

        for proc in processes:
            name = proc["name"]
            exe = proc["exe"]
            btn = ctk.CTkButton(
                frame,
                text=f"{name}  (PID {proc['pid']})",
                font=FONT_NORMAL,
                anchor="e",
                height=34,
                fg_color="transparent",
                hover_color=("gray80", "gray25"),
                command=lambda e=exe: on_select(e)
            )
            btn.pack(fill="x", pady=2)

        ctk.CTkButton(
            win,
            text="انصراف",
            font=FONT_NORMAL,
            command=win.destroy
        ).pack(pady=14)

        self.wait_window(win)
        if selected["path"]:
            self.app_path_var.set(selected["path"])

    def add_rule(self):
        app = self.app_path_var.get().strip()
        iface_display = self.iface_var.get()

        if not app or not os.path.isfile(app):
            messagebox.showwarning("خطا", "لطفاً یک فایل .exe معتبر انتخاب کنید.")
            return
        if not iface_display or "هیچ اینترفیس" in iface_display:
            messagebox.showwarning("خطا", "هیچ اینترفیس فعالی یافت نشد.")
            return

        try:
            name, ip = iface_display.split("  •  ")
        except ValueError:
            messagebox.showerror("خطا", "مشکل در خواندن اطلاعات اینترفیس.")
            return

        rule = {
            "app": app,
            "interface_name": name.strip(),
            "ip": ip.strip()
        }

        for r in self.rules:
            if r["app"].lower() == app.lower() and r["ip"] == rule["ip"]:
                messagebox.showinfo("توجه", "این قانون قبلاً ذخیره شده است.")
                return

        self.rules.append(rule)
        self.save_rules()
        self.refresh_rules_list()
        messagebox.showinfo("موفق", f"قانون برای {Path(app).name} ذخیره شد.")

    def delete_rule(self, index):
        if 0 <= index < len(self.rules):
            del self.rules[index]
            self.save_rules()
            self.refresh_rules_list()

    def launch_bound(self):
        app = self.app_path_var.get().strip()
        iface_display = self.iface_var.get()

        if not app or not os.path.isfile(app):
            messagebox.showwarning("خطا", "ابتدا یک برنامه معتبر انتخاب کنید.")
            return
        if not self.forcebind:
            messagebox.showerror(
                "ForceBindIP پیدا نشد",
                "فایل ForceBindIP64.exe را در کنار برنامه قرار دهید.\n\n"
                "دانلود: https://r1ch.net/projects/forcebindip"
            )
            return

        try:
            _, ip = iface_display.split("  •  ")
            ip = ip.strip()
        except ValueError:
            messagebox.showerror("خطا", "مشکل در خواندن IP اینترفیس.")
            return

        self._run_forcebind(ip, app)

    def launch_rule(self, rule):
        if not self.forcebind:
            messagebox.showerror("خطا", "ForceBindIP64.exe پیدا نشد.")
            return
        self._run_forcebind(rule["ip"], rule["app"])

    def _run_forcebind(self, ip: str, app: str):
        try:
            cmd = [self.forcebind, ip, app]
            subprocess.Popen(cmd, shell=False)
            messagebox.showinfo("اجرا شد", f"برنامه {Path(app).name}\nبا اینترفیس {ip} اجرا شد.")
        except Exception as e:
            messagebox.showerror("خطا در اجرا", str(e))


if __name__ == "__main__":
    app = App()
    app.mainloop()
