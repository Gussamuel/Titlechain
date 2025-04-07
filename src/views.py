import tkinter as tk
from tkinter import ttk
import os
import sys
import json
import requests, ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from requests.exceptions import SSLError, ConnectTimeout

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLSv1_2,
            **pool_kwargs
        )

def center_window(win, width, height):
    win.update_idletasks()  # Ensure dimensions are updated
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

def fetch_properties_from_db():
    """
    Attempts to fetch properties from the TitleChainDb database.
    Returns a list of property dictionaries on success, or None on failure.
    Assumes that a persistent DB connection has been stored in db_connection_global.connection.
    """
    try:
        from src.db_connection_global import connection as db_conn
    except ImportError as e:
        print("DEBUG: Failed to import persistent DB connection:", e)
        return None

    if db_conn is None:
        print("DEBUG: No persistent DB connection available in fetch_properties_from_db.")
        return None

    try:
        cursor = db_conn.cursor()
        query = """
            SELECT 
                transaction_id AS "Transaction ID",
                property_address AS "Property Address", 
                policy_date AS "Policy Date", 
                policy_number AS "Policy Number", 
                vested_parties AS "Vested Parties", 
                underwriters AS "Underwriters", 
                coverage_amount AS "Coverage Amount", 
                owners_policy AS "Owner's Policy", 
                lenders_policy AS "Lender's Policy", 
                standard_policy_exceptions AS "Standard Policy Exceptions", 
                property_specific_exceptions AS "Property Specific Exceptions", 
                legal_description AS "Legal Description/Derivation Clause", 
                revised AS "Revised"
            FROM Orders
        """
        print("DEBUG: Executing DB query to fetch properties.")
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            print("DEBUG: No properties found in DB.")
            return []  # Returning empty list to indicate query succeeded but no entries were found.
        columns = [column[0] for column in cursor.description]
        properties = [dict(zip(columns, row)) for row in rows]
        print("DEBUG: Fetched properties from DB:", properties)
        return properties
    except Exception as e:
        print("DEBUG: Exception in fetch_properties_from_db:", e)
        return None

class PropertyView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Updated columns: added "Transaction ID" as the first column.
        self.columns = [
            "Transaction ID",
            "Property Address", 
            "Policy Date",
            "Policy Number",         # New column for Policy Number
            "Vested Parties",
            "Underwriters", 
            "Coverage Amount", 
            "Owner's Policy",
            "Lender's Policy",
            "Standard Policy Exceptions", 
            "Property Specific Exceptions",
            "Legal Description/Derivation Clause",
            "Revised",
            "Revision"
        ]

        self.data = []  # Store the properties data locally for filtering
        # Determine the base directory.
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running as a PyInstaller bundle – assume the EXE is in TitleChain\dist,
            # so go up one level to TitleChain, then into the data folder.
            base_dir = os.path.dirname(os.path.dirname(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        properties_file = os.path.join(base_dir, "data", "properties.json")
        if not os.path.exists(properties_file):
            print(f"DEBUG: ❌ properties.json not found on startup at {properties_file}. Creating new file.")
            try:
                with open(properties_file, "w") as f:
                    json.dump([], f)
                print(f"DEBUG: ✅ properties.json created successfully on startup at {properties_file}.")
            except Exception as e:
                print("DEBUG: ❌ Could not create properties.json on startup:", e)
        else:
            print(f"DEBUG: ✅ properties.json found on startup at {properties_file}.")

        # Configure the grid to make widgets expand
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Search frame
        search_frame = ttk.Frame(self)
        search_frame.grid(row=0, column=0, sticky='ew', pady=5)
        search_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky='ew', padx=5)

        search_btn = ttk.Button(search_frame, text="Search", command=self.search_properties)
        search_btn.grid(row=0, column=2, padx=5)

        reset_btn = ttk.Button(search_frame, text="Reset", command=self.reset_search)
        reset_btn.grid(row=0, column=3, padx=5)

        # Create a frame for the Treeview and scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky='nsew')

        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show='headings')

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Define columns with left alignment.
        for col in self.columns:
            self.tree.heading(col, text=col, anchor='w')
            self.tree.column(col, width=120, anchor='w')

        self.display_no_data_message()

        refresh_btn = ttk.Button(self, text="Refresh", command=self.refresh_view)
        refresh_btn.grid(row=2, column=0, pady=10)

        # Bind double-click to show property details.
        self.tree.bind("<Double-1>", self.on_double_click)

    def display_no_data_message(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.tree.insert("", tk.END, values=["No data available"] + [""] * (len(self.columns) - 1))
        print("DEBUG: ✅ No properties available; displaying message.")

    def reset_search(self):
        self.search_var.set("")
        print("DEBUG: ✅ Search reset.")
        self.refresh_view()

    def refresh_view(self):
        # Clear existing rows in the Treeview.
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Define the blockchain endpoint template.
        blockchain_url_template = "http://192.168.1.29:5000/blocks/{}"
        
        # Create a requests session with our TLS adapter.
        session = requests.Session()
        session.mount("https://", TLSAdapter())

        print("DEBUG: ✅ Attempting to fetch properties from blockchain...")

        # First, fetch block 1.
        block1_url = blockchain_url_template.format(1)
        try:
            print(f"DEBUG: Fetching block 1 from: {block1_url}")
            response = session.get(block1_url, timeout=10, verify=False)
            response.raise_for_status()
            block1_data = response.json()
        except Exception as e:
            print("DEBUG: ❌ Exception while fetching block 1:", e)
            block1_data = None

        # If block 1 returns data, accumulate transactions from it and subsequent blocks.
        if block1_data:
            if isinstance(block1_data, dict) and "transactions" in block1_data:
                all_transactions = block1_data["transactions"]
                print(f"DEBUG: Block 1 contains {len(all_transactions)} transaction(s).")
            elif isinstance(block1_data, list):
                all_transactions = block1_data
                print(f"DEBUG: Block 1 returned a list with {len(all_transactions)} transaction(s).")
            else:
                print("DEBUG: ❌ Unexpected format for block 1.")
                all_transactions = []

            # Iterate over subsequent blocks until a block returns 404 or empty.
            block_num = 2
            while True:
                current_url = blockchain_url_template.format(block_num)
                try:
                    print(f"DEBUG: Fetching block {block_num} from: {current_url}")
                    response = session.get(current_url, timeout=10, verify=False)
                    # If the block is out-of-range, the server should return 404.
                    if response.status_code == 404:
                        print(f"DEBUG: Block {block_num} returned 404 (no more blocks). Ending iteration.")
                        break
                    response.raise_for_status()
                    block_data = response.json()
                    if not block_data:
                        print(f"DEBUG: Block {block_num} returned no data. Ending iteration.")
                        break
                    if isinstance(block_data, dict) and "transactions" in block_data:
                        tx_list = block_data["transactions"]
                        print(f"DEBUG: Block {block_num} contains {len(tx_list)} transaction(s).")
                        all_transactions.extend(tx_list)
                    elif isinstance(block_data, list):
                        print(f"DEBUG: Block {block_num} returned a list with {len(block_data)} transaction(s).")
                        all_transactions.extend(block_data)
                    else:
                        print(f"DEBUG: Block {block_num} returned unexpected format.")
                    block_num += 1
                except Exception as e:
                    # If we catch an exception and it’s due to a 404, break out.
                    if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                        print(f"DEBUG: Block {block_num} not found (404). Ending iteration.")
                    else:
                        print(f"DEBUG: Exception while fetching block {block_num}: {e}")
                    break

            self.data = all_transactions
        else:
            # If block 1 returns no data, fall back to the DB.
            print("DEBUG: ❌ Could not fetch properties from blockchain (block 1 empty). Attempting to load from DB...")
            try:
                db_data = fetch_properties_from_db()
            except Exception as e:
                print("DEBUG: Exception while fetching DB data:", e)
                db_data = None

            if db_data is None or len(db_data) == 0:
                print("DEBUG: ❌ Could not fetch properties from DB. Loading from properties.json...")
                try:
                    if getattr(sys, 'frozen', False):
                        base_dir = os.path.dirname(os.path.dirname(sys.executable))
                    else:
                        base_dir = os.path.dirname(os.path.abspath(__file__))
                    properties_file = os.path.join(base_dir, "data", "properties.json")
                    with open(properties_file, "r") as f:
                        self.data = json.load(f)
                    print(f"DEBUG: ✅ Loaded properties from properties.json at {properties_file}.")
                except Exception as e:
                    print("DEBUG: ❌ Error loading properties from properties.json:", e)
                    self.data = []
            else:
                print("DEBUG: ✅ Fetched properties from DB. Row count:", len(db_data))
                self.data = db_data

        # If data is still empty, display the no-data message.
        if not self.data:
            self.display_no_data_message()
            return

        # Update the Treeview with the data.
        for prop in self.data:
            # Ensure prop is a dict. If not, try to parse it.
            if not isinstance(prop, dict):
                try:
                    prop = json.loads(prop)
                except Exception as e:
                    print("DEBUG: Could not parse property entry as dict:", prop, e)
                    continue

            # Process the revision value for display.
            if "Revised" in prop:
                revised_val = prop["Revised"]
                revision_display = "Yes" if revised_val else "No"
            else:
                revision_raw = prop.get("Revision", "")
                try:
                    rev_int = int(revision_raw)
                    revision_display = "Yes" if rev_int == 1 else "No" if rev_int == 0 else str(revision_raw)
                except Exception:
                    if str(revision_raw).lower() in ["yes"]:
                        revision_display = "Yes"
                    elif str(revision_raw).lower() in ["no"]:
                        revision_display = "No"
                    else:
                        revision_display = str(revision_raw)
            
            self.tree.insert("", tk.END, values=( 
                prop.get("Transaction ID", "N/A"),
                prop.get("Property Address", ""),
                prop.get("Policy Date", ""),
                prop.get("Policy Number", ""),
                prop.get("Vested Parties", ""),
                prop.get("Underwriters", ""),
                prop.get("Coverage Amount", ""),
                prop.get("Owner's policy", ""),
                prop.get("Lender Policy", ""),
                prop.get("Standard Policy Exception", ""),
                prop.get("Property Specific Exceptions", ""),
                prop.get("Legal Description", ""),
                revision_display
            ))
        
        print(f"DEBUG: Total entries loaded: {len(self.data)}")
        print("DEBUG: ✅ Properties refreshed.")

        # Print each transaction in a human-readable format.
        print("DEBUG: Fetched the following properties:")
        for idx, prop in enumerate(self.data, start=1):
            print(f"\n       Entry {idx}:")
            for key, val in prop.items():
                print(f"          {key}: {val}")

    def search_properties(self):
        query = self.search_var.get().lower()
        filtered_data = [
            prop for prop in self.data
            if any(query in str(value).lower() for value in prop.values())
        ]
        for row in self.tree.get_children():
            self.tree.delete(row)
        if not filtered_data:
            self.display_no_data_message()
            return
        for prop in filtered_data:
            self.tree.insert("", tk.END, values=(
                prop.get("Transaction ID", "N/A"),
                prop.get("Property Address", ""),
                prop.get("Policy Date", ""),
                prop.get("Policy Number", ""),   # New field
                prop.get("Vested Parties", ""),
                prop.get("Underwriters", ""),
                prop.get("Coverage Amount", ""),
                prop.get("Owner's Policy", ""),
                prop.get("Lender's Policy", ""),
                prop.get("Standard Policy Exceptions", ""),
                prop.get("Property Specific Exceptions", ""),
                prop.get("Legal Description/Derivation Clause", ""),
                prop.get("Revised", "")
            ))
        print("DEBUG: Searching for:", query)

    def on_double_click(self, event):
        rowid = self.tree.identify_row(event.y)
        if not rowid:
            return
        idx = self.tree.index(rowid)
        try:
            prop = self.data[idx]
        except IndexError:
            print("DEBUG: ❌ Double-click index out of range.")
            return
        self.show_property_details(prop)
        print("DEBUG: ✅ Displaying property details.")

    def show_property_details(self, prop):
        details_win = tk.Toplevel(self)
        details_win.title("Property Details")
        center_window(details_win, 600, 400)
        frame = ttk.Frame(details_win, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Convert revised for display if necessary.
        rev = prop.get("Revised", "N/A")
        try:
            rev_int = int(rev)
            revised_display = "Yes" if rev_int == 1 else ("No" if rev_int == 0 else str(rev))
        except Exception:
            revised_display = str(rev)
        
        # Include Transaction ID as the first field.
        fields = [
            ("Transaction ID", prop.get("Transaction ID", "N/A")),
            ("Property Address", prop.get("Property Address", "N/A")),
            ("Policy Date", prop.get("Policy Date", "N/A")),
            ("Policy Number", prop.get("Policy Number", "N/A")),
            ("Vested Parties", prop.get("Vested Parties", "N/A")),
            ("Underwriters", prop.get("Underwriters", "N/A")),
            ("Coverage Amount", prop.get("Coverage Amount", "N/A")),
            ("Owner's Policy", prop.get("Owner's Policy", "N/A")),
            ("Lender's Policy", prop.get("Lender's Policy", "N/A")),
            ("Standard Policy Exceptions", prop.get("Standard Policy Exceptions", "N/A")),
            ("Property Specific Exceptions", prop.get("Property Specific Exceptions", "N/A")),
            ("Legal Description/Derivation Clause", prop.get("Legal Description/Derivation Clause", "N/A")),
            ("Revised", revised_display)
        ]
        if str(prop.get("Revised", "No")).lower() in ["yes", "1"]:
            fields.append(("Revision Note", prop.get("Revision Note", "N/A")))
            fields.append(("Revision Parent Policy", prop.get("Revision Parent Policy", "N/A")))
        
        for idx, (key, value) in enumerate(fields):
            ttk.Label(frame, text=f"{key}:", font=("Helvetica", 10, "bold"), anchor="w")\
               .grid(row=idx, column=0, sticky="w", pady=2)
            ttk.Label(frame, text=value, font=("Helvetica", 10), anchor="w")\
               .grid(row=idx, column=1, sticky="w", pady=2)
        
        ttk.Button(frame, text="Close", command=details_win.destroy)\
           .grid(row=len(fields), column=0, columnspan=2, pady=10)
