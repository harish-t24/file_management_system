import customtkinter as ctk
from tkinter import messagebox
from logic.person_ops import persons, delete_person_list
from ui.view import view_person
from ui.form import open_form
import os
import shutil


def delete_person(pid, refresh):
    confirm = messagebox.askyesno("Confirm", "Delete this person?")

    if not confirm:
        return

    # delete full folder
    folder = os.path.join("data", pid)

    if os.path.exists(folder):
        shutil.rmtree(folder)

    # remove from list
    delete_person_list(pid)

    # refresh dashboard
    refresh()


def show_dashboard(root, content):

    # ===== CLEAR SCREEN =====
    for w in content.winfo_children():
        w.destroy()

    # ===== MAIN CONTAINER =====
    frame = ctk.CTkFrame(content)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ===== TITLE =====
    ctk.CTkLabel(frame,
                 text="📊 Dashboard",
                 font=("Segoe UI", 20, "bold")
    ).pack(pady=10)

    # ===== ADD BUTTON =====
    ctk.CTkButton(frame,
                  text="➕ Add Person",
                  command=lambda:
                  open_form(root, content, show_dashboard)
    ).pack(pady=10)

    # ===== PERSON LIST =====
    if not persons:
        ctk.CTkLabel(frame, text="No persons found").pack(pady=20)
        return

    for pid, name in persons:

        row = ctk.CTkFrame(frame)
        row.pack(fill="x", padx=10, pady=5)

        # Name + ID
        ctk.CTkLabel(row,
                     text=f"{name} ({pid})"
        ).pack(side="left", padx=10)

        # ===== VIEW BUTTON =====
        ctk.CTkButton(row,
                      text="View",
                      width=70,
                      command=lambda pid=pid:
                      view_person(root, content, pid, show_dashboard)
        ).pack(side="right", padx=5)

        # ===== DELETE BUTTON =====
        ctk.CTkButton(row,
                      text="Delete",
                      width=70,
                      fg_color="red",
                      hover_color="#aa0000",
                      command=lambda pid=pid:
                      delete_person(pid,
                                    lambda: show_dashboard(root, content))
        ).pack(side="right", padx=5)