import psutil, subprocess, time, os

def is_softpro_running():
    # Check for a process whose name contains "select" (adjust as needed)
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and "select" in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def is_titlechain_running():
    # Check for TitleChain.exe in running processes (adjust as needed)
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == "titlechain.exe":
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def launch_titlechain():
    # Determine the base directory where listener.exe is located.
    base_dir = os.path.abspath(os.path.dirname(__file__))
    # Change working directory to the dist folder.
    # For example, if your folder structure is:
    #   TitleChain/
    #      dist/
    #         TitleChain.exe
    #         listener.exe
    os.chdir(base_dir)
    print("DEBUG: Working directory set to:", os.getcwd())
    
    # Construct the full path to TitleChain.exe.
    titlechain_exe = os.path.join(base_dir, "TitleChain.exe")
    if os.path.exists(titlechain_exe):
        subprocess.Popen([titlechain_exe])
        print("DEBUG: Launched TitleChain from:", titlechain_exe)
    else:
        print("DEBUG: TitleChain.exe not found at:", titlechain_exe)

def main():
    if is_softpro_running():
        if not is_titlechain_running():
            launch_titlechain()
        else:
            print("DEBUG: TitleChain is already running.")
    else:
        print("DEBUG: SoftPro is not running; no action taken.")

if __name__ == "__main__":
    main()
