import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from blockchain_tab import BlockchainTab  # Import the BlockchainTab class
#DEMO VERSION, PRIVATE VARIABLES ARE NOT USED, FOR DUMMY TESTING ONLY

class TitleChainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Titlechain")
        self.geometry("800x850")

        # Configure the grid layout for the main window
        self.grid_rowconfigure(0, weight=1)  # Notebook row
        self.grid_rowconfigure(1, weight=0)  # Button row
        self.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Main Menu")
        self.setup_main_menu()

        self.blockchain_tab = BlockchainTab(self.notebook)
        self.notebook.add(self.blockchain_tab, text="Blockchain")

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        self.button_frame.grid_columnconfigure(0, weight=1)

        self.quit_button = ttk.Button(self.button_frame, text="Quit", command=self.quit_app)
        self.quit_button.pack(anchor="center")

    def setup_main_menu(self):
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        label = ttk.Label(self.main_frame, text="Welcome to Titlechain", font=("Arial", 30))
        label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def quit_app(self):
        response = messagebox.askyesno("Exit", "Are you sure you want to quit?")
        if response:
            self.destroy()

if __name__ == "__main__":
    app = TitleChainApp()
    app.mainloop()