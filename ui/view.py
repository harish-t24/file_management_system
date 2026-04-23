import customtkinter as ctk
from tkinter import messagebox
from logic.file_ops import load_json, save_json
from utils.helpers import simple_input
from logic.person_ops import update_person
from tkcalendar import Calendar
from datetime import datetime
import os

# ── THEME ─────────────────────────────────────────────────────────────────────
BG_DARK    = "#0f0f1a"
BG_SIDEBAR = "#13132b"
BG_CARD    = "#1a1a35"
BG_CARD2   = "#1f1f3d"
ACCENT     = "#5b6ef5"
ACCENT2    = "#7c83fd"
SUCCESS    = "#2ecc71"
TEXT_PRI   = "#ffffff"
TEXT_SEC   = "#9a9ab8"
TEXT_DIM   = "#555575"
BORDER     = "#2a2a50"


# ===== CALENDAR POPUP =====
def open_calendar(root, current_value, set_value):
    top = ctk.CTkToplevel(root)
    top.title("Select Date")
    top.geometry("300x320")
    top.transient(root)
    top.grab_set()
    top.focus_force()
    top.lift()

    cal = Calendar(top, date_pattern="dd/mm/yyyy")
    cal.pack(pady=10, fill="both", expand=True)

    try:
        day, month, year = current_value.split("/")
        cal.selection_set(datetime(int(year), int(month), int(day)))
    except:
        pass

    def select():
        set_value(cal.get_date())
        top.destroy()

    ctk.CTkButton(top, text="Select", command=select,
                  fg_color=ACCENT, hover_color="#3a55d0").pack(pady=10)


# ===== VIEW =====
def view_person(root, content, pid, show_dashboard):
    for w in content.winfo_children():
        w.destroy()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    sidebar = ctk.CTkFrame(content, width=185, fg_color=BG_SIDEBAR, corner_radius=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    logo_frame = ctk.CTkFrame(sidebar, fg_color=BG_DARK, corner_radius=0, height=56)
    logo_frame.pack(fill="x")
    logo_frame.pack_propagate(False)
    ctk.CTkLabel(logo_frame, text="👤 PersonMgr",
                 font=ctk.CTkFont(family="Georgia", size=14, weight="bold"),
                 text_color=ACCENT2).pack(expand=True)

    nav_items = [("🏠", "Dashboard"), ("➕", "Add Person"), ("📁", "File Ops"), ("🔍", "Search")]
    nav_btns = {}

    ctk.CTkLabel(sidebar, text="MENU", font=ctk.CTkFont(size=9, weight="bold"),
                 text_color=TEXT_DIM).pack(anchor="w", padx=16, pady=(16, 4))

    def make_nav(name):
        def click():
            for n, b in nav_btns.items():
                b.configure(fg_color=BG_CARD if n == name else "transparent",
                            text_color=TEXT_PRI if n == name else TEXT_SEC)
            if name == "Dashboard":
                show_dashboard(root, content)
            elif name == "Add Person":
                from ui.form import open_form
                open_form(root, content, show_dashboard)
            elif name == "File Ops":
                from ui.dashboard import show_file_ops
                show_file_ops(root, content)
            elif name == "Search":
                from ui.dashboard import show_search_modal
                show_search_modal(root)
        return click

    for icon, name in nav_items:
        btn = ctk.CTkButton(sidebar, text=f"  {icon}   {name}", anchor="w",
                            fg_color="transparent", hover_color=BG_CARD2,
                            text_color=TEXT_SEC, font=ctk.CTkFont(size=13),
                            height=40, corner_radius=8, command=make_nav(name))
        btn.pack(fill="x", padx=10, pady=2)
        nav_btns[name] = btn

    # ── Main ──────────────────────────────────────────────────────────────────
    main_frame = ctk.CTkFrame(content, fg_color=BG_DARK, corner_radius=0)
    main_frame.pack(side="left", fill="both", expand=True)

    person_folder = os.path.join("data", pid)
    file_name = os.path.join(person_folder, "data.json")
    data = load_json(file_name)

    if not data:
        messagebox.showerror("Error", "Data not found")
        return

    name_display = data.get("Full Name", pid)

    # Topbar
    topbar = ctk.CTkFrame(main_frame, fg_color=BG_SIDEBAR, height=56, corner_radius=0)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)
    ctk.CTkLabel(topbar, text=f"👤  {name_display}",
                 font=ctk.CTkFont(family="Georgia", size=18, weight="bold"),
                 text_color=TEXT_PRI).pack(side="left", padx=20)
    ctk.CTkButton(topbar, text="← Back", width=80, height=30,
                  fg_color=BG_CARD, hover_color=BG_CARD2,
                  font=ctk.CTkFont(size=12), corner_radius=8,
                  command=lambda: show_dashboard(root, content)).pack(side="right", padx=16)

    # ID badge
    info_bar = ctk.CTkFrame(main_frame, fg_color=BG_CARD, height=36, corner_radius=0)
    info_bar.pack(fill="x")
    info_bar.pack_propagate(False)
    ctk.CTkLabel(info_bar, text=f"  ID: {pid}",
                 font=ctk.CTkFont(size=11), text_color=TEXT_DIM).pack(side="left", padx=12)

    # Scrollable data
    outer = ctk.CTkFrame(main_frame, fg_color=BG_DARK)
    outer.pack(fill="both", expand=True)

    canvas = ctk.CTkCanvas(outer, bg=BG_DARK, highlightthickness=0)
    inner = ctk.CTkFrame(canvas, fg_color=BG_DARK)
    scrollbar = ctk.CTkScrollbar(outer, orientation="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=inner, anchor="nw")

    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def on_mousewheel(event):
        canvas.yview_scroll(int(-event.delta / 60), "units")

    inner.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
    inner.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    # Group fields into sections for display
    SECTION_MAP = {
        "Personal": ["Full Name", "Father's Name", "Date of Birth", "Age", "Marital Status",
                     "Spouse Name", "Nationality", "Qualification", "Height", "Weight", "Aadhaar Number"],
        "Family": ["Number of Children", "Children DOB", "Father's Age", "Mother's Age",
                   "Spouse Age", "Brother's Age", "Sister's Age"],
        "Professional": ["Employer / Business Name", "Designation", "Nature of Business", "Annual Income"],
        "Contact": ["Office Contact Number", "Mobile Number 1", "Mobile Number 2", "Email ID"],
        "Identity": ["PAN Number", "Aadhaar Number"],
        "Additional": ["Wedding Anniversary"],
        "Other": [],
    }

    displayed_keys = set()
    for keys in SECTION_MAP.values():
        displayed_keys.update(keys)

    # Collect ungrouped fields
    for k in data.keys():
        if k not in displayed_keys:
            SECTION_MAP["Other"].append(k)

    SECTION_ICONS = {
        "Personal": "👤", "Family": "👨‍👩‍👧", "Professional": "💼",
        "Contact": "📞", "Identity": "🆔", "Additional": "💍", "Other": "📋"
    }

    date_fields = ["Date of Birth", "Wedding Anniversary", "Nominee DOB", "DOB of each child"]

    padx = 20

    for sec_name, keys in SECTION_MAP.items():
        sec_data = {k: data[k] for k in keys if k in data and data[k]}
        if not sec_data:
            continue

        # Section header
        sec_hdr = ctk.CTkFrame(inner, fg_color=BG_CARD2, corner_radius=10)
        sec_hdr.pack(fill="x", padx=padx, pady=(14, 4))
        ctk.CTkLabel(sec_hdr,
                     text=f"  {SECTION_ICONS.get(sec_name, '•')}  {sec_name}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRI, anchor="w").pack(anchor="w", padx=10, pady=8)

        # Fields
        for key, value in sec_data.items():
            row = ctk.CTkFrame(inner, fg_color=BG_CARD, corner_radius=8)
            row.pack(fill="x", padx=padx, pady=3)

            ctk.CTkLabel(row, text=key,
                         width=200, anchor="w",
                         font=ctk.CTkFont(size=11), text_color=TEXT_SEC
                         ).pack(side="left", padx=14, pady=8)

            val_label = ctk.CTkLabel(row, text=str(value),
                                     font=ctk.CTkFont(size=12), text_color=TEXT_PRI,
                                     anchor="w")
            val_label.pack(side="left", padx=6, fill="x", expand=True)

            def make_edit(k, label):
                def edit_field():
                    if k in date_fields:
                        def set_date(new_val):
                            data[k] = new_val
                            save_json(file_name, data)
                            label.configure(text=new_val)
                        open_calendar(root, data.get(k, ""), set_date)
                    else:
                        new_val = simple_input(root, f"Edit {k}")
                        if new_val:
                            data[k] = new_val
                            save_json(file_name, data)
                            label.configure(text=new_val)
                            if k == "Full Name":
                                update_person(pid, new_val)
                                show_dashboard(root, content)
                return edit_field

            ctk.CTkButton(row, text="✏", width=36, height=28,
                          fg_color=BG_CARD2, hover_color="#2a2a5a",
                          corner_radius=6, font=ctk.CTkFont(size=13),
                          command=make_edit(key, val_label)
                          ).pack(side="right", padx=10, pady=6)