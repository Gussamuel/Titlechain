import sys
import os
import json
import uuid
import tkinter as tk
from tkinter import messagebox
from src.db_connection import DBConnectionGUI
from ttkbootstrap import Style
import subprocess
import ctypes

import sys
import tkinter as tk

# Single instance check (only executed once)
try:
    import win32event, win32api, win32con
except ImportError:
    print("DEBUG: win32 modules not available; skipping single instance check.")
else:
    # Define ERROR_ALREADY_EXISTS if not present.
    ERROR_ALREADY_EXISTS = 183
    mutex = win32event.CreateMutex(None, False, "TitleChain_SingleInstance_Mutex")
    if win32api.GetLastError() == ERROR_ALREADY_EXISTS:
        try:
            root = tk.Tk()
            root.withdraw()  # Hide main window
            from tkinter import messagebox
            messagebox.showerror("Error", "Only one instance of TitleChain can be open at a time.")
        except Exception:
            print("Only one instance of TitleChain can be open at a time.")
        sys.exit(0)

# Set a global flag so subsequent modules know the check was already done.
SINGLE_INSTANCE_CHECK_DONE = True

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    base_dir = os.path.dirname(os.path.dirname(sys.executable))
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(base_dir, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

def load_users(logged_in_email=None):
    print("DEBUG: load_users() called")
    if not os.path.exists(DATA_DIR):
        print(f"DEBUG: DATA_DIR '{DATA_DIR}' does not exist. Creating it.")
        os.makedirs(DATA_DIR)
    if os.path.exists(USERS_FILE):
        print(f"DEBUG: USERS_FILE '{USERS_FILE}' exists. Loading users.")
        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
                if logged_in_email:
                    if logged_in_email in users:
                        print(f"DEBUG: Loaded details for user {logged_in_email}:")
                        for key, value in users[logged_in_email].items():
                            print(f"    {key}: {value}")
                    else:
                        print(f"DEBUG: No details found for user {logged_in_email}.")
                else:
                    print("DEBUG: Loaded users (details not printed).")
                return users
        except Exception as e:
            print("DEBUG: Error loading users:", e)
            return {}
    else:
        print(f"DEBUG: USERS_FILE '{USERS_FILE}' does not exist. Returning empty dict.")
    return {}

def save_users(users):
    print("DEBUG: save_users() called with users:", users)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)
    print("DEBUG: Users saved successfully.")

def center_window(win, width, height):
    win.update_idletasks()  # Ensure win.winfo_screenwidth() is accurate
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

def is_admin():
    """Returns True if the current process has admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_command_as_admin(cmd):
    """
    Uses ShellExecuteW with the 'runas' verb to run a command with elevated privileges.
    Returns True if successful (HINSTANCE > 32), False otherwise.
    """
    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", f'/c {cmd}', None, 1)
    return ret > 32

def create_launch_daemon():
    """
    Creates a scheduled task that runs listener.exe at user logon with highest privileges.
    Returns True if the task exists or is successfully created; otherwise, False.
    """
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    def run_command_as_admin(cmd):
        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", f'/c {cmd}', None, 1)
        return ret > 32

    task_name = "TitleChainListener"

    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(os.path.dirname(__file__))

    listener_path = os.path.join(base_dir, "listener", "listener.exe")
    print("DEBUG: Listener path resolved to:", listener_path)
    
    # Query Task Scheduler to check if the task already exists.
    query_cmd = f'schtasks /query /tn "{task_name}"'
    result = subprocess.run(query_cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("DEBUG: Scheduled Task already exists.")
        return True

    response = messagebox.askyesno(
        "Create Task Scheduler for TitleChain",
        "No task scheduler for TitleChain was detected. Would you like to create one so that TitleChain automatically launches when SoftPro starts?"
    )
    if not response:
        print("DEBUG: User declined to create scheduled task.")
        return False

    cmd = f'schtasks /create /tn "{task_name}" /tr "{listener_path}" /sc onlogon /rl HIGHEST /f'
    
    try:
        if not is_admin():
            print("DEBUG: Not running as admin. Elevating command...")
            if run_command_as_admin(cmd):
                print("DEBUG: Scheduled task created successfully (via runas).")
            else:
                messagebox.showerror("Error", "Failed to create scheduled task with administrative privileges.")
                print("DEBUG: Failed to create scheduled task via elevation.")
                return False
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("DEBUG: Scheduled task created successfully.")
            else:
                messagebox.showerror("Error", f"Failed to create scheduled task:\n{result.stderr}")
                print("DEBUG: Failed to create scheduled task:", result.stderr)
                return False

        run_cmd = f'schtasks /run /tn "{task_name}"'
        run_result = subprocess.run(run_cmd, shell=True, capture_output=True, text=True)
        if run_result.returncode == 0:
            print("DEBUG: Scheduled task started successfully.")
        else:
            print("DEBUG: Failed to run scheduled task immediately:", run_result.stderr)
            try:
                subprocess.Popen([listener_path])
                print("DEBUG: Launched listener.exe directly as fallback.")
            except Exception as e:
                print("DEBUG: Fallback launch failed:", e)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Exception creating scheduled task: {e}")
        print("DEBUG: Exception creating scheduled task:", e)
        return False

class RegistrationGUI(tk.Toplevel):
    def __init__(self, master, on_registration_success):
        super().__init__(master)
        self.title("Register")
        desired_width = 310
        desired_height = 230
        center_window(self, desired_width, desired_height)
        self.resizable(False, False)
        self.on_registration_success = on_registration_success
        print("DEBUG: ✅ RegistrationGUI initialized")

        # First Name
        tk.Label(self, text="First Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.first_name_entry = tk.Entry(self, width=25)
        self.first_name_entry.grid(row=0, column=1, padx=10, pady=5)

        # Last Name
        tk.Label(self, text="Last Name:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.last_name_entry = tk.Entry(self, width=25)
        self.last_name_entry.grid(row=1, column=1, padx=10, pady=5)

        # Email
        tk.Label(self, text="Email:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.email_entry = tk.Entry(self, width=25)
        self.email_entry.grid(row=2, column=1, padx=10, pady=5)

        # Confirm Email
        tk.Label(self, text="Confirm Email:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.confirm_email_entry = tk.Entry(self, width=25)
        self.confirm_email_entry.grid(row=3, column=1, padx=10, pady=5)

        # Password
        tk.Label(self, text="Password:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.password_entry = tk.Entry(self, width=25, show="*")
        self.password_entry.grid(row=4, column=1, padx=10, pady=5)

        # Confirm Password
        tk.Label(self, text="Confirm Password:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.confirm_password_entry = tk.Entry(self, width=25, show="*")
        self.confirm_password_entry.grid(row=5, column=1, padx=10, pady=5)

        # Buttons
        tk.Button(self, text="Register", width=10, command=self.validate_and_register).grid(row=6, column=0, padx=20, pady=10)
        tk.Button(self, text="Cancel", width=10, command=self.cancel_registration).grid(row=6, column=1, padx=20, pady=10)

    def validate_and_register(self):
        print("DEBUG: validate_and_register() called")
        for entry in [self.first_name_entry, self.last_name_entry,
                      self.email_entry, self.confirm_email_entry,
                      self.password_entry, self.confirm_password_entry]:
            entry.config(bg="white")

        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip().lower()
        confirm_email = self.confirm_email_entry.get().strip().lower()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        print(f"DEBUG: Registration inputs - first_name: {first_name}, last_name: {last_name}, email: {email}")
        
        valid = True
        if not first_name:
            self.first_name_entry.config(bg="red")
            valid = False
        if not last_name:
            self.last_name_entry.config(bg="red")
            valid = False
        if not email or email != confirm_email:
            self.email_entry.config(bg="red")
            self.confirm_email_entry.config(bg="red")
            valid = False
        if not password or password != confirm_password:
            self.password_entry.config(bg="red")
            self.confirm_password_entry.config(bg="red")
            valid = False

        if not valid:
            messagebox.showerror("Error", "Please correct the highlighted fields.")
            print("DEBUG: Registration validation failed.")
            return

        if not messagebox.askyesno("Confirm Registration", "Confirm your inputs before submitting?"):
            print("DEBUG: Registration confirmation declined by user.")
            return

        users = load_users()  # We call load_users without email here because we don't need to print details for all users.
        if email in users:
            messagebox.showerror("Registration Failed", "User with this email already exists!")
            print("DEBUG: Registration failed - duplicate email.")
            return

        user_id = str(uuid.uuid4())
        new_user = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,  # In production, use secure password hashing!
            "user_id": user_id,
            "can_create_db": False  # Default permission; adjust as needed.
        }
        users[email] = new_user
        save_users(users)
        messagebox.showinfo("Registration Success", "Registration Successful!")
        print("DEBUG: Registration successful for new user:", new_user)
        self.on_registration_success(new_user)
        self.destroy()

    def cancel_registration(self):
        print("DEBUG: Registration cancelled by user.")
        self.destroy()

class LoginGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Titlechain Login")
        desired_width = 400
        desired_height = 200
        center_window(self, desired_width, desired_height)
        self.resizable(False, False)
        self.style = Style(theme="flatly")
        self.logged_in_user = None
        print("DEBUG: ✅ LoginGUI initialized")

        if create_launch_daemon():
            print("DEBUG: ✅ Scheduled task is set up.")
        else:
            print("DEBUG: Scheduled task was not created.")

        tk.Label(self, text="Email:").pack(pady=(20, 0))
        self.email_entry = tk.Entry(self, width=40)
        self.email_entry.pack(pady=5)

        tk.Label(self, text="Password:").pack(pady=(10, 0))
        self.password_entry = tk.Entry(self, show="*", width=40)
        self.password_entry.pack(pady=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Submit", width=8, command=self.submit_login).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Register", width=8, command=self.open_registration).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Forgot Password", width=13, command=self.forgot_password).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Exit", width=8, command=self.exit).grid(row=0, column=3, padx=5)

    def submit_login(self):
        email = self.email_entry.get().strip().lower()
        password = self.password_entry.get().strip()
        print(f"DEBUG: submit_login() called with email: {email}")

        # Pass the email so load_users only prints the details for this user.
        users = load_users(email)
        if email in users and users[email]["password"] == password:
            messagebox.showinfo("Login Successful", f"Welcome, {users[email]['first_name']}!")
            print("DEBUG: Login successful for user:", users[email])
            self.logged_in_user = users[email]
            self.withdraw()
            print("DEBUG: Launching DBConnectionGUI from submit_login")
            dbconn = DBConnectionGUI(self.master, self.logged_in_user)
        else:
            messagebox.showerror("Invalid Credentials", "Invalid Credentials!")
            print("DEBUG: Invalid credentials for email:", email)
            self.email_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)

    def open_registration(self):
        print("DEBUG: Opening registration window")
        self.withdraw()
        reg_window = RegistrationGUI(self, self.on_registration_success)
        self.wait_window(reg_window)
        self.deiconify()

    def on_registration_success(self, new_user):
        print("DEBUG: on_registration_success() called with new_user:", new_user)
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, new_user["email"])
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, new_user["password"])
        messagebox.showinfo("Registration", "Please submit your login credentials.")

    def forgot_password(self):
        messagebox.showinfo("Forgot your password?", "Please contact your system administrator.")
        
    def exit(self):
        response = messagebox.askyesno("Exit", "Are you sure you want to quit?")
        if response:
            self.destroy()
            sys.exit()
