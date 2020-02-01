from pathlib import Path

import toml
from PySide2.QtCore import Signal, QObject, QRect
from PySide2.QtWidgets import QApplication
from pynput.keyboard import Listener

import Code

"""
Pressing media buttons resets window hide timer.
But timer can be reset only from main thread.

To execute timer reset on main thread used signal which is
emitted on media key press and to which Ui class is connected
with reset function.

To avoid problems signal should be wrapped in some class
"""


class Communicator(QObject):
    resetHideTimer = Signal()
    showWindow = Signal()
    onPlayerReload = Signal()


class Application(QApplication):
    def __init__(self):
        super().__init__()

        self.whitelist = ['deezer', 'spotify', 'MellowPlayer3']
        self.is_media_buttons_enabled = True
        self.window_opacity = 0.8
        self.window_pos_x = 120
        self.window_pos_y = 70
        self.load_config()

        self.communicator = Communicator()
        self.communicator.onPlayerReload.connect(self.load_any_player)
        Listener(on_press=self.handle_media_buttons_press, on_release=None).start()

        self.window = Code.Ui(self)
        self.load_any_player()
        self.window.show()
        self.window.saved_geometry = QRect(self.window.geometry())

    def load_config(self):
        try:
            config = toml.load(f"{Path.home()}/.config/media-player-config")
            self.whitelist = config['app']['players_whitelist']
            self.is_media_buttons_enabled = config['app']['enable_media_buttons_actions']
            self.window_pos_x = config['window']['pos_x']
            self.window_pos_y = config['window']['pos_y']
            self.window_opacity = config['window']['opacity']
        except (toml.decoder.TomlDecodeError, FileNotFoundError):
            pass

    def handle_media_buttons_press(self, key):
        # <269025046> - previous track, <269025047> - next track, <269025044> - play/pause
        if str(key) == '<269025046>' or str(key) == '<269025047>' or str(key) == '<269025044>':
            if not self.window.properties:
                self.communicator.onPlayerReload.emit()

            self.communicator.showWindow.emit()
            self.communicator.resetHideTimer.emit()

        if not self.is_media_buttons_enabled \
                or not self.window.properties \
                or self.window.is_animation_started:
            return

        if str(key) == '<269025046>':
            self.window.player_interface.Previous()
        elif str(key) == '<269025047>':
            self.window.player_interface.Next()
        elif str(key) == '<269025044>':
            self.window.player_interface.PlayPause()

    def select_first_whitelisted_player(self, player_info: list) -> Code.dbus_helper.PlayerInfo:
        for player in reversed(player_info):
            cleared_name = player.service_name.replace('org.mpris.MediaPlayer2.', '')

            if cleared_name in self.whitelist and player.track_title != 'Unknown':
                return player

        return Code.dbus_helper.PlayerInfo()

    def load_any_player(self):
        all_players = Code.dbus_helper.get_all_players_info()
        whitelisted_player = self.select_first_whitelisted_player(all_players)
        self.window.set_player_info(whitelisted_player)
