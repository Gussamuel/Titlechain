import sys
import time
import psutil
import subprocess
import os

def wait_for_softpro_launch():
    print("DEBUG: Waiting for any process containing 'select' in its name...")
    while True:
        for proc in psutil.process_iter(['name']):
            try:
                pname = proc.info['name']
                if pname and "select" in pname.lower():
                    print("DEBUG: SOFTPRO LAUNCH DETECTED, INITIALIZING")
                    
                    # If frozen, use the directory of the executable; otherwise use this file's directory.
                    if getattr(sys, 'frozen', False):
                        base_dir = os.path.dirname(sys.executable)
                    else:
                        base_dir = os.path.abspath(os.path.dirname(__file__))
                    
                    # Go up one directory to find TitleChain.exe:
                    # dist/
                    #   TitleChain.exe
                    #   listener/
                    #     listener.exe
                    titlechain_exe = os.path.abspath(os.path.join(base_dir, "..", "TitleChain.exe"))
                    
                    print("DEBUG: Launching TitleChain from:", titlechain_exe)
                    subprocess.Popen([titlechain_exe])
                    return
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        time.sleep(5)

if __name__ == "__main__":
    wait_for_softpro_launch()
