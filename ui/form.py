import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
from utils.helpers import generate_id
from logic.file_ops import save_json
from logic.person_ops import add_person
import os
import shutil


def open_form(root, content, show_dashboard):

    # ===== CLEAR SCREEN =====
    for w in content.winfo_children():
        w.destroy()

    frame = ctk.CTkFrame(content)
    frame.pack(fill="both", expand=True)

    # ===== SCROLL =====
    canvas = ctk.CTkCanvas(frame)
    inner = ctk.CTkFrame(canvas)

    scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    canvas.create_window((0, 0), window=inner, anchor="nw")

    inner.bind("<Configure>", lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    ))

    def on_mousewheel(event):
        canvas.yview_scroll(int(-event.delta / 60), "units")

    inner.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
    inner.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    entries = {}
    entry_order = {}

    # ===== BACK BUTTON =====
    ctk.CTkButton(inner,
                  text="⬅ Back",
                  command=lambda: show_dashboard(root, content)
    ).pack(pady=5)

    # ===== SECTION =====
    def section(title):
        ctk.CTkLabel(inner,
                     text=title,
                     font=("Segoe UI", 14, "bold")
        ).pack(fill="x", pady=8)

    # ===== ADD FIELD =====
    def add(label, field_type="text", options=None):
        row = ctk.CTkFrame(inner)
        row.pack(fill="x", pady=4, padx=5)

        ctk.CTkLabel(row, text=label, width=200).pack(side="left", padx=5)

        if field_type == "text":
            e = ctk.CTkEntry(row)
            e.pack(side="right", fill="x", expand=True, padx=5)

            entry_order[label] = e

            def focus_next(event):
                keys = list(entry_order.keys())
                idx = keys.index(label)
                if idx < len(keys) - 1:
                    entry_order[keys[idx + 1]].focus()

            e.bind("<Return>", focus_next)
            entries[label] = e

        elif field_type == "dropdown":
            var = ctk.StringVar()
            e = ctk.CTkOptionMenu(row, variable=var, values=options)
            e.pack(side="right", padx=5)
            entries[label] = var

        elif field_type == "file":
            var = ctk.StringVar()

            # Upload Button
            btn = ctk.CTkButton(row, text="Upload")

            def upload():
                f = filedialog.askopenfilename()
                if f:
                    filename = os.path.basename(f)
                    var.set(filename)
                    var.full_path = f

                    btn.configure(text="Uploaded ✓",
                                  fg_color="green",
                                  hover_color="#0f8f0f")

            btn.configure(command=upload)
            btn.pack(side="right", padx=5)

            # Clickable file name (OPEN FILE)
            def open_file():
                if hasattr(var, "full_path"):
                    try:
                        os.startfile(var.full_path)  # Windows
                    except:
                        messagebox.showerror("Error", "Cannot open file")

            file_btn = ctk.CTkButton(
                row,
                textvariable=var,
                fg_color="transparent",
                text_color="#4da6ff",
                hover_color="#1f6aa5",
                command=open_file
            )
            file_btn.pack(side="right", padx=5)

            entries[label] = var

    # ===== FORM CONTENT =====
    section("👤 Personal Details")
    add("Full Name")
    add("Father’s Name")
    add("Date of Birth")
    add("Marital Status", "dropdown", ["Single", "Married"])
    add("Spouse Name")
    add("Nationality")
    add("Qualification")
    add("Height")
    add("Weight")
    add("Aadhaar Number")

    section("👨‍👩‍👧 Family Details")
    add("Number of Children")
    add("Children DOB")
    add("Father’s Age")
    add("Mother’s Age")
    add("Spouse Age")
    add("Brother’s Age")
    add("Sister’s Age")

    section("💼 Professional Details")
    add("Employer / Business Name")
    add("Designation")
    add("Nature of Business")
    add("Annual Income")

    section("📞 Contact Details")
    add("Office Contact Number")
    add("Mobile Number 1")
    add("Mobile Number 2")
    add("Email ID")

    section("🆔 Identity Details")
    add("PAN Number")
    add("Aadhaar Number")

    section("💍 Additional Details")
    add("Wedding Anniversary")

    section("🧾 Nominee Details")
    add("Nominee Relationship", "dropdown",
        ["Father", "Mother", "Spouse", "Children", "Appointee"])
    add("Nominee Name")
    add("Nominee DOB")
    add("Nominee Father’s Name")

    section("🛡 Insurance Details")
    for p in ["Self", "Father", "Mother", "Spouse", "Children"]:
        for f in ["Policy Number", "Sum Assured", "Year of Issue", "Company"]:
            add(f"{p} {f}")

    section("🏥 Health Details")
    add("Health problems")
    add("Lifestyle habits")
    add("Pregnancy details")
    add("Other remarks")

    section("🏠 Address Details")
    add("Communication Address")
    add("Permanent Address")

    section("📋 Plan Details")
    add("Product Name")
    add("Premium")
    add("Mode", "dropdown", ["Yearly", "Half-yearly", "Quarterly"])
    add("Sum Assured")
    add("Rider")

    section("📎 Document Attachments")
    for doc in [
        "Age Proof", "ID Proof", "Address Proof", "Photo",
        "School ID", "Form 16", "Bank Statement",
        "Bank Cheque 1", "Bank Cheque 2",
        "Proposal Form 1", "Proposal Form 2",
        "Visiting Card"
    ]:
        add(doc, "file")

    section("👥 References")
    add("Friend’s Name")
    add("Mobile Number")
    add("Age")

    section("🪪 PAN & Financial Details")
    add("PAN Number")
    add("PAN Card Copy", "file")

    add("Risk Cover")
    add("Pension Plan")
    add("Investment Plan")
    add("Mutual Fund")
    add("Mediclaim")
    add("Money Back Policy")
    add("Children’s Education Plan")

    add("Reminder Date 1")
    add("Reminder Date 2")

    # ===== SAVE =====
    def save():
        data = {}

        pid = generate_id()
        person_folder = os.path.join("data", pid)
        files_folder = os.path.join(person_folder, "files")

        os.makedirs(files_folder, exist_ok=True)

        for k, v in entries.items():
            if hasattr(v, "full_path"):
                src = v.full_path
                filename = os.path.basename(src)
                dest = os.path.join(files_folder, filename)

                shutil.copy(src, dest)
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

    ctk.CTkButton(inner,
                  text="💾 Save",
                  command=save).pack(pady=15)