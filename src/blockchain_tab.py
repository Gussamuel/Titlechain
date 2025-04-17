import tkinter as tk
from tkinter import ttk

# We import these to create the single TransactionManager, TransactionForm, etc.
from src.transaction_man import TransactionManager
from src.transaction_form import TransactionForm
from src.views import PropertyView
from src.softpro_plugin import SoftProTool

class BlockchainTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Create an inner notebook for everything blockchain-related
        self.inner_notebook = ttk.Notebook(self)
        self.inner_notebook.pack(expand=True, fill="both")

        # 1) Create the single TransactionManager (directly here),
        #    with self.inner_notebook as parent so it displays as a tab.
        self.transaction_manager = TransactionManager(self.inner_notebook)
        self.inner_notebook.add(self.transaction_manager, text="Transaction Manager")

        # 2) Create a TransactionForm that uses the manager’s callback
        self.transaction_form = TransactionForm(
            self.inner_notebook,
            add_transaction_callback=self.transaction_manager.add_pending_transaction
        )
        self.inner_notebook.add(self.transaction_form, text="Add Transaction")

        # 3) Create the PropertyView tab
        self.property_view = PropertyView(self.inner_notebook)
        self.inner_notebook.add(self.property_view, text="View Properties")


        # 4) SoftPro Plugin
        self.softpro_tool = SoftProTool(self.inner_notebook)
        self.inner_notebook.add(self.softpro_tool, text="SoftPro Plugin")