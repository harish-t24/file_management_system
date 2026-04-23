import customtkinter as ctk
from tkinter import messagebox
from logic.person_ops import persons, delete_person_list
from ui.view import view_person
from ui.form import open_form
from datetime import datetime
import os
import shutil
import json


NOTIF_FILE = "data/notifications.json"

# ── THEME COLORS ─────────────────────────────────────────────────────────────
BG_DARK    = "#0f0f1a"
BG_SIDEBAR = "#13132b"
BG_CARD    = "#1a1a35"
BG_CARD2   = "#1f1f3d"
ACCENT     = "#5b6ef5"
ACCENT2    = "#7c83fd"
SUCCESS    = "#2ecc71"
WARNING    = "#f39c12"
DANGER     = "#e53935"
TEXT_PRI   = "#ffffff"
TEXT_SEC   = "#9a9ab8"
TEXT_DIM   = "#555575"
BORDER     = "#2a2a50"


# ===== LOAD / SAVE =====
def load_notifications():
    if not os.path.exists(NOTIF_FILE):
        return []
    try:
        with open(NOTIF_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_notifications(data):
    os.makedirs("data", exist_ok=True)
    with open(NOTIF_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ===== DATE HELPER =====
def get_next_dob_date(dob):
    today = datetime.now()
    day, month, year = dob.split("/")
    dob_date = datetime(today.year, int(month), int(day))
    if dob_date < today:
        dob_date = datetime(today.year + 1, int(month), int(day))
    return dob_date


# ===== STORE NOTIFICATIONS =====
def update_notifications():
    today = datetime.now()
    notifications = load_notifications()

    if not os.path.exists("data"):
        return notifications

    updated_notifications = []

    for pid in os.listdir("data"):
        file_path = os.path.join("data", pid, "data.json")
        if not os.path.exists(file_path):
            continue
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            name = data.get("Full Name", "Unknown")
            dob = data.get("Date of Birth")
            if dob:
                msg = f"{name} birthday on {dob}"
                found = False
                for n in notifications:
                    if n["msg"].startswith(name + " birthday"):
                        n["msg"] = msg
                        found = True
                        updated_notifications.append(n)
                        break
                if not found:
                    updated_notifications.append({
                        "msg": msg,
                        "date": str(today.date())
                    })
        except:
            continue

    save_notifications(updated_notifications)
    return updated_notifications


# ===== UPCOMING DOB =====
def get_upcoming_birthdays_list():
    today = datetime.now()
    upcoming = []

    if not os.path.exists("data"):
        return []

    for pid in os.listdir("data"):
        file_path = os.path.join("data", pid, "data.json")
        if not os.path.exists(file_path):
            continue
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            name = data.get("Full Name", "Unknown")
            dob = data.get("Date of Birth")
            if dob:
                next_dob = get_next_dob_date(dob)
                diff = (next_dob - today).days
                if 0 <= diff <= 7:
                    upcoming.append((name, dob, diff))
        except:
            continue

    upcoming.sort(key=lambda x: x[2])
    return upcoming


# ===== SIDEBAR BUILDER =====
def _build_sidebar(root, content, active="Dashboard"):
    sidebar = ctk.CTkFrame(content, width=185, fg_color=BG_SIDEBAR, corner_radius=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    # Logo
    logo_frame = ctk.CTkFrame(sidebar, fg_color=BG_DARK, corner_radius=0, height=56)
    logo_frame.pack(fill="x")
    logo_frame.pack_propagate(False)
    ctk.CTkLabel(
        logo_frame, text="👤 PersonMgr",
        font=ctk.CTkFont(family="Georgia", size=14, weight="bold"),
        text_color=ACCENT2
    ).pack(expand=True)

    nav_items = [
        ("🏠", "Dashboard"),
        ("➕", "Add Person"),
        ("📁", "File Ops"),
        ("🔍", "Search"),
    ]

    nav_btns = {}

    def make_click(name):
        def click():
            for n, b in nav_btns.items():
                b.configure(
                    fg_color=BG_CARD if n == name else "transparent",
                    text_color=TEXT_PRI if n == name else TEXT_SEC
                )
            if name == "Dashboard":
                show_dashboard(root, content)
            elif name == "Add Person":
                open_form(root, content, show_dashboard)
            elif name == "File Ops":
                show_file_ops(root, content)
            elif name == "Search":
                show_search_modal(root)
        return click

    ctk.CTkLabel(sidebar, text="MENU", font=ctk.CTkFont(size=9, weight="bold"),
                 text_color=TEXT_DIM).pack(anchor="w", padx=16, pady=(16, 4))

    for icon, name in nav_items:
        is_active = (name == active)
        btn = ctk.CTkButton(
            sidebar,
            text=f"  {icon}   {name}",
            anchor="w",
            fg_color=BG_CARD if is_active else "transparent",
            hover_color=BG_CARD2,
            text_color=TEXT_PRI if is_active else TEXT_SEC,
            font=ctk.CTkFont(size=13),
            height=40,
            corner_radius=8,
            border_width=0,
            command=make_click(name)
        )
        btn.pack(fill="x", padx=10, pady=2)
        nav_btns[name] = btn

    return sidebar


# ===== NOTIFICATION UI =====
def show_notifications_ui(root, content):
    for w in content.winfo_children():
        w.destroy()

    sidebar = _build_sidebar(root, content, active="Dashboard")

    main = ctk.CTkFrame(content, fg_color=BG_DARK, corner_radius=0)
    main.pack(side="left", fill="both", expand=True)

    # Topbar
    topbar = ctk.CTkFrame(main, fg_color=BG_SIDEBAR, height=56, corner_radius=0)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)
    ctk.CTkLabel(topbar, text="🔔  Notifications",
                 font=ctk.CTkFont(family="Georgia", size=18, weight="bold"),
                 text_color=TEXT_PRI).pack(side="left", padx=20)
    ctk.CTkButton(topbar, text="← Back", width=80, height=30,
                  fg_color=BG_CARD, hover_color=BG_CARD2,
                  font=ctk.CTkFont(size=12), corner_radius=8,
                  command=lambda: show_dashboard(root, content)).pack(side="right", padx=16)

    scroll = ctk.CTkScrollableFrame(main, fg_color=BG_DARK)
    scroll.pack(fill="both", expand=True, padx=20, pady=16)

    notifications = load_notifications()

    def extract_dob(n):
        try:
            dob = n["msg"].split("on ")[1]
            return get_next_dob_date(dob)
        except:
            return datetime.max

    notifications.sort(key=extract_dob)

    if not notifications:
        ctk.CTkLabel(scroll, text="No notifications 🎉",
                     text_color=TEXT_SEC, font=ctk.CTkFont(size=14)).pack(pady=40)
        return

    for n in notifications:
        card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=10)
        card.pack(fill="x", pady=5)
        ctk.CTkLabel(card, text=f"🎂  {n['msg']}",
                     font=ctk.CTkFont(size=13), text_color=TEXT_PRI,
                     anchor="w").pack(anchor="w", padx=14, pady=(10, 2))
        ctk.CTkLabel(card, text=n["date"],
                     font=ctk.CTkFont(size=11), text_color=TEXT_DIM,
                     anchor="w").pack(anchor="w", padx=14, pady=(0, 10))


# ===== FILE OPS =====
def show_file_ops(root, content):
    for w in content.winfo_children():
        w.destroy()

    _build_sidebar(root, content, active="File Ops")

    main = ctk.CTkFrame(content, fg_color=BG_DARK, corner_radius=0)
    main.pack(side="left", fill="both", expand=True)

    topbar = ctk.CTkFrame(main, fg_color=BG_SIDEBAR, height=56, corner_radius=0)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)
    ctk.CTkLabel(topbar, text="📁  File Ops",
                 font=ctk.CTkFont(family="Georgia", size=18, weight="bold"),
                 text_color=TEXT_PRI).pack(side="left", padx=20)

    scroll = ctk.CTkScrollableFrame(main, fg_color=BG_DARK)
    scroll.pack(fill="both", expand=True, padx=20, pady=16)

    # ── Upcoming Birthdays Card ───────────────────────────────────────────────
    bday_card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=12)
    bday_card.pack(fill="x", pady=8)

    bday_hdr = ctk.CTkFrame(bday_card, fg_color=BG_CARD2, corner_radius=10, height=44)
    bday_hdr.pack(fill="x")
    bday_hdr.pack_propagate(False)
    ctk.CTkLabel(bday_hdr, text="🎂   Upcoming Birthdays",
                 font=ctk.CTkFont(family="Georgia", size=14, weight="bold"),
                 text_color=TEXT_PRI).pack(side="left", padx=14)
    ctk.CTkLabel(bday_hdr, text="Next 30 days",
                 font=ctk.CTkFont(size=10), text_color=TEXT_DIM).pack(side="right", padx=14)

    all_upcoming = []
    if os.path.exists("data"):
        today = datetime.now()
        for pid in os.listdir("data"):
            fp = os.path.join("data", pid, "data.json")
            if not os.path.exists(fp):
                continue
            try:
                with open(fp) as f:
                    d = json.load(f)
                name = d.get("Full Name", "Unknown")
                dob = d.get("Date of Birth")
                if dob:
                    nxt = get_next_dob_date(dob)
                    diff = (nxt - today).days
                    if 0 <= diff <= 30:
                        all_upcoming.append((name, dob, diff))
            except:
                pass

    all_upcoming.sort(key=lambda x: x[2])

    if not all_upcoming:
        ctk.CTkLabel(bday_card, text="No birthdays in the next 30 days.",
                     text_color=TEXT_SEC, font=ctk.CTkFont(size=12)).pack(pady=16)
    else:
        for name, dob, diff in all_upcoming:
            row = ctk.CTkFrame(bday_card, fg_color="transparent", height=48)
            row.pack(fill="x", padx=14, pady=4)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text="👤", font=ctk.CTkFont(size=18), width=30).pack(side="left")
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=8)
            ctk.CTkLabel(info, text=name, font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT_PRI, anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=f"Birthday · {dob}",
                         font=ctk.CTkFont(size=10), text_color=TEXT_SEC, anchor="w").pack(anchor="w")

            if diff == 0:
                tag, tc, bg = "🎉 TODAY", SUCCESS, "#0d2a1a"
            elif diff <= 3:
                tag, tc, bg = f"In {diff}d", WARNING, "#2a1a00"
            else:
                tag, tc, bg = f"In {diff}d", ACCENT2, "#1a1a35"

            ctk.CTkLabel(row, text=tag, fg_color=bg, corner_radius=6,
                         text_color=tc, font=ctk.CTkFont(size=10, weight="bold"),
                         padx=8, pady=3).pack(side="right")

    # ── Export Card ───────────────────────────────────────────────────────────
    exp_card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=12)
    exp_card.pack(fill="x", pady=8)

    exp_hdr = ctk.CTkFrame(exp_card, fg_color=BG_CARD2, corner_radius=10, height=44)
    exp_hdr.pack(fill="x")
    exp_hdr.pack_propagate(False)
    ctk.CTkLabel(exp_hdr, text="📤   Export Data",
                 font=ctk.CTkFont(family="Georgia", size=14, weight="bold"),
                 text_color=TEXT_PRI).pack(side="left", padx=14)

    status_lbl = ctk.CTkLabel(exp_card, text="", font=ctk.CTkFont(size=11), text_color=SUCCESS)
    status_lbl.pack(anchor="w", padx=14)

    def export_json():
        all_data = []
        if os.path.exists("data"):
            for pid in os.listdir("data"):
                fp = os.path.join("data", pid, "data.json")
                if os.path.exists(fp):
                    try:
                        with open(fp) as f:
                            all_data.append(json.load(f))
                    except:
                        pass
        path = os.path.join(os.path.expanduser("~"), "persons_export.json")
        with open(path, "w") as f:
            json.dump(all_data, f, indent=2)
        status_lbl.configure(text=f"✅  Exported to {path}")

    ctk.CTkButton(exp_card, text="Export All as JSON", height=36,
                  fg_color=ACCENT, hover_color="#3a55d0",
                  font=ctk.CTkFont(size=13), corner_radius=8,
                  command=export_json).pack(padx=14, pady=(8, 14), anchor="w")


# ===== SEARCH MODAL =====
def show_search_modal(root):
    modal = ctk.CTkToplevel(root)
    modal.title("Search Files")
    modal.geometry("460x320")
    modal.resizable(False, False)
    modal.configure(fg_color=BG_CARD)
    modal.transient(root)
    modal.grab_set()
    modal.focus_force()
    modal.lift()

    hdr = ctk.CTkFrame(modal, fg_color=BG_SIDEBAR, corner_radius=0, height=46)
    hdr.pack(fill="x")
    hdr.pack_propagate(False)
    ctk.CTkLabel(hdr, text="🔍   Search Files",
                 font=ctk.CTkFont(family="Georgia", size=14, weight="bold"),
                 text_color=TEXT_PRI).pack(side="left", padx=14)
    ctk.CTkButton(hdr, text="✕", width=30, height=30, fg_color="transparent",
                  hover_color="#3a1a1a", font=ctk.CTkFont(size=13),
                  command=modal.destroy).pack(side="right", padx=8)

    row = ctk.CTkFrame(modal, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=14)
    entry = ctk.CTkEntry(row, placeholder_text="Enter file name...",
                         height=36, corner_radius=8, font=ctk.CTkFont(size=13))
    entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

    result_frame = ctk.CTkScrollableFrame(modal, fg_color=BG_DARK, corner_radius=8)
    result_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def do_search():
        for w in result_frame.winfo_children():
            w.destroy()
        q = entry.get().lower()
        found = []
        if os.path.exists("data"):
            for pid in os.listdir("data"):
                files_dir = os.path.join("data", pid, "files")
                if os.path.isdir(files_dir):
                    for fname in os.listdir(files_dir):
                        if q in fname.lower():
                            found.append((pid, fname))
        if not found:
            ctk.CTkLabel(result_frame, text="No files found.",
                         text_color=TEXT_SEC, font=ctk.CTkFont(size=12)).pack(pady=12)
        for pid, fname in found:
            item = ctk.CTkFrame(result_frame, fg_color=BG_CARD, corner_radius=6, height=32)
            item.pack(fill="x", pady=3)
            item.pack_propagate(False)
            ctk.CTkLabel(item, text=f"• {fname}  ", font=ctk.CTkFont(size=12),
                         text_color=TEXT_PRI, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(item, text=f"[{pid}]", font=ctk.CTkFont(size=10),
                         text_color=TEXT_DIM).pack(side="right", padx=10)

    ctk.CTkButton(row, text="Search", width=90, height=36,
                  fg_color=ACCENT, hover_color="#3a55d0",
                  corner_radius=8, font=ctk.CTkFont(size=13, weight="bold"),
                  command=do_search).pack(side="left")

    entry.bind("<Return>", lambda e: do_search())


# ===== DELETE =====
def delete_person(pid, refresh):
    if not messagebox.askyesno("Confirm", "Delete this person?"):
        return
    folder = os.path.join("data", pid)
    if os.path.exists(folder):
        shutil.rmtree(folder)
    delete_person_list(pid)
    refresh()


# ===== DASHBOARD =====
def show_dashboard(root, content):
    for w in content.winfo_children():
        w.destroy()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    _build_sidebar(root, content, active="Dashboard")

    # ── Main area ─────────────────────────────────────────────────────────────
    main = ctk.CTkFrame(content, fg_color=BG_DARK, corner_radius=0)
    main.pack(side="left", fill="both", expand=True)

    # ── Topbar ────────────────────────────────────────────────────────────────
    topbar = ctk.CTkFrame(main, fg_color=BG_SIDEBAR, height=56, corner_radius=0)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)

    ctk.CTkLabel(topbar, text="Dashboard",
                 font=ctk.CTkFont(family="Georgia", size=18, weight="bold"),
                 text_color=TEXT_PRI).pack(side="left", padx=20)

    right_bar = ctk.CTkFrame(topbar, fg_color="transparent")
    right_bar.pack(side="right", padx=12)

    notifications = update_notifications()
    count = len(notifications)

    ctk.CTkButton(
        right_bar, text=f"🔔  {count}",
        width=60, height=32, corner_radius=8,
        fg_color=BG_CARD, hover_color=BG_CARD2,
        font=ctk.CTkFont(size=12),
        command=lambda: show_notifications_ui(root, content)
    ).pack(side="left", padx=4)

    ctk.CTkButton(
        right_bar, text="🔍",
        width=36, height=32, corner_radius=8,
        fg_color=BG_CARD, hover_color=BG_CARD2,
        font=ctk.CTkFont(size=14),
        command=lambda: show_search_modal(root)
    ).pack(side="left", padx=4)

    # ── Body ──────────────────────────────────────────────────────────────────
    body = ctk.CTkFrame(main, fg_color=BG_DARK)
    body.pack(fill="both", expand=True, padx=20, pady=14)

    # Search bar
    search_entry = ctk.CTkEntry(
        body,
        placeholder_text="🔍  Search by name or ID...",
        height=40, corner_radius=10,
        font=ctk.CTkFont(size=13),
        fg_color=BG_CARD, border_color=BORDER
    )
    search_entry.pack(fill="x", pady=(0, 12))

    # ── Upcoming Birthday Banner ───────────────────────────────────────────────
    upcoming = get_upcoming_birthdays_list()
    if upcoming:
        name, dob, diff = upcoming[0]
        banner = ctk.CTkFrame(body, fg_color=BG_CARD, corner_radius=12)
        banner.pack(fill="x", pady=(0, 12))

        left = ctk.CTkFrame(banner, fg_color="transparent")
        left.pack(side="left", padx=16, pady=12)
        ctk.CTkLabel(left, text="🎂  Upcoming Birthday",
                     font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(anchor="w")
        ctk.CTkLabel(left, text=name,
                     font=ctk.CTkFont(family="Georgia", size=16, weight="bold"),
                     text_color=TEXT_PRI).pack(anchor="w")
        ctk.CTkLabel(left, text=f"{dob}",
                     font=ctk.CTkFont(size=12), text_color=TEXT_SEC).pack(anchor="w")

        if diff == 0:
            status, color = "🎉 TODAY!", SUCCESS
        elif diff == 1:
            status, color = "Tomorrow", WARNING
        else:
            status, color = f"In {diff} days", ACCENT2

        ctk.CTkLabel(banner, text=status,
                     font=ctk.CTkFont(family="Georgia", size=15, weight="bold"),
                     text_color=color).pack(side="right", padx=20)

    # ── Person List ───────────────────────────────────────────────────────────
    list_header = ctk.CTkFrame(body, fg_color="transparent", height=28)
    list_header.pack(fill="x")
    list_header.pack_propagate(False)
    ctk.CTkLabel(list_header, text="All Persons",
                 font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_DIM).pack(side="left")
    ctk.CTkLabel(list_header, text=f"{len(persons)} total",
                 font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(side="right")

    container = ctk.CTkScrollableFrame(body, fg_color="transparent")
    container.pack(fill="both", expand=True, pady=6)

    def display_cards(data):
        for w in container.winfo_children():
            w.destroy()

        if not data:
            empty = ctk.CTkFrame(container, fg_color=BG_CARD, corner_radius=12, height=80)
            empty.pack(fill="x", pady=8)
            ctk.CTkLabel(empty, text="No persons found",
                         text_color=TEXT_SEC, font=ctk.CTkFont(size=13)).pack(expand=True)
            return

        for pid, name in data:
            card = ctk.CTkFrame(container, fg_color=BG_CARD, corner_radius=10)
            card.pack(fill="x", pady=5)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=10)

            # Avatar circle
            av = ctk.CTkLabel(inner, text="👤",
                              font=ctk.CTkFont(size=22), width=38)
            av.pack(side="left")

            # Info
            info = ctk.CTkFrame(inner, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=10)
            ctk.CTkLabel(info, text=name,
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=TEXT_PRI, anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=f"ID: {pid}",
                         font=ctk.CTkFont(size=11),
                         text_color=TEXT_DIM, anchor="w").pack(anchor="w")

            # Buttons
            btns = ctk.CTkFrame(inner, fg_color="transparent")
            btns.pack(side="right")

            ctk.CTkButton(
                btns, text="✏  View",
                width=80, height=30, corner_radius=7,
                fg_color=BG_CARD2, hover_color="#2a2a5a",
                font=ctk.CTkFont(size=12),
                command=lambda p=pid: view_person(root, content, p, show_dashboard)
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                btns, text="🗑",
                width=34, height=30, corner_radius=7,
                fg_color="#2a0a0a", hover_color="#4a1a1a",
                font=ctk.CTkFont(size=13),
                command=lambda p=pid: delete_person(
                    p, lambda: show_dashboard(root, content))
            ).pack(side="left")

    def on_search(event=None):
        q = search_entry.get().lower()
        filtered = [(pid, name) for pid, name in persons
                    if q in pid.lower() or q in name.lower()]
        display_cards(filtered)

    search_entry.bind("<KeyRelease>", on_search)

    display_cards(persons)

    # ── Add Person Button ─────────────────────────────────────────────────────
    ctk.CTkButton(
        main, text="➕   Add Person",
        height=42, corner_radius=10,
        fg_color=SUCCESS, hover_color="#27ae60",
        font=ctk.CTkFont(size=14, weight="bold"),
        command=lambda: open_form(root, content, show_dashboard)
    ).pack(fill="x", padx=20, pady=(0, 14))
