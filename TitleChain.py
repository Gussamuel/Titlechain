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
# Note: Do not instantiate TransactionManager here – it is created inside BlockchainTab.

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

        # Home tab
        self.home_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.home_tab, text="🏠 Home")
        self.setup_home_tab()

        # Blockchain tab – this tab instantiates TransactionManager, TransactionForm, and PropertyView.
        from src.blockchain_tab import BlockchainTab
        self.blockchain_tab = BlockchainTab(self.notebook)
        self.notebook.add(self.blockchain_tab, text="🔗 Blockchain")

        # Title Search tab
        from src.title_search import TitleTab
        self.title_search_tab = TitleTab(self.notebook)
        self.notebook.add(self.title_search_tab, text="📖 Title Search")

        # Quit button
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.quit_button = self.create_rounded_button(self.button_frame, "Exit", self.quit_app, "danger")
        self.quit_button.pack(pady=5)

    def setup_home_tab(self):
        welcome_label = ttk.Label(
            self.home_tab, text="🏡 Welcome to TitleChain", font=("Helvetica", 24, "bold"), foreground="#1976D2"
        )
        welcome_label.pack(pady=40)

        # Navigation Buttons on Home tab.
        button_frame = ttk.Frame(self.home_tab)
        button_frame.pack(pady=20)

        self.create_rounded_button(button_frame, "Submit a Transaction", self.go_to_submit_transaction, "primary").pack(pady=10)
        self.create_rounded_button(button_frame, "View Properties", self.go_to_view_properties, "info").pack(pady=10)
        self.create_rounded_button(button_frame, "Title Search", self.go_to_title_search, "success").pack(pady=10)

    def create_rounded_button(self, parent, text, command, color):
        btn = Button(parent, text=text, command=command, bootstyle=f"{color}-outline", width=25, padding=10)
        btn.bind("<Enter>", lambda e: btn.configure(bootstyle=f"{color}"))
        btn.bind("<Leave>", lambda e: btn.configure(bootstyle=f"{color}-outline"))
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


#Now, i need to make a change to the "revision" portion of the code. specifically, there needs to be an input field below the revision checkbox that is greyed out and nonusable UNLESS the revision checkbox is clicked. once its clicked, the input becomes available. the user CANT submit unless the input box has been filed out. that means the validation needs to be considered as well as the double click feature that displays transaction information. i do NOT want this to be a column, but when the user clicks on the transaction to check the details, the revision note should be there if there is a revision note. lastly, the user needs to be required to pick from a list of transactions from the property view list to "tie" the revision to. the user CANT submit until picking the transaction that the revision is tied to. to prevent mistakes, the policy number from the transaction in the property list MUST match the policy number of their current transaction submission. if it doesn't, they should be required to change the policy number OR pick a new transaction that matches the policy number they have entered. after that, the revised transaction needs to be "paired" with the previous transaction, im not sure how to display this but maybe you can give me some ideas. does this make sense?
#Add debug statements for when the pending_transactions and properties json files get deleted WHILE titlechain is running
#Add short term memory for if pending_transactions gets deleted while titlechain is running, constantly store data, if pending is deleted, recreate it, repopulate it with data. data gets deleted on restart
#Login page so that transactions can be submitted with a name
#refresh blockchain on submission, refresh on restart.