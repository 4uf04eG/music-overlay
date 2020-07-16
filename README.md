# Music overlay
<img src='https://i.ibb.co/XYRsc3N/screenshot.png'>
<img src='https://i.ibb.co/f0wvRTG/Untitled.png'><br>
Small music overlay heavily inspired by the overlay available in Windows 10.
It serves the same functionality and has two primary goals:<br>
    1. Bring that functionality to Linux<br>
    2. Avoid browsers and other media players from being shown in overlay.
Only you decide which media players to whitelist and which are not.

## Installation
### Arch: 
   Package available in AUR and can be easily installed with any AUR helper.
   For example: yaourt -S music-overlay
### All distros
    # Install python and python-setuptools if required
    git clone https://github.com/4uf04eG/music-overlay.git
    cd music-overlay
    sudo python3 setup.py install
    cp -n default_config.toml $HOME/.config/music-overlay-config
    
## Configuration
   After installation in hidden folder .config located in your home folder 
   you can find configuration file called music-overlay-config.
   
   It has several parameters:
   
   #### App 
   Parameter players_whitelist uses dbus player names. To get one for your application start music player and use:

      dbus-send --session --dest=org.freedesktop.DBus --type=method_call --print-reply \
      /org/freedesktop/DBus org.freedesktop.DBus.ListNames | grep org.mpris.MediaPlayer2
   Result will show dbus names for running players where you can find the one you need.
   
   #### Shortcuts
   Shortcut parameters allow you to define your own key combination to control player.
   By default the have only key codes for media button. New combinations can be written as a string
   with '+' delimiter and no spaces between keys. Example: 'alt_r+f7'. 
   
   Keys like 'shift' and 'alt' and 'ctrl'
   which can be either left or right should be writen as '*key name*' for left key
   and '*key name*_r' for the right one. So, for example, if you need to use right shift just write 'shift_r'
   
   #### Window
   With window parameters you can set horizontal and vertical offsets
   as well as window opacity. If your system does not support
   translucent windows, opacity parameter will be ignored.
   
   You can change layout type there also. To select minimized layout type 'mini'.
   
## Usage
   Just open terminal and write command music-overlay to show overlay.
   It's easier to add command to autostart.
   
   Overlay with playing track is being shown 
   only when you press one of defined shortcuts.
   
## Known bugs
1. KDE: cannot show player over full screen windows
2. LXDE: task panel icon is not hidden
