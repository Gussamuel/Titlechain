import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import os
import sys
import json

# ❌✅

class TransactionManager(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Determine the base directory.
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(__file__)
        self.pending_file = os.path.join(base_dir, "pending_transactions.json")
        
        # Check if pending_transactions.json exists; if not, create it.
        if not os.path.exists(self.pending_file):
            print("DEBUG: ❌ pending_transactions.json not found. Creating new file.")
            try:
                with open(self.pending_file, "w") as f:
                    json.dump([], f)
                print("DEBUG: ✅ pending_transactions.json created successfully.")
            except Exception as e:
                print("DEBUG: ❌ Could not create pending_transactions.json:", e)
        else:
            print("DEBUG: ✅ pending_transactions.json found.")
        
        # Load pending transactions from file.
        try:
            with open(self.pending_file, "r") as f:
                data = json.load(f)
            # Convert timestamp strings back to datetime objects.
            for transaction in data:
                if "timestamp" in transaction:
                    transaction["timestamp"] = datetime.fromisoformat(transaction["timestamp"])
            self.pending_transactions = data
            print("DEBUG: ✅ Loaded pending transactions from file.")
        except Exception as e:
            print("DEBUG: ❌ Error loading pending transactions:", e)
            self.pending_transactions = []
        
        # Dirty flag to track if changes occur.
        self.dirty = False

        # Configure grid layout for the frame.
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Button frame (only Delete Selected now)
        button_frame = ttk.Frame(self)
        button_frame.grid(row=0, column=0, sticky="ew", pady=10, padx=10)
        button_frame.grid_columnconfigure(0, weight=1)
        
        self.delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_transaction)
        self.delete_button.pack(side="left", padx=10)
        
        # Create a frame for the Treeview and scrollbars.
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        columns = (
            "Select",
            "Property Address", 
            "Policy Date",
            "Vested Parties",
            "Underwriters", 
            "Coverage Amount",
            "Owner's Policy",
            "Lender's Policy",
            "Standard Policy Exceptions", 
            "Property Specific Exceptions", 
            "Legal Description/Derivation Clause",
            "Revision",
            "Remaining Time"
        )
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Define headings and column alignment.
        for col in columns:
            if col == "Select":
                self.tree.heading(col, text=col, anchor="center")
                self.tree.column(col, width=50, anchor="center")
            else:
                self.tree.heading(col, text=col, anchor="w")
                self.tree.column(col, anchor="w", minwidth=0)
        
        # Minimal tweak: remove extra header padding.
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
        
        # Start the timer for processing expired transactions.
        self.after(1000, self.remove_expired_transactions)
        self.update_transactions()
    
    def adjust_column_widths(self, event=None):
        total_width = self.tree.winfo_width()
        num_columns = len(self.tree["columns"])
        select_width = 50  # Fixed width for the Select column.
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
                print("DEBUG: Toggled selection for transaction at index", idx)
                self.update_transactions()
    
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
        print("DEBUG: ✅ Added new pending transaction.")
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
            self.tree.insert("", "end", iid=idx, values=(
                select_display,
                transaction.get("Property Address", "N/A"),
                transaction.get("Policy Date", "N/A"),
                transaction.get("Vested Parties", "N/A"),
                transaction.get("Underwriters", "N/A"),
                transaction.get("Coverage Amount", "N/A"),
                transaction.get("Owner's Policy", "N/A"),
                transaction.get("Lender's Policy", "N/A"),
                transaction.get("Standard Policy Exceptions", "N/A"),
                transaction.get("Property Specific Exceptions", "N/A"),
                transaction.get("Legal Description/Derivation Clause", "N/A"),
                transaction.get("Revision", "N/A"),
                remaining_str
            ))
        if self.dirty:
            self.save_transactions_to_file()
            self.dirty = False
    
    def save_transactions_to_file(self):
        data_to_save = []
        for transaction in self.pending_transactions:
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
    
    def remove_expired_transactions(self):
        now = datetime.now()
        expired = []
        remaining = []
        # Using 1 minute for testing; change to 15 minutes for production.
        for transaction in self.pending_transactions:
            if now - transaction['timestamp'] >= timedelta(minutes=1):
                expired.append(transaction)
            else:
                remaining.append(transaction)
        for transaction in expired:
            try:
                self.submit_to_blockchain(transaction)
                print("DEBUG: ✅ Transaction submitted to blockchain.")
            except Exception as e:
                print("DEBUG: ❌ Error submitting to blockchain:", e)
                self.save_transaction_to_properties(transaction)
        if len(remaining) != len(self.pending_transactions):
            self.dirty = True
        self.pending_transactions = remaining
        self.update_transactions()
        self.after(1000, self.remove_expired_transactions)
    
    def submit_to_blockchain(self, transaction):
        # Dummy simulation: always fail to simulate connection error.
        raise Exception("Simulated blockchain connection failure")
    
    def save_transaction_to_properties(self, transaction):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(__file__)
        properties_file = os.path.join(base_dir, "properties.json")
        if os.path.exists(properties_file):
            try:
                with open(properties_file, "r") as f:
                    properties = json.load(f)
                print("DEBUG: ✅ Loaded properties.json.")
            except Exception as e:
                print("DEBUG: ❌ Error loading properties.json:", e)
                properties = []
        else:
            print("DEBUG: ❌ properties.json not found. It will be created now.")
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
