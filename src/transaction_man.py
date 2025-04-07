import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import os
import sys
import json
import requests
import re

def center_window(win, width, height):
    win.update_idletasks()  # Ensure dimensions are updated
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

class TransactionManager(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_dir = os.path.dirname(os.path.dirname(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        # Set the pending transactions file inside the "data" folder.
        self.pending_file = os.path.join(base_dir, "data", "pending_transactions.json")
        if not os.path.exists(self.pending_file):
            print(f"DEBUG: ❌ pending_transactions.json not found at {self.pending_file}. Creating new file.")
            try:
                with open(self.pending_file, "w") as f:
                    json.dump([], f)
                print(f"DEBUG: ✅ pending_transactions.json created successfully at {self.pending_file}.")
            except Exception as e:
                print("DEBUG: ❌ Could not create pending_transactions.json:", e)
        else:
            print(f"DEBUG: ✅ pending_transactions.json found at {self.pending_file}.")

        # Load pending transactions from file.
        try:
            with open(self.pending_file, "r") as f:
                data = json.load(f)
            for transaction in data:
                if "timestamp" in transaction:
                    transaction["timestamp"] = datetime.fromisoformat(transaction["timestamp"])
            self.pending_transactions = data
            print("DEBUG: ✅ Loaded pending transactions from file.")
        except Exception as e:
            print("DEBUG: ❌ Error loading pending transactions:", e)
            self.pending_transactions = []
        
        self.dirty = False

        # Configure grid layout.
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Button frame.
        button_frame = ttk.Frame(self)
        button_frame.grid(row=0, column=0, sticky="ew", pady=10, padx=10)
        button_frame.grid_columnconfigure(0, weight=1)
        self.delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_transaction)
        self.delete_button.pack(side="left", padx=10)
        
        # Frame for Treeview and scrollbars.
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        columns = (
            "Select",
            "Property Address", 
            "Policy Date",
            "Policy Number",              # New column for Policy Number
            "Vested Parties",
            "Underwriters", 
            "Coverage Amount",
            "Owner's Policy",
            "Lender's Policy",
            "Standard Policy Exceptions", 
            "Property Specific Exceptions", 
            "Legal Description/Derivation Clause",
            "Revised",
            "Revision",
            "Remaining Time"
        )
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            if col == "Select":
                self.tree.heading(col, text=col, anchor="center")
                self.tree.column(col, width=50, anchor="center")
            else:
                self.tree.heading(col, text=col, anchor="w")
                self.tree.column(col, anchor="w", minwidth=0)
        
        style = ttk.Style(self)
        style.configure("Treeview.Heading", padding=(0, 0))
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.bind("<Configure>", self.adjust_column_widths)
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<Double-1>", self.on_double_click)
        
        self.after(1000, self.remove_expired_transactions)
        self.update_transactions()
    
    def adjust_column_widths(self, event=None):
        total_width = self.tree.winfo_width()
        num_columns = len(self.tree["columns"])
        select_width = 50
        other_width = (total_width - select_width) // (num_columns - 1) if num_columns > 1 else total_width
        for col in self.tree["columns"]:
            if col == "Select":
                self.tree.column(col, width=select_width)
            else:
                self.tree.column(col, width=other_width)
    
    def on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        col = self.tree.identify_column(event.x)
        if col == "#1":
            rowid = self.tree.identify_row(event.y)
            if rowid:
                try:
                    idx = int(rowid)
                except ValueError:
                    return
                current = self.pending_transactions[idx].get("selected", False)
                self.pending_transactions[idx]["selected"] = not current
                self.dirty = True
                print("DEBUG: ✅ Toggled selection for transaction at index", idx)
                self.update_transactions()
    
    def on_double_click(self, event):
        rowid = self.tree.identify_row(event.y)
        if not rowid:
            return
        idx = self.tree.index(rowid)
        try:
            transaction = self.pending_transactions[idx]
        except IndexError:
            print("DEBUG: ❌ Double-click index out of range.")
            return
        self.show_transaction_details(transaction)
        print("DEBUG: ✅ Displaying transaction details.")
    
    def show_transaction_details(self, transaction):
        details_win = tk.Toplevel(self)
        details_win.title("Transaction Details")
        center_window(details_win, 600, 400)
        frame = ttk.Frame(details_win, padding=10)
        frame.pack(fill="both", expand=True)
        
        fields = [
            ("Property Address", transaction.get("Property Address", "N/A")),
            ("Policy Date", transaction.get("Policy Date", "N/A")),
            ("Policy Number", transaction.get("Policy Number", "N/A")),
            ("Vested Parties", transaction.get("Vested Parties", "N/A")),
            ("Underwriters", transaction.get("Underwriters", "N/A")),
            ("Coverage Amount", transaction.get("Coverage Amount", "N/A")),
            ("Owner's Policy", transaction.get("Owner's Policy", "N/A")),
            ("Lender's Policy", transaction.get("Lender's Policy", "N/A")),
            ("Standard Policy Exceptions", transaction.get("Standard Policy Exceptions", "N/A")),
            ("Property Specific Exceptions", transaction.get("Property Specific Exceptions", "N/A")),
            ("Legal Description/Derivation Clause", transaction.get("Legal Description/Derivation Clause", "N/A")),
            ("Revised", transaction.get("Revised", "N/A"))
        ]
        if transaction.get("Revised", "No") == "Yes":
            fields.append(("Revision Note", transaction.get("Revision Note", "N/A")))
            fields.append(("Revision Parent Policy", transaction.get("Revision Parent Policy", "N/A")))
        
        for idx, (key, value) in enumerate(fields):
            ttk.Label(frame, text=f"{key}:", font=("Helvetica", 10, "bold"), anchor="w")\
               .grid(row=idx, column=0, sticky="w", pady=2)
            ttk.Label(frame, text=value, font=("Helvetica", 10), anchor="w")\
               .grid(row=idx, column=1, sticky="w", pady=2)
        
        ttk.Button(frame, text="Close", command=details_win.destroy)\
           .grid(row=len(fields), column=0, columnspan=2, pady=10)
    
    def add_pending_transaction(self, transaction):
        transaction['timestamp'] = datetime.now()
        transaction["selected"] = False

        street = transaction.get("Street", "").strip()
        apt = transaction.get("Apt/Building (if applicable)", "").strip()
        city = transaction.get("City", "").strip()
        state = transaction.get("State", "").strip()
        zip_code = transaction.get("Zip", "").strip()
        address_parts = [street]
        if apt:
            address_parts.append(apt)
        address_parts.append(city)
        address_parts.append(state)
        address_parts.append(zip_code)
        transaction["Property Address"] = ", ".join([part for part in address_parts if part])
        
        transaction["Policy Date"] = transaction.get("Policy Date (MM/DD/YYYY)", "").strip()
        transaction["Policy Number"] = transaction.get("Policy Number", "").strip()
        transaction["Legal Description/Derivation Clause"] = transaction.get("Legal Description", "").strip()
        
        spe = transaction.get("Standard Policy Exceptions", "")
        if not isinstance(spe, str):
            standard_exceptions_map = {
                "1. Rights or claims of parties in possession not shown by the public records.": "1",
                "2. Easements or claims of easements not shown by the public records.": "2",
                "3. Encroachments, overlaps, boundary line disputes, or other matters disclosed by an accurate survey.": "3",
                "4. Any lien, or right to a lien, for services, labor or material not shown by the public records.": "4",
                "5. Taxes or special assessments not yet due or payable.": "5",
            }
            try:
                selected_exceptions = [standard_exceptions_map[exc] for exc in spe]
                transaction["Standard Policy Exceptions"] = ", ".join(selected_exceptions) if selected_exceptions else "None"
                print("DEBUG: ✅ Processed standard policy exceptions.")
            except Exception as e:
                print("DEBUG: ❌ Conversion error while processing standard policy exceptions:", e)
                transaction["Standard Policy Exceptions"] = "None"
        self.pending_transactions.append(transaction)
        self.dirty = True
        self.update_transactions()
    
    def update_transactions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        now = datetime.now()
        for idx, transaction in enumerate(self.pending_transactions):
            remaining_td = max(timedelta(minutes=1) - (now - transaction['timestamp']), timedelta(0))
            total_seconds = int(remaining_td.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            remaining_str = f"{minutes:02d}:{seconds:02d}"
            select_display = "[X]" if transaction.get("selected", False) else "[ ]"
            self.tree.insert("", tk.END, iid=idx, values=( 
                select_display,
                transaction.get("Property Address", "N/A"),
                transaction.get("Policy Date", "N/A"),
                transaction.get("Policy Number", "N/A"),
                transaction.get("Vested Parties", "N/A"),
                transaction.get("Underwriters", "N/A"),
                transaction.get("Coverage Amount", "N/A"),
                transaction.get("Owner's Policy", "N/A"),
                transaction.get("Lender's Policy", "N/A"),
                transaction.get("Standard Policy Exceptions", "N/A"),
                transaction.get("Property Specific Exceptions", "N/A"),
                transaction.get("Legal Description/Derivation Clause", "N/A"),
                transaction.get("Revised", "N/A"),
                transaction.get("Revision", "N/A"),
                remaining_str
            ))
        
        # If the data has changed, save it.
        if self.dirty:
            self.save_transactions_to_file()
            self.dirty = False
        
        # Only print detailed debug info if the number of transactions has changed.
        if not hasattr(self, '_last_transaction_count'):
            self._last_transaction_count = len(self.pending_transactions)
            self._print_detailed_transactions()
        elif len(self.pending_transactions) != self._last_transaction_count:
            self._print_detailed_transactions()
            self._last_transaction_count = len(self.pending_transactions)
    
    def _print_detailed_transactions(self):
        print("DEBUG: Detailed pending transactions info:")
        for i, transaction in enumerate(self.pending_transactions, start=1):
            print(f"DEBUG: Transaction {i}:")
            for key, value in transaction.items():
                print(f"    {key}: {value}")
            print()  # Blank line for separation
        print(f"DEBUG: Total pending transactions: {len(self.pending_transactions)}")
    
    def save_transactions_to_file(self):
        data_to_save = []
        for transaction in self.pending_transactions:
            if transaction.get("processed", False):
                continue
            t = transaction.copy()
            if "timestamp" in t and isinstance(t["timestamp"], datetime):
                t["timestamp"] = t["timestamp"].isoformat()
            data_to_save.append(t)
        try:
            with open(self.pending_file, "w") as f:
                json.dump(data_to_save, f, indent=4)
            print("DEBUG: ✅ Pending transactions saved to file.")
        except Exception as e:
            print("DEBUG: ❌ Error saving pending transactions:", e)
    
    def submit_transaction_to_db(self, transaction):
        """
        Submits the given transaction to the TitleChainDb database using the persistent connection.
        The transaction must contain a Transaction ID provided by the blockchain.
        """
        # Skip submission if already processed.
        if transaction.get("processed", False):
            print("DEBUG: Transaction already processed, skipping DB submission.")
            return

        try:
            from src.db_connection_global import connection as db_conn
        except ImportError as e:
            print("DEBUG: Failed to import persistent DB connection:", e)
            raise Exception("Persistent DB connection not available.")

        if db_conn is None:
            print("DEBUG: No persistent DB connection available!")
            raise Exception("No DB connection available.")

        try:
            cursor = db_conn.cursor()
            insert_sql = """
                INSERT INTO Orders 
                    (transaction_id, property_address, policy_date, policy_number, vested_parties, underwriters, coverage_amount,
                    owners_policy, lenders_policy, standard_policy_exceptions, property_specific_exceptions, legal_description, revision)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            # Require that Transaction ID is provided by blockchain.
            transaction_id = transaction.get("Transaction ID")
            if not transaction_id:
                print("DEBUG: No Transaction ID found from blockchain; cannot submit to DB.")
                raise Exception("Transaction ID not found from blockchain submission.")
            
            # Convert Revision: if not a valid int, default as per boolean value.
            revision_raw = transaction.get("Revision", 1)
            try:
                revision_value = int(revision_raw)
            except Exception:
                revision_value = 1 if str(revision_raw).lower() == "yes" else 0

            # Convert Policy Date.
            policy_date_str = transaction.get("Policy Date")
            try:
                policy_date_value = datetime.strptime(policy_date_str, "%m/%d/%Y").date()
            except Exception as e:
                print("DEBUG: ❌ Failed to parse Policy Date:", policy_date_str, e)
                policy_date_value = None

            # Convert Coverage Amount.
            coverage_raw = transaction.get("Coverage Amount")
            try:
                coverage_clean = re.sub(r'[^\d\.]', '', coverage_raw)
                coverage_amount = float(coverage_clean)
            except Exception as e:
                print("DEBUG: ❌ Failed to convert Coverage Amount:", coverage_raw, e)
                coverage_amount = None

            # Normalize Property Address.
            property_address = transaction.get("Property Address")
            if property_address:
                property_address = property_address.replace("Tennessee", "TN").replace("tennessee", "TN")
            
            values = (
                transaction_id,
                property_address,
                policy_date_value,
                transaction.get("Policy Number"),
                transaction.get("Vested Parties"),
                transaction.get("Underwriters"),
                coverage_amount,
                transaction.get("Owner's Policy"),
                transaction.get("Lender's Policy"),
                transaction.get("Standard Policy Exceptions"),
                transaction.get("Property Specific Exceptions"),
                transaction.get("Legal Description/Derivation Clause"),
                revision_value
            )
            print("DEBUG: Inserting transaction with values:", values)
            cursor.execute(insert_sql, values)
            db_conn.commit()
            print("DEBUG: Transaction submitted to database successfully.")
            # Mark transaction as processed.
            transaction["processed"] = True
        except Exception as e:
            print("DEBUG: Exception while submitting transaction to DB:", e)
            raise
    
    def remove_expired_transactions(self):
        now = datetime.now()
        remaining = []
        for transaction in self.pending_transactions:
            if transaction.get("processed", False):
                continue
            if now - transaction['timestamp'] >= timedelta(minutes=1):
                db_success = False
                blockchain_success = False

                # Attempt to submit to the blockchain.
                try:
                    self.submit_to_blockchain(transaction)
                    print("DEBUG: ✅ Transaction submitted to blockchain.")
                    blockchain_success = True
                except Exception as e:
                    print("DEBUG: ❌ Error submitting to blockchain:", e)

                # Attempt to submit to the database.
                try:
                    self.submit_transaction_to_db(transaction)
                    print("DEBUG: ✅ Transaction submitted to TitleChainDb.")
                    db_success = True
                except Exception as e:
                    print("DEBUG: ❌ Error submitting to TitleChainDb:", e)

                # If both submissions failed, fallback to saving to properties.json.
                if not (db_success or blockchain_success):
                    print("DEBUG: ❌ Neither submission succeeded; saving transaction to properties.json.")
                    self.save_transaction_to_properties(transaction)

                transaction["processed"] = True
            else:
                remaining.append(transaction)
        if len(remaining) != len(self.pending_transactions):
            self.dirty = True
        self.pending_transactions = remaining
        self.update_transactions()
        self.after(1000, self.remove_expired_transactions)
    
    def submit_to_blockchain(self, transaction):
        """
        Submits the given transaction to the blockchain by sending an HTTP POST
        request to the specified endpoint.

        - "Policy Date" is converted from MM/DD/YYYY to YYYY-MM-DD.
        - "Revised" is determined from the "Revision" field:
            if "Revision" equals "Yes" or "1" then Revised is True,
            otherwise Revised is False.
        - If Revised is False, the "Revision" key is sent as an empty string;
            if True, it's sent as a string (pointer to the original transaction).
        - After a successful submission, the blockchain response is parsed for
            the transaction ID which is then stored in the transaction dictionary.
        """
        blockchain_url = "http://192.168.1.29:5000/transactions"
        
        # Convert Policy Date.
        policy_date_raw = transaction.get("Policy Date", "").strip()
        if policy_date_raw:
            try:
                date_obj = datetime.strptime(policy_date_raw, "%m/%d/%Y")
                formatted_date = date_obj.strftime("%Y-%m-%d")
            except Exception as e:
                print("DEBUG: Exception converting Policy Date:", e)
                formatted_date = policy_date_raw
        else:
            formatted_date = ""
        
        # Determine Revised boolean.
        revision_field = str(transaction.get("Revision", "")).strip()
        revised = revision_field.lower() in ["yes", "1"]
        
        # Build payload in the desired order.
        payload = {
            "Property Address": transaction.get("Property Address", "").strip(),
            "Policy Date": formatted_date,
            "Policy Number": transaction.get("Policy Number", "").strip(),
            "Vested Parties": transaction.get("Vested Parties", "").strip(),
            "Underwriters": transaction.get("Underwriters", "").strip(),
            "Coverage Amount": str(transaction.get("Coverage Amount", "")).strip(),
            "Owner's policy": transaction.get("Owner's Policy", "").strip(),
            "Lender Policy": transaction.get("Lender's Policy", "").strip(),
            "Standard Policy Exception": transaction.get("Standard Policy Exceptions", "").strip(),
            "Property Specific Exceptions": transaction.get("Property Specific Exceptions", "").strip(),
            "Legal Description": transaction.get("Legal Description/Derivation Clause", "").strip(),
            "Revised": revised
        }
        # Send Revision as a string if revised is True; otherwise, as an empty string.
        payload["Revision"] = str(transaction.get("Revision", "")) if revised else ""
        
        try:
            json_data = json.dumps(payload)
            headers = {"Content-Type": "application/json"}
            response = requests.post(blockchain_url, data=json_data, headers=headers, timeout=20)
            response.raise_for_status()  # Raise an error if status is not 200
            print("DEBUG: Transaction submitted to blockchain successfully.")
            
            # Parse the response for the transaction ID.
            response_json = response.json()
            blockchain_tx_id = response_json.get("transaction_id")
            if blockchain_tx_id:
                transaction["Transaction ID"] = blockchain_tx_id
                print("DEBUG: Received Transaction ID from blockchain:", blockchain_tx_id)
            else:
                print("DEBUG: No Transaction ID returned by blockchain; attempting a GET request.")
                # (Optional) If necessary, perform a GET to fetch the latest transaction(s).
                get_url = blockchain_url  # Assuming the GET endpoint is the same.
                get_response = requests.get(get_url, timeout=20)
                get_response.raise_for_status()
                tx_list = get_response.json()
                if tx_list and isinstance(tx_list, list):
                    # Assume the most recent transaction is last (or sort as needed).
                    latest_tx = tx_list[-1]
                    blockchain_tx_id = latest_tx.get("transaction_id")
                    if blockchain_tx_id:
                        transaction["Transaction ID"] = blockchain_tx_id
                        print("DEBUG: Retrieved Transaction ID via GET:", blockchain_tx_id)
                    else:
                        print("DEBUG: No Transaction ID found in GET response.")
                else:
                    print("DEBUG: GET response did not return a valid list.")
        except requests.exceptions.ConnectTimeout as e:
            print("DEBUG: Connection to blockchain timed out:", e)
            raise
        except Exception as e:
            print("DEBUG: Exception while submitting to blockchain:", e)
            raise
    
    def save_transaction_to_properties(self, transaction):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(os.path.dirname(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        properties_file = os.path.join(base_dir, "data", "properties.json")
        if not os.path.exists(properties_file):
            print(f"DEBUG: ❌ properties.json not found. Creating new file at {properties_file}.")
            try:
                with open(properties_file, "w") as f:
                    json.dump([], f)
                print(f"DEBUG: ✅ properties.json created successfully at {properties_file}.")
            except Exception as e:
                print("DEBUG: ❌ Could not create properties.json:", e)
        try:
            with open(properties_file, "r") as f:
                properties = json.load(f)
            print("DEBUG: ✅ Loaded properties.json.")
        except Exception as e:
            print("DEBUG: ❌ Error loading properties.json:", e)
            properties = []
        properties.append(transaction)
        try:
            with open(properties_file, "w") as f:
                json.dump(properties, f, indent=4, default=str)
            print("DEBUG: ✅ Transaction saved to properties.json.")
        except Exception as e:
            print("DEBUG: ❌ Error saving transaction to properties.json:", e)
    
    def delete_transaction(self):
        new_list = [t for t in self.pending_transactions if not t.get("selected", False)]
        num_deleted = len(self.pending_transactions) - len(new_list)
        if num_deleted == 0:
            messagebox.showerror("Error", "No transactions selected for deletion.")
            return
        self.pending_transactions = new_list
        self.dirty = True
        self.update_transactions()
        messagebox.showinfo("Success", f"Deleted {num_deleted} transaction(s).")
