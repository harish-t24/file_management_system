import customtkinter as ctk
from ui.dashboard import show_dashboard
from logic.person_ops import load_persons

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("900x600")
root.title("Person Manager")

content = ctk.CTkFrame(root)
content.pack(fill="both", expand=True)

load_persons()
show_dashboard(root, content)

root.mainloop()