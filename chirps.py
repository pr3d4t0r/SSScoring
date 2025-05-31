import numpy as np
import time
import pyaudio

# Constants
SAMPLE_RATE = 44100
BEEP_DURATION = 0.1
PAUSE_1 = 0.1
PAUSE_2 = 0.2
FREQ_START = 150
FREQ_END = 1850
RAMP_DURATION = 15.0
TOTAL_DURATION = 25.0

def generateSineWave(freq, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    audio = 0.5 * np.sin(2 * np.pi * freq * t)
    return (audio * 32767).astype(np.int16).tobytes()

def main():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=SAMPLE_RATE,
                    output=True)
    t = 0.0
    while t < TOTAL_DURATION:
        if t < RAMP_DURATION:
            progress = t / RAMP_DURATION
            freq = FREQ_START + (FREQ_END - FREQ_START) * progress
            tone = generateSineWave(freq, BEEP_DURATION)
            stream.write(tone)
            time.sleep(PAUSE_1)
            t += BEEP_DURATION + PAUSE_1
        else:
            tone = generateSineWave(FREQ_END, BEEP_DURATION)
            stream.write(tone)
            time.sleep(PAUSE_2)
            t += BEEP_DURATION + PAUSE_2
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == '__main__':
    main()

