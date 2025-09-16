import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading

REQUIREMENTS = [
    "PyQt6",
    "supermemo2",
    "requests",
    "flask",
    "jwt",
    "playsound"
]

class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Studify Module Installer")
        self.geometry("400x300")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        self.header = tk.Label(self, text="Finish Setting Up Studify! A simple study app.", font=("Arial", 16))
        self.header.pack(pady=(20, 10))

        self.label = tk.Label(self, text="Installing required modules...")
        self.label.pack(pady=10)

        self.progress = ttk.Progressbar(self, length=300, mode='determinate', maximum=len(REQUIREMENTS))
        self.progress.pack(pady=10)

        self.status = tk.Label(self, text="Ready to install.")
        self.status.pack(pady=10)

        self.install_btn = tk.Button(self, text="Install", command=self.start_install)
        self.install_btn.pack(pady=10)

    def start_install(self):
        self.install_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.install_modules, daemon=True).start()

    def install_modules(self):
        for idx, module in enumerate(REQUIREMENTS, 1):
            self.status.config(text=f"Installing {module}...")
            self.progress['value'] = idx - 1
            self.update_idletasks()
            try:
                subprocess.check_call(["pip", "install", module])
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", f"Failed to install {module}")
        self.progress['value'] = len(REQUIREMENTS)
        self.status.config(text="All modules installed!")
        messagebox.showinfo("Done", "All required modules have been installed.")

if __name__ == "__main__":
    app = InstallerApp()
    app.mainloop()
