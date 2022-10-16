"""
Host Controller

Module responsible for overall control flow on the host end. Runs on host process start.
"""

import time
import logging as log
from serial.serialutil import SerialException

from constants import *
import media_manager as media
import message_protocol as msp
from host_serial_manager import HostSerialManager
from audio_listener import AudioListener


### Setup ###

log.basicConfig(format = "%(asctime)s [%(levelname)s] %(message)s",
                datefmt = "%d-%m-%Y %I:%M:%S %p",
                level = log.DEBUG)

log.addLevelName(TRACE, 'TRACE') # TRACE logging level for repetitive messages

log.info("*** Starting volume knob host process ***")

# Init other modules/classes
serial_manager = HostSerialManager()
audio = AudioListener()
media.init()


### Handlers ###

def handle_vol_request_msg(msg: msp.VolumeRequestMessage):
    # Get current system volume
    vol = media.get_volume()
    # Construct a volume message and send it to the device
    reply = msp.VolumeMessage(vol)
    serial_manager.send(reply)


def handle_vol_change_msg(msg: msp.VolumeMessage):
    # Set system volume to new level
    media.set_volume(msg.volume)


def handle_toggle_playback_msg(msg: msp.TogglePlaybackMessage):
    media.toggle_playback()
    # TODO: Retrieve playback status and send to device


def handle_skip_msg(msg: msp.SkipMessage):
    media.skip(msg.forward)


# Register message handlers
log.info("Registering message handlers")
serial_manager.register_handler(msp.VolumeRequestMessage, handle_vol_request_msg)
serial_manager.register_handler(msp.VolumeMessage, handle_vol_change_msg)
serial_manager.register_handler(msp.TogglePlaybackMessage, handle_toggle_playback_msg)
serial_manager.register_handler(msp.SkipMessage, handle_skip_msg)


### Main Program Loop ###

while(True):

    log.info("Attempting device connection...")

    try:

        with serial_manager:

            log.info("Device connection successful")

            while(True):

                serial_manager.update()
                audio.update(serial_manager)

                time.sleep(0.02)

    except SerialException:
        log.info(f"Failed to connect to device; retrying in {RECONNECT_DELAY} seconds")

    time.sleep(RECONNECT_DELAY)