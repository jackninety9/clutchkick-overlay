import os
import sys
import requests
import irsdk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import subprocess

# Call the compiled update helper (only when frozen as an .exe)
def run_updater():
    if getattr(sys, 'frozen', False):  # Only when running as .exe
        exe_dir = os.path.dirname(sys.executable)
        updater_path = os.path.join(exe_dir, "update_helper.exe")
        if os.path.exists(updater_path):
            try:
                result = subprocess.run([updater_path], check=True)
            except subprocess.CalledProcessError:
                print("Updater failed to run.")
        else:
            print("Updater not found.")

# Run the updater BEFORE anything else
run_updater()

# Determine the path where the .exe or script is located
def get_exe_path():
    if getattr(sys, 'frozen', False):  # If running as a PyInstaller .exe
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# Define your resources relative to the .exe location
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/jackninety9/clutchkick-overlay/main/"
SCRIPT_NAME = "clutchkick_overlay.py"
LOCAL_VERSION_FILE = os.path.join(get_exe_path(), "local_version.txt")

# Version check & updater (source-only)
def get_remote_version():
    try:
        response = requests.get(GITHUB_RAW_BASE + "version.txt", timeout=5)
        if response.status_code == 200:
            return response.text.strip()
    except Exception as e:
        print("Error fetching remote version:", e)
    return None

def get_local_version():
    try:
        with open(LOCAL_VERSION_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"

def write_local_version(version):
    with open(LOCAL_VERSION_FILE, "w") as f:
        f.write(version)

def update_script():
    try:
        response = requests.get(GITHUB_RAW_BASE + SCRIPT_NAME, timeout=10)
        if response.status_code == 200:
            with open(SCRIPT_NAME, "w", encoding="utf-8") as f:
                f.write(response.text)
            print("Script updated successfully.")
            return True
    except Exception as e:
        print("Failed to update script:", e)
    return False



def check_for_update():
    try:
        response = requests.get(GITHUB_RAW_BASE + "version.txt", timeout=5)
        if response.status_code == 200:
            remote_version = response.text.strip()
            local_version = get_local_version()

            if remote_version != local_version:
                print(f"Update available: {local_version} → {remote_version}")

                if getattr(sys, 'frozen', False):
                    # Launch updater and exit
                    updater_path = os.path.join(get_exe_path(), "update_helper.exe")
                    current_exe = sys.executable
                    subprocess.Popen([updater_path, remote_version, current_exe])
                    sys.exit()
                else:
                    print("Running in script mode. Manual update only.")
    except Exception as e:
        print("Error checking for updates:", e)


# Run version check (only in source mode)
check_for_update()

# Initialize iRacing SDK
ir = irsdk.IRSDK()

offset_x = 0
offset_y = 0

throttle_data = []
brake_data = []

def update_data(label, gear_speed_incident_label, ax, canvas):
    if ir.is_initialized and ir.is_connected:
        try:
            brake_bias = ir['dcBrakeBias']
            label.config(text=f"Brake Bias: {brake_bias:.2f}%" if brake_bias else "Brake Bias: --")

            throttle_value = ir['Throttle']
            brake_value = ir['Brake']

            throttle_data.append(throttle_value)
            brake_data.append(brake_value)

            if len(throttle_data) > 100:
                throttle_data.pop(0)
                brake_data.pop(0)

            ax.clear()
            ax.fill_between(range(len(throttle_data)), throttle_data, color='#00bfa6', alpha=1, label='Throttle')
            ax.fill_between(range(len(brake_data)), brake_data, color='#ff7043', alpha=1, label='Brake')
            ax.set_ylim(0, 1)
            ax.axis('off')
            canvas.draw()

            gear = ir['Gear']
            speed = ir['Speed'] * 3600 / 1000
            incidents = ir['PlayerCarDriverIncidentCount']

            gear_speed_incident_label.config(
                text=f"Gear: {gear} | Speed: {speed:.2f} km/h | Incidents: {incidents}x"
                if gear is not None and speed is not None and incidents is not None
                else "Gear: -- | Speed: -- km/h | Incidents: --x"
            )
        except KeyError:
            label.config(text="Brake Bias not available")
            gear_speed_incident_label.config(text="Gear: -- | Speed: -- km/h | Incidents: --x")
    else:
        label.config(text="Not connected to iRacing")
        gear_speed_incident_label.config(text="Gear: -- | Speed: -- km/h | Incidents: --x")

    label.after(1, update_data, label, gear_speed_incident_label, ax, canvas)

def on_click(event):
    global offset_x, offset_y
    offset_x = event.x
    offset_y = event.y

def on_drag(event):
    x = root.winfo_pointerx() - offset_x
    y = root.winfo_pointery() - offset_y
    root.geometry(f'+{x}+{y}')

def close_window():
    ir.shutdown()
    root.quit()
    root.destroy()

def create_overlay():
    global root
    root = tk.Tk()
    root.overrideredirect(True)
    root.configure(bg='#121212')
    root.wm_attributes('-transparentcolor', '#121212')
    root.attributes('-alpha', 0.9)
    root.attributes('-topmost', True)

    # Position window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 500
    window_height = 250
    x_position = (screen_width - window_width) // 2
    y_position = int(screen_height * 0.8) - window_height
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    display_frame = tk.Frame(root, bg='#121212')
    display_frame.pack(expand=True, fill=tk.BOTH)

    # Context menu
    def show_context_menu(event):
        context_menu.post(event.x_root, event.y_root)

    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Close", command=close_window)

    # Graph area
    fig, ax = plt.subplots(figsize=(7.5, 0.5), facecolor='#121212')
    canvas = FigureCanvasTkAgg(fig, master=display_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.configure(bg='#121212', highlightthickness=0, bd=0)
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


    # Spacer to separate graph from version text
    spacer = tk.Frame(display_frame, height=2, bg="#121212")
    spacer.pack(side=tk.TOP)

    # Version Label
    local_version = get_local_version()
    version_label = tk.Label(
        display_frame,
        text=f"v{local_version}",
        font=("Arial", 8),  # More universal fallback font
        fg="#888888",
        bg="#121212"
    )
    version_label.pack(side=tk.TOP, pady=(0, 4))


    # Brake Bias Label
    label = tk.Label(
        display_frame,
        text="BB: --",
        font=("AvenirNextLTPro-Bold", 22),
        fg="#ffffff",
        bg="#121212"
    )
    label.pack(side=tk.TOP, pady=(0, 2))

    # Gear/Speed/Incidents Label
    gear_speed_incident_label = tk.Label(
        display_frame,
        text="Gear: -- | Speed: -- km/h | Incidents: --x",
        font=("AvenirNextLTPro-Demi", 13),
        fg="#bbbbbb",
        bg="#121212"
    )
    gear_speed_incident_label.pack(side=tk.TOP)

    # Move/Context Menu Button
    move_button = tk.Label(
        display_frame,
        text="☰",
        font=("AvenirNextLTPro-Bold", 16),
        fg="#ffffff",
        bg="#2a2a2a",
        cursor="fleur",
        padx=6,
        pady=2
    )
    move_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
    move_button.bind("<Button-1>", on_click)
    move_button.bind("<B1-Motion>", on_drag)
    move_button.bind("<Button-3>", show_context_menu)

    update_data(label, gear_speed_incident_label, ax, canvas)
    root.mainloop()

if __name__ == "__main__":
    ir.startup()
    create_overlay()
