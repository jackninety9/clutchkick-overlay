import urllib.request
import time
import os
import subprocess
import traceback

# pyinstaller --windowed --onefile update_helper.py

# GitHub URLs
GITHUB_RAW_VERSION = "https://raw.githubusercontent.com/jackninety9/clutchkick-overlay/main/version.txt"
GITHUB_MAIN_EXE_URL = "https://github.com/jackninety9/clutchkick-overlay/raw/main/dist/clutchkick_overlay.exe"
GITHUB_UPDATER_EXE_URL = "https://github.com/jackninety9/clutchkick-overlay/raw/main/dist/update_helper.exe"

# Local file paths
LOCAL_VERSION_FILE = "local_version.txt"
LOCAL_MAIN_EXE = "clutchkick_overlay.exe"
LOCAL_UPDATER_EXE = "update_helper.exe"
TEMP_UPDATER_EXE = "update_helper_new.exe"

def get_text_from_url(url):
    url_with_bust = f"{url}?_={int(time.time())}"
    with urllib.request.urlopen(url_with_bust) as response:
        return response.read().decode().strip()

def download_file(url, path):
    urllib.request.urlretrieve(url, path)

def wait_until_file_is_unlocked(path, timeout=10):
    start = time.time()
    while True:
        try:
            os.rename(path, path)
            return True
        except PermissionError:
            if time.time() - start > timeout:
                print(f"Timeout waiting for {path} to be unlocked.")
                return False
            time.sleep(0.5)

def check_for_update():
    if not os.path.exists(LOCAL_VERSION_FILE):
        print("No local_version.txt found.")
        return False

    with open(LOCAL_VERSION_FILE, 'r') as file:
        local_version = file.read().strip()

    try:
        latest_version = get_text_from_url(GITHUB_RAW_VERSION)
    except Exception as e:
        print(f"Failed to fetch latest version: {e}")
        return False

    if local_version != latest_version:
        print("New version found. Updating...")

        if not wait_until_file_is_unlocked(LOCAL_MAIN_EXE):
            print("clutchkick_overlay.exe is locked. Cannot update.")
            return False

        try:
            # Update clutchkick_overlay.exe
            download_file(GITHUB_MAIN_EXE_URL, LOCAL_MAIN_EXE)
            print("clutchkick_overlay.exe updated.")

            # Download new update_helper as temp file
            download_file(GITHUB_UPDATER_EXE_URL, TEMP_UPDATER_EXE)
            print("Downloaded new update_helper.exe to temp file.")

            # Update version file
            with open(LOCAL_VERSION_FILE, 'w') as file:
                file.write(latest_version)
            print("local_version.txt updated.")

            return True
        except Exception as e:
            print("Failed during update process:")
            traceback.print_exc()
            return False
    else:
        print("You have the latest version.")
        return True

if __name__ == "__main__":
    updated = check_for_update()
    if updated:
        print("Relaunching clutchkick_overlay.exe...")
        subprocess.Popen([LOCAL_MAIN_EXE, "--updated"])
