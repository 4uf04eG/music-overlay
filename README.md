# Music overlay
<img src='https://i.ibb.co/XYRsc3N/screenshot.png'><br>
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
    sudo python setup.py install
    
## Configuration
   After installation in hidden folder .config located in your home folder 
   you can find configuration file called music-overlay-config.

   Parameter players_whitelist uses dbus player names. To get one for your application start music player and use:

      dbus-send --session --dest=org.freedesktop.DBus --type=method_call --print-reply          
      /org/freedesktop/DBus org.freedesktop.DBus.ListNames | grep org.mpris.MediaPlayer2
   Result will show dbus names for running players where you can find the one you need.
   
   <b>Parameter enable_media_buttons_actions does not override system media shortcuts</b>. So either set it to false or remove system shortcuts.
   
## Usage
   Just open terminal and write command music-overlay to show overlay.
   It's easier to add command to autostart.<br>
   Overlay with playing track is being shown 
   only when you press media buttons(previous, next, play/pause) 
   
## Known bugs
1. KDE: cannot show player over full screen windows
2. LXDE: task panel icon is not hidden
