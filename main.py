import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from blockchain_tab import BlockchainTab  # Import the BlockchainTab class

class TitleChainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("TitleChain")
        self.geometry("800x600")

        # Configure the grid layout for the main window
        self.grid_rowconfigure(0, weight=1)  # Notebook row
        self.grid_rowconfigure(1, weight=0)  # Button row
        self.grid_columnconfigure(0, weight=1)

        # Initialize the notebook (tab control)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Main menu tab
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Main Menu")
        self.setup_main_menu()

        # Blockchain tab (contains transaction form and property view)
        self.blockchain_tab = BlockchainTab(self.notebook)
        self.notebook.add(self.blockchain_tab, text="Blockchain")

        # Quit button at the bottom
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.quit_button = ttk.Button(self.button_frame, text="Quit", command=self.quit_app)
        self.quit_button.pack(anchor="center")

    def setup_main_menu(self):
        # Configure grid for the main_frame
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Welcome label
        welcome_label = ttk.Label(
            self.main_frame,
            text="Welcome to TitleChain",
            font=("Helvetica", 24, "bold")
        )
        welcome_label.grid(row=0, column=0, padx=20, pady=(40, 10), sticky="n")

        # Subheading label
        prompt_label = ttk.Label(
            self.main_frame,
            text="What would you like to do?",
            font=("Helvetica", 16)
        )
        prompt_label.grid(row=1, column=0, padx=20, pady=10, sticky="n")

        # Frame for navigation buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, pady=30)

        # Submit Transaction button
        submit_btn = ttk.Button(
            button_frame,
            text="Submit a Transaction",
            command=self.go_to_submit_transaction,
            width=25
        )
        submit_btn.pack(pady=10)

        # View Properties button
        view_btn = ttk.Button(
            button_frame,
            text="View Properties",
            command=self.go_to_view_properties,
            width=25
        )
        view_btn.pack(pady=10)

        # Additional navigation buttons can be added here
        # Example:
        # settings_btn = ttk.Button(
        #     button_frame,
        #     text="Settings",
        #     command=self.go_to_settings,
        #     width=25
        # )
        # settings_btn.pack(pady=10)

    def go_to_submit_transaction(self):
        # Switch to the Blockchain tab and select the "Add Transaction" sub-tab
        self.notebook.select(self.blockchain_tab)
        self.blockchain_tab.inner_notebook.select(self.blockchain_tab.transaction_form)

    def go_to_view_properties(self):
        # Switch to the Blockchain tab and select the "View Properties" sub-tab
        self.notebook.select(self.blockchain_tab)
        self.blockchain_tab.inner_notebook.select(self.blockchain_tab.property_view)

    def quit_app(self):
        response = messagebox.askyesno("Exit", "Are you sure you want to quit?")
        if response:
            self.destroy()

if __name__ == "__main__":
    app = TitleChainApp()
    app.mainloop()