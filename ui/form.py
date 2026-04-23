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

    ctk.CTkLabel(sidebar, text="SECTIONS", font=ctk.CTkFont(size=9, weight="bold"),
                 text_color=TEXT_DIM).pack(anchor="w", padx=16, pady=(16, 4))
    sec_nav_scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
    sec_nav_scroll.pack(fill="both", expand=True, padx=4)

    # ── Main panel ────────────────────────────────────────────────────────────
    main = ctk.CTkFrame(content, fg_color=BG_DARK, corner_radius=0)
    main.pack(side="left", fill="both", expand=True)

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

    scroll = ctk.CTkScrollableFrame(main, fg_color=BG_DARK)
    scroll.pack(fill="both", expand=True, padx=20, pady=12)

    entries = {}

    # ══════════════════════════════════════════════════════════
    # WIDGET HELPERS
    # ══════════════════════════════════════════════════════════
    def lbl(parent, text):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=11),
                     text_color=TEXT_SEC, anchor="w").pack(anchor="w", pady=(6, 1))

    def txt_entry(parent, placeholder, key):
        e = ctk.CTkEntry(parent, placeholder_text=placeholder, height=32,
                         corner_radius=7, font=ctk.CTkFont(size=12),
                         fg_color=BG_DARK, border_color=BORDER)
        e.pack(fill="x", pady=(0, 4))
        entries[key] = e

    def ddmenu(parent, key, values):
        var = ctk.StringVar(value=values[0])
        ctk.CTkOptionMenu(parent, variable=var, values=values,
                          height=32, corner_radius=7,
                          fg_color=BG_CARD2, button_color=ACCENT,
                          font=ctk.CTkFont(size=12)).pack(fill="x", pady=(0, 4))
        entries[key] = var

    def date_pick(parent, key):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 4))
        var = ctk.StringVar()
        ctk.CTkEntry(row, textvariable=var, height=32, corner_radius=7,
                     font=ctk.CTkFont(size=12), fg_color=BG_DARK,
                     border_color=BORDER, placeholder_text="DD/MM/YYYY").pack(
            side="left", fill="x", expand=True)
        def pick(v=var):
            top = ctk.CTkToplevel(root)
            top.title("Select Date")
            top.geometry("300x320")
            top.transient(root); top.grab_set(); top.focus_force(); top.lift()
            cal = Calendar(top, date_pattern="dd/mm/yyyy")
            cal.pack(pady=10, fill="both", expand=True)
            ctk.CTkButton(top, text="Select", fg_color=ACCENT,
                          command=lambda: [v.set(cal.get_date()), top.destroy()]).pack(pady=10)
        ctk.CTkButton(row, text="📅", width=36, height=32,
                      fg_color=BG_CARD2, hover_color=ACCENT,
                      corner_radius=7, command=pick).pack(side="right", padx=(4, 0))
        entries[key] = var

    def two_col(parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", pady=2)
        L = ctk.CTkFrame(f, fg_color="transparent")
        L.pack(side="left", fill="x", expand=True, padx=(0, 4))
        R = ctk.CTkFrame(f, fg_color="transparent")
        R.pack(side="left", fill="x", expand=True, padx=(4, 0))
        return L, R

    def col_entry(col, lbl_text, key):
        ctk.CTkLabel(col, text=lbl_text, font=ctk.CTkFont(size=11),
                     text_color=TEXT_SEC, anchor="w").pack(anchor="w")
        e = ctk.CTkEntry(col, placeholder_text=lbl_text, height=32,
                         corner_radius=7, font=ctk.CTkFont(size=12),
                         fg_color=BG_DARK, border_color=BORDER)
        e.pack(fill="x", pady=(0, 4))
        entries[key] = e

    def col_date(col, lbl_text, key):
        ctk.CTkLabel(col, text=lbl_text, font=ctk.CTkFont(size=11),
                     text_color=TEXT_SEC, anchor="w").pack(anchor="w")
        row = ctk.CTkFrame(col, fg_color="transparent")
        row.pack(fill="x", pady=(0, 4))
        var = ctk.StringVar()
        ctk.CTkEntry(row, textvariable=var, height=32, corner_radius=7,
                     font=ctk.CTkFont(size=12), fg_color=BG_DARK,
                     border_color=BORDER, placeholder_text="DD/MM/YYYY").pack(
            side="left", fill="x", expand=True)
        def pick(v=var):
            top = ctk.CTkToplevel(root)
            top.title("Select Date")
            top.geometry("300x320")
            top.transient(root); top.grab_set(); top.focus_force(); top.lift()
            cal = Calendar(top, date_pattern="dd/mm/yyyy")
            cal.pack(pady=10, fill="both", expand=True)
            ctk.CTkButton(top, text="Select", fg_color=ACCENT,
                          command=lambda: [v.set(cal.get_date()), top.destroy()]).pack(pady=10)
        ctk.CTkButton(row, text="📅", width=32, height=32,
                      fg_color=BG_CARD2, corner_radius=7, command=pick).pack(side="right", padx=(2, 0))
        entries[key] = var

    def col_dd(col, lbl_text, key, values):
        ctk.CTkLabel(col, text=lbl_text, font=ctk.CTkFont(size=11),
                     text_color=TEXT_SEC, anchor="w").pack(anchor="w")
        var = ctk.StringVar(value=values[0])
        ctk.CTkOptionMenu(col, variable=var, values=values, height=32,
                          corner_radius=7, fg_color=BG_CARD2, button_color=ACCENT,
                          font=ctk.CTkFont(size=12)).pack(fill="x", pady=(0, 4))
        entries[key] = var

    def upload_field(parent, key):
        var = ctk.StringVar()
        box = ctk.CTkFrame(parent, fg_color=BG_DARK, corner_radius=8,
                           border_width=1, border_color=BORDER)
        box.pack(fill="x", pady=(0, 6))
        icon_lbl = ctk.CTkLabel(box, text="⬆", font=ctk.CTkFont(size=20), text_color=TEXT_DIM)
        icon_lbl.pack(pady=(10, 2))
        ctk.CTkLabel(box, textvariable=var, font=ctk.CTkFont(size=10),
                     text_color=ACCENT2).pack()
        up_btn = ctk.CTkButton(box, text="Upload File", height=28, width=120,
                               fg_color=BG_CARD2, hover_color=ACCENT,
                               corner_radius=7, font=ctk.CTkFont(size=11))
        def do_upload(v=var, b=up_btn, il=icon_lbl):
            f = filedialog.askopenfilename()
            if f:
                v.set(os.path.basename(f)); v.full_path = f
                b.configure(text="✓ Uploaded", fg_color="#0d2a1a")
                il.configure(text="✅")
        up_btn.configure(command=do_upload)
        up_btn.pack(pady=(4, 10))
        entries[key] = var

    # ══════════════════════════════════════════════════════════
    # SECTION BUILDER
    # ══════════════════════════════════════════════════════════
    def section(title, icon=""):
        full = f"{icon}  {title}" if icon else title
        acc = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=12)
        acc.pack(fill="x", pady=5)

        hdr = ctk.CTkFrame(acc, fg_color=BG_CARD2, corner_radius=10, height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tog = ctk.CTkLabel(hdr, text="▼", font=ctk.CTkFont(size=11),
                           text_color=ACCENT2, width=20)
        tog.pack(side="right", padx=12)
        ctk.CTkLabel(hdr, text=full, font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_PRI, anchor="w").pack(side="left", padx=14)

        body = ctk.CTkFrame(acc, fg_color="transparent")
        body.pack(fill="x", padx=14, pady=(4, 10))
        state = [True]

        def toggle(e=None):
            if state[0]:
                body.pack_forget(); tog.configure(text="▶")
            else:
                body.pack(fill="x", padx=14, pady=(4, 10)); tog.configure(text="▼")
            state[0] = not state[0]

        hdr.bind("<Button-1>", toggle)
        tog.bind("<Button-1>", toggle)

        nb = ctk.CTkButton(sec_nav_scroll, text=f"{icon} {title}", anchor="w",
                           fg_color="transparent", hover_color=BG_CARD,
                           text_color=TEXT_SEC, font=ctk.CTkFont(size=10),
                           height=26, corner_radius=6)
        nb.pack(fill="x", pady=1)

        def go(f=acc):
            sec_nav_scroll._parent_canvas.update_idletasks()
            try:
                scroll._parent_canvas.yview_moveto(
                    f.winfo_y() / max(scroll._parent_canvas.winfo_height(), 1))
            except:
                pass
        nb.configure(command=go)
        return body

    # ══════════════════════════════════════════════════════════
    # 1. PERSONAL
    # ══════════════════════════════════════════════════════════
    s = section("Personal", "👤")
    lbl(s, "Full Name");          txt_entry(s, "Full Name", "Full Name")
    L, R = two_col(s)
    col_entry(L, "Father's Name", "Father's Name")
    col_date(R, "Date of Birth", "Date of Birth")
    L, R = two_col(s)
    col_dd(L, "Marital Status", "Marital Status",
           ["Single", "Married", "Divorced", "Widowed"])
    col_entry(R, "Spouse Name", "Spouse Name")
    L, R = two_col(s)
    col_entry(L, "Nationality", "Nationality")
    col_entry(R, "Aadhaar Number", "Aadhaar Number")
    lbl(s, "Qualification");      txt_entry(s, "Qualification", "Qualification")
    L, R = two_col(s)
    col_entry(L, "Height", "Height")
    col_entry(R, "Weight", "Weight")

    # ══════════════════════════════════════════════════════════
    # 2. FAMILY
    # ══════════════════════════════════════════════════════════
    s = section("Family", "👨‍👩‍👧")
    L, R = two_col(s)
    col_dd(L, "Number of Children", "Number of Children", ["0","1","2","3","4","5+"])
    col_date(R, "DOB Of Each Children", "DOB Of Each Children")
    ctk.CTkLabel(s, text="Family Members :", font=ctk.CTkFont(size=12, weight="bold"),
                 text_color=TEXT_PRI).pack(anchor="w", pady=(8, 2))
    L, R = two_col(s)
    col_entry(L, "Father's Age", "Father's Age")
    col_entry(R, "Mother's Age", "Mother's Age")
    L, R = two_col(s)
    col_entry(L, "Spouse's Age", "Spouse's Age")
    col_entry(R, "Brother's Age", "Brother's Age")
    L, R = two_col(s)
    col_date(L, "Date of Birth", "Family DOB")
    col_entry(R, "Sister's Age", "Sister's Age")

    # ══════════════════════════════════════════════════════════
    # 3. PROFESSIONAL
    # ══════════════════════════════════════════════════════════
    s = section("Professional", "💼")
    lbl(s, "Employer / Business Name");  txt_entry(s, "Employer / Business Name", "Employer / Business Name")
    lbl(s, "Designation");               txt_entry(s, "Designation", "Designation")
    lbl(s, "Nature of Business / Occupation"); txt_entry(s, "Nature of Business / Occupation", "Nature of Business / Occupation")
    lbl(s, "Annual Income");             txt_entry(s, "Annual Income", "Annual Income")

    # ══════════════════════════════════════════════════════════
    # 4. CONTACT
    # ══════════════════════════════════════════════════════════
    s = section("Contact", "📞")
    lbl(s, "Office Contact Number"); txt_entry(s, "Office Contact Number", "Office Contact Number")
    L, R = two_col(s)
    col_entry(L, "Mobile Number 1", "Mobile Number 1")
    col_entry(R, "Mobile Number 2", "Mobile Number 2")
    L, R = two_col(s)
    col_entry(L, "Mobile Number 3", "Mobile Number 3")
    col_entry(R, "Mobile Number 4", "Mobile Number 4")
    lbl(s, "Email ID"); txt_entry(s, "Email ID", "Email ID")

    # ══════════════════════════════════════════════════════════
    # 5. IDENTITY
    # ══════════════════════════════════════════════════════════
    s = section("Identity Details", "🆔")
    L, R = two_col(s)
    col_entry(L, "Pan Number", "PAN Number")
    col_entry(R, "Aadhar Number", "Aadhar Number")

    # ══════════════════════════════════════════════════════════
    # 6. ADDITIONAL DETAILS
    # ══════════════════════════════════════════════════════════
    s = section("Additional Details", "💍")
    lbl(s, "Wedding Anniversary"); date_pick(s, "Wedding Anniversary")

    # ══════════════════════════════════════════════════════════
    # 7. NOMINEE DETAILS
    # ══════════════════════════════════════════════════════════
    s = section("Nominee Details", "🧾")
    L, R = two_col(s)
    col_entry(L, "Nominee Name", "Nominee Name")
    col_dd(R, "Nominee Relationship", "Nominee Relationship",
           ["Father", "Mother", "Spouse", "Children", "Appointee"])
    L, R = two_col(s)
    col_date(L, "Nominee DOB", "Nominee DOB")
    col_entry(R, "Nominee Father's Name", "Nominee Father's Name")

    # ══════════════════════════════════════════════════════════
    # 8. INSURANCE DETAILS
    # ══════════════════════════════════════════════════════════
    s = section("Insurance Details", "🛡")

    tab_row = ctk.CTkFrame(s, fg_color=BG_CARD2, corner_radius=8)
    tab_row.pack(fill="x", pady=(0, 8))

    ins_bodies = {}
    ins_btns = {}

    def show_ins(name):
        for n, b in ins_btns.items():
            b.configure(fg_color=ACCENT if n == name else "transparent",
                        text_color=TEXT_PRI)
        for n, f in ins_bodies.items():
            if n == name:
                f.pack(fill="x", pady=4)
            else:
                f.pack_forget()

    for tab in ["Self", "Father", "Mother", "Spouse", "Children"]:
        b = ctk.CTkButton(tab_row, text=tab, height=30, width=60,
                          fg_color=ACCENT if tab == "Self" else "transparent",
                          hover_color=BG_CARD, text_color=TEXT_PRI,
                          font=ctk.CTkFont(size=11), corner_radius=6,
                          command=lambda t=tab: show_ins(t))
        b.pack(side="left", padx=3, pady=3)
        ins_btns[tab] = b

        bf = ctk.CTkFrame(s, fg_color="transparent")
        ins_bodies[tab] = bf

        lbl(bf, "Policy Number");  txt_entry(bf, "Policy Number", f"{tab} Policy Number")
        L2, R2 = two_col(bf)
        col_entry(L2, "Aadhaar Number", f"{tab} Aadhaar Number")
        col_entry(R2, "Sum Assured",    f"{tab} Sum Assured")
        L2, R2 = two_col(bf)
        col_entry(L2, "Sum Assured",    f"{tab} Sum Assured 2")
        years = [str(y) for y in range(2000, datetime.now().year + 2)]
        col_dd(R2, "Year of Issue", f"{tab} Year of Issue", years)
        lbl(bf, "Company"); txt_entry(bf, "Company", f"{tab} Company")

    ins_bodies["Self"].pack(fill="x", pady=4)

    # ══════════════════════════════════════════════════════════
    # 9. HEALTH DETAILS
    # ══════════════════════════════════════════════════════════
    s = section("Health Details", "🏥")
    lbl(s, "Health Problems"); txt_entry(s, "Health Problems", "Health Problems")
    lbl(s, "Lifestyle habits (Smoking / Drinking)")
    txt_entry(s, "Lifestyle habits (Smoking / Drinking)", "Lifestyle habits")
    L, R = two_col(s)
    col_entry(L, "Pregnancy Details", "Pregnancy Details")
    col_entry(R, "Other Remarks", "Other Remarks")

    # ══════════════════════════════════════════════════════════
    # 10. ADDRESS
    # ══════════════════════════════════════════════════════════
    s = section("Address Details", "🏠")
    lbl(s, "Communication Address")
    t1 = ctk.CTkTextbox(s, height=70, corner_radius=7, fg_color=BG_DARK,
                        border_color=BORDER, font=ctk.CTkFont(size=12))
    t1.pack(fill="x", pady=(0, 6)); entries["Communication Address"] = t1
    lbl(s, "Permanent Address")
    t2 = ctk.CTkTextbox(s, height=70, corner_radius=7, fg_color=BG_DARK,
                        border_color=BORDER, font=ctk.CTkFont(size=12))
    t2.pack(fill="x", pady=(0, 6)); entries["Permanent Address"] = t2

    # ══════════════════════════════════════════════════════════
    # 11. PLAN DETAILS
    # ══════════════════════════════════════════════════════════
    s = section("Plan Details", "📋")
    lbl(s, "Product Name"); txt_entry(s, "Product Name", "Product Name")
    lbl(s, "Premium Mode (Yearly / Half-Yearly / Quarterly)")
    ddmenu(s, "Premium Mode", ["Yearly", "Half-Yearly", "Quarterly"])
    L, R = two_col(s)
    col_entry(L, "Sum Assured", "Plan Sum Assured")
    col_entry(R, "Rider", "Rider")

    # ══════════════════════════════════════════════════════════
    # 12. DOCUMENT ATTACHMENTS
    # ══════════════════════════════════════════════════════════
    s = section("Document Attachments", "📎")
    for doc in ["Age Proof", "ID Proof", "Address Proof", "Photo",
                "School ID", "Form 16", "Bank Statement",
                "Bank Cheque 1", "Bank Cheque 2",
                "Proposal Form 1", "Proposal Form 2", "Visiting Card"]:
        lbl(s, doc); upload_field(s, doc)

    # ══════════════════════════════════════════════════════════
    # 13. REFERENCE
    # ══════════════════════════════════════════════════════════
    s = section("Reference", "👥")
    lbl(s, "Friend's Name");   txt_entry(s, "Friend's Name", "Friend's Name")
    lbl(s, "Mobile Number");   txt_entry(s, "Reference Mobile", "Reference Mobile")
    lbl(s, "Age");             txt_entry(s, "Age", "Reference Age")

    # ══════════════════════════════════════════════════════════
    # 14. PAN CARD & FINANCIAL DETAILS
    # ══════════════════════════════════════════════════════════
    s = section("PAN Card and Financial Details", "🪪")

    ctk.CTkLabel(s, text="PAN Details", font=ctk.CTkFont(size=12, weight="bold"),
                 text_color=TEXT_PRI).pack(anchor="w", pady=(4, 2))
    lbl(s, "PAN Number"); txt_entry(s, "Enter PAN Number", "PAN Number")
    lbl(s, "Upload PAN Card"); upload_field(s, "PAN Card Copy")

    ctk.CTkLabel(s, text="Financial and Investment Details",
                 font=ctk.CTkFont(size=12, weight="bold"),
                 text_color=TEXT_PRI).pack(anchor="w", pady=(10, 2))

    plan_opts = ["Select Plan", "Plan A", "Plan B", "Plan C"]
    L, R = two_col(s)
    col_dd(L, "Risk Cover",    "Risk Cover",    plan_opts)
    col_dd(R, "Pension Plan",  "Pension Plan",  plan_opts)
    L, R = two_col(s)
    col_dd(L, "Investment Plan", "Investment Plan", plan_opts)
    col_dd(R, "Mutual Funds",    "Mutual Funds",    plan_opts)
    L, R = two_col(s)
    col_dd(L, "Medi Claim",       "Medi Claim",       plan_opts)
    col_dd(R, "Money Bank Policy", "Money Bank Policy", plan_opts)
    lbl(s, "Children's Education Plan")
    ddmenu(s, "Children's Education Plan", plan_opts)

    ctk.CTkLabel(s, text="Remainder Details",
                 font=ctk.CTkFont(size=12, weight="bold"),
                 text_color=TEXT_PRI).pack(anchor="w", pady=(10, 2))
    L, R = two_col(s)
    col_date(L, "Remainder Date 1", "Reminder Date 1")
    col_date(R, "Remainder Date 2", "Reminder Date 2")

    # ══════════════════════════════════════════════════════════
    # 15. ADDITIONAL FUNCTIONALITIES
    # ══════════════════════════════════════════════════════════
    s = section("Additional Functionalities", "⚙️")
    lbl(s, "Auto Age Calculation");      txt_entry(s, "Auto Age Calculation", "Auto Age Calculation")
    lbl(s, "Dropdown Selections");       txt_entry(s, "Dropdown Selections", "Dropdown Selections")
    lbl(s, "File Attachment Handling");  txt_entry(s, "File Attachment Handling", "File Attachment Handling")
    lbl(s, "Structured Data Management"); txt_entry(s, "Structured Data Management", "Structured Data Management")

    # ══════════════════════════════════════════════════════════
    # 16. NOTES
    # ══════════════════════════════════════════════════════════
    notes_frame = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=12)
    notes_frame.pack(fill="x", pady=5)
    notes_hdr = ctk.CTkFrame(notes_frame, fg_color=BG_CARD2, corner_radius=10, height=44)
    notes_hdr.pack(fill="x")
    notes_hdr.pack_propagate(False)
    ctk.CTkLabel(notes_hdr, text="📝  Notes",
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color=TEXT_PRI, anchor="w").pack(side="left", padx=14)
    notes_box = ctk.CTkTextbox(notes_frame, height=120, corner_radius=8,
                               fg_color=BG_DARK, border_color=BORDER,
                               font=ctk.CTkFont(size=12))
    notes_box.pack(fill="x", padx=14, pady=(8, 14))
    notes_box.insert("1.0", "Write notes here...")
    entries["Notes"] = notes_box

    # ══════════════════════════════════════════════════════════
    # SAVE
    # ══════════════════════════════════════════════════════════
    def save():
        data = {}
        pid = generate_id()
        person_folder = os.path.join("data", pid)
        files_folder  = os.path.join(person_folder, "files")
        os.makedirs(files_folder, exist_ok=True)

        for k, v in entries.items():
            if hasattr(v, "full_path"):
                try:
                    fn = os.path.basename(v.full_path)
                    shutil.copy(v.full_path, os.path.join(files_folder, fn))
                    data[k] = fn
                except:
                    data[k] = v.get()
            elif isinstance(v, ctk.CTkTextbox):
                data[k] = v.get("1.0", "end").strip()
            elif isinstance(v, (ctk.StringVar, ctk.CTkEntry)):
                data[k] = v.get()
            else:
                try:
                    data[k] = v.get()
                except:
                    pass

        data["ID"] = pid
        dob = data.get("Date of Birth", "")
        if dob:
            try:
                birth_year = int(dob.split("/")[2])
                data["Age"] = str(datetime.now().year - birth_year)
                data["Auto Age Calculation"] = data["Age"]
            except:
                pass

        save_json(os.path.join(person_folder, "data.json"), data)
        add_person(pid, data.get("Full Name", "Unknown"))
        messagebox.showinfo("✅ Saved", f"Person '{data.get('Full Name', pid)}' Added Successfully!")
        show_dashboard(root, content)

    ctk.CTkButton(
        main, text="💾   Submit",
        height=44, corner_radius=10,
        fg_color=ACCENT, hover_color="#3a55d0",
        font=ctk.CTkFont(size=14, weight="bold"),
        command=save
    ).pack(fill="x", padx=20, pady=(0, 14))