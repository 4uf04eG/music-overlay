#Music overlay
<img src='https://i.ibb.co/XYRsc3N/screenshot.png'>
Small music overlay heavily inspired by the overlay available in Windows 10.
It serves the same functionality and has two primary goals:
    1. Bring that functionality to Linux
    2. Avoid browsers and other media players from being shown in overlay
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
   There are some settings:
    | Fill lated | Fill later |
    | ------------- | ------------- |
    | Content Cell  | Content Cell  |
    | Content Cell  | Content Cell  |
   
## Usage
   Just open terminal and write command music-overlay to show overlay.
   It's easier to add command to autostart.<br>
   Overlay with playing track if there's one is being shown 
   only when you press media buttons(previous, next, play/pause) 
   
## Known bugs
1. KDE: cannot show player over full screen windows
2. LXDE: task panel icon is not hidden