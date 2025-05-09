import requests
import os
import sys
import time
import shutil
import subprocess

# URLs for the GitHub repository
GITHUB_RAW_VERSION = "https://raw.githubusercontent.com/jackninety9/clutchkick-overlay/main/version.txt"
GITHUB_EXE_URL = "https://github.com/jackninety9/clutchkick-overlay/raw/main/clutchkick_overlay.exe"

def get_local_version(path):
    """Fetch the local version from the local_version.txt file."""
    try:
        with open(path, "r") as f:
            version = f.read().strip()
            print(f"Local version read: {version}")
            return version
    except Exception as e:
        print(f"Error reading local version: {e}")
        return "0.0.0"

def write_local_version(path, version):
    """Write the version number to local_version.txt."""
    try:
        with open(path, "w") as f:
            f.write(version)
            print(f"Updated local version to: {version}")
    except Exception as e:
        print(f"Error writing local version: {e}")

def get_remote_version():
    """Fetch the remote version from the GitHub repository."""
    try:
        r = requests.get(GITHUB_RAW_VERSION, timeout=5)
        if r.status_code == 200:
            return r.text.strip()
    except Exception as e:
        print(f"Error fetching remote version: {e}")
    return None

def download_new_exe(target_path):
    """Download the latest EXE file from GitHub."""
    try:
        r = requests.get(GITHUB_EXE_URL, stream=True, timeout=10)
        if r.status_code == 200:
            with open(target_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded new EXE to: {target_path}")
            return True
    except Exception as e:
        print(f"Error downloading new EXE: {e}")
    return False

def main():
    exe_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
    local_version_path = os.path.join(exe_dir, "local_version.txt")
    exe_path = os.path.join(exe_dir, "clutchkick_overlay.exe")
    temp_path = os.path.join(exe_dir, "new_overlay.exe")

    print(f"Checking for updates in directory: {exe_dir}")
    
    local_version = get_local_version(local_version_path)
    remote_version = get_remote_version()

    if not remote_version or remote_version == local_version:
        print("Already up-to-date or failed to fetch remote version.")
        return  # Up to date or failed to fetch

    print(f"Updating from v{local_version} to v{remote_version}...")

    if download_new_exe(temp_path):
        try:
            time.sleep(1)  # Give time for the old EXE to close
            if os.path.exists(exe_path):
                os.remove(exe_path)
                print(f"Removed old EXE: {exe_path}")
            shutil.move(temp_path, exe_path)
            print(f"Moved new EXE to: {exe_path}")

            # Update version file
            write_local_version(local_version_path, remote_version)
            print(f"Local version file updated to {remote_version}")

            # Restart with the updated EXE
            subprocess.Popen([exe_path])
            print(f"Restarted program with new EXE: {exe_path}")
            sys.exit(0)

        except Exception as e:
            print(f"Update failed: {e}")

if __name__ == "__main__":
    main()
