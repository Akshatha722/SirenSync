import sounddevice as sd
import numpy as np

SAMPLE_RATE = 44100
DURATION = 5
CHUNK_SIZE = 0.5

print("Recording audio for 5 seconds...")
print("Play an ambulance siren near your microphone!")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    device=1
)

sd.wait()

print("\nAudio Frequency Analysis:")

chunk_samples = int(CHUNK_SIZE * SAMPLE_RATE)

for i in range(0, len(audio), chunk_samples):

    chunk = audio[i:i + chunk_samples, 0]

    if len(chunk) != chunk_samples:
        continue

    chunk = chunk - np.mean(chunk)

    window = np.hanning(len(chunk))

    spectrum = np.abs(np.fft.rfft(chunk * window))

    frequencies = np.fft.rfftfreq(
        len(chunk),
        1 / SAMPLE_RATE
    )

    mask = (frequencies >= 300) & (frequencies <= 2000)

    peak_frequency = frequencies[mask][
        np.argmax(spectrum[mask])
    ]

    print(f"Dominant frequency: {peak_frequency:.2f} Hz")

print("\nAnalysis completed!")