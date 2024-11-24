import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta

class TransactionManager(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Store pending transactions
        self.pending_transactions = []

        # Buttons for Edit/Delete
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=10, padx=10)

        self.edit_button = ttk.Button(button_frame, text="Edit Selected", command=self.edit_transaction)
        self.edit_button.pack(side="left", padx=10)

        self.delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_transaction)
        self.delete_button.pack(side="left", padx=10)

        # Treeview for displaying pending transactions
        self.tree = ttk.Treeview(
            self, columns=("Property Address", "Buyer", "Seller", "Remaining Time"), show="headings"
        )
        self.tree.heading("Property Address", text="Property Address")
        self.tree.heading("Buyer", text="Buyer")
        self.tree.heading("Seller", text="Seller")
        self.tree.heading("Remaining Time", text="Remaining Time")

        self.tree.pack(fill="both", expand=True, side="left", padx=10, pady=10)

        # Add scrollbars
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def add_pending_transaction(self, transaction):
        """Add a transaction to the pending list with a timestamp."""
        transaction['timestamp'] = datetime.now()
        self.pending_transactions.append(transaction)
        self.update_transactions()

    def update_transactions(self):
        """Update the treeview with the current pending transactions."""
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Add pending transactions to the treeview
        now = datetime.now()
        for idx, transaction in enumerate(self.pending_transactions):
            remaining_time = max(timedelta(minutes=15) - (now - transaction['timestamp']), timedelta(0))
            self.tree.insert("", "end", iid=idx, values=(
                transaction["Property Address"],
                transaction["Buyer"],
                transaction["Seller"],
                str(remaining_time)
            ))

    def edit_transaction(self):
        """Edit the selected transaction."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No transaction selected.")
            return

        idx = int(selected_item[0])
        transaction = self.pending_transactions[idx]

        # Editing logic can be added here (e.g., open a new form pre-filled with transaction data)
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