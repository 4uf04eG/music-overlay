from enum import Enum
from pathlib import Path

import toml
from PySide2.QtCore import Signal, QObject, QRect, QWaitCondition, QMutex
from PySide2.QtWidgets import QApplication
from pynput.keyboard import Listener

import MusicOverlay

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
    mutex = QMutex()
    waitCondition = QWaitCondition()


class Layout(Enum):
    FULL = 1,
    MINI = 2


class Application(QApplication):
    def __init__(self):
        super().__init__()

        self.whitelist = ['deezer', 'spotify', 'MellowPlayer3']
        self.previous_shortcuts = [['<269025046>']]
        self.next_shortcuts = [['<269025047>']]
        self.play_pause_shortcuts = [['<269025044>']]
        self.all_shortcuts = self.previous_shortcuts + self.next_shortcuts + self.play_pause_shortcuts
        self.window_opacity = 0.8
        self.window_pos_x = 120
        self.window_pos_y = 70
        self.window_layout = Layout.FULL
        self.load_config()

        self.communicator = Communicator()
        self.communicator.onPlayerReload.connect(self.load_any_player)
        self.current_keys_pressed = set()
        Listener(on_press=self.on_key_press, on_release=self.on_key_release).start()

        self.window = MusicOverlay.Ui(self)
        self.load_any_player()
        self.window.show()
        self.window.saved_geometry = QRect(self.window.geometry())
        self.window.hide()

    def load_config(self):
        try:
            config = toml.load(f"{Path.home()}/.config/music-overlay-config")
            self.whitelist = config['app']['players_whitelist']

            self.previous_shortcuts = [key.split('+') for key in config['shortcuts']['previous_keys']]
            self.next_shortcuts = [key.split('+') for key in config['shortcuts']['next_keys']]
            self.play_pause_shortcuts = [key.split('+') for key in config['shortcuts']['play_pause_keys']]
            self.all_shortcuts = self.previous_shortcuts + self.next_shortcuts + self.play_pause_shortcuts

            self.window_pos_x = config['window']['pos_x']
            self.window_pos_y = config['window']['pos_y']
            self.window_opacity = config['window']['opacity']

            if config['window']['layout'] == 'mini':
                self.window_layout = Layout.MINI
        except (toml.TomlDecodeError, FileNotFoundError):
            pass

    def on_key_press(self, key):
        cleared_name = str(key).replace('Key.', '').replace('\'', '')

        if any([cleared_name in COMBO for COMBO in self.all_shortcuts]):
            self.current_keys_pressed.add(cleared_name)

            if any(all(k in self.current_keys_pressed for k in COMBO) for COMBO in self.next_shortcuts):
                self.handle_media_buttons_press("next")
            elif any(all(k in self.current_keys_pressed for k in COMBO) for COMBO in self.previous_shortcuts):
                self.handle_media_buttons_press("prev")
            elif any(all(k in self.current_keys_pressed for k in COMBO) for COMBO in self.play_pause_shortcuts):
                self.handle_media_buttons_press("play_pause")

    def on_key_release(self, key):
        cleared_name = str(key).replace('Key.', '')

        if any([cleared_name in COMBO for COMBO in self.all_shortcuts]):
            self.current_keys_pressed.remove(cleared_name)

    def handle_media_buttons_press(self, key: str):
        if not self.window.properties:
            self.communicator.onPlayerReload.emit()
            self.communicator.mutex.lock()
            self.communicator.waitCondition.wait(self.communicator.mutex)
            self.communicator.mutex.unlock()

        if not self.window.properties:  # If no suitable player found
            return

        self.communicator.showWindow.emit()
        self.communicator.resetHideTimer.emit()

        if key == 'prev':
            self.window.player_interface.Previous()
        elif key == 'next':
            self.window.player_interface.Next()
        elif key == 'play_pause':
            self.window.player_interface.PlayPause()

    def select_first_whitelisted_player(self, player_info: list) -> MusicOverlay.dbus_helper.PlayerInfo:
        for player in reversed(player_info):
            cleared_name = player.service_name.replace('org.mpris.MediaPlayer2.', '')

            if cleared_name in self.whitelist and player.track_title != 'Unknown':
                return player

        return MusicOverlay.dbus_helper.PlayerInfo()

    def load_any_player(self):
        all_players = MusicOverlay.dbus_helper.get_all_players_info()
        whitelisted_player = self.select_first_whitelisted_player(all_players)
        self.window.set_player_info(whitelisted_player)
        self.communicator.waitCondition.wakeAll()
