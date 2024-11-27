import tkinter as tk
from tkinter import ttk
from utils import fetch_properties  # This will fetch data from the blockchain when ready

class PropertyView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.columns = [
            "Property Address", "Policy Date", "Vested Parties",
            "Standard Policy Exceptions", "Property Specific Exceptions",
            "Legal Description/Derivation Clause"
        ]

        self.data = []  # Store the properties data locally for filtering

        # Configure the grid to make widgets expand
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Search frame
        search_frame = ttk.Frame(self)
        search_frame.grid(row=0, column=0, sticky='ew', pady=5)
        search_frame.grid_columnconfigure(1, weight=1)

        # Search label and entry
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky='ew', padx=5)

        # Search button
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_properties)
        search_btn.grid(row=0, column=2, padx=5)

        # Reset button
        reset_btn = ttk.Button(search_frame, text="Reset", command=self.refresh_view)
        reset_btn.grid(row=0, column=3, padx=5)

        # Create a frame for the Treeview and scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky='nsew')

        # Create the Treeview
        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show='headings')

        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Position the Treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Configure grid in tree_frame
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Define columns with appropriate settings
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')

        # Initially, display a message indicating no data is available
        self.display_no_data_message()

        # Refresh button
        refresh_btn = ttk.Button(self, text="Refresh", command=self.refresh_view)
        refresh_btn.grid(row=2, column=0, pady=10)

    def display_no_data_message(self):
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Insert a single row indicating no data is available yet
        self.tree.insert("", tk.END, values=["No data available"] + [""] * (len(self.tree["columns"]) - 1))

    def refresh_view(self):
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Fetch properties from the blockchain (when ready)
        self.data = fetch_properties()

        if not self.data:
            self.display_no_data_message()
            return

        for prop in self.data:
            self.tree.insert("", tk.END, values=(
                prop.get("Property Address", ""),
                prop.get("Buyer", ""),
                prop.get("Seller", ""),
                prop.get("Purchase Price", ""),
                prop.get("Policy Types", ""),
                prop.get("Loan Amount", ""),
                prop.get("Lien Holder", ""),
                prop.get("Lien Amount", ""),
                prop.get("Tax Year", ""),
                prop.get("Due Date", ""),
                prop.get("Easement Type", ""),
                prop.get("Zoning Code", ""),
            ))

    def search_properties(self):
        # Get search query
        query = self.search_var.get().lower()

        # Filter properties based on the query
        filtered_data = [
            prop for prop in self.data
            if any(query in str(value).lower() for value in prop.values())
        ]

        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not filtered_data:
            self.display_no_data_message()
            return

        # Insert filtered data
        for prop in filtered_data:
            self.tree.insert("", tk.END, values=(
                prop.get("Property Address", ""),
                prop.get("Buyer", ""),
                prop.get("Seller", ""),
                prop.get("Purchase Price", ""),
                prop.get("Policy Types", ""),
                prop.get("Loan Amount", ""),
                prop.get("Lien Holder", ""),
                prop.get("Lien Amount", ""),
                prop.get("Tax Year", ""),
                prop.get("Due Date", ""),
                prop.get("Easement Type", ""),
                prop.get("Zoning Code", ""),
            ))


# For testing purposes (optional)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Property View")
    root.geometry("1200x1000")

    # Configure root window grid
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    property_view = PropertyView(root)
    property_view.grid(row=0, column=0, sticky='nsew')

    root.mainloop()