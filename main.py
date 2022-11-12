from time import monotonic, sleep
from board import BUTTON_LATCH, BUTTON_CLOCK, BUTTON_OUT, D10, SPI, SPEAKER_ENABLE, DISPLAY
import sdcardio
from storage import mount, VfsFat
from gc import collect
import badgey
from keypad import ShiftRegisterKeys, Event
from alarm import time, exit_and_deep_sleep_until_alarms
from digitalio import DigitalInOut
from os import chdir

DISPLAY.brightness = 0  # turn off display

# initialize sdcard, and mount it
cs = D10
sd = sdcardio.SDCard(SPI(), cs)
vfs = VfsFat(sd)
mount(vfs, '/sd')
chdir('/sd')

#  setup for PyBadge buttons
# the Events are specified so that they can be used as keys
LEFT_PRESS = Event(7, True)
UP_PRESS = Event(6, True)
DOWN_PRESS = Event(5, True)
RIGHT_PRESS = Event(4, True)
SEL_PRESS = Event(3, True)
START_PRESS = Event(2, True)
A_PRESS = Event(1, True)
B_PRESS = Event(0, True)

# this dictionary stores strings corresponding to the method names in badgey.py
# later, these strings will be used to call the methods using getattr()
press_events = {LEFT_PRESS: "on_LEFT_PRESS", UP_PRESS: "on_UP_PRESS",
                DOWN_PRESS: "on_DOWN_PRESS", RIGHT_PRESS: "on_RIGHT_PRESS",
                SEL_PRESS: "on_SEL_PRESS", START_PRESS: "on_START_PRESS",
                A_PRESS: "on_A_PRESS", B_PRESS: "on_B_PRESS"}

# initialize the keypad
pad = ShiftRegisterKeys(clock=BUTTON_CLOCK,
                        data=BUTTON_OUT,
                        latch=BUTTON_LATCH,
                        key_count=8,
                        value_when_pressed=True,
                        max_events=1)
latest_event = None

# lists holding the song file name, each item will correspond to a specific btn
track_bank = [["wheels_raffi.wav", "wheels_coco.wav"],  # tracks for bank_up
              ["sunflower.wav", ],    # tracks for bank_down
              ["rocks_and_flowers.wav", "old_cookie.wav"],  # bank_left
              ["wonderwall.wav", ],    # tracks for bank_right
              ["shake_sillies.wav", "happy_and.wav"]]  # tracks for bank_sel

# enable the speaker and initialize the SoundManager
speakerEnable = DigitalInOut(SPEAKER_ENABLE)
# SoundManager requires speaker object, and a list of track lists
radio = badgey.SoundManager(speakerEnable, track_bank)
radio.sound.level = 0.025

time_on = monotonic()
radio.wake_time = monotonic()
last_read = 0

while True:
    sleep(0.001)
    # checks if button has been pressed
    latest_event = pad.events.get()
    last_read = monotonic()

    if (last_read - time_on) > 900:
        # no matter what, sleep device after 15 minutes on
        wake = time.TimeAlarm(monotonic_time=monotonic() + 1209600)
        exit_and_deep_sleep_until_alarms(wake)

    if (last_read - radio.wake_time) > 30:
        # turn off speaker, if there is no sound playing
        if not radio.sound.playing:
            radio.speaker.switch_to_output(value=False)
        radio.wake_time = monotonic()

    collect()  # constant garbage collecting required

    # using getattr we turn the string value from the latest_event dictionary
    # into a SoundManager module call. This removes the giant stack of
    # if/else statements, and makes it more similar to assigning a callback
    event_value = press_events.get(latest_event, "none_event")
    if event_value != "none_event":
        run_event = getattr(radio, event_value)
        if event_value == "on_SEL_PRESS":
            radio.speaker.switch_to_output(value=False)
            wake = time.TimeAlarm(monotonic_time=monotonic() + 1209600)
            exit_and_deep_sleep_until_alarms(wake)
        run_event()
