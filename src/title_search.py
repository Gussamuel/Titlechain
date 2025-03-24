import os
import sys
import tkinter as tk
from tkinter import ttk
import json
import webbrowser

# Determine the base directory of the program
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running as a PyInstaller bundle
    base_dir = sys._MEIPASS
else:
    # Running as a script
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the JSON file path relative to the base directory
json_path = os.path.join(base_dir, "data", "stateTitle.json")

# Load the JSON data
try:
    with open(json_path, "r") as f:
        counties_data = json.load(f)
except FileNotFoundError:
    print(f"Error: File not found at {json_path}")
    raise

# Create the Title Search tab
class TitleTab(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Configure grid for dynamic resizing
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Title label
        title_label = ttk.Label(self, text="Title Search", font=('Helvetica', 20, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # State Dropdown
        state_label = ttk.Label(self, text="Select State:", font=('Helvetica', 12))
        state_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.state_var = tk.StringVar()
        self.state_menu = ttk.Combobox(self, textvariable=self.state_var, state="readonly", font=('Helvetica', 12))
        self.state_menu['values'] = list(counties_data.keys())
        self.state_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.state_menu.bind("<<ComboboxSelected>>", self.update_county_options)

        # County Dropdown
        county_label = ttk.Label(self, text="Select County/Parish/Municipality:", font=('Helvetica', 12))
        county_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.county_var = tk.StringVar()
        self.county_menu = ttk.Combobox(self, textvariable=self.county_var, state="readonly", font=('Helvetica', 12))
        self.county_menu.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Buttons and link area
        self.show_link_button = ttk.Button(self, text="Show Link", command=self.show_link)
        self.show_link_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.link_label = ttk.Label(self, text="", font=('Helvetica', 12), foreground="blue", cursor="hand2")
        self.link_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.link_label.bind("<Button-1>", lambda e: self.open_link(self.link_label.cget("text")))
        self.link_label.bind("<Enter>", lambda e: self.link_label.config(font=('Helvetica', 12, 'underline')))
        self.link_label.bind("<Leave>", lambda e: self.link_label.config(font=('Helvetica', 12)))

        self.link_button = ttk.Button(self, text="Go to Register of Deeds", state=tk.DISABLED)
        self.link_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    def update_county_options(self, *args):
        selected_state = self.state_var.get()
        counties = counties_data.get(selected_state, {})
        self.county_menu['values'] = list(counties.keys())
        self.county_var.set('')  # Reset county selection
        self.link_label.config(text="")
        self.link_button.config(state=tk.DISABLED)

    def show_link(self):
        selected_state = self.state_var.get()
        selected_county = self.county_var.get()
        link = counties_data.get(selected_state, {}).get(selected_county, None)
        if link:
            self.link_label.config(text=link)
            self.link_button.config(state=tk.NORMAL, command=lambda: self.open_link(link))
        else:
            self.link_label.config(text="No link available")
            self.link_button.config(state=tk.DISABLED)

    def open_link(self, link):
        if link and link != "No link available":
            webbrowser.open(link)