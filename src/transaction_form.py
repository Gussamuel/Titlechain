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

        # Data to store entered values (from all pages)
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
        """Render fields for Property Address and Policy Date.
        Using tk.Text for single-line inputs and binding Tab for focus traversal."""
        # Added "Policy Number" as a required field.
        fields = ["Street", "City", "State (ST)", "Zip", "Policy Date (MM/DD/YYYY)", "Policy Number"]
        optional_fields = ["Apt/Building (if applicable)"]

        self.entry_fields = {}

        for idx, field in enumerate(fields + optional_fields):
            ttk.Label(self.page_area, text=f"{field}:").grid(row=idx + 1, column=0, sticky="w", padx=10, pady=5)
            entry = tk.Text(self.page_area, height=1, width=30)
            entry.grid(row=idx + 1, column=1, sticky="ew", padx=10, pady=5)
            # Bind Tab and Shift-Tab for focus traversal.
            entry.bind("<Tab>", lambda event: event.widget.tk_focusNext().focus() or "break")
            entry.bind("<Shift-Tab>", lambda event: event.widget.tk_focusPrev().focus() or "break")
            # Reinsert saved data if any.
            if field in self.transaction_data:
                entry.insert("1.0", self.transaction_data[field])
            self.entry_fields[field] = entry

    def render_transaction_details(self):
        """Render fields for Vested Parties, Underwriters, Coverage Amount, and Policy Type."""
        self.transaction_fields = {}

        large_fields = ["Vested Parties", "Underwriters"]
        for idx, field in enumerate(large_fields):
            ttk.Label(self.page_area, text=f"{field}:").grid(row=idx + 1, column=0, sticky="w", padx=10, pady=5)
            text_area = tk.Text(self.page_area, height=6, width=50)
            text_area.grid(row=idx + 1, column=1, columnspan=2, sticky="nsew", padx=10, pady=5)
            if field in self.transaction_data:
                text_area.insert("1.0", self.transaction_data[field])
            self.transaction_fields[field] = text_area

        # Coverage Amount as a single-line input.
        ttk.Label(self.page_area, text="Coverage Amount (in 0.00):").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        entry = tk.Text(self.page_area, height=1, width=30)
        entry.grid(row=3, column=1, columnspan=2, sticky="ew", padx=10, pady=5)
        entry.bind("<Tab>", lambda event: event.widget.tk_focusNext().focus() or "break")
        entry.bind("<Shift-Tab>", lambda event: event.widget.tk_focusPrev().focus() or "break")
        if "Coverage Amount" in self.transaction_data:
            entry.insert("1.0", self.transaction_data["Coverage Amount"])
        self.transaction_fields["Coverage Amount"] = entry

        # --- New Section: Owner's Policy / Lender's Policy ---
        self.owners_policy_var = tk.BooleanVar()
        self.lenders_policy_var = tk.BooleanVar()

        def on_owners_policy_change():
            if self.owners_policy_var.get():
                self.lenders_policy_var.set(False)
                print("DEBUG: ✅ Owner's Policy checked, Lender's Policy unchecked.")
            else:
                print("DEBUG: ℹ️ Owner's Policy unchecked.")

        def on_lenders_policy_change():
            if self.lenders_policy_var.get():
                self.owners_policy_var.set(False)
                print("DEBUG: ✅ Lender's Policy checked, Owner's Policy unchecked.")
            else:
                print("DEBUG: ℹ️ Lender's Policy unchecked.")

        owners_policy_checkbox = ttk.Checkbutton(self.page_area, text="Owner's Policy", variable=self.owners_policy_var, command=on_owners_policy_change)
        owners_policy_checkbox.grid(row=4, column=0, sticky="w", padx=10, pady=5)

        lenders_policy_checkbox = ttk.Checkbutton(self.page_area, text="Lender's Policy", variable=self.lenders_policy_var, command=on_lenders_policy_change)
        lenders_policy_checkbox.grid(row=4, column=1, sticky="w", padx=10, pady=5)

    def render_policy_exceptions_and_revisions(self):
        """Render fields for Standard Policy Exceptions, Legal Description, and Property Specific Exceptions."""
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
            if "Standard Policy Exceptions" in self.transaction_data:
                exception_number = str(idx - 2)
                if exception_number in self.transaction_data["Standard Policy Exceptions"]:
                    var.set(True)

        ttk.Label(self.page_area, text="Legal Description/Derivation Clause: (if None, type 'None')").grid(row=8, column=0, sticky="w", padx=10, pady=5)
        self.legal_description = tk.Text(self.page_area, height=5, width=50)
        self.legal_description.grid(row=9, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        if "Legal Description" in self.transaction_data:
            self.legal_description.insert("1.0", self.transaction_data["Legal Description"])

        ttk.Label(self.page_area, text="Property Specific Exceptions: (if None, type 'None')").grid(row=10, column=0, sticky="w", padx=10, pady=5)
        self.property_specific_exceptions = tk.Text(self.page_area, height=5, width=50)
        self.property_specific_exceptions.grid(row=11, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        if "Property Specific Exceptions" in self.transaction_data:
            self.property_specific_exceptions.insert("1.0", self.transaction_data["Property Specific Exceptions"])

        ttk.Label(self.page_area, text="Check the 'Revised' box only if this transaction already exists on the blockchain and needs to be updated or replaced:").grid(row=12, column=0, sticky="w", padx=10, pady=5)
        self.revised_var = tk.BooleanVar()
        revised_checkbox = ttk.Checkbutton(self.page_area, text="Revised", variable=self.revised_var)
        revised_checkbox.grid(row=13, column=0, sticky="w", padx=5, pady=5)
        if "Revision" in self.transaction_data:
            self.revised_var.set(self.transaction_data["Revision"] == "Yes")

    def toggle_select_all(self):
        """Toggle all checkboxes when 'Select All' is clicked."""
        select_all_state = self.select_all_var.get()
        for var in self.exceptions_vars.values():
            var.set(select_all_state)

    def save_current_page_data(self):
        """Save data from the currently visible page into self.transaction_data."""
        page_title = self.pages[self.current_page_index]
        print(f"DEBUG: Saving data from page: {page_title}")
        if page_title == "Property Details/Policy Date":
            for field, entry in self.entry_fields.items():
                self.transaction_data[field] = entry.get("1.0", tk.END).strip()
        elif page_title == "Transaction Details":
            for field, widget in self.transaction_fields.items():
                self.transaction_data[field] = widget.get("1.0", tk.END).strip()
            self.transaction_data["Owner's Policy"] = "Yes" if self.owners_policy_var.get() else "No"
            self.transaction_data["Lender's Policy"] = "Yes" if self.lenders_policy_var.get() else "No"
        elif page_title == "Policy Exceptions and Revisions":
            selected_exceptions = [str(idx + 1) for idx, (key, var) in enumerate(self.exceptions_vars.items()) if var.get()]
            self.transaction_data["Standard Policy Exceptions"] = ", ".join(selected_exceptions) if selected_exceptions else "None"
            self.transaction_data["Legal Description"] = self.legal_description.get("1.0", tk.END).strip()
            self.transaction_data["Property Specific Exceptions"] = self.property_specific_exceptions.get("1.0", tk.END).strip()
            self.transaction_data["Revision"] = "Yes" if self.revised_var.get() else "No"
        print("DEBUG: ✅ Current saved data:", self.transaction_data)

    def validate_page(self):
        """Ensure required fields are filled before moving forward."""
        page_title = self.pages[self.current_page_index]
        missing_fields = []
        if page_title == "Property Details/Policy Date":
            optional_fields = ["Apt/Building (if applicable)"]
            for field, widget in self.entry_fields.items():
                if field in optional_fields:
                    continue
                value = widget.get("1.0", tk.END).strip()
                if not value:
                    missing_fields.append(field)
                    widget.config(bg="lightcoral")
        elif page_title == "Transaction Details":
            for field, widget in self.transaction_fields.items():
                value = widget.get("1.0", tk.END).strip() if widget.winfo_class() == "Text" else widget.get().strip()
                if not value:
                    missing_fields.append(field)
                    widget.config(bg="lightcoral")
            if not (self.owners_policy_var.get() or self.lenders_policy_var.get()):
                missing_fields.append("Owner's/Lender's Policy")
        elif page_title == "Policy Exceptions and Revisions":
            if not any(var.get() for var in self.exceptions_vars.values()):
                missing_fields.append("Standard Policy Exceptions")
            if not self.legal_description.get("1.0", tk.END).strip():
                missing_fields.append("Legal Description/Derivation Clause")
                self.legal_description.config(bg="lightcoral")
            if not self.property_specific_exceptions.get("1.0", tk.END).strip():
                missing_fields.append("Property Specific Exceptions")
                self.property_specific_exceptions.config(bg="lightcoral")
        if missing_fields:
            error_message = "Fill out all required fields:\n" + "\n".join(missing_fields)
            messagebox.showerror("Error", error_message)
            return False
        return True

    def previous_page(self):
        """Navigate to the previous page."""
        if self.current_page_index > 0:
            self.save_current_page_data()
            self.current_page_index -= 1
            self.render_page()

    def next_page(self):
        """Navigate to the next page with validation."""
        if not self.validate_page():
            return
        self.save_current_page_data()
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
        self.save_current_page_data()
        transaction_data = self.transaction_data.copy()
        print("DEBUG: Attempting to submit transaction...")
        print("DEBUG: Full transaction data:", transaction_data)
        if self.add_transaction_callback:
            try:
                self.add_transaction_callback(transaction_data)
                print("DEBUG: ✅ Transaction successfully sent to TransactionManager.")
            except Exception as e:
                print(f"DEBUG: ⚠️ {e}")
                messagebox.showerror("Error", f"Transaction submission failed: {e}")
                return
        else:
            print("DEBUG: ⚠️ No transaction manager callback found!")
            return
        messagebox.showinfo("Success", "Transaction submitted successfully!")
        print("DEBUG: ✅ Submission complete. Resetting form...")
        self.reset_form()

    def reset_form(self):
        """Reset the form to its initial state."""
        for widget in self.page_area.winfo_children():
            widget.destroy()
        self.transaction_data = {}
        self.entry_fields = {}
        self.transaction_fields = {}
        self.exceptions_vars = {}
        self.current_page_index = 0
        print("DEBUG: Resetting form; current_page_index set to", self.current_page_index)
        self.render_page()
        self.page_area.update_idletasks()
