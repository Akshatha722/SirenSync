import sounddevice as sd

duration = 5
sample_rate = 44100

print("Listening...Play an ambulance siren near the laptop microphone!")

audio = sd.rec(
    int(duration * sample_rate),
    samplerate=sample_rate,
    channels=1,
    device=1
)

sd.wait()

print("Recording completed!")
print("Audio shape:", audio.shape)
print("Maximum sound level:", abs(audio).max())
print("Average sound level:", (audio ** 2).mean() ** 0.5)