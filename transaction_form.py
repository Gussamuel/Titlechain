import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from utils import submit_transaction

class TransactionForm(ttk.Frame):
    def __init__(self, parent, add_transaction_callback=None):
        super().__init__(parent)
        self.add_transaction_callback = add_transaction_callback

        # Define categories and fields
        self.categories = {
            "Property Details": [
                "Property Address", "City", "State", "Zip Code", "County"
            ],
            "Participants": [
                "Buyer", "Seller", "Listing Agent", "Selling Agent", "Lender", 
                "Title Company 1", "Title Company 2"
            ],
            "Financial Details": [
                "Purchase Price", "Loan Amount", "Policy Types", "Policy Premiums", 
                "Lien Holder", "Lien Amount"
            ],
            "Important Dates": [
                "Lien Date", "Expiration Date", "Due Date", "Permit Issue Date", 
                "Survey Date", "Litigation Filing Date"
            ],
            "Additional Information": [
                "Tax Year", "Amount Due", "Amount Paid", "Easement Type", 
                "Easement Granted To", "Easement Description", "Zoning Code", 
                "Zoning Description", "Inspection Status", "Surveyor Name", 
                "Boundary Description", "Litigation Type", "Plaintiff", "Defendant", 
                "Case Status"
            ]
        }

        self.entries = {}
        self.current_category_index = 0
        self.category_keys = list(self.categories.keys())

        # Configure the grid to expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create the category frame (content area)
        self.category_frame = ttk.Frame(self)
        self.category_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)

        # Create the navigation button frame
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=1, column=0, pady=10)

        # Setup the initial category frame
        self.setup_category_frame()
        self.setup_navigation_buttons()

    def setup_category_frame(self):
        # Clear all widgets in the category frame
        for widget in self.category_frame.winfo_children():
            widget.destroy()

        # Configure grid in category_frame
        self.category_frame.grid_columnconfigure(0, weight=0)  # Labels
        self.category_frame.grid_columnconfigure(1, weight=1)  # Entries

        # Display the category title
        category = self.category_keys[self.current_category_index]
        title_label = ttk.Label(self.category_frame, text=category, font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='w')

        fields = self.categories[category]

        for idx, field in enumerate(fields):
            label = ttk.Label(self.category_frame, text=field + ":")
            label.grid(row=idx + 1, column=0, padx=10, pady=5, sticky='w')

            entry = ttk.Entry(self.category_frame, width=60)
            entry.grid(row=idx + 1, column=1, padx=10, pady=5, sticky='w')
            self.entries[field] = entry

    def setup_navigation_buttons(self):
        # Clear all widgets in the button frame
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        # Create Previous button
        if self.current_category_index > 0:
            prev_button = ttk.Button(self.button_frame, text="Previous", command=self.prev_category)
            prev_button.grid(row=0, column=0, padx=5, sticky='e')
        else:
            # Add a placeholder to maintain button alignment
            ttk.Label(self.button_frame).grid(row=0, column=0)

        # Create Next or Submit button
        if self.current_category_index < len(self.categories) - 1:
            next_button = ttk.Button(self.button_frame, text="Next", command=self.next_category)
            next_button.grid(row=0, column=1, padx=5, sticky='w')
        else:
            submit_button = ttk.Button(self.button_frame, text="Submit Transaction", command=self.confirm_submission)
            submit_button.grid(row=0, column=1, padx=5, sticky='w')

    def next_category(self):
        self.current_category_index += 1
        self.setup_category_frame()
        self.setup_navigation_buttons()

    def prev_category(self):
        self.current_category_index -= 1
        self.setup_category_frame()
        self.setup_navigation_buttons()

    def confirm_submission(self):
        """
        Show a confirmation dialog before submitting the transaction.
        """
        confirm = messagebox.askyesno(
            "Confirm Submission",
            "Are you sure you want to submit this transaction? "
            "You will have 15 minutes to un-submit it if you made a mistake."
        )

        if confirm:
            self.submit_form()

    def submit_form(self):
        transaction_data = {field: entry.get() for field, entry in self.entries.items()}

        if not all(transaction_data.values()):
            messagebox.showerror("Error", "All fields must be filled out.")
            return

        # Use the callback if provided
        if self.add_transaction_callback:
            self.add_transaction_callback(transaction_data)
            messagebox.showinfo("Success", "Transaction added to pending list.")
        else:
            success = submit_transaction(transaction_data)
            if success:
                messagebox.showinfo("Success", "Transaction added to the blockchain successfully.")
            else:
                messagebox.showerror("Error", "Failed to add transaction to the blockchain.")

        self.clear_form()
        self.current_category_index = 0
        self.setup_category_frame()
        self.setup_navigation_buttons()

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

# Main application setup
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Transaction Form")
    root.geometry("800x850")

    # Configure root grid
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    transaction_form = TransactionForm(root)
    transaction_form.grid(row=0, column=0, sticky='nsew')

    root.mainloop()