from audiomixer import Mixer
from audiocore import WaveFile
from audioio import AudioOut
from board import A0
from time import monotonic


def OmniInc(current_val, change, min=0.02, max=0.4):
    """helper function to inc/decrement things. Was originally used for
    volume and brightness"""
    current = current_val
    current += change
    if current < min:
        current = min
    elif current > max:
        current = max
    return current


class SoundManager:
    """class to control the flow of sound in response to button presses"""

    def __init__(self, speaker, tracks):
        """initialize the mixer object, and setup track bank infrastructure"""
        self.wake_time = monotonic()
        audio = AudioOut(A0)
        mixer = Mixer(voice_count=1, sample_rate=22050,
                      channel_count=1, bits_per_sample=16,
                      samples_signed=True)
        audio.play(mixer)  # attach mixer to audio playback
        self.sound = mixer.voice[0]
        self.speaker = speaker
        self.repeat = False
        self.playable = False

        # the 'tracks' list of lists is iterated through to turn everything
        # into WaveFile objects. Requires CircuitPython 8.0
        self.internal_track_banks = []
        for bank_num, bank in enumerate(tracks.copy()):
            for file_num, file in enumerate(bank):
                tracks[bank_num][file_num] = WaveFile(file)
            self.internal_track_banks.append(bank)
        self.current_song = None
        self.current_bank = 0

    def play_from_bank(self, event_bank):
        """helper function to grab file from a bank, then rotate the tracks"""
        self.speaker.switch_to_output(value=True)
        self.current_song = self.internal_track_banks[event_bank][0]
        self.sound.play(self.current_song)
        rotated_track = self.internal_track_banks[event_bank].pop(-1)
        self.internal_track_banks[event_bank].insert(0, rotated_track)

    def play_based_on_mode(self):
        if self.repeat:
            self.on_START_PRESS()
        else:
            self.play_from_bank(self.current_bank)

    def on_UP_PRESS(self):
        self.play_from_bank(0)
        self.wake_time = monotonic()
        self.current_bank = 0
        self.playable = True

    def on_DOWN_PRESS(self):
        self.play_from_bank(1)
        self.wake_time = monotonic()
        self.current_bank = 1
        self.playable = True

    def on_LEFT_PRESS(self):
        self.play_from_bank(2)
        self.wake_time = monotonic()
        self.current_bank = 2
        self.playable = True

    def on_RIGHT_PRESS(self):
        self.play_from_bank(3)
        self.wake_time = monotonic()
        self.current_bank = 3
        self.playable = True

    def on_SEL_PRESS(self):
        self.repeat = not self.repeat

    def on_START_PRESS(self):
        self.wake_time = monotonic()
        if not self.sound.playing and self.current_song is not None:
            self.speaker.switch_to_output(value=True)
            self.sound.play(self.current_song)
            self.playable = True
        elif self.sound.playing:
            self.sound.stop()
            self.playable = False
            self.speaker.switch_to_output(value=False)

    def on_A_PRESS(self):
        self.sound.level = OmniInc(self.sound.level, 0.02)
        # print(self.sound.level)

    def on_B_PRESS(self):
        self.sound.level = OmniInc(self.sound.level, -0.02)
        # print(self.sound.level)

    def none_event(self):
        return None
