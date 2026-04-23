import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
from tkcalendar import Calendar
from utils.helpers import generate_id
from logic.file_ops import save_json
from logic.person_ops import add_person
import os
import shutil

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


def open_form(root, content, show_dashboard):

    # ── Clear ─────────────────────────────────────────────────────────────────
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

    def make_nav(name):
        def click():
            for n, b in nav_btns.items():
                b.configure(fg_color=BG_CARD if n == name else "transparent",
                            text_color=TEXT_PRI if n == name else TEXT_SEC)
            if name == "Dashboard":
                show_dashboard(root, content)
            elif name == "Add Person":
                open_form(root, content, show_dashboard)
            elif name == "File Ops":
                from ui.dashboard import show_file_ops
                show_file_ops(root, content)
            elif name == "Search":
                from ui.dashboard import show_search_modal
                show_search_modal(root)
        return click

    ctk.CTkLabel(sidebar, text="MENU", font=ctk.CTkFont(size=9, weight="bold"),
                 text_color=TEXT_DIM).pack(anchor="w", padx=16, pady=(16, 4))

    for icon, name in nav_items:
        is_active = (name == "Add Person")
        btn = ctk.CTkButton(sidebar, text=f"  {icon}   {name}", anchor="w",
                            fg_color=BG_CARD if is_active else "transparent",
                            hover_color=BG_CARD2,
                            text_color=TEXT_PRI if is_active else TEXT_SEC,
                            font=ctk.CTkFont(size=13), height=40, corner_radius=8,
                            command=make_nav(name))
        btn.pack(fill="x", padx=10, pady=2)
        nav_btns[name] = btn

    # Section quick-nav in sidebar
    ctk.CTkLabel(sidebar, text="SECTIONS", font=ctk.CTkFont(size=9, weight="bold"),
                 text_color=TEXT_DIM).pack(anchor="w", padx=16, pady=(16, 4))
    sec_nav_scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
    sec_nav_scroll.pack(fill="both", expand=True, padx=4)
    sec_nav_btns = {}

    # ── Main panel ────────────────────────────────────────────────────────────
    main = ctk.CTkFrame(content, fg_color=BG_DARK, corner_radius=0)
    main.pack(side="left", fill="both", expand=True)

    # Topbar
    topbar = ctk.CTkFrame(main, fg_color=BG_SIDEBAR, height=56, corner_radius=0)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)
    ctk.CTkLabel(topbar, text="➕  Add Person",
                 font=ctk.CTkFont(family="Georgia", size=18, weight="bold"),
                 text_color=TEXT_PRI).pack(side="left", padx=20)
    ctk.CTkButton(topbar, text="← Back", width=80, height=30,
                  fg_color=BG_CARD, hover_color=BG_CARD2,
                  font=ctk.CTkFont(size=12), corner_radius=8,
                  command=lambda: show_dashboard(root, content)).pack(side="right", padx=16)

    # Scroll area
    scroll = ctk.CTkScrollableFrame(main, fg_color=BG_DARK)
    scroll.pack(fill="both", expand=True, padx=20, pady=12)

    entries = {}
    section_frames = {}

    # ── Field builder ─────────────────────────────────────────────────────────
    def add(parent, label, field_type="text", options=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=4)

        ctk.CTkLabel(row, text=label,
                     font=ctk.CTkFont(size=11), text_color=TEXT_SEC,
                     anchor="w").pack(anchor="w")

        if field_type == "text":
            e = ctk.CTkEntry(row, placeholder_text=label, height=34,
                             corner_radius=7, font=ctk.CTkFont(size=12),
                             fg_color=BG_DARK, border_color=BORDER)
            e.pack(fill="x", pady=(2, 0))
            entries[label] = e

        elif field_type == "dropdown":
            var = ctk.StringVar(value=options[0] if options else "")
            dd = ctk.CTkOptionMenu(row, variable=var, values=options,
                                   height=34, corner_radius=7,
                                   fg_color=BG_CARD2, button_color=ACCENT,
                                   font=ctk.CTkFont(size=12))
            dd.pack(fill="x", pady=(2, 0))
            entries[label] = var

        elif field_type == "textarea":
            txt = ctk.CTkTextbox(row, height=90, corner_radius=7,
                                 fg_color=BG_DARK, border_color=BORDER,
                                 font=ctk.CTkFont(size=12))
            txt.pack(fill="x", pady=(2, 0))
            entries[label] = txt

        elif field_type == "date":
            container = ctk.CTkFrame(row, fg_color="transparent")
            container.pack(fill="x", pady=(2, 0))
            var = ctk.StringVar()
            entry = ctk.CTkEntry(container, textvariable=var, height=34,
                                 corner_radius=7, font=ctk.CTkFont(size=12),
                                 fg_color=BG_DARK, border_color=BORDER)
            entry.pack(side="left", fill="x", expand=True)

            def pick_date(v=var):
                top = ctk.CTkToplevel(root)
                top.title("Select Date")
                top.geometry("300x320")
                top.transient(root)
                top.grab_set()
                top.focus_force()
                top.lift()
                cal = Calendar(top, date_pattern="dd/mm/yyyy")
                cal.pack(pady=10, fill="both", expand=True)
                def select():
                    v.set(cal.get_date())
                    top.destroy()
                ctk.CTkButton(top, text="Select", command=select).pack(pady=10)

            ctk.CTkButton(container, text="📅", width=38, height=34,
                          fg_color=BG_CARD2, hover_color=ACCENT,
                          corner_radius=7, command=pick_date).pack(side="right", padx=(4, 0))
            entries[label] = var

        elif field_type == "file":
            var = ctk.StringVar()
            f_row = ctk.CTkFrame(row, fg_color="transparent")
            f_row.pack(fill="x", pady=(2, 0))
            name_lbl = ctk.CTkLabel(f_row, textvariable=var,
                                    font=ctk.CTkFont(size=11), text_color=ACCENT2,
                                    anchor="w")
            name_lbl.pack(side="left", fill="x", expand=True)

            btn = ctk.CTkButton(f_row, text="Upload", width=80, height=30,
                                fg_color=BG_CARD2, hover_color=ACCENT,
                                corner_radius=7, font=ctk.CTkFont(size=11))

            def upload(v=var, b=btn):
                f = filedialog.askopenfilename()
                if f:
                    filename = os.path.basename(f)
                    v.set(filename)
                    v.full_path = f
                    b.configure(text="✓ Done", fg_color="#0d2a1a")

            btn.configure(command=upload)
            btn.pack(side="right", padx=(4, 0))
            entries[label] = var

    # ── Section / accordion builder ───────────────────────────────────────────
    def section(title, icon=""):
        full_title = f"{icon}  {title}" if icon else title

        acc = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=12)
        acc.pack(fill="x", pady=5)

        hdr = ctk.CTkFrame(acc, fg_color=BG_CARD2, corner_radius=10, height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        toggle_lbl = ctk.CTkLabel(hdr, text="▶", font=ctk.CTkFont(size=11),
                                  text_color=ACCENT2, width=20)
        toggle_lbl.pack(side="right", padx=12)

        ctk.CTkLabel(hdr, text=full_title,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRI, anchor="w").pack(side="left", padx=14)

        body = ctk.CTkFrame(acc, fg_color="transparent")
        # Body hidden by default (collapsed)

        open_state = [False]

        def toggle(e=None):
            if open_state[0]:
                body.pack_forget()
                toggle_lbl.configure(text="▶")
            else:
                body.pack(fill="x", pady=(0, 10))
                toggle_lbl.configure(text="▼")
            open_state[0] = not open_state[0]

        hdr.bind("<Button-1>", toggle)
        toggle_lbl.bind("<Button-1>", toggle)

        section_frames[title] = acc

        # Sidebar quick-nav button
        nav_btn = ctk.CTkButton(sec_nav_scroll, text=f"{icon} {title}",
                                anchor="w", fg_color="transparent",
                                hover_color=BG_CARD, text_color=TEXT_SEC,
                                font=ctk.CTkFont(size=10), height=26, corner_radius=6)
        nav_btn.pack(fill="x", pady=1)
        sec_nav_btns[title] = nav_btn

        def scroll_to(frame=acc):
            scroll._parent_canvas.update_idletasks()
            scroll._parent_canvas.yview_moveto(
                frame.winfo_y() / max(scroll.winfo_height(), 1))

        nav_btn.configure(command=scroll_to)

        return body

    # ── All Sections ──────────────────────────────────────────────────────────

    sec = section("Personal Details", "👤")
    add(sec, "Full Name")
    add(sec, "Father's Name")
    add(sec, "Date of Birth", "date")
    add(sec, "Marital Status", "dropdown", ["Single", "Married"])
    add(sec, "Spouse Name")
    add(sec, "Nationality")
    add(sec, "Qualification")
    add(sec, "Height")
    add(sec, "Weight")
    add(sec, "Aadhaar Number")

    sec = section("Family Details", "👨‍👩‍👧")
    add(sec, "Number of Children")
    add(sec, "Children DOB", "date")
    add(sec, "Father's Age")
    add(sec, "Mother's Age")
    add(sec, "Spouse Age")
    add(sec, "Brother's Age")
    add(sec, "Sister's Age")

    sec = section("Professional Details", "💼")
    add(sec, "Employer / Business Name")
    add(sec, "Designation")
    add(sec, "Nature of Business")
    add(sec, "Annual Income")

    sec = section("Contact Details", "📞")
    add(sec, "Office Contact Number")
    add(sec, "Mobile Number 1")
    add(sec, "Mobile Number 2")
    add(sec, "Email ID")

    sec = section("Identity Details", "🆔")
    add(sec, "PAN Number")
    add(sec, "Aadhaar Number")

    sec = section("Additional Details", "💍")
    add(sec, "Wedding Anniversary", "date")

    sec = section("Nominee Details", "🧾")
    add(sec, "Nominee Relationship", "dropdown",
        ["Father", "Mother", "Spouse", "Children", "Appointee"])
    add(sec, "Nominee Name")
    add(sec, "Nominee DOB", "date")
    add(sec, "Nominee Father's Name")

    sec = section("Insurance Details", "🛡")
    for p in ["Self", "Father", "Mother", "Spouse", "Children"]:
        for f in ["Policy Number", "Sum Assured", "Year of Issue", "Company"]:
            add(sec, f"{p} {f}")

    sec = section("Health Details", "🏥")
    add(sec, "Health problems")
    add(sec, "Lifestyle habits")
    add(sec, "Pregnancy details")
    add(sec, "Other remarks")

    sec = section("Address Details", "🏠")
    add(sec, "Communication Address")
    add(sec, "Permanent Address")

    sec = section("Plan Details", "📋")
    add(sec, "Product Name")
    add(sec, "Premium")
    add(sec, "Mode", "dropdown", ["Yearly", "Half-yearly", "Quarterly"])
    add(sec, "Sum Assured")
    add(sec, "Rider")

    sec = section("Document Attachments", "📎")
    for d in ["Age Proof", "ID Proof", "Address Proof", "Photo",
              "School ID", "Form 16", "Bank Statement",
              "Bank Cheque 1", "Bank Cheque 2",
              "Proposal Form 1", "Proposal Form 2", "Visiting Card"]:
        add(sec, d, "file")

    sec = section("References", "👥")
    add(sec, "Friend's Name")
    add(sec, "Mobile Number")
    add(sec, "Age")

    sec = section("PAN & Financial Details", "🪪")
    add(sec, "PAN Number")
    add(sec, "PAN Card Copy", "file")
    add(sec, "Risk Cover")
    add(sec, "Pension Plan")
    add(sec, "Investment Plan")
    add(sec, "Mutual Fund")
    add(sec, "Mediclaim")
    add(sec, "Money Back Policy")
    add(sec, "Children's Education Plan")
    add(sec, "Reminder Date 1", "date")
    add(sec, "Reminder Date 2", "date")

    # ── Notes (always visible) ────────────────────────────────────────────────
    notes_frame = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=12)
    notes_frame.pack(fill="x", pady=5)
    ctk.CTkLabel(notes_frame, text="📝  Notes",
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color=TEXT_PRI).pack(anchor="w", padx=14, pady=(12, 4))
    notes_box = ctk.CTkTextbox(notes_frame, height=120, corner_radius=8,
                               fg_color=BG_DARK, border_color=BORDER,
                               font=ctk.CTkFont(size=12))
    notes_box.pack(fill="x", padx=14, pady=(0, 14))
    notes_box.insert("1.0", "Write notes here...")
    entries["Notes"] = notes_box

    # ── Save ──────────────────────────────────────────────────────────────────
    def save():
        data = {}
        pid = generate_id()
        person_folder = os.path.join("data", pid)
        files_folder = os.path.join(person_folder, "files")
        os.makedirs(files_folder, exist_ok=True)

        for k, v in entries.items():
            if hasattr(v, "full_path"):
                filename = os.path.basename(v.full_path)
                shutil.copy(v.full_path, os.path.join(files_folder, filename))
                data[k] = filename
            elif isinstance(v, ctk.CTkTextbox):
                data[k] = v.get("1.0", "end").strip()
            else:
                data[k] = v.get()

        data["ID"] = pid
        if "Date of Birth" in data:
            try:
                data["Age"] = datetime.now().year - int(data["Date of Birth"][:4])
            except:
                pass

        save_json(os.path.join(person_folder, "data.json"), data)
        add_person(pid, data.get("Full Name", "Unknown"))
        messagebox.showinfo("Saved", "Person Added Successfully ✅")
        show_dashboard(root, content)

    ctk.CTkButton(
        main, text="💾   Save Person",
        height=44, corner_radius=10,
        fg_color=ACCENT, hover_color="#3a55d0",
        font=ctk.CTkFont(size=14, weight="bold"),
        command=save
    ).pack(fill="x", padx=20, pady=(0, 14))
