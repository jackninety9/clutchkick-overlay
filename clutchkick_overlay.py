import irsdk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os
import subprocess
import sys
import time
import tkinter.font as tkFont
from tkinter import TclError

# pyinstaller --windowed --onefile --icon=images/ryan_gosling.ico --add-data "fonts/AvenirNextLTPro-Bold.otf;fonts" --add-data "fonts/AvenirNextLTPro-Demi.otf;fonts" clutchkick_overlay.py

def replace_update_helper():
    if os.path.exists("update_helper_new.exe"):
        print("Attempting to replace update_helper.exe...")
        for attempt in range(5):  # Try up to 5 times
            try:
                os.remove("update_helper.exe")
                os.rename("update_helper_new.exe", "update_helper.exe")
                print("update_helper.exe updated successfully.")
                return
            except PermissionError:
                print(f"Attempt {attempt + 1}: Access denied. Retrying...")
                time.sleep(1)
            except Exception as e:
                print(f"Unexpected error during update_helper.exe replacement: {e}")
                break
        print("Failed to replace update_helper.exe after several attempts.")

if "--updated" not in sys.argv:
    replace_update_helper()
    subprocess.Popen(["update_helper.exe"])
    sys.exit()
    
def get_local_version():
    try:
        with open("local_version.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "unknown"


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

def load_custom_fonts():
    fonts = {}
    try:
        # Get the path to the bundled fonts folder (PyInstaller includes it in the bundle)
        fonts_dir = os.path.join(os.path.dirname(sys.executable), 'fonts')

        # Load the two fonts (Bold and Demi)
        fonts['Bold'] = tkFont.Font(family=os.path.join(fonts_dir, 'AvenirNextLTPro-Bold.otf'), size=22)
        fonts['Demi'] = tkFont.Font(family=os.path.join(fonts_dir, 'AvenirNextLTPro-Demi.otf'), size=13)

        return fonts
    except TclError as e:
        print(f"Failed to load custom fonts: {e}")
        return None

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
    
    # Version Label (update after fixing updater)
    local_version = get_local_version()
    version_label = tk.Label(
        display_frame,
        text=f"Current Version: v{local_version}",
        font=("Arial", 8),  # More universal fallback font
        fg="#888888",
        bg="#121212"
    )
    version_label.pack(side=tk.TOP, pady=(0, 4))

    # Load custom fonts
    fonts = load_custom_fonts()

    # Brake Bias Label
    label = tk.Label(
        display_frame,
        text="BB: --",
        font=fonts['Bold'] if fonts else ("AvenirNextLTPro-Bold", 22),  # Use Bold font if available
        fg="#ffffff",
        bg="#121212"
    )
    label.pack(side=tk.TOP, pady=(0, 2))

    # Gear/Speed/Incidents Label
    gear_speed_incident_label = tk.Label(
        display_frame,
        text="Gear: -- | Speed: -- km/h | Incidents: --x",
        font=fonts['Demi'] if fonts else ("AvenirNextLTPro-Demi", 13),  # Use Demi font if available
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
