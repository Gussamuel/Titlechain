import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from utils import submit_transaction

class TransactionForm(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        fields = [
            "Property Address",
            "City",
            "State",
            "Zip Code",
            "County",
            "Buyer",
            "Seller",
            "Listing Agent",
            "Selling Agent",
            "Lender",
            "Title Company 1",
            "Title Company 2",
            "Purchase Price",
            "Loan Amount",
            "Policy Types",
            "Policy Premiums"
        ]

        self.entries = {}

        # Configure grid weights for responsiveness
        self.grid_columnconfigure(0, weight=1)  # Labels column
        self.grid_columnconfigure(1, weight=3)  # Entries column

        for idx, field in enumerate(fields):
            # Configure each row to have equal weight (optional)
            self.grid_rowconfigure(idx, weight=1)

            label = ttk.Label(self, text=field + ":")
            label.grid(row=idx, column=0, padx=10, pady=5, sticky=tk.W)

            entry = ttk.Entry(self)
            entry.grid(row=idx, column=1, padx=10, pady=5, sticky='ew')  # Expand horizontally
            self.entries[field] = entry

        # Submit button spans both columns and is centered
        submit_btn = ttk.Button(self, text="Submit Transaction", command=self.submit_form)
        submit_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)

        # Configure the last row to have some weight if needed
        self.grid_rowconfigure(len(fields), weight=1)

    def submit_form(self):
        transaction_data = {field: entry.get() for field, entry in self.entries.items()}

        if not all(transaction_data.values()):
            messagebox.showerror("Error", "All fields must be filled out.")
            return

        success = submit_transaction(transaction_data)
        if success:
            messagebox.showinfo("Success", "Transaction added to the blockchain successfully.")
            self.clear_form()
        else:
            messagebox.showerror("Error", "Failed to add transaction to the blockchain.")

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)