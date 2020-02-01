import urllib.request as request
from threading import Thread

import dbus.mainloop.glib
from PySide2 import QtCore
from PySide2.QtCore import Qt, QEvent, QEasingCurve, QRect, QPoint, QSize
from PySide2.QtGui import QPixmap, QFontMetrics
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QDialog, QSlider, QLabel, QPushButton

from MusicOverlay.dbus_helper import *


def set_elided_text(label: QLabel, text: str):
    metrics = QFontMetrics(label.font())
    clipped_text = metrics.elidedText(text, Qt.ElideRight, label.width())
    label.setText(clipped_text)


class Ui(QDialog):
    def __init__(self, application):
        super(Ui, self).__init__()
        QUiLoader().load("Resources/layout.ui", self)
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.application = application

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Dialog | Qt.Tool)

        self.setWindowOpacity(application.window_opacity)
        self.move(application.window_pos_x, application.window_pos_y)
        self.saved_geometry = None  # Should be set after first show action

        self.track_title_label = self.findChild(QLabel, 'track_title')
        self.artist_label = self.findChild(QLabel, 'artist')
        self.volume_slider = self.findChild(QSlider, 'volume')
        self.album_cover = self.findChild(QLabel, 'album_cover')

        self.placeholder = self.findChild(QLabel, 'slider_value')
        self.slider = self.findChild(QSlider, 'volume')
        self.slider_timer_id = -1
        self.slider.valueChanged.connect(self.on_slider_value_changed)

        self.player_interface = None
        self.properties = None

        self.prev_btn = self.findChild(QPushButton, 'prev_btn')
        self.pause_btn = self.findChild(QPushButton, 'pause_btn')
        self.next_btn = self.findChild(QPushButton, 'next_btn')
        self.prev_btn.clicked.connect(lambda: self.player_interface.Previous() if self.properties else False)
        self.pause_btn.clicked.connect(lambda: self.player_interface.PlayPause() if self.properties else False)
        self.next_btn.clicked.connect(lambda: self.player_interface.Next() if self.properties else False)

        self.hide_timer_id = -1
        self.installEventFilter(self)
        self.application.communicator.resetHideTimer.connect(self.reset_hide_timer)

        self.long_load_timer_id = -1
        self.album_cover_loaded = False

        self.show_hide_animation = QtCore.QPropertyAnimation(self, b"geometry")
        self.show_hide_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.show_hide_animation.finished.connect(self.on_animation_finished)
        self.is_animation_started = False
        self.application.communicator.showWindow.connect(lambda: self.show_hide_with_animation(QEvent.Show))

    def reset_hide_timer(self):
        if self.hide_timer_id != -1:
            self.killTimer(self.hide_timer_id)

        self.hide_timer_id = self.startTimer(3000)

    """
    Setup function for player object
    
    Player object used to interact with dbus interface.
    But it's much easier to have properties and player interfaces obtained from that object
    
    Player interface's needed to change control play options(Next, Previous, PlayPause).
    Properties interface's needed to set and get properties.
    Track changes handled by properties listener.
    """

    def set_up_player(self, player_object):
        self.properties = create_property_interface(player_object)
        self.player_interface = create_player_interface(player_object)
        player_object.connect_to_signal("PropertiesChanged", self.on_properties_changed)

    def on_slider_value_changed(self):
        if self.slider_timer_id != -1:
            self.killTimer(self.slider_timer_id)

        self.slider_timer_id = self.startTimer(5)
        self.placeholder.setText(str(self.slider.value()))

    """
    UI update function
    
    It uses class PlayerInfo defined in dbus.helper.py,
    which contains needed player info.
    
    If player object have not been created it creates
    new one using service name, sets playback button to right state
    and creates service listener to select another player when
    current one closed.
    
    Album cover can be either downloaded from url link
    or loaded from disk. It depends on whether the player stores
    covers. 
    """

    def set_player_info(self, info: PlayerInfo):
        set_elided_text(self.track_title_label, info.track_title)
        set_elided_text(self.artist_label, info.artist)
        self.volume_slider.setValue(info.volume * 100)
        self.album_cover_loaded = False

        if not self.player_interface and info.service_name:
            self.set_up_player(create_dbus_object(info.service_name))
            self.set_playback_button(info.playback_status)
            create_player_owner_watch(info.service_name, self.on_player_owner_changed)

        if self.properties:
            if not get_dbus_param(self.properties, 'CanGoPrevious'):
                self.prev_btn.setEnabled(False)
            else:
                self.prev_btn.setEnabled(True)

            if not get_dbus_param(self.properties, 'CanGoNext'):
                self.next_btn.setEnabled(False)
            else:
                self.next_btn.setEnabled(True)

        self.long_load_timer_id = self.startTimer(50)
        Thread(target=self.load_album_cover, args=[info.art_url]).start()

    def load_album_cover(self, art_url: str):
        try:
            pixmap = QPixmap()
            result = request.urlopen(art_url).read()
            pixmap.loadFromData(result)
            self.album_cover.setPixmap(pixmap)
            self.album_cover_loaded = True
        except Exception:
            pass

    def reset_player_info(self):
        self.set_player_info(PlayerInfo())
        self.set_playback_button("Stopped")

    def on_properties_changed(self, *args):
        if 'Metadata' in args[1]:  # Track changed
            self.set_player_info(get_player_info(self.properties))

        if 'PlaybackStatus' in args[1]:  # Track paused/resumed
            self.set_playback_button(args[1]['PlaybackStatus'])

    def set_playback_button(self, playback_status: str):
        pixmap = QPixmap()

        if playback_status == 'Playing':
            pixmap.load('Resources/Images/pause.png')
        else:
            pixmap.load('Resources/Images/play.png')

        self.pause_btn.setIcon(pixmap)

    """
    Used to clear player data when player's disconnected 
    """

    def on_player_owner_changed(self, proxy):
        if not proxy:  # If player has no owner, it was closed
            self.player_interface = None
            self.properties = None
            self.reset_player_info()

    def show_hide_with_animation(self, action: QEvent):
        if self.is_animation_started:
            return

        end_top_left_corner = QPoint(self.pos() + QPoint(0, self.height()))
        final_geometry = QRect(end_top_left_corner, QSize(self.width(), 0))

        if action == QEvent.Hide:
            self.is_animation_started = True
            self.show_hide_animation.setDuration(500)
            self.show_hide_animation.setStartValue(self.saved_geometry)
            self.show_hide_animation.setEndValue(final_geometry)
            self.show_hide_animation.start()
        elif action == QEvent.Show and self.isHidden():
            self.is_animation_started = True
            self.show_hide_animation.setDuration(250)
            self.show_hide_animation.setStartValue(final_geometry)
            self.show_hide_animation.setEndValue(self.saved_geometry)
            self.show_hide_animation.start()
            self.show()

    def on_animation_finished(self):
        self.is_animation_started = False

        if self.geometry() != self.saved_geometry:
            self.hide()

        self.setGeometry(self.saved_geometry)

    def timerEvent(self, event):
        if event.timerId() == self.hide_timer_id:
            self.killTimer(self.hide_timer_id)
            self.hide_timer_id = -1
            self.show_hide_with_animation(QEvent.Hide)

        elif event.timerId() == self.slider_timer_id:
            self.killTimer(self.slider_timer_id)
            self.slider_timer_id = -1

            if self.properties:
                set_dbus_param(self.properties, 'Volume', self.slider.value() / 100)
        elif event.timerId() == self.long_load_timer_id:
            self.killTimer(self.long_load_timer_id)
            self.long_load_timer_id = -1

            if not self.album_cover_loaded:
                self.album_cover.setText('LOADING')

    """
    Controls when to hide the window and when not
    
    Window hides instantly on mouse click or
    in 3 seconds if no cursor over it 
    """

    def eventFilter(self, source, event) -> bool:
        if event.type() == QEvent.Enter:
            if self.hide_timer_id != -1:
                self.killTimer(self.hide_timer_id)
                self.hide_timer_id = -1
            return True

        if event.type() == QEvent.Leave and not self.is_animation_started:
            if self.isVisible():
                self.hide_timer_id = self.startTimer(3000)
            return True

        if event.type() == QEvent.Show:
            self.hide_timer_id = self.startTimer(3000)
            return True

        if event.type() == QEvent.MouseButtonPress:
            if self.hide_timer_id != -1:
                self.killTimer(self.hide_timer_id)
                self.hide_timer_id = -1

            self.show_hide_with_animation(QEvent.Hide)
            return True

        return False
