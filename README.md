# Windows-like-Trackpad-for-Linux

A python scripts that brings Windows style trackpad gesture in linux.

---

- Swipe 3 fingers horizontally to scroll between different windows
- Swipe 3 fingers down to show desktop
- Swipe 3 fingers up to show all the app window
- Press 3 fingers to click middle mouse button
- Swipe 4 fingers to move between workspaces (It will create a workspace automatically)
- Swipe 4 fingers up to show all workspace
- Swipe 4 fingers down to click a copyable full screen screenshot

---

## How to save it in autostart

Save **Main.py** then make it into a executable using (from where the file is located)
```
chmod +x Main.py
```
Then create a .desktop file using 
```
nano ~/.local/share/applications/TrackpadGestures.desktop
```
and paste this inside
```
[Desktop Entry]
Type=Application
Name=Trackpad Gestures
Exec=/full/path/to/Main.py
Icon=input-touchpad
Terminal=false
StartupNotify=false
```
Restart your device and it will work
