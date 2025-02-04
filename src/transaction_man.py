import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta

class TransactionManager(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Store pending transactions
        self.pending_transactions = []

        # Configure grid layout for the frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Buttons for Edit/Delete
        button_frame = ttk.Frame(self)
        button_frame.grid(row=0, column=0, sticky="ew", pady=10, padx=10)
        button_frame.grid_columnconfigure(0, weight=1)

        self.edit_button = ttk.Button(button_frame, text="Edit Selected", command=self.edit_transaction)
        self.edit_button.pack(side="left", padx=10)

        self.delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_transaction)
        self.delete_button.pack(side="left", padx=10)

        # Create a frame for the Treeview and scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky="nsew")

        # Configure tree_frame for expansion
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Treeview for displaying pending transactions
        self.tree = ttk.Treeview(
            tree_frame,
            columns=(
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
            ),
            show="headings"
        )

        # Define headings
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)

        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Position the Treeview and vertical scrollbar
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Bind resize event to dynamically adjust column widths
        tree_frame.bind("<Configure>", self.adjust_column_widths)

        # Start the auto-update timer for expired transactions
        self.after(1000, self.remove_expired_transactions)

    def adjust_column_widths(self, event=None):
        """Dynamically adjust column widths to fit the Treeview's width."""
        total_width = self.tree.winfo_width()
        num_columns = len(self.tree["columns"])
        column_width = total_width // num_columns if num_columns > 0 else total_width

        for col in self.tree["columns"]:
            self.tree.column(col, width=column_width)

    def add_pending_transaction(self, transaction):
        """Add a transaction to the pending list with a timestamp."""
        transaction['timestamp'] = datetime.now()

        # Convert Standard Policy Exceptions to numerical format
        standard_exceptions_map = {
            "1. Rights or claims of parties in possession not shown by the public records.": "1",
            "2. Easements or claims of easements not shown by the public records.": "2",
            "3. Encroachments, overlaps, boundary line disputes, or other matters disclosed by an accurate survey.": "3",
            "4. Any lien, or right to a lien, for services, labor or material not shown by the public records.": "4",
            "5. Taxes or special assessments not yet due or payable.": "5",
        }

        selected_exceptions = [standard_exceptions_map[exc] for exc in transaction.get("Standard Policy Exceptions", [])]
        transaction["Standard Policy Exceptions"] = ", ".join(selected_exceptions) if selected_exceptions else "None"

        self.pending_transactions.append(transaction)
        self.update_transactions()

    def update_transactions(self):
        """Update the Treeview with the current pending transactions."""
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)

        now = datetime.now()
        for idx, transaction in enumerate(self.pending_transactions):
            remaining_time = max(timedelta(minutes=15) - (now - transaction['timestamp']), timedelta(0))
            
            # Add the transaction to the Treeview
            self.tree.insert("", "end", iid=idx, values=(
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
                str(remaining_time)  # Store remaining time in Treeview
            ))

    def remove_expired_transactions(self):
        """Remove transactions that have expired (after 15 minutes)."""
        now = datetime.now()
        self.pending_transactions = [
            transaction for transaction in self.pending_transactions
            if now - transaction['timestamp'] < timedelta(minutes=15)
        ]

        self.update_transactions()
        self.after(1000, self.remove_expired_transactions)  # Run every 1 second

    def edit_transaction(self):
        """Edit the selected transaction."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No transaction selected.")
            return

        idx = int(selected_item[0])
        transaction = self.pending_transactions[idx]

        messagebox.showinfo("Edit Transaction", f"Edit functionality not implemented yet for:\n{transaction}")

    def delete_transaction(self):
        """Delete the selected transaction."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No transaction selected.")
            return

        idx = int(selected_item[0])
        del self.pending_transactions[idx]
        self.update_transactions()
        messagebox.showinfo("Success", "Transaction deleted.")

# Main application setup for testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Transaction Manager")
    root.geometry("1000x750")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    transaction_manager = TransactionManager(root)
    transaction_manager.grid(row=0, column=0, sticky="nsew")

    root.mainloop()
