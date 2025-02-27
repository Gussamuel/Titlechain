import tkinter as tk
from tkinter import ttk
from src.transaction_form import TransactionForm
from src.views import PropertyView
from src.transaction_man import TransactionManager

class BlockchainTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.inner_notebook = ttk.Notebook(self)
        self.inner_notebook.pack(expand=True, fill='both')
        
        # Instantiate Transaction Manager first.
        self.transaction_manager = TransactionManager(self.inner_notebook)
        self.inner_notebook.add(self.transaction_manager, text="Transaction Manager")
        
        # Create Transaction Form with the proper callback.
        self.transaction_form = TransactionForm(
            self.inner_notebook,
            add_transaction_callback=self.transaction_manager.add_pending_transaction
        )
        self.inner_notebook.add(self.transaction_form, text="Add Transaction")
        
        self.property_view = PropertyView(self.inner_notebook)
        self.inner_notebook.add(self.property_view, text="View Properties")
