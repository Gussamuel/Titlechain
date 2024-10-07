import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from blockchain_tab import BlockchainTab  # Import the blockchain tab class
from mls_tab import MLSTab  # Import the blockchain tab class

class TitleChainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Titlechain")
        self.geometry("400x300")

        # Create a Notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        # Add the MLS tab
        self.mls_tab = MLSTab(self.notebook)
        self.notebook.add(self.mls_tab, text="MLS")
        
        # Add the blockchain tab
        self.blockchain_tab = BlockchainTab(self.notebook)  # Fixed instance name
        self.notebook.add(self.blockchain_tab, text="Blockchain")  # Use the correct instance

        # Create a main menu tab (optional)
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Main Menu")
        self.setup_main_menu()

        self.quit_button = tk.Button(self, text="Quit", command=self.quit)
        self.quit_button.pack(pady=10)

    def setup_main_menu(self):
        # Add content to the main menu tab
        label = tk.Label(self.main_frame, text="Welcome to the Title Blockchain")
        label.pack(pady=20)

    def quit(self):
        response = messagebox.askyesno("Exit", "Are you sure you want to quit?")
        if response:
            self.destroy()

if __name__ == "__main__":
    app = TitleChainApp()
    app.mainloop()