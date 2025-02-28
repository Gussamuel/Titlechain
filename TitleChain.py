import os
import sys
import clr
import pythonnet
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Button

# We'll import only the modules we need directly.
from src.title_search import TitleTab
from src.blockchain_tab import BlockchainTab

sdk_path = os.path.abspath(os.path.dirname(__file__))
if sdk_path not in sys.path:
    sys.path.append(sdk_path)

required_dlls = [
    "SoftPro.Select.Client.dll",
    "SoftPro.Documents.Client.dll",
    "SoftPro.Accounting.Client.dll"
]
missing_dlls = [dll for dll in required_dlls if not os.path.exists(os.path.join(sdk_path, dll))]
if missing_dlls:
    raise FileNotFoundError(f"DEBUG: ❌ Missing DLLs in {sdk_path}: {missing_dlls}")

print("DEBUG: ✅ All required DLLs are present in the TitleChain root folder!")
pythonnet.load("coreclr")

try:
    clr.AddReference(os.path.join(sdk_path, "SoftPro.Select.Client.dll"))
    clr.AddReference(os.path.join(sdk_path, "SoftPro.Documents.Client.dll"))
    clr.AddReference(os.path.join(sdk_path, "SoftPro.Accounting.Client.dll"))
    print("DEBUG: ✅ SoftPro DLLs loaded successfully!")
except Exception as e:
    print(f"DEBUG: ❌ Error loading SoftPro DLLs: {e}")

class TitleChainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TitleChain")
        self.geometry("1200x1000")

        # Apply ttkbootstrap theme
        self.style = Style(theme="flatly")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create the main Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # 1) Create a Home tab
        self.home_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.home_tab, text="🏠 Home")
        self.setup_home_tab()

        # 2) Create the Blockchain tab (includes Transaction Manager, Add Transaction, and View Properties)
        self.blockchain_tab = BlockchainTab(self.notebook)
        self.notebook.add(self.blockchain_tab, text="🔗 Blockchain")

        # 3) Create the Title Search tab
        self.title_search_tab = TitleTab(self.notebook)
        self.notebook.add(self.title_search_tab, text="📖 Title Search")

        # Quit button at bottom
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.quit_button = self.create_button(self.button_frame, "Exit", self.quit_app, "danger")
        self.quit_button.pack(pady=5)

    def setup_home_tab(self):
        """Populate the Home tab with a welcome label and the three navigation buttons."""
        welcome_label = ttk.Label(
            self.home_tab, text="Welcome to TitleChain 🏠🔗", font=("Helvetica", 20, "bold")
        )
        welcome_label.pack(pady=50)

        # Frame to hold the three main nav buttons
        button_frame = ttk.Frame(self.home_tab)
        button_frame.pack(pady=20)

        self.create_button(
            button_frame, "Submit a Transaction", self.go_to_submit_transaction, "primary"
        ).pack(pady=10)

        self.create_button(
            button_frame, "View Properties", self.go_to_view_properties, "info"
        ).pack(pady=10)

        self.create_button(
            button_frame, "Title Search", self.go_to_title_search, "success"
        ).pack(pady=10)

    def create_button(self, parent, text, command, color):
        btn = Button(parent, text=text, command=command, bootstyle=f"{color}-outline", width=25, padding=10)
        btn.bind("<Enter>", lambda e: btn.configure(bootstyle=f"{color}"))
        btn.bind("<Leave>", lambda e: btn.configure(bootstyle=f"{color}-outline"))
        return btn
    #
    #  Helper methods to switch tabs:
    #
    def go_to_submit_transaction(self):
        """Switch to the Blockchain tab, then select the 'Add Transaction' sub‐tab."""
        self.notebook.select(self.blockchain_tab)  # Switch main notebook to the blockchain tab
        # Now select the 'Add Transaction' page in the blockchain_tab's inner notebook
        self.blockchain_tab.inner_notebook.select(self.blockchain_tab.transaction_form)

    def go_to_view_properties(self):
        """Switch to the Blockchain tab, then select the 'View Properties' sub‐tab."""
        self.notebook.select(self.blockchain_tab)
        self.blockchain_tab.inner_notebook.select(self.blockchain_tab.property_view)

    def go_to_title_search(self):
        """Switch to the top‐level Title Search tab."""
        self.notebook.select(self.title_search_tab)

    def quit_app(self):
        response = messagebox.askyesno("Exit", "Are you sure you want to quit?")
        if response:
            self.destroy()

if __name__ == "__main__":
    app = TitleChainApp()
    app.mainloop()
