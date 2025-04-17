import tkinter as tk
from tkinter import ttk, messagebox
import sys
import pyodbc
import clr
import pythonnet
from ttkbootstrap import Style
from src import db_connection_global
from src import db_softpro_connection_global

pythonnet.load("coreclr")
clr.AddReference("System.Data")
from System.Data.Sql import SqlDataSourceEnumerator

def center_window(win, width, height):
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

class DBConnectionGUI(tk.Toplevel):
    def __init__(self, master, logged_in_user=None, mode="titlechain"):
        super().__init__(master)
        self.transient(master)
        self.grab_set()
        self.deiconify()
        center_window(self, 600, 400)
        self.resizable(False, False)
        self.style = Style(theme="flatly")
        self.title("Connect to SQL Server")

        # Ensure logged_in_user is a dict and warn if no user info was passed.
        if logged_in_user is None or not logged_in_user:
            print("DEBUG: No logged in user information provided.")
            logged_in_user = {}
        self.logged_in_user = logged_in_user

        self.mode = mode
        self.database_name = "TitleChainDb" if mode == "titlechain" else "SelectDb"

        print("DEBUG: ✅ DBConnectionGUI initialized")
        print("DEBUG: Logged in user in DBConnectionGUI:")
        if self.logged_in_user:
            for k, v in self.logged_in_user.items():
                print(f"       • {k}: {v}")
        else:
            print("       • No user info available.")
        print("DEBUG: Mode:", self.mode)
        print("DEBUG: Database:", self.database_name)

        if self.mode == "softpro" and db_softpro_connection_global.softpro_connection:
            print("DEBUG: ✅ Connection to 'SelectDb' already made!")
            self.destroy()
            return

        top_frame = tk.Frame(self)
        top_frame.pack(pady=(10, 5), fill="x", padx=105)
        tk.Label(top_frame, text="Server Instance:").pack(side=tk.LEFT, padx=(5, 2))
        self.server_entry = tk.Entry(top_frame, width=30)
        self.server_entry.pack(side=tk.LEFT, padx=5)

        key = "default_server" if self.mode == "titlechain" else "default_select_server"
        default_server = self.logged_in_user.get(key, "")
        self.set_default_var = tk.BooleanVar(value=bool(default_server))
        if default_server:
            self.server_entry.insert(0, default_server)

        self.scan_button = tk.Button(top_frame, text="Scan", width=8, command=self.scan_for_servers)
        self.scan_button.pack(side=tk.LEFT, padx=5)

        tk.Label(self, text="Discovered Servers:").pack(pady=(10, 0))
        self.server_tree = ttk.Treeview(self, columns=["instance"], show="tree", height=6)
        self.server_tree.pack(padx=10, pady=5, fill="both", expand=True)
        self.server_tree.bind("<Double-1>", self.on_tree_double_click)
        tk.Checkbutton(self, text="Set as default", variable=self.set_default_var).pack(pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=(5, 5))
        self.connect_button = tk.Button(btn_frame, text="Connect", width=10, command=self.connect_to_server)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        self.exit_button = tk.Button(btn_frame, text="Exit", width=10, command=self.on_exit)
        self.exit_button.pack(side=tk.LEFT, padx=5)

    def scan_for_servers(self):
        self.scan_button.config(state="disabled")
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)

        def background_scan():
            try:
                enumerator = SqlDataSourceEnumerator.Instance
                data_table = enumerator.GetDataSources()
                rows = data_table.Rows
                discovered = []
                for i in range(rows.Count):
                    row = rows[i]
                    server_name = row["ServerName"]
                    instance_name = row["InstanceName"]
                    display_text = server_name
                    if instance_name:
                        display_text += f"\\{instance_name}"
                    discovered.append(display_text)
                self.master.after(0, lambda: update_tree(discovered))
            except Exception as e:
                self.master.after(0, lambda: messagebox.showerror("Scan Error", str(e)))
            finally:
                self.master.after(0, lambda: self.scan_button.config(state="normal"))

        def update_tree(servers):
            for srv in servers:
                node_id = self.server_tree.insert("", "end", text=srv)
                self.server_tree.set(node_id, "instance", srv)
            if not servers:
                messagebox.showinfo("Scan Complete", "No SQL Servers found.")

        import threading
        threading.Thread(target=background_scan, daemon=True).start()

    def on_tree_double_click(self, event):
        item_id = self.server_tree.focus()
        instance_name = self.server_tree.set(item_id, "instance")
        if instance_name:
            self.server_entry.delete(0, tk.END)
            self.server_entry.insert(0, instance_name)

    def connect_to_server(self):
        for widget in (self.scan_button, self.server_entry, self.connect_button, self.exit_button):
            widget.config(state="disabled")

        server = self.server_entry.get().strip()
        if not server:
            messagebox.showerror("Error", "Please enter or select a server instance.")
            for widget in (self.scan_button, self.server_entry, self.connect_button, self.exit_button):
                widget.config(state="normal")
            return

        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={self.database_name};Trusted_Connection=yes;"
        print("DEBUG: Attempting connection with conn_str:", conn_str)

        try:
            self.connection = pyodbc.connect(conn_str)
            messagebox.showinfo("Connected", f"Connected to {self.database_name} on {server}")

            if self.mode == "softpro":
                db_softpro_connection_global.softpro_connection = self.connection
                print("DEBUG: ✅ SoftPro connection stored.")
            else:
                db_connection_global.connection = self.connection
                print("DEBUG: ✅ TitleChain connection stored.")

            # Update user preferences with the selected default (if checked)
            self.update_default_server(server)

            if self.mode == "softpro":
                # Display only the logged in user's info from users.json.
                self.display_user_info()
            else:
                self.master.after(100, self.launch_main_ui)

            self.destroy()
        except Exception as e:
            print("DEBUG: Connection attempt failed:", e)
            # If in titlechain mode, check if the error indicates that the database doesn't exist.
            if self.mode == "titlechain" and ("Cannot open database" in str(e) or "Invalid catalog name" in str(e)):
                print("DEBUG: TitleChainDb not found on server.")
                if not self.logged_in_user.get("can_create_db", False):
                    print("DEBUG: ❌ Access Denied: Invalid Privileges")
                    messagebox.showerror(
                        "Permission Denied",
                        "TitleChainDb does not exist and you do not have permission to create it.\nPlease contact a system administrator."
                    )
                    for widget in (self.scan_button, self.server_entry, self.connect_button, self.exit_button):
                        widget.config(state="normal")
                    return
                if messagebox.askyesno("Database Not Found", "TitleChainDb not found. Create a new database?"):
                    if self.create_db(server):
                        print("DEBUG: ✅ Access Granted: Valid Privileges")
                        messagebox.showinfo("Database Created", "TitleChainDb created successfully.\nPlease click Connect again to establish a connection.")
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
                    return
            else:
                messagebox.showerror("Connection Error", f"Error connecting:\n{e}")
                for widget in (self.scan_button, self.server_entry, self.connect_button, self.exit_button):
                    widget.config(state="normal")


    def create_db(self, server):
        print("DEBUG: create_db() called for server:", server)
        try:
            # 1) Create the database
            master_conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};DATABASE=master;Trusted_Connection=yes;"
            )
            print("DEBUG: Connecting to master with:", master_conn_str)
            conn_master = pyodbc.connect(master_conn_str, autocommit=True)
            cursor_master = conn_master.cursor()
            cursor_master.execute(f"CREATE DATABASE {self.database_name}")
            conn_master.close()
            print("DEBUG: Database created:", self.database_name)

            # 2) Connect to the new TitleChainDb
            new_db_conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};DATABASE={self.database_name};Trusted_Connection=yes;"
            )
            print("DEBUG: Connecting to new database with:", new_db_conn_str)
            conn_new = pyodbc.connect(new_db_conn_str, autocommit=True)
            cursor = conn_new.cursor()

            # 3) Ensure zref schema exists
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'zref')
                    EXEC('CREATE SCHEMA zref');
            """)

            # 4) DDL for lookup tables (must run before core tables to satisfy FKs)
            ddl_statements = [
                # --- ZREF Lookup Tables ---
                """
                CREATE TABLE zref.DocReportType (
                    Code         NVARCHAR(10)   NOT NULL PRIMARY KEY,
                    Description  NVARCHAR(255)  NULL,
                    IsActive     BIT            NOT NULL DEFAULT 1,
                    IsProtected  BIT            NOT NULL DEFAULT 0,
                    SortOrder    SMALLINT       NULL
                )
                """,
                """
                CREATE TABLE zref.Easement (
                    ID          INT            NOT NULL PRIMARY KEY,
                    Description NVARCHAR(255)  NULL,
                    IsActive    BIT            NOT NULL DEFAULT 1,
                    IsProtected BIT            NOT NULL DEFAULT 0,
                    SortOrder   SMALLINT       NULL
                )
                """,
                """
                CREATE TABLE zref.Exception1099 (
                    ID          INT            NOT NULL PRIMARY KEY,
                    Code        NVARCHAR(50)   NULL,
                    Description NVARCHAR(255)  NULL,
                    IsActive    BIT            NOT NULL DEFAULT 1,
                    IsProtected BIT            NOT NULL DEFAULT 0,
                    SortOrder   SMALLINT       NULL
                )
                """,
                """
                CREATE TABLE zref.RequirementExceptionNumberingType (
                    ID          INT            NOT NULL PRIMARY KEY,
                    Description NVARCHAR(255)  NULL,
                    IsActive    BIT            NOT NULL DEFAULT 1,
                    IsProtected BIT            NOT NULL DEFAULT 0,
                    SortOrder   SMALLINT       NULL
                )
                """,
                """
                CREATE TABLE zref.RequirementExceptionType (
                    ID          INT            NOT NULL PRIMARY KEY,
                    Description NVARCHAR(255)  NULL,
                    IsActive    BIT            NOT NULL DEFAULT 1,
                    IsProtected BIT            NOT NULL DEFAULT 0,
                    SortOrder   SMALLINT       NULL
                )
                """,
                # --- Core Tables ---
                """
                CREATE TABLE dbo.Properties (
                    PropertyID        UNIQUEIDENTIFIER   NOT NULL PRIMARY KEY,
                    SoftProParcelId   INT                NOT NULL,
                    SoftProRootId     INT                NULL,
                    ParcelNumber      NVARCHAR(50)       NULL,
                    ParcelType        SMALLINT           NULL,
                    CreatedOn         DATETIME2          NOT NULL
                )
                """,
                """
                CREATE TABLE dbo.Owners (
                    OwnerID           UNIQUEIDENTIFIER   NOT NULL PRIMARY KEY,
                    PropertyID        UNIQUEIDENTIFIER   NOT NULL REFERENCES dbo.Properties(PropertyID),
                    SoftProGrantorId  INT                NOT NULL,
                    Name              NVARCHAR(200)      NULL,
                    Address           NVARCHAR(500)      NULL,
                    CreatedOn         DATETIME2          NOT NULL
                )
                """,
                """
                CREATE TABLE dbo.Policies (
                    PolicyID          UNIQUEIDENTIFIER   NOT NULL PRIMARY KEY,
                    PropertyID        UNIQUEIDENTIFIER   NOT NULL REFERENCES dbo.Properties(PropertyID),
                    SoftProPolicyId   INT                NOT NULL,
                    PolicyNumber      NVARCHAR(50)       NULL,
                    PolicyDate        DATE               NULL,
                    CoverageAmount    DECIMAL(18,2)      NULL,
                    PolicyType        NVARCHAR(50)       NULL,
                    CreatedOn         DATETIME2          NOT NULL
                )
                """,
                """
                CREATE TABLE dbo.Documents (
                    DocumentID        UNIQUEIDENTIFIER   NOT NULL PRIMARY KEY,
                    PropertyID        UNIQUEIDENTIFIER   NOT NULL REFERENCES dbo.Properties(PropertyID),
                    SoftProDocId      INT                NOT NULL,
                    FileName          NVARCHAR(255)      NULL,
                    FilePath          NVARCHAR(1024)     NULL,
                    DocType           NVARCHAR(100)      NULL,
                    CreatedOn         DATETIME2          NOT NULL,
                    DateRecorded      DATETIME2          NULL,
                    InstrumentNumber  NVARCHAR(50)       NULL
                )
                """,
                """
                CREATE TABLE dbo.Easements (
                    EasementID        UNIQUEIDENTIFIER   NOT NULL PRIMARY KEY,
                    PropertyID        UNIQUEIDENTIFIER   NOT NULL REFERENCES dbo.Properties(PropertyID),
                    SoftProEasementId INT                NULL,
                    ZrefEasementID    INT                NULL REFERENCES zref.Easement(ID),
                    Code              NVARCHAR(10)       NULL,
                    Description       NVARCHAR(100)      NULL,
                    CreatedOn         DATETIME2          NOT NULL
                )
                """,
                """
                CREATE TABLE dbo.PolicyExceptions (
                    ExceptionID       UNIQUEIDENTIFIER   NOT NULL PRIMARY KEY,
                    PropertyID        UNIQUEIDENTIFIER   NOT NULL REFERENCES dbo.Properties(PropertyID),
                    SoftProExceptionId INT               NOT NULL,
                    ExceptionCode     INT                NULL,
                    Description       NVARCHAR(MAX)      NULL,
                    CreatedOn         DATETIME2          NOT NULL
                )
                """,
                """
                CREATE TABLE dbo.Requirements (
                    RequirementID     UNIQUEIDENTIFIER   NOT NULL PRIMARY KEY,
                    PropertyID        UNIQUEIDENTIFIER   NOT NULL REFERENCES dbo.Properties(PropertyID),
                    SoftProReqId      INT                NOT NULL,
                    ReqTypeCode       INT                NULL,
                    ReqTypeDesc       NVARCHAR(MAX)      NULL,
                    NumberingTypeCode INT                NULL,
                    NumberingTypeDesc NVARCHAR(MAX)      NULL,
                    CreatedOn         DATETIME2          NOT NULL
                )
                """,
                """
                CREATE TABLE dbo.Orders (
                    id                            INT IDENTITY(1,1) PRIMARY KEY,
                    transaction_id                UNIQUEIDENTIFIER DEFAULT NEWID(),
                    property_address              NVARCHAR(255),
                    policy_date                   DATE,
                    policy_number                 NVARCHAR(100),
                    vested_parties                NVARCHAR(255),
                    underwriters                  NVARCHAR(255),
                    coverage_amount               DECIMAL(18,2),
                    owners_policy                 NVARCHAR(255),
                    lenders_policy                NVARCHAR(255),
                    standard_policy_exceptions    NVARCHAR(MAX),
                    property_specific_exceptions  NVARCHAR(MAX),
                    legal_description             NVARCHAR(MAX),
                    revised                       INT DEFAULT 1,
                    revision                      NVARCHAR(MAX)
                )
                """
            ]

            # 5) Execute each DDL
            for ddl in ddl_statements:
                print("DEBUG: Executing DDL…")
                cursor.execute(ddl)

            conn_new.close()
            print("DEBUG: All tables created in", self.database_name)
            return True

        except Exception as e:
            print("DEBUG: Exception in create_db:", e)
            return False

    def update_default_server(self, server):
        try:
            # import helpers
            try:
                from src.login import load_users, save_users
            except ImportError:
                from login import load_users, save_users

            # grab current email
            user_email = self.logged_in_user.get("email", "")
            if not user_email:
                print("DEBUG: No user email found; skipping default server update.")
                return

            # load only this user's data
            users = load_users(user_email)

            # pick key based on mode
            key = "default_server" if self.mode == "titlechain" else "default_select_server"
            print(f"DEBUG: Updating default server for '{user_email}' under '{key}'")

            if self.set_default_var.get():
                users[user_email][key] = server
                print(f"DEBUG: ✅ Saved default server: {server}")
            else:
                users[user_email].pop(key, None)
                print("DEBUG: 🧹 Removed default server setting")

            # persist change
            save_users(users)

            # final confirmation
            print("DEBUG: ✅ Profile updated.")
        except Exception as e:
            print("DEBUG: update_default_server error:", e)

    def display_user_info(self):
        try:
            # we already have the user dict in self.logged_in_user
            user_info = self.logged_in_user or {}
            if not user_info:
                messagebox.showerror("Error", "User information not found.")
                return
        except Exception as e:
            print("DEBUG: display_user_info error:", e)
            messagebox.showerror("Error", f"Failed to display user information: {e}")

    def on_exit(self):
        if self.mode == "softpro":
            print("DEBUG: SoftPro DB window closed.")
            self.destroy()
        else:
            if messagebox.askyesno("Exit", "Are you sure you want to quit?"):
                self.destroy()
                sys.exit()

    def launch_main_ui(self):
        try:
            print("DEBUG: Launching TitleChainApp")
            from TitleChain import TitleChainApp
            main_app = TitleChainApp(self.master)
            main_app.deiconify()
        except Exception as e:
            print("DEBUG: Exception launching TitleChainApp:", e)
