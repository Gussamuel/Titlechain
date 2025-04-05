import tkinter as tk
from tkinter import ttk, messagebox
import sys
import pyodbc
import clr
import pythonnet
from ttkbootstrap import Style
from src import db_connection_global

# We need pythonnet for .NET interop
pythonnet.load("coreclr")
clr.AddReference("System.Data")
from System.Data.Sql import SqlDataSourceEnumerator

def center_window(win, width, height):
    win.update_idletasks()  # Ensure win.winfo_screenwidth() is accurate
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

class DBConnectionGUI(tk.Toplevel):
    def __init__(self, master, logged_in_user):
        super().__init__(master)
        self.transient(master)
        self.grab_set()
        self.deiconify()  # Ensure the Toplevel window is visible
        desired_width = 600
        desired_height = 400
        center_window(self, desired_width, desired_height)
        self.resizable(False, False)
        self.style = Style(theme="flatly")        
        self.title("Connect to TitleChain (SQL Express)")
        print("DEBUG: ✅ DBConnectionGUI initialized")
        self.logged_in_user = logged_in_user
        self.database_name = "TitleChainDb"
        print("DEBUG: Logged in user in DBConnectionGUI:", self.logged_in_user)

        # Label + entry for server instance
        top_frame = tk.Frame(self)
        top_frame.pack(pady=(10, 5), fill="x", padx=105)
        tk.Label(top_frame, text="Server Instance:").pack(side=tk.LEFT, padx=(5,2))
        self.server_entry = tk.Entry(top_frame, width=30)
        self.server_entry.pack(side=tk.LEFT, padx=5)
        # Pre-populate server entry if user has a default saved
        default_server = self.logged_in_user.get("default_server", "")
        if default_server:
            print("DEBUG: Found default server in user profile:", default_server)
            self.server_entry.delete(0, tk.END)
            self.server_entry.insert(0, default_server)
            self.set_default_var = tk.BooleanVar(value=True)
        else:
            self.set_default_var = tk.BooleanVar(value=False)

        # "Scan" button to discover SQL servers
        self.scan_button = tk.Button(top_frame, text="Scan", width=8, command=self.scan_for_servers)
        self.scan_button.pack(side=tk.LEFT, padx=5)

        # Treeview to display discovered servers
        tk.Label(self, text="Discovered Servers:").pack(pady=(10,0))
        self.server_tree = ttk.Treeview(self, columns=["instance"], show="tree", height=6)
        self.server_tree.pack(padx=10, pady=5, fill="both", expand=True)
        self.server_tree.bind("<Double-1>", self.on_tree_double_click)

        # "Set as default" checkbox
        tk.Checkbutton(self, text="Set as default", variable=self.set_default_var).pack(pady=5)

        # Buttons for Connect / Exit
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=(5, 5))
        self.connect_button = tk.Button(btn_frame, text="Connect", width=10, command=self.connect_to_server)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        self.exit_button = tk.Button(btn_frame, text="Exit", width=10, command=self.on_exit)
        self.exit_button.pack(side=tk.LEFT, padx=5)

        self.connection = None
        print("DEBUG: DBConnectionGUI __init__ complete")

    def scan_for_servers(self):
        """
        Uses .NET's SqlDataSourceEnumerator on a background thread
        to find SQL Servers. Updates the Treeview on the main thread.
        """
        print("DEBUG: scan_for_servers() called")
        # Disable the scan button to prevent re-entry.
        self.scan_button.config(state="disabled")
        # Clear existing items in the tree.
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)
        
        def background_scan():
            try:
                enumerator = SqlDataSourceEnumerator.Instance
                data_table = enumerator.GetDataSources()
                rows = data_table.Rows
                print(f"DEBUG: Found {rows.Count} server(s).")
                discovered = []
                for i in range(rows.Count):
                    row = rows[i]
                    server_name = row["ServerName"]
                    instance_name = row["InstanceName"]
                    display_text = server_name
                    if instance_name:
                        display_text += f"\\{instance_name}"
                    discovered.append(display_text)
                # Update the treeview on the main thread.
                self.master.after(0, lambda: update_tree(discovered))
            except Exception as e:
                self.master.after(0, lambda: messagebox.showerror("Scan Error", f"Error scanning for SQL Servers:\n{e}"))
                print("DEBUG: Exception scanning for servers:", e)
            finally:
                self.master.after(0, lambda: self.scan_button.config(state="normal"))
        
        def update_tree(servers):
            for srv in servers:
                node_id = self.server_tree.insert("", "end", text=srv)
                self.server_tree.set(node_id, "instance", srv)
            if not servers:
                messagebox.showinfo("Scan Complete", "No SQL Servers found. Make sure SQL Browser is running.")
        
        import threading
        threading.Thread(target=background_scan, daemon=True).start()

    def on_tree_double_click(self, event):
        """
        Populate the server entry with the double-clicked value.
        """
        item_id = self.server_tree.focus()
        instance_name = self.server_tree.set(item_id, "instance")
        if instance_name:
            self.server_entry.delete(0, tk.END)
            self.server_entry.insert(0, instance_name)
    
    def update_default_server(self, server):
        """
        Update the logged-in user's default server in the user profile.
        If the 'Set as default' checkbox is checked, store the server;
        if not, remove any default entry.
        """
        try:
            from src.login import load_users, save_users  # Adjust the import as needed.
        except ImportError:
            from login import load_users, save_users

        try:
            users = load_users()
            user_email = self.logged_in_user["email"]
            if user_email in users:
                if self.set_default_var.get():
                    users[user_email]["default_server"] = server
                    print("DEBUG: Default server saved for user:", server)
                else:
                    if "default_server" in users[user_email]:
                        del users[user_email]["default_server"]
                        print("DEBUG: Default server removed from user profile.")
                save_users(users)
        except Exception as e:
            print("DEBUG: Exception in update_default_server:", e)


    def connect_to_server(self):
        """
        Attempt to connect to the 'TitleChainDb' on the specified server.
        If the DB doesn't exist, create it if the user has permission.
        """
        # Disable UI elements immediately to prevent further clicks.
        for widget in (self.scan_button, self.server_entry, self.connect_button, self.exit_button):
            widget.config(state="disabled")
        
        server = self.server_entry.get().strip()
        if not server:
            messagebox.showerror("Error", "Please enter or select a server instance.")
            # Re-enable the UI elements if no server is provided.
            for widget in (self.scan_button, self.server_entry, self.connect_button, self.exit_button):
                widget.config(state="normal")
            return

        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={self.database_name};Trusted_Connection=yes;"
        print("DEBUG: Attempting connection with conn_str:", conn_str)

        try:
            self.connection = pyodbc.connect(conn_str)
            messagebox.showinfo("Connected", f"Connected to {self.database_name} on {server}")
            # Update default server in user profile.
            self.update_default_server(server)
            # Save connection to global variable.
            db_connection_global.connection = self.connection
            
            # Now launch the main UI.
            self.destroy()
            self.master.after(100, self.launch_main_ui)
        except Exception as e:
            print("DEBUG: Connection attempt failed:", e)
            if "Cannot open database" in str(e) or "Invalid catalog name" in str(e):
                print("DEBUG: TitleChainDb not found on server.")
                if not self.logged_in_user.get("can_create_db", False):
                    print("DEBUG: ❌ Access Denied: Invalid Privileges")
                    messagebox.showerror(
                        "Permission Denied",
                        "TitleChainDb does not exist and you do not have permission to create it.\nPlease contact a system administrator."
                    )
                    # Re-enable UI elements since connection failed.
                    for widget in (self.scan_button, self.server_entry, self.connect_button, self.exit_button):
                        widget.config(state="normal")
                    return
                if messagebox.askyesno("Database Not Found", "TitleChainDb not found. Create a new database?"):
                    if self.create_db(server):
                        print("DEBUG: ✅ Access Granted: Valid Privileges")
                        messagebox.showinfo("Database Created", "TitleChainDb created successfully.\nPlease click Connect again to establish a connection.")
                        # Re-enable UI elements so user can manually reconnect.
                        for widget in (self.scan_button, self.server_entry, self.connect_button, self.exit_button):
                            widget.config(state="normal")
                        return
                    else:
                        messagebox.showerror("Error", "Failed to create TitleChainDb.")
                        for widget in (self.scan_button, self.server_entry, self.connect_button, self.exit_button):
                            widget.config(state="normal")
                        return
                else:
                    print("DEBUG: User declined to create TitleChainDb.")
                    for widget in (self.scan_button, self.server_entry, self.connect_button, self.exit_button):
                        widget.config(state="normal")
            else:
                messagebox.showerror("Connection Error", f"Error connecting:\n{e}")
                for widget in (self.scan_button, self.server_entry, self.connect_button, self.exit_button):
                    widget.config(state="normal")

    def create_db(self, server):
        """
        Connect to the master database, create TitleChainDb, then create the Orders table.
        Uses autocommit=True to avoid multi-statement transaction issues.
        """
        print("DEBUG: create_db() called for server:", server)
        try:
            master_conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE=master;Trusted_Connection=yes;"
            print("DEBUG: Connecting to master with:", master_conn_str)
            conn_master = pyodbc.connect(master_conn_str, autocommit=True)
            cursor = conn_master.cursor()
            cursor.execute(f"CREATE DATABASE {self.database_name}")
            conn_master.close()
            print("DEBUG: Database created:", self.database_name)

            new_db_conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={self.database_name};Trusted_Connection=yes;"
            print("DEBUG: Connecting to new database with:", new_db_conn_str)
            conn_new = pyodbc.connect(new_db_conn_str, autocommit=True)
            cursor = conn_new.cursor()
            create_table_sql = """
                CREATE TABLE Orders (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    transaction_id UNIQUEIDENTIFIER DEFAULT NEWID(),
                    property_address NVARCHAR(255),
                    policy_date DATE,
                    policy_number NVARCHAR(100),
                    vested_parties NVARCHAR(255),
                    underwriters NVARCHAR(255),
                    coverage_amount DECIMAL(18,2),
                    owners_policy NVARCHAR(255),
                    lenders_policy NVARCHAR(255),
                    standard_policy_exceptions NVARCHAR(MAX),
                    property_specific_exceptions NVARCHAR(MAX),
                    legal_description NVARCHAR(MAX),
                    revision INT DEFAULT 1
                )
            """
            print("DEBUG: Creating Orders table.")
            cursor.execute(create_table_sql)
            conn_new.close()
            print("DEBUG: Orders table created in TitleChainDb.")
            return True
        except Exception as e:
            print("DEBUG: Exception in create_db:", e)
            return False

    def on_exit(self):
        response = messagebox.askyesno("Exit", "Are you sure you want to quit?")
        if response:
            self.destroy()
            sys.exit()

    def launch_main_ui(self):
        """
        Launch the main TitleChain UI after a successful database connection.
        """
        try:
            print("DEBUG: Launching TitleChainApp")
            from TitleChain import TitleChainApp
            # Pass the same root (self.master) so the new UI shares the theme and settings.
            main_app = TitleChainApp(self.master)
            main_app.deiconify()  # Make sure it shows up.
            # No need to call main_app.mainloop() because the root's mainloop is running.
        except Exception as e:
            print("DEBUG: Exception launching TitleChainApp:", e)
