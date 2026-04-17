import customtkinter as ctk
from tkinter import messagebox
from logic.person_ops import persons, delete_person_list
from ui.view import view_person
from ui.form import open_form
import os
import shutil


# ===== DELETE =====
def delete_person(pid, refresh):
    confirm = messagebox.askyesno("Confirm", "Delete this person?")
    if not confirm:
        return

    folder = os.path.join("data", pid)

    if os.path.exists(folder):
        shutil.rmtree(folder)

    delete_person_list(pid)
    refresh()


# ===== DASHBOARD =====
def show_dashboard(root, content):

    # CLEAR SCREEN
    for w in content.winfo_children():
        w.destroy()

    main = ctk.CTkFrame(content, corner_radius=15)
    main.pack(fill="both", expand=True, padx=20, pady=20)

    # ===== HEADER =====
    header = ctk.CTkFrame(main, fg_color="transparent")
    header.pack(fill="x", pady=10)

    ctk.CTkLabel(header,
                 text="📊 Dashboard",
                 font=("Segoe UI", 24, "bold")
    ).pack(side="left")

    ctk.CTkButton(header,
                  text="➕ Add Person",
                  corner_radius=10,
                  command=lambda:
                  open_form(root, content, show_dashboard)
    ).pack(side="right")

    # ===== SEARCH =====
    search_frame = ctk.CTkFrame(main, corner_radius=12)
    search_frame.pack(fill="x", pady=15)

    search_entry = ctk.CTkEntry(
        search_frame,
        placeholder_text="🔍 Search by name or ID...",
        height=42,
        corner_radius=12,
        fg_color="#2b2b3c",
        border_width=1
    )
    search_entry.pack(fill="x", padx=10, pady=10)

    # ===== CARD AREA =====
    card_container = ctk.CTkScrollableFrame(main, corner_radius=10)
    card_container.pack(fill="both", expand=True)

    # ===== DISPLAY CARDS =====
    def display_cards(data):

        for w in card_container.winfo_children():
            w.destroy()

        if not data:
            ctk.CTkLabel(card_container,
                         text="No persons found",
                         font=("Segoe UI", 14)
            ).pack(pady=20)
            return

        row_frame = None

        for i, (pid, name) in enumerate(data):

            if i % 2 == 0:
                row_frame = ctk.CTkFrame(card_container, fg_color="transparent")
                row_frame.pack(fill="x")

            card = ctk.CTkFrame(row_frame,
                                corner_radius=15,
                                height=150)
            card.pack(side="left", expand=True, fill="x", padx=10, pady=10)

            ctk.CTkLabel(card,
                         text=f"👤 {name}",
                         font=("Segoe UI", 16, "bold")
            ).pack(anchor="w", padx=15, pady=5)

            ctk.CTkLabel(card,
                         text=f"ID: {pid}",
                         text_color="gray"
            ).pack(anchor="w", padx=15)

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(fill="x", pady=10)

            ctk.CTkButton(btn_frame,
                          text="View",
                          width=80,
                          command=lambda pid=pid:
                          view_person(root, content, pid, show_dashboard)
            ).pack(side="left", padx=10)

            ctk.CTkButton(btn_frame,
                          text="Delete",
                          width=80,
                          fg_color="#e53935",
                          hover_color="#c62828",
                          command=lambda pid=pid:
                          delete_person(pid,
                                        lambda: show_dashboard(root, content))
            ).pack(side="right", padx=10)

    # ===== SEARCH LOGIC =====
    def on_search(event=None):
        query = search_entry.get().lower()

        filtered = [
            (pid, name)
            for pid, name in persons
            if query in pid.lower() or query in name.lower()
        ]

        display_cards(filtered)

    search_entry.bind("<KeyRelease>", on_search)

    # ===== SAFE FOCUS HANDLING (ONLY DASHBOARD) =====
    def remove_focus(event):
        if event.widget != search_entry and not isinstance(event.widget, ctk.CTkEntry):
            main.focus()

    main.bind("<Button-1>", remove_focus)

    # ===== INITIAL LOAD =====
    display_cards(persons)