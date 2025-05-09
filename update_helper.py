import requests
import os
import sys
import time
import shutil
import subprocess

GITHUB_RAW_VERSION = "https://raw.githubusercontent.com/jackninety9/clutchkick-overlay/main/version.txt"
GITHUB_EXE_URL = "https://github.com/jackninety9/clutchkick-overlay/raw/main/clutchkick_overlay.exe"

def get_local_version(path):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except:
        return "0.0.0"

def write_local_version(path, version):
    with open(path, "w") as f:
        f.write(version)

def get_remote_version():
    try:
        r = requests.get(GITHUB_RAW_VERSION, timeout=5)
        if r.status_code == 200:
            return r.text.strip()
    except:
        return None

def download_new_exe(target_path):
    try:
        r = requests.get(GITHUB_EXE_URL, stream=True, timeout=10)
        if r.status_code == 200:
            with open(target_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except:
        pass
    return False

def main():
    exe_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
    local_version_path = os.path.join(exe_dir, "local_version.txt")
    exe_path = os.path.join(exe_dir, "clutchkick_overlay.exe")
    temp_path = os.path.join(exe_dir, "new_overlay.exe")

    local_version = get_local_version(local_version_path)
    remote_version = get_remote_version()

    if not remote_version or remote_version == local_version:
        return  # Up to date or failed to fetch

    print(f"Updating from v{local_version} to v{remote_version}...")

    if download_new_exe(temp_path):
        try:
            time.sleep(1)  # Give main exe time to exit if needed
            if os.path.exists(exe_path):
                os.remove(exe_path)
            shutil.move(temp_path, exe_path)
            write_local_version(local_version_path, remote_version)
            subprocess.Popen([exe_path])
            sys.exit(0)
        except Exception as e:
            print("Update failed:", e)

if __name__ == "__main__":
    main()
