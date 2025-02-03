import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from src.blockchain_tab import BlockchainTab
from src.title_search import TitleTab
import pythonnet
import sys
import clr

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
    raise FileNotFoundError(f"❌ Missing DLLs in {sdk_path}: {missing_dlls}")

print("✅ All required DLLs are present in the TitleChain root folder!")

# ✅ Initialize pythonnet
pythonnet.load("coreclr")

# ✅ Load SoftPro assemblies
try:
    clr.AddReference(os.path.join(sdk_path, "SoftPro.Select.Client.dll"))
    clr.AddReference(os.path.join(sdk_path, "SoftPro.Documents.Client.dll"))
    clr.AddReference(os.path.join(sdk_path, "SoftPro.Accounting.Client.dll"))
    print("✅ SoftPro DLLs loaded successfully!")
except Exception as e:
    print(f"❌ Error loading SoftPro DLLs: {e}")

# ✅ Import SoftPro components
try:
    from SoftPro.Select.Client import SelectClient
    from SoftPro.Documents.Client import DocumentManager
    from SoftPro.Accounting.Client import AccountingManager
    print("✅ SoftPro modules imported successfully!")
except ImportError as e:
    print(f"❌ Import Error: {e}")
class TitleChainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("TitleChain")
        self.geometry("1200x1000")
        self.configure(bg="#F0F0F0")  # Light background

        # Apply a canvas gradient for a smooth background
        self.canvas = tk.Canvas(self, width=1200, height=1000)
        self.canvas.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew")
        self.create_gradient(self.canvas)

        # Apply modern style theme
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure styling
        self.style.configure("TFrame", background="#F0F0F0")
        self.style.configure("TLabel", background="#F0F0F0", foreground="black", font=("Helvetica", 12))
        self.style.configure("TButton", font=("Helvetica", 12), padding=10, relief="flat", background="#90CAF9", foreground="black")
        self.style.map("TButton", background=[("active", "#64B5F6")])

        # Fix shrinking tab issue by setting consistent padding and font size
        self.style.configure("TNotebook", background="#F0F0F0", borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            font=("Helvetica", 12, "bold"),  # Keep font consistent
            padding=(20, 10),  # Ensures tabs do not shrink
            background="#E3F2FD",
            foreground="black"
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", "#64B5F6")],  # Active tab color
            foreground=[("selected", "white")],
            padding=[("selected", (20, 10))]  # Prevents shrinking when selected
        )

        # Configure the grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initialize the notebook (tab control)
        self.notebook = ttk.Notebook(self, style="TNotebook")
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Main menu tab
        self.main_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.main_frame, text="🏠  Home")
        self.setup_main_menu()

        # Blockchain tab
        self.blockchain_tab = BlockchainTab(self.notebook)
        self.notebook.add(self.blockchain_tab, text="🔗 Blockchain")

        # Title Search tab
        self.title_search_tab = TitleTab(self.notebook)
        self.notebook.add(self.title_search_tab, text="📖 Title Search")

        # Quit button at the bottom
        self.button_frame = ttk.Frame(self, style="TFrame", borderwidth=0, relief="flat", height=50)  # Set height
        self.button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=0)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.pack_propagate(False)  # Prevent auto-resizing collapse

        self.quit_button = ttk.Button(self.button_frame, text="Exit", command=self.quit_app, style="TButton")
        self.quit_button.pack(anchor="center", pady=5)

    def setup_main_menu(self):
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Title Frame
        title_frame = ttk.Frame(self.main_frame, style="TFrame")
        title_frame.grid(row=0, column=0, padx=20, pady=(40, 10), sticky="n")

        # Welcome Label
        welcome_label = ttk.Label(
            title_frame, text="🏡 Welcome to TitleChain", font=("Helvetica", 24, "bold"), foreground="#1976D2"
        )
        welcome_label.pack(anchor="center")

        # Subheading
        integration_label = ttk.Label(
            title_frame, text="A blockchain-based SoftPro integration.", font=("Helvetica", 16), foreground="black"
        )
        integration_label.pack(anchor="center")

        # Prompt Label
        prompt_label = ttk.Label(
            self.main_frame, text="What would you like to do?", font=("Helvetica", 16), foreground="black"
        )
        prompt_label.grid(row=1, column=0, padx=20, pady=10, sticky="n")

        # Navigation Buttons
        button_frame = ttk.Frame(self.main_frame, style="TFrame")
        button_frame.grid(row=2, column=0, pady=30)

        self.create_modern_button(button_frame, "Submit a Transaction", self.go_to_submit_transaction)
        self.create_modern_button(button_frame, "View Properties", self.go_to_view_properties)
        self.create_modern_button(button_frame, "Title Search", self.go_to_title_search)

    def create_modern_button(self, parent, text, command):
        """Create a modern, rounded button with hover effect"""
        btn = ttk.Button(parent, text=text, command=command, style="TButton", width=25)
        btn.pack(pady=10)
        return btn

    def create_gradient(self, canvas):
        """Create a smooth vertical gradient background"""
        for i in range(100):
            r = min(240 - i, 255)  # Ensure value doesn't exceed 255
            g = min(250 - i, 255)
            b = min(255 - i, 255)
            color = f"#{int(r):02X}{int(g):02X}{int(b):02X}"  # Ensures valid hex format
            canvas.create_line(0, i * 10, 1200, i * 10, fill=color, width=10)

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
