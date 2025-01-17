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
                "Standard Policy Exceptions", 
                "Property Specific Exceptions", 
                "Legal Description/Derivation Clause", 
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
        self.pending_transactions.append(transaction)
        self.update_transactions()

    def update_transactions(self):
        """Update the Treeview with the current pending transactions."""
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Add pending transactions to the Treeview
        now = datetime.now()
        for idx, transaction in enumerate(self.pending_transactions):
            remaining_time = max(timedelta(minutes=15) - (now - transaction['timestamp']), timedelta(0))
            self.tree.insert("", "end", iid=idx, values=(
                transaction.get("Property Address", "N/A"),
                transaction.get("Policy Date", "N/A"),
                transaction.get("Vested Parties", "N/A"),
                transaction.get("Standard Policy Exceptions", "N/A"),
                transaction.get("Property Specific Exceptions", "N/A"),
                transaction.get("Legal Description/Derivation Clause", "N/A"),
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

# Main application setup for testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Transaction Manager")
    root.geometry("1200x600")

    # Configure grid for dynamic resizing
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    transaction_manager = TransactionManager(root)
    transaction_manager.grid(row=0, column=0, sticky="nsew")

    # Example transactions
    example_transactions = [
        {
            "Property Address": "600 E Trinity Lane #303, Nashville, TN 37207",
            "Policy Date": "10/30/24",
            "Vested Parties": "Ashley Akers, a single woman",
            "Standard Policy Exceptions": "Standard exceptions",
            "Property Specific Exceptions": "Specific exceptions",
            "Legal Description/Derivation Clause": "Exhibit A",
        },
        {
            "Property Address": "123 Main Street, Anytown, USA",
            "Policy Date": "11/15/24",
            "Vested Parties": "John Doe",
            "Standard Policy Exceptions": "Standard exceptions",
            "Property Specific Exceptions": "Specific exceptions",
            "Legal Description/Derivation Clause": "Exhibit B",
        },
    ]

    for transaction in example_transactions:
        transaction_manager.add_pending_transaction(transaction)

    root.mainloop()