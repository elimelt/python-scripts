import os
from synth import Synth, Oscillator, TremoloEffect, ADSREnvelope, LFO, FadeEffect, ReverbEffect, DelayEffect
import numpy as np

def generate_piano_freqs():
  N = 36
  notes = np.zeros(N)
  for i in range(N):
    notes[i] = 2 ** (i / 12) * 440
  return notes

def first_n_primes(n):
    primes = []
    candidate = 2
    while len(primes) < n:
        for p in primes:
            if candidate % p == 0:
                break
        else:
            primes.append(candidate)
        candidate += 1
    return primes

def random_tpm(n):
    tpm = np.random.rand(n, n)
    tpm /= tpm.sum(axis=1, keepdims=True)
    return tpm

def guassian_tpm(n):
    tpm = np.zeros((n, n))
    for i in range(n):
        tpm[i] = np.exp(-0.5 * (np.arange(n) - i) ** 2)
    tpm /= tpm.sum(axis=1, keepdims=True)
    return tpm

def markov_chain_sequence(n, transitions):
    states = np.arange(len(transitions))
    sequence = [np.random.choice(states)]
    for _ in range(n - 1):
        sequence.append(np.random.choice(states, p=transitions[sequence[-1]]))
    return sequence


if __name__ == "__main__":
    notes = generate_piano_freqs()
    print(notes)

    N = 1000
    transitions = random_tpm(len(notes))
    sequence = markov_chain_sequence(N, transitions)
    frequencies = notes[sequence]
    durations = np.ones(N) * 0.1

    synth = Synth()


    synth.add_oscillator(Oscillator(frequency=440, amplitude=0.9, waveform='sine'))

    synth.save_sequence("random.wav", frequencies, durations)

    os.system("afplay random.wav")