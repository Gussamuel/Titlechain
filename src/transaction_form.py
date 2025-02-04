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
        fields = ["Street", "City", "State", "Zip", "Policy Date (MM/DD/YYYY)"]
        optional_fields = ["Apt/Building (if applicable)"]

        self.entry_fields = {}

        for idx, field in enumerate(fields + optional_fields):
            ttk.Label(self.page_area, text=f"{field}:").grid(row=idx + 1, column=0, sticky="w", padx=10, pady=5)
            entry = tk.Text(self.page_area, height=1, width=30)
            entry.grid(row=idx + 1, column=1, sticky="ew", padx=10, pady=5)
            self.entry_fields[field] = entry

    def render_transaction_details(self):
        """Render fields for Vested Parties, Underwriters, Coverage Amount, and Policy Type."""
        self.transaction_fields = {}

        large_fields = ["Vested Parties", "Underwriters"]
        for idx, field in enumerate(large_fields):
            ttk.Label(self.page_area, text=f"{field}:").grid(row=idx + 1, column=0, sticky="w", padx=10, pady=5)
            text_area = tk.Text(self.page_area, height=6, width=50)
            text_area.grid(row=idx + 1, column=1, columnspan=2, sticky="nsew", padx=10, pady=5)
            self.transaction_fields[field] = text_area

        # Coverage Amount
        ttk.Label(self.page_area, text="Coverage Amount:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        entry = tk.Text(self.page_area, height=1, width=30)
        entry.grid(row=3, column=1, columnspan=2, sticky="ew", padx=10, pady=5)
        self.transaction_fields["Coverage Amount"] = entry

    def render_policy_exceptions_and_revisions(self):
        """Render fields for Standard Policy Exceptions and Legal Description."""
        self.exceptions_vars = {}

        ttk.Label(self.page_area, text="Standard Policy Exceptions:").grid(row=1, column=0, sticky="w", padx=10, pady=5)

        # "Select All" Checkbox
        self.select_all_var = tk.BooleanVar()
        select_all_checkbox = ttk.Checkbutton(self.page_area, text="Select All", variable=self.select_all_var, command=self.toggle_select_all)
        select_all_checkbox.grid(row=2, column=0, sticky="w")

        exceptions = [
            "1. Rights or claims of parties in possession not shown by the public records.",
            "2. Easements or claims of easements not shown by the public records.",
            "3. Encroachments, overlaps, boundary line disputes, or other matters disclosed by an accurate survey.",
            "4. Any lien, or right to a lien, for services, labor or material not shown by the public records.",
            "5. Taxes or special assessments not yet due or payable."
        ]

        for idx, exception in enumerate(exceptions, start=3):
            var = tk.BooleanVar()
            checkbox = ttk.Checkbutton(self.page_area, text=exception, variable=var)
            checkbox.grid(row=idx, column=0, sticky="w")
            self.exceptions_vars[exception] = var

        # Legal Description
        ttk.Label(self.page_area, text="Legal Description/Derivation Clause:").grid(row=8, column=0, sticky="w", padx=10, pady=5)
        self.legal_description = tk.Text(self.page_area, height=5, width=50)
        self.legal_description.grid(row=9, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

        ttk.Label(self.page_area, text="Check the 'Revised' box only if this transaction already exists on the blockchain and needs to be updated or replaced:").grid(row=10, column=0, sticky="w", padx=10, pady=5)

        # Revised checkbox
        self.revised_var = tk.BooleanVar()
        revised_checkbox = ttk.Checkbutton(self.page_area, text="Revised", variable=self.revised_var)
        revised_checkbox.grid(row=11, column=0, sticky="w", padx=5, pady=5)

    def toggle_select_all(self):
        """Toggle all checkboxes when 'Select All' is clicked."""
        select_all_state = self.select_all_var.get()
        for var in self.exceptions_vars.values():
            var.set(select_all_state)

    def validate_page(self):
        """Ensure required fields are filled before moving forward."""
        page_title = self.pages[self.current_page_index]
        errors = []

        # Property Details validation
        if page_title == "Property Details/Policy Date":
            for field, entry in self.entry_fields.items():
                if field != "Apt/Building (if applicable)":
                    if isinstance(entry, tk.Text):
                        value = entry.get("1.0", tk.END).strip()  # For tk.Text
                    else:
                        value = entry.get().strip()  # For ttk.Entry
                    
                    if not value:
                        errors.append(entry)

        # Transaction Details validation
        elif page_title == "Transaction Details":
            for field, widget in self.transaction_fields.items():
                if isinstance(widget, tk.Text):
                    if not widget.get("1.0", tk.END).strip():
                        errors.append(widget)
                elif not widget.get().strip():
                    errors.append(widget)

        # Policy Exceptions validation
        elif page_title == "Policy Exceptions and Revisions":
            if not any(var.get() for var in self.exceptions_vars.values()):
                errors.append("exception")
            if not self.legal_description.get("1.0", tk.END).strip():
                errors.append(self.legal_description)

        if errors:
            messagebox.showerror("Error", "Fill out all required fields.")
            for field in errors:
                if isinstance(field, tk.Widget):
                    field.config(bg="lightcoral")
            return False

        return True
    
    def previous_page(self):
        """Navigate to the previous page."""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.render_page()

    def next_page(self):
        """Navigate to the next page with validation."""
        if not self.validate_page():
            return

        if self.current_page_index == len(self.pages) - 1:
            self.confirm_submission()
        else:
            self.current_page_index += 1
            self.render_page()

    def confirm_submission(self):
        """Show confirmation before submission."""
        confirm = messagebox.askyesno(
            "Confirm Submission",
            "Are you sure you want to submit? You will have 15 minutes to edit or cancel this submission if confirmed."
        )
        if confirm:
            self.submit_transaction()

    def submit_transaction(self):
        """Capture all data and submit the form."""
        transaction_data = {field: entry.get().strip() for field, entry in self.entry_fields.items()}
        transaction_data.update({field: text.get("1.0", tk.END).strip() for field, text in self.transaction_fields.items()})
        transaction_data["Standard Policy Exceptions"] = [key for key, var in self.exceptions_vars.items() if var.get()]
        transaction_data["Legal Description"] = self.legal_description.get("1.0", tk.END).strip()

        if self.add_transaction_callback:
            self.add_transaction_callback(transaction_data)
        messagebox.showinfo("Success", "Transaction submitted successfully!")
        self.reset_form()
