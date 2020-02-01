import re
from pathlib import Path

import dbus


class PlayerInfo:
    service_name = ""
    track_title = "Unknown"
    artist = "Unknown"
    playback_status = "Stopped"
    volume = 0.0
    art_url = f'file://{str(Path().absolute())}/Resources/Images/no_cover.png'

    def set_data(
            self,
            metadata: dict,
            service: str = "",
            playback_status: str = "Stopped",
            volume: int = 0.0
    ):
        if 'xesam:title' in metadata and metadata['xesam:title']:
            self.track_title = str(metadata['xesam:title'])
        if 'xesam:artist' in metadata and len(metadata['xesam:artist']) > 0:
            if isinstance(metadata['xesam:artist'], dbus.String):
                self.artist = str(metadata['xesam:artist'])
            else:
                self.artist = ' & '.join(metadata['xesam:artist'])
        if 'mpris:artUrl' in metadata:
            self.art_url = str(metadata['mpris:artUrl'])

        self.service_name = str(service)
        self.playback_status = str(playback_status)
        self.volume = volume
        return self


def get_all_players_info() -> list:
    infos = []

    for service in dbus.SessionBus().list_names():
        if re.match('org.mpris.MediaPlayer2.', service):
            player = create_dbus_object(service)
            property_interface = create_property_interface(player)

            try:
                volume = get_dbus_param(property_interface, 'Volume')
            except dbus.DBusException:
                volume = 0.0

            metadata = get_dbus_param(property_interface, 'Metadata')
            playback_status = get_dbus_param(property_interface, 'PlaybackStatus')
            infos.append(PlayerInfo().set_data(metadata, service, playback_status, volume))

    return infos


def get_player_info(property_interface: dbus.Interface):
    metadata = get_dbus_param(property_interface, 'Metadata')
    volume = get_dbus_param(property_interface, 'Volume')
    return PlayerInfo().set_data(metadata, volume=volume)


def create_dbus_object(service_name: str):
    return dbus.SessionBus().get_object(service_name, '/org/mpris/MediaPlayer2')


def create_property_interface(service_object):
    return dbus.Interface(service_object, 'org.freedesktop.DBus.Properties')


def create_player_interface(service_object):
    return dbus.Interface(service_object, 'org.mpris.MediaPlayer2.Player')


def set_dbus_param(properties_interface: dbus.Interface, param_name: str, value):
    properties_interface.Set('org.mpris.MediaPlayer2.Player', param_name, value)


def get_dbus_param(properties_interface: dbus.Interface, param_name: str):
    return properties_interface.Get('org.mpris.MediaPlayer2.Player', param_name)


def create_player_owner_watch(service_name: str, callback):
    dbus.SessionBus().watch_name_owner(service_name, callback)
