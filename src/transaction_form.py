import tkinter as tk
from tkinter import ttk, messagebox

class TransactionForm(ttk.Frame):
    def __init__(self, parent, add_transaction_callback=None):
        super().__init__(parent)
        self.add_transaction_callback = add_transaction_callback

        # Define consolidated pages
        self.pages = [
            "Property Details/Policy Date",
            "Transaction Details",
            "Policy Exceptions and Revisions"
        ]

        # Data to store entered values
        self.transaction_data = {}
        self.current_page_index = 0

        # Configure the grid to allow dynamic resizing
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Setup the layout
        self.setup_page_area()
        self.setup_navigation_buttons()

        # Render the first page
        self.render_page()

    def setup_page_area(self):
        """Set up the area where the form fields will appear."""
        self.page_area = ttk.Frame(self)
        self.page_area.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.page_area.grid_rowconfigure(0, weight=1)
        self.page_area.grid_columnconfigure(0, weight=1)

    def setup_navigation_buttons(self):
        """Set up the navigation buttons (Next, Previous, Submit)."""
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=1, column=0, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        # Previous button
        self.prev_button = ttk.Button(self.button_frame, text="Previous", command=self.previous_page)
        self.prev_button.grid(row=0, column=0, padx=5, sticky="e")

        # Next button
        self.next_button = ttk.Button(self.button_frame, text="Next", command=self.next_page)
        self.next_button.grid(row=0, column=1, padx=5, sticky="w")

    def render_page(self):
        """Render the current page based on the page index."""
        for widget in self.page_area.winfo_children():
            widget.destroy()

        page_title = self.pages[self.current_page_index]
        ttk.Label(self.page_area, text=page_title, font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # Render fields for the current page
        if page_title == "Property Details/Policy Date":
            self.render_property_details()
        elif page_title == "Transaction Details":
            self.render_transaction_details()
        elif page_title == "Policy Exceptions and Revisions":
            self.render_policy_exceptions_and_revisions()

        # Update button visibility
        self.prev_button["state"] = tk.NORMAL if self.current_page_index > 0 else tk.DISABLED
        self.next_button["text"] = "Submit" if self.current_page_index == len(self.pages) - 1 else "Next"

    def render_property_details(self):
        """Render fields for Property Address and Policy Date."""
        fields = ["Street", "Apt/Building (if applicable)", "City", "State", "Zip", "Policy Date (MM/DD/YYYY)"]
        for idx, field in enumerate(fields):
            ttk.Label(self.page_area, text=f"{field}:").grid(row=idx + 1, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(self.page_area, width=40)
            entry.grid(row=idx + 1, column=1, sticky="ew", padx=10, pady=5)
            self.transaction_data[field] = entry

    def render_transaction_details(self):
        """Render fields for Vested Parties, Underwriters, Coverage Amount, Owner's Policy, and Lender's Policy."""

        # Adjust input box sizes for "Vested Parties" and "Underwriters"
        large_fields = ["Vested Parties", "Underwriters"]
        for idx, field in enumerate(large_fields):
            ttk.Label(self.page_area, text=f"{field}:").grid(row=idx + 1, column=0, sticky="w", padx=10, pady=5)
            text_area = tk.Text(self.page_area, height=6, width=50)  # Increased size
            text_area.grid(row=idx + 1, column=1, columnspan=2, sticky="nsew", padx=10, pady=5)  # Span 2 columns
            self.transaction_data[field] = text_area

        # Coverage Amount with a standard input box
        ttk.Label(self.page_area, text="Coverage Amount:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        entry = ttk.Entry(self.page_area, width=30)  # Increased width
        entry.grid(row=3, column=1, columnspan=2, sticky="ew", padx=10, pady=5)
        self.transaction_data["Coverage Amount"] = entry

        # Policy Type Section
        ttk.Label(self.page_area, text="Policy Type:").grid(row=4, column=0, sticky="w", padx=10, pady=5)

        # Frame to group checkboxes together
        policy_frame = ttk.Frame(self.page_area)
        policy_frame.grid(row=4, column=1, columnspan=2, sticky="w", padx=10, pady=5)

        self.owners_policy_var = tk.BooleanVar()
        owners_checkbox = ttk.Checkbutton(
            policy_frame, text="Owner's Policy", variable=self.owners_policy_var, command=self.sync_policy_checkboxes
        )
        owners_checkbox.pack(side="left", padx=5)  # Pack instead of grid for better alignment

        self.lenders_policy_var = tk.BooleanVar()
        lenders_checkbox = ttk.Checkbutton(
            policy_frame, text="Lender's Policy", variable=self.lenders_policy_var, command=self.sync_policy_checkboxes
        )
        lenders_checkbox.pack(side="left", padx=5)

        self.transaction_data["Owner's Policy"] = self.owners_policy_var
        self.transaction_data["Lender's Policy"] = self.lenders_policy_var

    def sync_policy_checkboxes(self):
        """Ensure only one policy can be selected at a time."""
        if self.owners_policy_var.get():
            self.lenders_policy_var.set(False)
        elif self.lenders_policy_var.get():
            self.owners_policy_var.set(False)

    def render_policy_exceptions_and_revisions(self):
        """Render fields for Standard Policy Exceptions, Property Specific Exceptions, Legal Description, Revised, and Revision."""
        
        ttk.Label(self.page_area, text="Standard Policy Exceptions:").grid(row=1, column=0, sticky="w", padx=10, pady=5)

        # Frame for checkboxes
        self.exceptions_frame = ttk.Frame(self.page_area)
        self.exceptions_frame.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # List of Standard Policy Exceptions
        standard_exceptions = [
            "1. Rights or claims of parties in possession not shown by the public records.",
            "2. Easements or claims of easements not shown by the public records.",
            "3. Encroachments, overlaps, boundary line disputes, or other matters that would be disclosed by an accurate survey.",
            "4. Any lien, or right to a lien, for services, labor or material not shown by the public records.",
            "5. Taxes or special assessments not yet due or payable."
        ]

        self.exceptions_vars = {}

        # "Select All" Checkbox
        self.select_all_var = tk.BooleanVar()
        select_all_checkbox = ttk.Checkbutton(
            self.exceptions_frame, text="Select All", variable=self.select_all_var, command=self.toggle_select_all
        )
        select_all_checkbox.grid(row=0, column=0, sticky="w")

        # Individual checkboxes for exceptions
        for idx, exception in enumerate(standard_exceptions, start=1):
            var = tk.BooleanVar()
            checkbox = ttk.Checkbutton(self.exceptions_frame, text=exception, variable=var)
            checkbox.grid(row=idx, column=0, sticky="w")
            self.exceptions_vars[exception] = var

        # Legal Description
        ttk.Label(self.page_area, text="Legal Description/Derivation Clause:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        legal_text = tk.Text(self.page_area, height=5, width=50)
        legal_text.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        self.transaction_data["Legal Description"] = legal_text

        # Revised checkbox with descriptive text

        ttk.Label(self.page_area, text="Check only if submitting a revision of an existing transaction.", wraplength=400).grid(
            row=5, column=0, columnspan=2, sticky="w", padx=5, pady=(5, 0)
        )

        self.revised_var = tk.BooleanVar()
        revised_checkbox = ttk.Checkbutton(self.page_area, text="Revised", variable=self.revised_var)
        revised_checkbox.grid(row=6, column=0, sticky="w", padx=5, pady=5)

        self.transaction_data["Revised"] = self.revised_var


    def toggle_select_all(self):
        """Toggle all checkboxes when 'Select All' is clicked."""
        select_all_state = self.select_all_var.get()
        for var in self.exceptions_vars.values():
            var.set(select_all_state)


    def next_page(self):
        """Navigate to the next page or submit the form."""
        if self.current_page_index == len(self.pages) - 1:
            self.confirm_submission()
        else:
            self.current_page_index += 1
            self.render_page()

    def previous_page(self):
        """Navigate to the previous page."""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.render_page()

    def confirm_submission(self):
        """Confirm before submitting the transaction."""
        confirm = messagebox.askyesno(
            "Confirm Submission",
            "Are you sure you want to submit this transaction? You will have 15 minutes to un-submit if needed."
        )
        if confirm:
            self.submit_form()

    def submit_form(self):
        """Submit the form and clear the data."""
        transaction_data = {}
        for key, widget in self.transaction_data.items():
            if isinstance(widget, tk.Text):
                transaction_data[key] = widget.get("1.0", tk.END).strip()
            else:
                transaction_data[key] = widget.get().strip()

        if not all(transaction_data.values()):
            messagebox.showerror("Error", "All fields must be filled out.")
            return

        if self.add_transaction_callback:
            self.add_transaction_callback(transaction_data)
        else:
            print("Transaction Submitted:", transaction_data)

        messagebox.showinfo("Success", "Transaction submitted! It will be added to pending transactions.")
        self.reset_form()

    def reset_form(self):
        """Reset the form for a new transaction."""
        self.transaction_data.clear()
        self.current_page_index = 0
        self.render_page()


# Main application setup
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Transaction Form")
    root.geometry("1000x750")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    transaction_form = TransactionForm(root)
    transaction_form.grid(row=0, column=0, sticky="nsew")

    root.mainloop()