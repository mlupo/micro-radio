from audiomixer import Mixer
from audiocore import WaveFile
from audioio import AudioOut
from board import A0
from time import monotonic


def OmniInc(current_val, change, min=0.025, max=0.4):
    current = current_val
    current += change
    if current < min:
        current = min
    elif current > max:
        current = max
    return current


class SoundManager:
    def __init__(self, speaker, tracks):
        self.wake_time = monotonic()
        audio = AudioOut(A0)
        mixer = Mixer(voice_count=1, sample_rate=22050,
                      channel_count=1, bits_per_sample=16,
                      samples_signed=True)
        audio.play(mixer)  # attach mixer to audio playback
        self.sound = mixer.voice[0]
        self.speaker = speaker

        self.internal_track_banks = []
        for bank_num, bank in enumerate(tracks.copy()):
            for file_num, file in enumerate(bank):
                tracks[bank_num][file_num] = WaveFile(file)
            self.internal_track_banks.append(bank)
        self.current_song = self.internal_track_banks[0][0]

    def play_from_bank(self, event_bank):
        self.speaker.switch_to_output(value=True)
        self.current_song = self.internal_track_banks[event_bank][0]
        self.sound.play(self.current_song)
        self.internal_track_banks[event_bank].reverse()

    def on_UP_PRESS(self):
        self.wake_time = monotonic()
        self.play_from_bank(0)

    def on_DOWN_PRESS(self):
        self.wake_time = monotonic()
        self.play_from_bank(1)

    def on_LEFT_PRESS(self):
        self.wake_time = monotonic()
        self.play_from_bank(2)

    def on_RIGHT_PRESS(self):
        self.wake_time = monotonic()
        self.play_from_bank(3)

    def on_SEL_PRESS(self):
        self.wake_time = monotonic()
        self.play_from_bank(4)

    def on_START_PRESS(self):
        self.wake_time = monotonic()
        if not self.sound.playing:
            self.speaker.switch_to_output(value=True)
            self.sound.play(self.current_song)
        elif self.sound.playing:
            self.sound.stop()
            self.speaker.switch_to_output(value=False)

    def on_A_PRESS(self):
        self.sound.level = OmniInc(self.sound.level, 0.025)
        print(self.sound.level)

    def on_B_PRESS(self):
        self.sound.level = OmniInc(self.sound.level, -0.025)
        print(self.sound.level)

    def none_event(self):
        return None
        # print("this is a non event")
