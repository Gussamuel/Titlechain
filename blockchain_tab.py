import tkinter as tk
from tkinter import ttk
from transaction_form import TransactionForm
from views import PropertyView
from transaction_man import TransactionManager

class BlockchainTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.inner_notebook = ttk.Notebook(self)
        self.inner_notebook.pack(expand=True, fill='both')

        self.transaction_form = TransactionForm(self.inner_notebook)
        self.inner_notebook.add(self.transaction_form, text="Add Transaction")
        
        self.property_view = PropertyView(self.inner_notebook)
        self.inner_notebook.add(self.property_view, text="View Properties")
        
        self.transaction_manager = TransactionManager(self.inner_notebook)
        self.inner_notebook.add(self.transaction_manager, text="Transaction Manager")