import os
import sys
import clr
import pythonnet
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Button
from src.login import LoginGUI

# 1) Define all subdirectories under TitleChain where DLLs might live.
#    These paths are relative to the TitleChain root folder (or sys._MEIPASS when frozen).
DLL_SUBDIRS = [
    r"DLLs\softpro.select.controls.sdk.4.5.5\lib\net46",
    r"DLLs\softpro.select.core.sdk.4.5.5\lib\net46",
    r"DLLs\softpro.select.plugin.sdk.4.6.8\build",
    r"DLLs\softpro.select.server.sdk.4.6.8\build",
    r"DLLs\softpro.select.shell.sdk.4.6.8\build",
    r"nonDLLs\softpro.select.controls.4.6.8\lib\net46",
    r"nonDLLs\softpro.select.core.4.6.8\lib\net46",
    r"nonDLLs\softpro.select.plugin.4.5.5\build",
    r"nonDLLs\softpro.select.server.core.4.6.8\lib\net46",
    r"nonDLLs\softpro.select.shell.core.4.6.8\lib\net46",
]

# 2) List of required DLL filenames.
REQUIRED_DLLS = [
    "SoftPro.OrderTracking.Controls.dll",
    "SoftPro.OrderTracking.SnapSections.dll",
    "SoftPro.Select.Controls.dll",
    "SoftPro.Accounting.Client.dll",
    "SoftPro.ClientModel.dll",
    "SoftPro.Documents.Client.dll",
    "SoftPro.EntityModel.dll",
    "SoftPro.Imaging.Client.dll",
    "SoftPro.OrderTracking.Client.dll",
    "SoftPro.ProceedsTracking.Client.dll",
    "SoftPro.Register.Client.dll",
    "SoftPro.Reporting.Client.dll",
    "SoftPro.Select.Client.dll",
    "Mono.Cecil.dll",
    "Mono.Cecil.Mdb.dll",
    "Mono.Cecil.Pdb.dll",
    "Mono.Cecil.Rocks.dll",
    "Newtonsoft.Json.dll",
    "NuGet.Common.dll",
    "NuGet.Configuration.dll",
    "NuGet.Frameworks.dll",
    "NuGet.Packaging.Core.dll",
    "NuGet.Packaging.dll",
    "NuGet.Versioning.dll",
    "SoftPro.Select.Sdk.Tasks.dll",
    "SoftPro.Accounting.Controls.dll",
    "SoftPro.OrderTracking.Controls.dll",
    "SoftPro.OrderTracking.SnapSections.dll",
    "SoftPro.Select.OrderTracking.Shared.dll",
    "SoftPro.PersistenceModel.dll",
    "SoftPro.Select.Service.dll",
    "SoftPro.ServerModel.dll",
    "SoftPro.Select.Shell.dll"
]

# 3) Determine the base directory.
if getattr(sys, 'frozen', False):
    # When frozen (using PyInstaller), sys._MEIPASS holds the temp folder.
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.abspath(os.path.dirname(__file__))

if base_dir not in sys.path:
    sys.path.append(base_dir)

# 4) Search for each required DLL in the subdirectories (relative to base_dir).
dll_candidates = {dll: [] for dll in REQUIRED_DLLS}

for subdir in DLL_SUBDIRS:
    full_subdir = os.path.join(base_dir, subdir)
    if not os.path.isdir(full_subdir):
        print(f"DEBUG: ❌ Directory does not exist: {full_subdir}")
        continue
    for dll in REQUIRED_DLLS:
        candidate_path = os.path.join(full_subdir, dll)
        if os.path.exists(candidate_path):
            dll_candidates[dll].append(candidate_path)

# Also check in the base directory itself.
for dll in REQUIRED_DLLS:
    candidate_path = os.path.join(base_dir, dll)
    if os.path.exists(candidate_path):
        dll_candidates[dll].append(candidate_path)

# 5) Verify that each required DLL was found at least once.
missing = [dll for dll in REQUIRED_DLLS if not dll_candidates[dll]]
if missing:
    raise FileNotFoundError(f"DEBUG: ❌ Missing DLLs in specified subdirectories and base: {missing}")

print("DEBUG: ✅ All required DLLs were located in the specified directories or base directory!")

# 6) Initialize pythonnet and load the DLL references.
pythonnet.load("coreclr")

for dll in REQUIRED_DLLS:
    # Load the first found instance for each DLL.
    dll_path = dll_candidates[dll][0]
    try:
        clr.AddReference(dll_path)
        print(f"DEBUG: ✅ {dll} loaded from: {dll_path}")
    except Exception as e:
        print(f"DEBUG: ❌ Error loading {dll_path}: {e}")

def center_window(win, width, height):
    win.update_idletasks()  # Ensure win.winfo_screenwidth() is accurate
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

class TitleChainApp(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("TitleChain")
        desired_width = 1800
        desired_height = 900
        center_window(self, desired_width, desired_height)
        self.resizable(False, False)
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

        # Blockchain tab – instantiate TransactionManager, TransactionForm, PropertyView.
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
            sys.exit()

if __name__ == "__main__":
    # Launch the login UI first.
    print("DEBUG: ❌✅❌✅❌✅ TITLECHAIN.PY MAIN")
    login_app = LoginGUI()
    login_app.mainloop()

# Now, i need to make a change to the "revision" portion of the code. specifically, there needs to be an input field below the revision checkbox that is greyed out and nonusable UNLESS the revision checkbox is clicked. once its clicked, the input becomes available. the user CANT submit unless the input box has been filed out. that means the validation needs to be considered as well as the double click feature that displays transaction information. i do NOT want this to be a column, but when the user clicks on the transaction to check the details, the revision note should be there if there is a revision note. lastly, the user needs to be required to pick from a list of transactions from the property view list to "tie" the revision to. the user CANT submit until picking the transaction that the revision is tied to. to prevent mistakes, the policy number from the transaction in the property list MUST match the policy number of their current transaction submission. if it doesn't, they should be required to change the policy number OR pick a new transaction that matches the policy number they have entered. after that, the revised transaction needs to be "paired" with the previous transaction, im not sure how to display this but maybe you can give me some ideas. does this make sense?
# Add debug statements for when the pending_transactions and properties json files get deleted WHILE titlechain is running
# Add short term memory for if pending_transactions gets deleted while titlechain is running, constantly store data, if pending is deleted, recreate it, repopulate it with data. data gets deleted on restart
# Login page so that transactions can be submitted with a name
# refresh blockchain on submission, refresh on restart.
# Fix the compile command so it can simply be "pyinstaller --onefile --add-data "DLLs;DLLs" --add-data "nonDLLs;nonDLLs" --add-data "data;data" Titlechain.py
# Access DLL files from their respective locations

# 1. Create a login GUI where the person can register to be a user (first name, last name, email, assign them a user number that's unique to them), but only certain users have the ability to CREATE databases if there isn't already a TitleChainDb in existence.There will be a list of users somewhere with certain permissions (this list should be stored in the "data" folder which will eventually be made private unless its for application use)

# 2. Create GUI for database connection. If the user cancels, titlechain closes. If not and the database doesn't exist, it will ask the user to create a new TitleChainDb (the user MUST have the permissions to do so, and if not, the program closes) and the columns will be

#             "Property Address", 
#             "Policy Date",
#             "Policy Number",  
#             "Vested Parties",
#             "Underwriters", 
#             "Coverage Amount",
#             "Owner's Policy",
#             "Lender's Policy",
#             "Standard Policy Exceptions", 
#             "Property Specific Exceptions", 
#             "Legal Description/Derivation Clause",
#             "Revision",

# 3. Once the titlechaindb exists, it will only ask the user to connect to a database on startup as opposed to creating one. the titlechaindb should be the only option because it was created by titlechain.

# 4. lastly we need to boot titlechain at the same time that softpro launches, which can be solved if we have titlechain launch on startup every time.








# 5. Clean up the UI, make buttons look nice, make sure window sizes are right, make sure style are right
#
# 6. Fix formatting for transaction_from, specifically the data formatting and the entry of the data
#
# 7. DONE/CHECK                   Fix double click view within property view and transaction manager, specifically center viewing, no expanding, and all data can be viewed (test with more data in the vest parties section)
# 
# 8. !!!!!!!!!!!!Revision tag. if the revised box is checked, a note is required in order to process. Potentially the revision to another entry in the DB. Ability to double click a property in the list which then allows you to create a revision for it, taking you to the submit transaction screen with details already filled in ready for change.
#
# 9. DONE                         Dont allow multiple windows to open for ANYTHING, check every window event
#
# 10. Adjust debug to where teh fetched properties display more elegantly.
#
# 11. Populate DB with a bunch of properties.
#
# 12. DONE                  Fix "Revisions" so they show yes's and no's.
#
# 13. Edit the scheduled task to where titlechain will open again after softpro is closed.
#
# 14. DONE                  REMOVED TRANSACTION ID CREATION. AFTER A SUBMISSION TO THE BLOCKCHAIN, GET THAT TRANSACTION AND THE TRANSACTION ID FROM THE BLOCKCHAIN AND MOVE IT TO THE DATABSE. REMOVE TRANSACTION ID CREATION
#
# 15. use http://192.168.1.24:5000/blocks/1 (create an iterator for the blocks as well as parsing through them)
#
# 16. Compare blockchain and database transaction IDs so we dont get dupes in the db
#
# 17. First time data import from Rudy title DB to titlechainDB and blockchain
#
# 18. Softpro functions need to be done, outputs needs to be done