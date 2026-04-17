import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
from utils.helpers import generate_id
from logic.file_ops import save_json
from logic.person_ops import add_person
import os
import shutil


def open_form(root, content, show_dashboard):

    # ===== CLEAR =====
    for w in content.winfo_children():
        w.destroy()

    main = ctk.CTkFrame(content, corner_radius=15)
    main.pack(fill="both", expand=True, padx=20, pady=20)

    # ===== HEADER =====
    header = ctk.CTkFrame(main, fg_color="transparent")
    header.pack(fill="x", pady=10)

    ctk.CTkLabel(header,
                 text="➕ Add Person",
                 font=("Segoe UI", 24, "bold")
    ).pack(side="left")

    ctk.CTkButton(header,
                  text="⬅ Back",
                  command=lambda: show_dashboard(root, content)
    ).pack(side="right")

    # ===== SCROLL =====
    scroll = ctk.CTkScrollableFrame(main, corner_radius=10)
    scroll.pack(fill="both", expand=True, pady=10)

    entries = {}

    # ===== FIELD =====
    def add(parent, label, field_type="text", options=None):

        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(fill="x", padx=5, pady=5)

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(row,
                     text=label,
                     width=220,
                     anchor="w",
                     font=("Segoe UI", 11, "bold")
        ).pack(side="left")

        # ===== TEXT =====
        if field_type == "text":
            e = ctk.CTkEntry(row)
            e.pack(side="right", fill="x", expand=True)
            entries[label] = e

        # ===== DROPDOWN =====
        elif field_type == "dropdown":
            var = ctk.StringVar()
            ctk.CTkOptionMenu(row, variable=var, values=options).pack(side="right")
            entries[label] = var

        # ===== FILE =====
        elif field_type == "file":
            var = ctk.StringVar()

            btn = ctk.CTkButton(row, text="Upload")

            def upload():
                f = filedialog.askopenfilename()
                if f:
                    filename = os.path.basename(f)
                    var.set(filename)
                    var.full_path = f
                    btn.configure(text="Uploaded ✓", fg_color="green")

            btn.configure(command=upload)
            btn.pack(side="right", padx=5)

            def open_file():
                if hasattr(var, "full_path"):
                    try:
                        os.startfile(var.full_path)
                    except:
                        messagebox.showerror("Error", "Cannot open file")

            ctk.CTkButton(row,
                          textvariable=var,
                          fg_color="transparent",
                          text_color="#4da6ff",
                          command=open_file
            ).pack(side="right")

            entries[label] = var

    # ===== SECTION =====
    def section(title):
        container = ctk.CTkFrame(scroll, corner_radius=12)
        container.pack(fill="x", pady=8)

        header = ctk.CTkButton(container,
                               text=f"▶ {title}",
                               anchor="w",
                               height=40)
        header.pack(fill="x")

        body = ctk.CTkFrame(container)
        body.pack(fill="x")
        body.pack_forget()

        def toggle():
            if body.winfo_ismapped():
                body.pack_forget()
                header.configure(text=f"▶ {title}")
            else:
                body.pack(fill="x")
                header.configure(text=f"▼ {title}")

        header.configure(command=toggle)
        return body

    # ===== ALL SECTIONS =====

    # Personal
    sec = section("👤 Personal Details")
    add(sec, "Full Name")
    add(sec, "Father’s Name")
    add(sec, "Date of Birth")
    add(sec, "Marital Status", "dropdown", ["Single", "Married"])
    add(sec, "Spouse Name")
    add(sec, "Nationality")
    add(sec, "Qualification")
    add(sec, "Height")
    add(sec, "Weight")
    add(sec, "Aadhaar Number")

    # Family
    sec = section("👨‍👩‍👧 Family Details")
    add(sec, "Number of Children")
    add(sec, "Children DOB")
    add(sec, "Father’s Age")
    add(sec, "Mother’s Age")
    add(sec, "Spouse Age")
    add(sec, "Brother’s Age")
    add(sec, "Sister’s Age")

    # Professional
    sec = section("💼 Professional Details")
    add(sec, "Employer / Business Name")
    add(sec, "Designation")
    add(sec, "Nature of Business")
    add(sec, "Annual Income")

    # Contact
    sec = section("📞 Contact Details")
    add(sec, "Office Contact Number")
    add(sec, "Mobile Number 1")
    add(sec, "Mobile Number 2")
    add(sec, "Email ID")

    # Identity
    sec = section("🆔 Identity Details")
    add(sec, "PAN Number")
    add(sec, "Aadhaar Number")

    # Additional
    sec = section("💍 Additional Details")
    add(sec, "Wedding Anniversary")

    # Nominee
    sec = section("🧾 Nominee Details")
    add(sec, "Nominee Relationship", "dropdown",
        ["Father", "Mother", "Spouse", "Children", "Appointee"])
    add(sec, "Nominee Name")
    add(sec, "Nominee DOB")
    add(sec, "Nominee Father’s Name")

    # Insurance
    sec = section("🛡 Insurance Details")
    for p in ["Self", "Father", "Mother", "Spouse", "Children"]:
        for f in ["Policy Number", "Sum Assured", "Year of Issue", "Company"]:
            add(sec, f"{p} {f}")

    # Health
    sec = section("🏥 Health Details")
    add(sec, "Health problems")
    add(sec, "Lifestyle habits")
    add(sec, "Pregnancy details")
    add(sec, "Other remarks")

    # Address
    sec = section("🏠 Address Details")
    add(sec, "Communication Address")
    add(sec, "Permanent Address")

    # Plan
    sec = section("📋 Plan Details")
    add(sec, "Product Name")
    add(sec, "Premium")
    add(sec, "Mode", "dropdown", ["Yearly", "Half-yearly", "Quarterly"])
    add(sec, "Sum Assured")
    add(sec, "Rider")

    # Documents
    sec = section("📎 Document Attachments")
    for d in [
        "Age Proof", "ID Proof", "Address Proof", "Photo",
        "School ID", "Form 16", "Bank Statement",
        "Bank Cheque 1", "Bank Cheque 2",
        "Proposal Form 1", "Proposal Form 2",
        "Visiting Card"
    ]:
        add(sec, d, "file")

    # References
    sec = section("👥 References")
    add(sec, "Friend’s Name")
    add(sec, "Mobile Number")
    add(sec, "Age")

    # Financial
    sec = section("🪪 PAN & Financial Details")
    add(sec, "PAN Number")
    add(sec, "PAN Card Copy", "file")
    add(sec, "Risk Cover")
    add(sec, "Pension Plan")
    add(sec, "Investment Plan")
    add(sec, "Mutual Fund")
    add(sec, "Mediclaim")
    add(sec, "Money Back Policy")
    add(sec, "Children’s Education Plan")
    add(sec, "Reminder Date 1")
    add(sec, "Reminder Date 2")

    # ===== SAVE =====
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

        messagebox.showinfo("Saved", "Person Added Successfully")
        show_dashboard(root, content)

    ctk.CTkButton(main,
                  text="💾 Save",
                  height=45,
                  command=save).pack(pady=10)