import os
import sys
import time
import requests

GITHUB_EXE_URL = "https://github.com/jackninety9/clutchkick-overlay/raw/main/clutchkick_overlay.exe"

def download_latest_exe(destination_path):
    response = requests.get(GITHUB_EXE_URL, stream=True)
    if response.status_code == 200:
        with open(destination_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return True
    return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: update_helper.exe <new_version> <target_exe_path>")
        sys.exit(1)

    new_version = sys.argv[1]
    target_exe_path = sys.argv[2]
    version_file_path = os.path.join(os.path.dirname(target_exe_path), "local_version.txt")

    print("Waiting for target app to close...")
    time.sleep(3)  # Give time for main app to exit

    print("Downloading latest version...")
    if download_latest_exe(target_exe_path):
        with open(version_file_path, "w") as f:
            f.write(new_version)
        print("Update complete. Restarting...")
        os.startfile(target_exe_path)
    else:
        print("Failed to download update.")
