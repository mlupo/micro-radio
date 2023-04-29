from neopixel import NeoPixel
from board import D8, BUTTON_LATCH, BUTTON_CLOCK, BUTTON_OUT, D10, SPI, SPEAKER_ENABLE, DISPLAY
from time import monotonic
from sdcardio import SDCard
from storage import mount, VfsFat
# from gc import collect
from keypad import ShiftRegisterKeys, Event
from alarm import time, exit_and_deep_sleep_until_alarms
from digitalio import DigitalInOut
from os import chdir
import badgey

status = NeoPixel(D8, 1, brightness=0.7, auto_write=True)
status.fill((250, 50, 50))
mode_fill = {True: (255, 50, 50), False: (50, 50, 250)}

DISPLAY.brightness = 0  # turn off display

# initialize sdcard, and mount it
cs = D10
sd = SDCard(SPI(), cs)
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
press_events = {LEFT_PRESS: badgey.on_LEFT_PRESS, UP_PRESS: badgey.on_UP_PRESS,
                DOWN_PRESS: badgey.on_DOWN_PRESS, RIGHT_PRESS: badgey.on_RIGHT_PRESS,
                SEL_PRESS: badgey.on_SEL_PRESS, START_PRESS: badgey.on_START_PRESS,
                A_PRESS: badgey.on_A_PRESS, B_PRESS: badgey.on_B_PRESS}

# initialize the keypad
pad = ShiftRegisterKeys(clock=BUTTON_CLOCK,
                        data=BUTTON_OUT,
                        latch=BUTTON_LATCH,
                        key_count=8,
                        value_when_pressed=True,
                        max_events=1)
latest_event = None

# lists holding the song file name, each item will correspond to a specific btn
track_bank = [["trim.wav", "candle_snow.wav",
              "snowy_blanket.wav", "grinch.wav"],  # up
              ["daydream.wav", "moonshadow.wav", "either.wav"],  # down
              ["spider_j.wav", "rocks_and_flowers.wav", "old_cookie.wav",
              "jelly_fish.wav"],  # left
              ["wheels_raffi.wav", "shake_sillies.wav",
              "happy_and.wav"],  # right
              ]

# enable the speaker and initialize the SoundManager
speakerEnable = DigitalInOut(SPEAKER_ENABLE)
# SoundManager requires speaker object, and a list of track lists
radio = badgey.SoundManager(speakerEnable, track_bank)
radio.sound.level = 0.08

radio.wake_time = monotonic()
last_read = 0
play_count = 0

while True:
    # checks if button has been pressed
    latest_event = pad.events.get()
    last_read = monotonic()

    if (last_read - radio.wake_time) > 540:
        # no matter what, sleep device after 9 minutes of inactivity
        wake = time.TimeAlarm(monotonic_time=(monotonic() + 1728000))
        exit_and_deep_sleep_until_alarms(wake)

    if (last_read - radio.wake_time) > 5:
        # turn off speaker, if there is no sound playing
        status.fill(mode_fill.get(radio.repeat))
        if not radio.sound.playing:
            if radio.playable and play_count <= 5:
                radio.play_based_on_mode()
                play_count += 1
            else:
                radio.speaker.switch_to_output(value=False)
        elif radio.sound.playing:
            radio.wake_time = monotonic()

    # constant garbage collecting required if sdcardio is imported
    # collect()

    # using getattr we turn the string value from the press_events dictionary
    # into a SoundManager module call. This removes the giant stack of
    # if/else statements, and makes it more similar to assigning a callback
    event_value = press_events.get(latest_event, "none_event")
    if event_value != "none_event":
        run_event = event_value
        # run_event = getattr(radio, event_value)
        run_event()
