# Windows-like-Trackpad-for-Linux

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
