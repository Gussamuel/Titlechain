import tkinter as tk
from tkinter import ttk
from src.utils import fetch_properties  # This will fetch data from the blockchain when ready
import os
import sys
import json

class PropertyView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.columns = [
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
            "Revision"
        ]

        self.data = []  # Store the properties data locally for filtering

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

    def reset_search(self):
        # Clear the search field then refresh the view.
        self.search_var.set("")
        print("DEBUG: ✅ Search reset.")

    def refresh_view(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        print("DEBUG: Attempting to fetch properties from blockchain...")
        self.data = fetch_properties()
        if not self.data:
            print("DEBUG: ❌ Could not fetch properties from blockchain. Loading from properties.json...")
            try:
                if getattr(sys, 'frozen', False):
                    base_dir = os.path.dirname(sys.executable)
                else:
                    base_dir = os.path.dirname(__file__)
                properties_file = os.path.join(base_dir, "properties.json")
                with open(properties_file, "r") as f:
                    self.data = json.load(f)
                print("DEBUG: ✅ Loaded properties from properties.json.")
            except Exception as e:
                print("DEBUG: ❌ Error loading properties from properties.json:", e)
                self.data = []
        if not self.data:
            self.display_no_data_message()
            return

        for prop in self.data:
            self.tree.insert("", tk.END, values=(
                prop.get("Property Address", ""),
                prop.get("Policy Date", ""),
                prop.get("Vested Parties", ""),
                prop.get("Underwriters", ""),
                prop.get("Coverage Amount", ""),
                prop.get("Owner's Policy", ""),
                prop.get("Lender's Policy", ""),
                prop.get("Standard Policy Exceptions", ""),
                prop.get("Property Specific Exceptions", ""),
                prop.get("Legal Description/Derivation Clause", ""),
                prop.get("Revision", "")
            ))

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
                prop.get("Property Address", ""),
                prop.get("Policy Date", ""),
                prop.get("Vested Parties", ""),
                prop.get("Underwriters", ""),
                prop.get("Coverage Amount", ""),
                prop.get("Owner's Policy", ""),
                prop.get("Lender's Policy", ""),
                prop.get("Standard Policy Exceptions", ""),
                prop.get("Property Specific Exceptions", ""),
                prop.get("Legal Description/Derivation Clause", ""),
                prop.get("Revision", "")
            ))
        print("DEBUG: Searching for '", query, "'")
    
    def on_double_click(self, event):
        # Get the row that was double-clicked.
        rowid = self.tree.identify_row(event.y)
        if not rowid:
            return
        # Use the tree index instead of directly converting rowid.
        idx = self.tree.index(rowid)
        try:
            prop = self.data[idx]
        except IndexError:
            print("DEBUG: ❌ Double-click index out of range.")
            return
        self.show_property_details(prop)
        print("DEBUG: ✅ Displaying details.")
    
    def show_property_details(self, prop):
        details_win = tk.Toplevel(self)
        details_win.title("Property Details")
        frame = ttk.Frame(details_win, padding=10)
        frame.pack(fill="both", expand=True)
        
        fields = [
            ("Property Address", prop.get("Property Address", "N/A")),
            ("Policy Date", prop.get("Policy Date", "N/A")),
            ("Vested Parties", prop.get("Vested Parties", "N/A")),
            ("Underwriters", prop.get("Underwriters", "N/A")),
            ("Coverage Amount", prop.get("Coverage Amount", "N/A")),
            ("Owner's Policy", prop.get("Owner's Policy", "N/A")),
            ("Lender's Policy", prop.get("Lender's Policy", "N/A")),
            ("Standard Policy Exceptions", prop.get("Standard Policy Exceptions", "N/A")),
            ("Property Specific Exceptions", prop.get("Property Specific Exceptions", "N/A")),
            ("Legal Description/Derivation Clause", prop.get("Legal Description/Derivation Clause", "N/A")),
            ("Revision", prop.get("Revision", "N/A"))
        ]
        
        for idx, (key, value) in enumerate(fields):
            ttk.Label(frame, text=f"{key}:", font=("Helvetica", 10, "bold"), anchor="w").grid(row=idx, column=0, sticky="w", pady=2)
            ttk.Label(frame, text=value, font=("Helvetica", 10), anchor="w").grid(row=idx, column=1, sticky="w", pady=2)
        
        ttk.Button(frame, text="Close", command=details_win.destroy).grid(row=len(fields), column=0, columnspan=2, pady=10)
