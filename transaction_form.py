import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from utils import submit_transaction

class TransactionForm(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

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

        # Create the initial category frame
        self.setup_category_frame()

    def setup_category_frame(self):
        # Clear all widgets for the new category screen
        for widget in self.winfo_children():
            widget.destroy()

        # Create a frame to hold the category content
        category_frame = ttk.Frame(self)
        category_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)

        # Configure grid in category_frame
        category_frame.grid_columnconfigure(0, weight=1, uniform="cols")
        category_frame.grid_columnconfigure(1, weight=2, uniform="cols")

        # Display the category title
        category = self.category_keys[self.current_category_index]
        title_label = ttk.Label(category_frame, text=category, font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='n')

        fields = self.categories[category]

        for idx, field in enumerate(fields):
            label = ttk.Label(category_frame, text=field + ":")
            label.grid(row=idx + 1, column=0, padx=10, pady=5, sticky='e')

            entry = ttk.Entry(category_frame)
            entry.grid(row=idx + 1, column=1, padx=10, pady=5, sticky='we')
            self.entries[field] = entry

            # Configure grid weights for entries
            category_frame.grid_rowconfigure(idx + 1, weight=1)

        # Navigation buttons frame
        button_frame = ttk.Frame(category_frame)
        button_frame.grid(row=len(fields) + 2, column=0, columnspan=2, pady=20)

        # Configure button_frame to center the buttons
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        if self.current_category_index > 0:
            prev_button = ttk.Button(button_frame, text="Previous", command=self.prev_category)
            prev_button.grid(row=0, column=0, padx=5, sticky='e')
        else:
            # Placeholder to keep alignment
            ttk.Label(button_frame).grid(row=0, column=0)

        if self.current_category_index < len(self.categories) - 1:
            next_button = ttk.Button(button_frame, text="Next", command=self.next_category)
            next_button.grid(row=0, column=1, padx=5, sticky='w')
        else:
            submit_button = ttk.Button(button_frame, text="Submit Transaction", command=self.submit_form)
            submit_button.grid(row=0, column=1, padx=5, sticky='w')

    def next_category(self):
        self.current_category_index += 1
        self.setup_category_frame()

    def prev_category(self):
        self.current_category_index -= 1
        self.setup_category_frame()

    def submit_form(self):
        transaction_data = {field: entry.get() for field, entry in self.entries.items()}

        if not all(transaction_data.values()):
            messagebox.showerror("Error", "All fields must be filled out.")
            return

        success = submit_transaction(transaction_data)
        if success:
            messagebox.showinfo("Success", "Transaction added to the blockchain successfully.")
            self.clear_form()
            self.current_category_index = 0
            self.setup_category_frame()
        else:
            messagebox.showerror("Error", "Failed to add transaction to the blockchain.")

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

# Main application setup
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Transaction Form")
    root.geometry("800x600")

    # Configure root grid
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    transaction_form = TransactionForm(root)
    transaction_form.grid(row=0, column=0, sticky='nsew')

    root.mainloop()