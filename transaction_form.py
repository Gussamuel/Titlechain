import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class TransactionForm(ttk.Frame):
    def __init__(self, parent, add_transaction_callback=None):
        super().__init__(parent)
        self.add_transaction_callback = add_transaction_callback

        # Define pages for the form
        self.pages = [
            "Property Address",
            "Policy Date",
            "Vested Parties",
            "Standard Policy Exceptions",
            "Property Specific Exceptions",
            "Legal Description/Derivation Clause",
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
        if page_title == "Property Address":
            self.render_property_address_fields()
        elif page_title == "Policy Date":
            self.render_policy_date_fields()
        elif page_title == "Vested Parties":
            self.render_vested_parties_fields()
        elif page_title == "Standard Policy Exceptions":
            self.render_text_area_field("Standard Policy Exceptions")
        elif page_title == "Property Specific Exceptions":
            self.render_text_area_field("Property Specific Exceptions")
        elif page_title == "Legal Description/Derivation Clause":
            self.render_text_area_field("Legal Description/Derivation Clause")

        # Update button visibility
        self.prev_button["state"] = tk.NORMAL if self.current_page_index > 0 else tk.DISABLED
        self.next_button["text"] = "Submit" if self.current_page_index == len(self.pages) - 1 else "Next"

    def render_property_address_fields(self):
        """Render fields for the Property Address page."""
        fields = ["Street", "Apt/Building (if applicable)", "City", "State", "Zip"]
        for idx, field in enumerate(fields):
            ttk.Label(self.page_area, text=f"{field}:").grid(row=idx + 1, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(self.page_area)
            entry.grid(row=idx + 1, column=1, sticky="ew", padx=10, pady=5)
            self.transaction_data[field] = entry

    def render_policy_date_fields(self):
        """Render fields for the Policy Date page."""
        ttk.Label(self.page_area, text="Policy Date (MM/DD/YYYY):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        entry = ttk.Entry(self.page_area)
        entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        self.transaction_data["Policy Date"] = entry

    def render_vested_parties_fields(self):
        """Render fields for the Vested Parties page."""
        ttk.Label(self.page_area, text="Vested Parties (one per line):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        text_area = tk.Text(self.page_area, height=8, width=40)
        text_area.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        self.transaction_data["Vested Parties"] = text_area

    def render_text_area_field(self, field_name):
        """Render a text area for fields that require detailed input."""
        ttk.Label(self.page_area, text=f"{field_name}:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        text_area = tk.Text(self.page_area, height=10, width=50)
        text_area.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        self.transaction_data[field_name] = text_area

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
    root.geometry("800x600")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    transaction_form = TransactionForm(root)
    transaction_form.grid(row=0, column=0, sticky="nsew")

    root.mainloop()