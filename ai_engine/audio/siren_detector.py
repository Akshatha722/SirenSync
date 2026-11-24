import sounddevice as sd
import numpy as np

SAMPLE_RATE = 44100
DURATION = 8
CHUNK_DURATION = 0.2
MICROPHONE_DEVICE = 1

print("SirenSync Improved Audio Detector")
print("Listening for 8 seconds...")
print("Play an ambulance siren near the microphone!")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    device=MICROPHONE_DEVICE
)

sd.wait()

chunk_size = int(CHUNK_DURATION * SAMPLE_RATE)
frequencies_found = []
sound_levels = []

for i in range(0, len(audio) - chunk_size + 1, chunk_size):

    chunk = audio[i:i + chunk_size, 0]

    rms = np.sqrt(np.mean(chunk ** 2))
    sound_levels.append(rms)

    chunk = chunk - np.mean(chunk)

    window = np.hanning(len(chunk))
    spectrum = np.abs(np.fft.rfft(chunk * window))

    frequencies = np.fft.rfftfreq(
        len(chunk),
        1 / SAMPLE_RATE
    )

    mask = (frequencies >= 400) & (frequencies <= 1800)

    peak = frequencies[mask][np.argmax(spectrum[mask])]

    frequencies_found.append(peak)


# Smooth frequency readings
smoothed = []

for i in range(len(frequencies_found)):

    start = max(0, i - 2)
    end = min(len(frequencies_found), i + 3)

    smoothed.append(
        np.median(frequencies_found[start:end])
    )
print("\nSmoothed frequency pattern:")
print([round(f) for f in smoothed])
# Find significant rising and falling patterns
turning_points = []

for i in range(1, len(smoothed) - 1):

    previous = smoothed[i - 1]
    current = smoothed[i]
    following = smoothed[i + 1]

    if current > previous and current > following:
        turning_points.append(current)

    elif current < previous and current < following:
        turning_points.append(current)


# Count meaningful frequency changes
significant_changes = 0

for i in range(1, len(turning_points)):

    difference = abs(
        turning_points[i] - turning_points[i - 1]
    )

    if difference >= 180:
        significant_changes += 1


average_sound = np.mean(sound_levels)

print("\nFrequency readings:", len(frequencies_found))
print("Average sound level:", round(average_sound, 5))
print("Significant pitch changes:", significant_changes)

if average_sound < 0.00005:
    print("\nResult: Very quiet audio.")

    print("Maximum sound level:", round(max(sound_levels), 5))

elif significant_changes >= 5:
    print("\nResult: Possible ambulance siren pattern detected.")

else:
    print("\nResult: No clear ambulance siren pattern detected.")

print("\nAudio analysis completed!")