import tkinter as tk
from tkinter import ttk
from utils import fetch_properties

class PropertyView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        columns = ("Property Address", "Buyer", "Seller", "Purchase Price", "Policy Types", "Loan Amount")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(expand=True, fill='both')

        refresh_btn = ttk.Button(self, text="Refresh", command=self.refresh_view)
        refresh_btn.pack(pady=10)

        self.refresh_view()

    def refresh_view(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        properties = fetch_properties()
        for prop in properties:
            self.tree.insert("", tk.END, values=(
                prop.get("Property Address"),
                prop.get("Buyer"),
                prop.get("Seller"),
                prop.get("Purchase Price"),
                prop.get("Policy Types"),
                prop.get("Loan Amount")
            ))