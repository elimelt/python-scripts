import numpy as np
from scipy.io.wavfile import write
from scipy.signal import lfilter

class Oscillator:
    def __init__(self, frequency=440, amplitude=1.0, waveform='sine', sample_rate=44100):
        self.frequency = frequency
        self.amplitude = amplitude
        self.waveform = waveform
        self.sample_rate = sample_rate

    def generate(self, duration):
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        if self.waveform == 'sine':
            return self.amplitude * np.sin(2 * np.pi * self.frequency * t)
        elif self.waveform == 'square':
            return self.amplitude * np.sign(np.sin(2 * np.pi * self.frequency * t))
        elif self.waveform == 'sawtooth':
            return self.amplitude * 2 * (t * self.frequency - np.floor(0.5 + t * self.frequency))
        elif self.waveform == 'triangle':
            return self.amplitude * 2 * np.abs(2 * (t * self.frequency - np.floor(0.5 + t * self.frequency))) - 1
        else:
            raise ValueError("Unsupported waveform type")

class Synth:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.oscillators = []
        self.effects = []

    def add_oscillator(self, oscillator):
        self.oscillators.append(oscillator)

    def add_effect(self, effect):
        self.effects.append(effect)

    def generate(self, duration):
        audio = np.zeros(int(self.sample_rate * duration))
        for osc in self.oscillators:
            audio += osc.generate(duration)
        for effect in self.effects:
            audio = effect.apply(audio, self.sample_rate)
        return audio / max(len(self.oscillators), 1)

    def generate_sequence(self, frequencies, durations):
        audio = np.array([])
        for freq, dur in zip(frequencies, durations):
            osc = Oscillator(frequency=freq, sample_rate=self.sample_rate)
            audio = np.concatenate((audio, osc.generate(dur)))
        for effect in self.effects:
            audio = effect.apply(audio, self.sample_rate)
        return audio

    def save(self, filename, duration):
        audio = self.generate(duration)
        write(filename, self.sample_rate, (audio * 32767).astype(np.int16))

    def save_sequence(self, filename, frequencies, durations):
        audio = self.generate_sequence(frequencies, durations)
        write(filename, self.sample_rate, (audio * 32767).astype(np.int16))

class TremoloEffect:
    def __init__(self, frequency=5, depth=0.5):
        self.frequency = frequency
        self.depth = depth

    def apply(self, audio, sample_rate):
        t = np.linspace(0, len(audio) / sample_rate, len(audio), endpoint=False)
        tremolo = 1 + self.depth * np.sin(2 * np.pi * self.frequency * t)
        return audio * tremolo

class FadeEffect:
    def __init__(self, fade_in_duration=0.1, fade_out_duration=0.1):
        self.fade_in_duration = fade_in_duration
        self.fade_out_duration = fade_out_duration

    def apply(self, audio, sample_rate):
        fade_in_samples = int(sample_rate * self.fade_in_duration)
        fade_out_samples = int(sample_rate * self.fade_out_duration)

        fade_in = np.linspace(0, 1, fade_in_samples)
        fade_out = np.linspace(1, 0, fade_out_samples)

        audio[:fade_in_samples] *= fade_in
        audio[-fade_out_samples:] *= fade_out

        return audio

class ReverbEffect:
    def __init__(self, decay=0.5, delay=0.02):
        self.decay = decay
        self.delay = delay

    def apply(self, audio, sample_rate):
        delay_samples = int(sample_rate * self.delay)
        impulse_response = np.zeros(delay_samples)
        impulse_response[0] = 1.0
        impulse_response[-1] = self.decay
        return lfilter(impulse_response, [1.0], audio)

class DelayEffect:
    def __init__(self, delay=0.5, decay=0.5):
        self.delay = delay
        self.decay = decay

    def apply(self, audio, sample_rate):
        delay_samples = int(sample_rate * self.delay)
        delayed_audio = np.zeros_like(audio)
        delayed_audio[delay_samples:] = audio[:-delay_samples] * self.decay
        return audio + delayed_audio

class ChorusEffect:
    def __init__(self, rate=1.5, depth=0.02):
        self.rate = rate
        self.depth = depth

    def apply(self, audio, sample_rate):
        t = np.linspace(0, len(audio) / sample_rate, len(audio), endpoint=False)
        chorus = np.sin(2 * np.pi * self.rate * t) * self.depth
        indices = np.arange(len(audio)) + (chorus * sample_rate).astype(int)
        indices = np.clip(indices, 0, len(audio) - 1)
        return audio[indices]

class ADSREnvelope:
    def __init__(self, attack=0.1, decay=0.1, sustain=0.7, release=0.1):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release

    def apply(self, audio, sample_rate):
        attack_samples = int(sample_rate * self.attack)
        decay_samples = int(sample_rate * self.decay)
        release_samples = int(sample_rate * self.release)
        sustain_samples = len(audio) - attack_samples - decay_samples - release_samples

        attack_curve = np.linspace(0, 1, attack_samples)
        decay_curve = np.linspace(1, self.sustain, decay_samples)
        sustain_curve = np.full(sustain_samples, self.sustain)
        release_curve = np.linspace(self.sustain, 0, release_samples)

        envelope = np.concatenate((attack_curve, decay_curve, sustain_curve, release_curve))
        return audio * envelope[:len(audio)]

class LFO:
    def __init__(self, frequency=5, depth=0.5, waveform='sine'):
        self.frequency = frequency
        self.depth = depth
        self.waveform = waveform

    def apply(self, audio, sample_rate):
        t = np.linspace(0, len(audio) / sample_rate, len(audio), endpoint=False)
        if self.waveform == 'sine':
            modulation = self.depth * np.sin(2 * np.pi * self.frequency * t)
        elif self.waveform == 'square':
            modulation = self.depth * np.sign(np.sin(2 * np.pi * self.frequency * t))
        elif self.waveform == 'sawtooth':
            modulation = self.depth * (2 * (t * self.frequency - np.floor(0.5 + t * self.frequency)))
        elif self.waveform == 'triangle':
            modulation = self.depth * (2 * np.abs(2 * (t * self.frequency - np.floor(0.5 + t * self.frequency))) - 1)
        else:
            raise ValueError("Unsupported waveform type")
        return audio * (1 + modulation)

class Composition:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.synth_channels = []

    def add_synth_channel(self, synth, start_time=0):
        self.synth_channels.append((synth, start_time))

    def generate(self, duration):
        audio = np.zeros(int(self.sample_rate * duration))
        for synth, start_time in self.synth_channels:
            start_sample = int(start_time * self.sample_rate)
            synth_audio = synth.generate(duration)
            audio[start_sample:start_sample + len(synth_audio)] += synth_audio
        return audio

    def save(self, filename, duration):
        audio = self.generate(duration)
        audio = np.clip(audio, -1, 1)  # Ensure audio is within [-1, 1] range
        write(filename, self.sample_rate, (audio * 32767).astype(np.int16))