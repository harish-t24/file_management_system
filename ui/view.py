import customtkinter as ctk
from tkinter import messagebox, filedialog
from logic.file_ops import load_json, save_json
from logic.person_ops import update_person
from utils.helpers import simple_input
import os
import shutil


def view_person(root, content, pid, show_dashboard):

    # ===== CLEAR =====
    for w in content.winfo_children():
        w.destroy()

    frame = ctk.CTkFrame(content)
    frame.pack(fill="both", expand=True, padx=15, pady=15)

    # ===== PATH =====
    person_folder = os.path.join("data", pid)
    file_name = os.path.join(person_folder, "data.json")

    data = load_json(file_name)

    if not data:
        messagebox.showerror("Error", "Data not found")
        return

    # ===== HEADER =====
    header = ctk.CTkFrame(frame, fg_color="transparent")
    header.pack(fill="x", pady=10)

    ctk.CTkLabel(header,
                 text=f"👤 {data.get('Full Name','Person')}",
                 font=("Segoe UI", 20, "bold")
    ).pack(side="left")

    ctk.CTkButton(header,
                  text="⬅ Back",
                  command=lambda: show_dashboard(root, content)
    ).pack(side="right")

    # ===== SCROLL AREA =====
    scroll = ctk.CTkScrollableFrame(frame, corner_radius=10)
    scroll.pack(fill="both", expand=True, pady=10)

    # ===== FILE FIELDS =====
    file_fields = [
        "Age Proof", "ID Proof", "Address Proof", "Photo",
        "School ID", "Form 16", "Bank Statement",
        "Bank Cheque 1", "Bank Cheque 2",
        "Proposal Form 1", "Proposal Form 2",
        "Visiting Card", "PAN Card Copy"
    ]

    # ===== OPEN FILE =====
    def open_file(filename):
        try:
            path = os.path.join("data", pid, "files", filename)
            if os.path.exists(path):
                os.startfile(path)
            else:
                messagebox.showerror("Error", "File not found")
        except:
            messagebox.showerror("Error", "Cannot open file")

    # ===== DISPLAY DATA =====
    for key, value in data.items():

        card = ctk.CTkFrame(scroll, corner_radius=12)
        card.pack(fill="x", padx=5, pady=5)

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=8)

        # Label
        ctk.CTkLabel(row,
                     text=key,
                     width=200,
                     anchor="w",
                     font=("Segoe UI", 11, "bold")
        ).pack(side="left")

        # ===== VALUE =====
        if key in file_fields and value:

            val = ctk.CTkButton(
                row,
                text=value,
                fg_color="transparent",
                text_color="#4da6ff",
                hover_color="#1f6aa5",
                command=lambda v=value: open_file(v)
            )
            val.pack(side="left", padx=5)

        else:
            val = ctk.CTkLabel(row, text=value)
            val.pack(side="left", padx=5)

        # ===== EDIT =====
        def make_edit(k, widget):

            def edit():

                # FILE FIELD
                if k in file_fields:
                    f = filedialog.askopenfilename()
                    if f:
                        filename = os.path.basename(f)
                        dest = os.path.join("data", pid, "files", filename)

                        shutil.copy(f, dest)
                        data[k] = filename
                        save_json(file_name, data)

                        widget.configure(text=filename)

                # TEXT FIELD
                else:
                    new_val = simple_input(root, f"Edit {k}")
                    if new_val:
                        data[k] = new_val
                        save_json(file_name, data)

                        widget.configure(text=new_val)

                        if k == "Full Name":
                            update_person(pid, new_val)
                            show_dashboard(root, content)

            return edit

        ctk.CTkButton(row,
                      text="✏",
                      width=40,
                      command=make_edit(key, val)
        ).pack(side="right")
