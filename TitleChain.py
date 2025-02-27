import os
import sys
import clr
import pythonnet
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Button
from src.blockchain_tab import BlockchainTab
from src.title_search import TitleTab
from src.transaction_form import TransactionForm
from src.transaction_man import TransactionManager

# ✅ Load SoftPro assemblies (ensure correct path)
sdk_path = os.path.abspath(os.path.dirname(__file__))  # TitleChain root folder
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

# ✅ Initialize pythonnet
pythonnet.load("coreclr")

# ✅ Load SoftPro assemblies
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

        # Initialize Transaction Manager
        self.transaction_manager = TransactionManager(self)

        # Pass transaction manager callback to form
        self.transaction_form = TransactionForm(self, add_transaction_callback=self.transaction_manager.add_pending_transaction)

        # ✅ Apply ttkbootstrap theme for modern styling
        self.style = Style(theme="flatly")  # Try "superhero", "minty", "darkly" for different looks

        # Configure the grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initialize the notebook (tab control)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Main menu tab
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="🏠  Home")
        self.setup_main_menu()

        # Blockchain tab
        self.blockchain_tab = BlockchainTab(self.notebook)
        self.notebook.add(self.blockchain_tab, text="🔗 Blockchain")

        # Title Search tab
        self.title_search_tab = TitleTab(self.notebook)
        self.notebook.add(self.title_search_tab, text="📖 Title Search")

        # Quit button at the bottom
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.quit_button = self.create_rounded_button(self.button_frame, "Exit", self.quit_app, "danger")
        self.quit_button.pack(pady=5)

    def setup_main_menu(self):
        """Set up the main menu UI"""
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Welcome Label
        title_frame = ttk.Frame(self.main_frame)
        title_frame.grid(row=0, column=0, padx=20, pady=(40, 10), sticky="n")

        welcome_label = ttk.Label(
            title_frame, text="🏡 Welcome to TitleChain", font=("Helvetica", 24, "bold"), foreground="#1976D2"
        )
        welcome_label.pack(anchor="center")

        # Prompt Label
        prompt_label = ttk.Label(self.main_frame, text="What would you like to do?", font=("Helvetica", 16))
        prompt_label.grid(row=1, column=0, padx=20, pady=10, sticky="n")

        # Navigation Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, pady=30)

        self.create_rounded_button(button_frame, "Submit a Transaction", self.go_to_submit_transaction, "primary").pack(pady=10)
        self.create_rounded_button(button_frame, "View Properties", self.go_to_view_properties, "info").pack(pady=10)
        self.create_rounded_button(button_frame, "Title Search", self.go_to_title_search, "success").pack(pady=10)

    def create_rounded_button(self, parent, text, command, color):
        """Create a fully rounded ttkbootstrap button with a hover effect."""
        btn = Button(parent, 
                    text=text, 
                    command=command, 
                    bootstyle=f"{color}-outline", 
                    width=25, 
                    padding=10)

        # ✅ Make button rounded (explicitly set corner radius)
        btn.configure(style=f"{color}.TButton")  # Apply rounded style

        # ✅ Add hover effect (change style on hover)
        btn.bind("<Enter>", lambda e: btn.configure(bootstyle=f"{color}"))  # Solid fill on hover
        btn.bind("<Leave>", lambda e: btn.configure(bootstyle=f"{color}-outline"))  # Outline when not hovering

        return btn
    
    def go_to_submit_transaction(self):
        self.notebook.select(self.blockchain_tab)
        self.blockchain_tab.inner_notebook.select(self.blockchain_tab.transaction_form)

    def go_to_view_properties(self):
        self.notebook.select(self.blockchain_tab)
        self.blockchain_tab.inner_notebook.select(self.blockchain_tab.property_view)

    def go_to_title_search(self):
        self.notebook.select(self.title_search_tab)

    def quit_app(self):
        response = messagebox.askyesno("Exit", "Are you sure you want to quit?")
        if response:
            self.destroy()


if __name__ == "__main__":
    app = TitleChainApp()
    app.mainloop()
