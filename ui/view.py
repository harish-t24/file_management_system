import customtkinter as ctk
from tkinter import messagebox, filedialog
from logic.file_ops import load_json, save_json
from utils.helpers import simple_input
from logic.person_ops import update_person
import os
import shutil


def view_person(root, content, pid, show_dashboard):

    # ===== CLEAR SCREEN =====
    for w in content.winfo_children():
        w.destroy()

    frame = ctk.CTkFrame(content)
    frame.pack(fill="both", expand=True)

    # ===== PATH =====
    person_folder = os.path.join("data", pid)
    file_name = os.path.join(person_folder, "data.json")

    data = load_json(file_name)

    if not data:
        messagebox.showerror("Error", "Data not found")
        return

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

    # ===== BACK BUTTON =====
    ctk.CTkButton(inner,
                  text="⬅ Back",
                  command=lambda: show_dashboard(root, content)
    ).pack(pady=5)

    # ===== FILE SECTION =====
    files_folder = os.path.join(person_folder, "files")
    os.makedirs(files_folder, exist_ok=True)

    ctk.CTkLabel(inner,
                 text="📁 Files",
                 font=("Segoe UI", 14, "bold")
    ).pack(anchor="w", padx=10, pady=10)

    # Upload file
    def upload_file():
        src = filedialog.askopenfilename()
        if src:
            filename = os.path.basename(src)
            dest = os.path.join(files_folder, filename)
            shutil.copy(src, dest)

            messagebox.showinfo("Success", "File uploaded")
            view_person(root, content, pid, show_dashboard)

    ctk.CTkButton(inner,
                  text="📤 Upload File",
                  command=upload_file
    ).pack(pady=5)

    # File list
    for f in os.listdir(files_folder):
        row = ctk.CTkFrame(inner)
        row.pack(fill="x", padx=10, pady=3)

        # Open file
        def open_file(fname=f):
            path = os.path.join(files_folder, fname)
            try:
                os.startfile(path)  # Windows
            except:
                messagebox.showerror("Error", "Cannot open file")

        ctk.CTkButton(row,
                      text=f,
                      fg_color="transparent",
                      text_color="lightblue",
                      command=open_file
        ).pack(side="left", padx=10)

        # Delete file
        def delete_file(fname=f):
            confirm = messagebox.askyesno("Delete", f"Delete {fname}?")
            if confirm:
                os.remove(os.path.join(files_folder, fname))
                view_person(root, content, pid, show_dashboard)

        ctk.CTkButton(row,
                      text="🗑",
                      width=40,
                      fg_color="red",
                      command=delete_file
        ).pack(side="right", padx=5)

    # ===== DETAILS SECTION =====
    ctk.CTkLabel(inner,
                 text="📋 Details",
                 font=("Segoe UI", 14, "bold")
    ).pack(anchor="w", padx=10, pady=15)

    for key, value in data.items():
        row = ctk.CTkFrame(inner)
        row.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(row,
                     text=key,
                     width=200
        ).pack(side="left", padx=5)

        val_label = ctk.CTkLabel(row, text=value)
        val_label.pack(side="left", padx=5)

        # Edit field
        def make_edit(k, label):

            def edit_field():

                file_fields = [
                    "Age Proof", "ID Proof", "Address Proof", "Photo",
                    "School ID", "Form 16", "Bank Statement",
                    "Bank Cheque 1", "Bank Cheque 2",
                    "Proposal Form 1", "Proposal Form 2",
                    "Visiting Card", "PAN Card Copy"
                ]

                # ===== FILE FIELD =====
                if k in file_fields:
                    from tkinter import filedialog
                    import shutil

                    src = filedialog.askopenfilename()

                    if src:
                        filename = os.path.basename(src)
                        dest = os.path.join("data", pid, "files", filename)

                        shutil.copy(src, dest)

                        data[k] = filename
                        save_json(file_name, data)

                        label.configure(text=filename)

                # ===== NORMAL FIELD =====
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

        ctk.CTkButton(row,
                      text="✏",
                      width=40,
                      command=make_edit(key, val_label)
        ).pack(side="right", padx=5)