import os
import sys
import requests
import irsdk
import tkinter as tk
import tkinter.font as tkfont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import subprocess

#pyinstaller --onefile --noconsole --icon=ryan_gosling.ico clutchkick_overlay.py

# pyinstaller --onefile --add-data "AvenirNextLTPro-Bold.otf;." --add-data "AvenirNextLTPro-Demi.otf;." --icon=ryan_gosling.ico clutchkick_overlay.py

def run_updater():
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        updater_path = os.path.join(exe_dir, "update_helper.exe")
        if os.path.exists(updater_path):
            try:
                subprocess.run([updater_path], check=True)
            except Exception as e:
                print(f"Updater error: {e}")

run_updater()

def get_exe_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/jackninety9/clutchkick-overlay/main/"
SCRIPT_NAME = "clutchkick_overlay.py"
LOCAL_VERSION_FILE = os.path.join(get_exe_path(), "local_version.txt")

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
                    updater_path = os.path.join(get_exe_path(), "update_helper.exe")
                    current_exe = sys.executable
                    subprocess.Popen([updater_path, remote_version, current_exe])
                    sys.exit()
                else:
                    print("Running in script mode. Manual update only.")
    except Exception as e:
        print("Error checking for updates:", e)

check_for_update()

ir = irsdk.IRSDK()

offset_x = 0
offset_y = 0

throttle_data = []
brake_data = []

# FONT LOADER
def load_custom_fonts():
    font_dir = get_exe_path()
    try:
        tkfont.Font(name="AvenirBold", file=os.path.join(font_dir, "AvenirNextLTPro-Bold.otf"), size=22)
        tkfont.Font(name="AvenirDemi", file=os.path.join(font_dir, "AvenirNextLTPro-Demi.otf"), size=13)
        tkfont.Font(name="AvenirSmall", file=os.path.join(font_dir, "AvenirNextLTPro-Bold.otf"), size=8)
        tkfont.Font(name="AvenirMenu", file=os.path.join(font_dir, "AvenirNextLTPro-Bold.otf"), size=16)
        return True
    except Exception as e:
        print("Font loading failed:", e)
        return False

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
            ax.fill_between(range(len(throttle_data)), throttle_data, color='#12b032', alpha=0.8, label='Throttle')
            ax.fill_between(range(len(brake_data)), brake_data, color='#d91313', alpha=0.8, label='Brake')
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

    font_loaded = load_custom_fonts()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 500
    window_height = 250
    x_position = (screen_width - window_width) // 2
    y_position = int(screen_height * 0.8) - window_height
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    display_frame = tk.Frame(root, bg='#121212')
    display_frame.pack(expand=True, fill=tk.BOTH)

    def show_context_menu(event):
        context_menu.post(event.x_root, event.y_root)

    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Close", command=close_window)

    fig, ax = plt.subplots(figsize=(7.5, 0.5), facecolor='#121212')
    canvas = FigureCanvasTkAgg(fig, master=display_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.configure(bg='#121212', highlightthickness=0, bd=0)
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    spacer = tk.Frame(display_frame, height=2, bg="#121212")
    spacer.pack(side=tk.TOP)

    local_version = get_local_version()
    version_label = tk.Label(
        display_frame,
        text=f"v{local_version}",
        font=("AvenirSmall" if font_loaded else "Arial", 8),
        fg="#888888",
        bg="#121212"
    )
    version_label.pack(side=tk.TOP, pady=(0, 4))

    label = tk.Label(
        display_frame,
        text="BB: --",
        font=("AvenirBold" if font_loaded else "Segoe UI", 22),
        fg="#ffffff",
        bg="#121212"
    )
    label.pack(side=tk.TOP, pady=(0, 2))

    gear_speed_incident_label = tk.Label(
        display_frame,
        text="Gear: -- | Speed: -- km/h | Incidents: --x",
        font=("AvenirDemi" if font_loaded else "Segoe UI", 13),
        fg="#bbbbbb",
        bg="#121212"
    )
    gear_speed_incident_label.pack(side=tk.TOP)

    move_button = tk.Label(
        display_frame,
        text="☰",
        font=("AvenirMenu" if font_loaded else "Arial", 16),
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
