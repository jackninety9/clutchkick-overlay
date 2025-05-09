# Clutchkick Overlay

## Overview
The **Clutchkick Overlay** heavily relies on irsdk and chatgpt, don't expect stability or competence. This overlay shows throttle and brake inputs, brake bias, and other telemetry such as speed, gear, and incidents.

This program is designed to run as a standalone executable.

## Install
- **Login to github**
- Click on Releases (right panel)
- Select "current_release"
- Download "current_release.zip"
- Extract zip into desired location
- Create shortcut of "clutchkick_overlay.exe"
- **Launch program when iRacing is running**

## Features
- **iRacing Telemetry**: Displays throttle, brake, and brake bias values, gear, speed, and incident count from iRacing.
- **Real-Time Graph**: Shows throttle and brake input graphs that update dynamically during gameplay.
- **Version Checking**: Automatically checks for updates from GitHub repository and updates the script if needed.

## Technical Details
- **iRacing SDK**: Utilizes the [iRacing SDK](https://www.iracing.com/sdk/) to access telemetry data.
- **Matplotlib**: Used for plotting real-time graphs of throttle and brake input data.
- **Tkinter**: Used for creating the transparent overlay window and displaying telemetry information.
- **Requests**: Handles automatic updates by downloading the latest script version from GitHub repository.

## Requirements
### Prerequisites:
- **iRacing** (for telemetry data)


## Automatic Updates
The program includes an automatic update feature that checks for new versions of the script from a GitHub repository. If an update is available, the program will automatically download and restart with the new version.
- The script checks for updates every time it's run.