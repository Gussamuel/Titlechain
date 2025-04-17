import tkinter as tk
from tkinter import Frame, Label, Button, messagebox
from src.db_connection import DBConnectionGUI
from src import db_softpro_connection_global as spg
from src import db_connection_global as tcg
import src.login_global as login_global
import src.softpro_extractor as extractor
import os
import csv
from tkinter import filedialog
import pandas as pd
from tkinter.filedialog import asksaveasfilename
from src.db_connection_global import connection as title_conn

import warnings
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

def center_window(win, width, height):
    win.update_idletasks()  # Ensure win.winfo_screenwidth() is accurate
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

class SoftProTool(Frame):
    def __init__(self, parent, *args, **kwargs):
        super(SoftProTool, self).__init__(parent, *args, **kwargs)
        self.init_ui()

    def init_ui(self):
        title_label = Label(self, text="SoftPro Plugin Tool", font=("Arial", 14, "bold"))
        title_label.pack(padx=10, pady=10)

        info_label = Label(self, text="This tab manages SoftPro integration.\n"
                                      "Click to connect to SoftPro's SQL database.")
        info_label.pack(padx=10, pady=5)

        # Connect to SelectDb
        connect_btn = Button(self, text="Connect to SelectDb", command=self.connect_softpro_db)
        connect_btn.pack(pady=5)

        # Transfer mock data into TitleChainDb
        transfer_btn = Button(self, text="Transfer to TitleChainDB", command=self.transfer_to_titlechain)
        transfer_btn.pack(pady=5)

        # View what's in TitleChainDb
        view_btn = Button(self, text="Show TitleChain Data", command=self.show_titlechain_data)
        view_btn.pack(pady=5)

        # ←─ New button: Export entire TitleChain to one Excel workbook
        export_excel_btn = Button(self, text="Export TitleChain to Excel", command=self.export_to_excel)
        export_excel_btn.pack(pady=5)

    def connect_softpro_db(self):
        user = login_global.current_user
        if not user or "email" not in user:
            messagebox.showerror("Error", "No logged‑in user found.")
            return

        # Reset any previous SoftPro connection so the dialog always appears
        spg.softpro_connection = None

        # Launch the SoftPro DB dialog
        DBConnectionGUI(self.winfo_toplevel(), user, mode="softpro")

    def transfer_to_titlechain(self):
        """Pull the mock‐seeded rows from SelectDb into TitleChainDb."""
        select_conn = spg.softpro_connection
        title_conn  = tcg.connection
        if not select_conn:
            messagebox.showerror("Error", "Not connected to SelectDb.")
            return
        if not title_conn:
            messagebox.showerror("Error", "Not connected to TitleChainDb.")
            return

        print("DEBUG: → Starting transfer_to_titlechain()")
        try:
            extractor.transfer_mock_data(select_conn, title_conn)
            print("DEBUG: ← transfer_to_titlechain() completed successfully")
            messagebox.showinfo("Success", "Mock data transferred to TitleChainDb!")
        except Exception as e:
            print(f"DEBUG: ⚠️ transfer_to_titlechain() error: {e}")
            messagebox.showerror("Transfer Error", str(e))

    def show_titlechain_data(self):
        """Open a window showing each table in TitleChainDb in its own tab (all rows!), with CSV export."""
        import os, csv
        from tkinter import ttk, messagebox, filedialog

        # 1) grab the persistent TitleChainDb connection
        from src.db_connection_global import connection as title_conn
        if not title_conn:
            messagebox.showerror("Error", "Not connected to TitleChainDb.")
            return

        # 2) fetch all user tables once
        cur = title_conn.cursor()
        try:
            cur.execute("""
                SELECT TABLE_SCHEMA, TABLE_NAME
                  FROM INFORMATION_SCHEMA.TABLES
                 WHERE TABLE_TYPE='BASE TABLE'
                   AND TABLE_SCHEMA NOT IN ('sys','INFORMATION_SCHEMA')
                 ORDER BY TABLE_SCHEMA, TABLE_NAME
            """)
            tables = cur.fetchall()
        except Exception as e:
            cur.close()
            messagebox.showerror("Error fetching tables", str(e))
            return

        # 3) build the UI
        win = tk.Toplevel(self)
        desired_width = 1800
        desired_height = 900

        win.title("TitleChainDb Contents")
        # Set its size _before_ centering
        win.geometry(f"{desired_width}x{desired_height}")  
        # Now center it on screen
        center_window(win, desired_width, desired_height)
        # Prevent the user from resizing
        win.resizable(False, False)

        from tkinter import ttk
        # ─── Export button ───────────────────────────────────────────────
        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill="x", padx=5, pady=5)
        export_btn = ttk.Button(
            btn_frame,
            text="Export CSV",
            command=lambda: export_all_csv(tables)
        )
        export_btn.pack(side="left")
        # ────────────────────────────────────────────────────────────────

        notebook = ttk.Notebook(win)
        notebook.pack(expand=True, fill="both", padx=5, pady=5)

        # 4) populate one tab per table
        for schema, tbl in tables:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=f"{schema}.{tbl}")

            try:
                cur.execute(f"SELECT * FROM [{schema}].[{tbl}]")
                cols = [col[0] for col in cur.description]
                rows = cur.fetchall()
            except Exception as ex:
                lbl = ttk.Label(frame, text=f"Error reading {schema}.{tbl}:\n{ex}", foreground="red")
                lbl.pack(expand=True, fill="both", padx=10, pady=10)
                continue

            tree = ttk.Treeview(frame, columns=cols, show="headings")
            vsb  = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
            hsb  = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

            for c in cols:
                tree.heading(c, text=c, anchor="w")
                tree.column(c, anchor="w", width=120, minwidth=50)

            for row in rows:
                tree.insert("", "end", values=[str(v) for v in row])

            tree.grid(row=0, column=0, sticky="nsew")
            vsb.grid(row=0, column=1, sticky="ns")
            hsb.grid(row=1, column=0, sticky="ew")
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)

        cur.close()

        # ─── CSV Export helper ─────────────────────────────────────────
        def export_all_csv(tables_list):
            path = filedialog.asksaveasfilename(
                title="Save all tables into CSV",
                defaultextension=".csv",
                filetypes=[("CSV files","*.csv"),("All files","*.*")]
            )
            if not path:
                return

            try:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)

                    for schema, tbl in tables_list:
                        writer.writerow([f"--- {schema}.{tbl} ---"])
                        c2 = title_conn.cursor()
                        c2.execute(f"SELECT * FROM [{schema}].[{tbl}]")
                        cols2 = [col[0] for col in c2.description]
                        rows2 = c2.fetchall()
                        c2.close()

                        writer.writerow(cols2)
                        for r in rows2:
                            writer.writerow(r)
                        writer.writerow([])

                messagebox.showinfo(
                    "Export Complete",
                    f"All tables have been written into:\n{path}"
                )
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

    # ─── New method: Export all TitleChain tables into a single Excel workbook ────
    def export_to_excel(self):
        path = asksaveasfilename(
            title="Save all TitleChain tables to Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files","*.xlsx"),("All files","*.*")]
        )
        if not path:
            return

        # list the tables you want to dump
        tables_list = [
            ("dbo","Properties"),
            ("dbo","Owners"),
            ("dbo","Policies"),
            ("dbo","Documents"),
            ("dbo","Easements"),
            ("dbo","PolicyExceptions"),
            ("dbo","Requirements"),
            ("dbo","Orders"),
        ]

        try:
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                for schema, tbl in tables_list:
                    sql = f"SELECT * FROM [{schema}].[{tbl}]"
                    df = pd.read_sql_query(sql, title_conn)
                    sheet = f"{schema}_{tbl}"
                    df.to_excel(writer, sheet_name=sheet[:31], index=False)

            messagebox.showinfo("Export Complete", f"All tables have been saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
