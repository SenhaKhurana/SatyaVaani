import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import queue


# ==========================================
# SATYAVAANI AUDIO CONFIGURATION
# ==========================================

SAMPLE_RATE = 16000
CHANNELS = 1

WINDOW_SECONDS = 2.0
WINDOW_SIZE = int(SAMPLE_RATE * WINDOW_SECONDS)

CHUNK_SECONDS = 0.5
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_SECONDS)


# ==========================================
# AUDIO BUFFER
# ==========================================

audio_queue = queue.Queue()

buffer = np.zeros(
    WINDOW_SIZE,
    dtype=np.float32
)

window_number = 0


# ==========================================
# MICROPHONE CALLBACK
# ==========================================

def audio_callback(indata, frames, time_info, status):

    if status:
        print("Audio status:", status)

    chunk = indata[:, 0].copy()

    audio_queue.put(chunk)


# ==========================================
# UPDATE AUDIO BUFFER
# ==========================================

def update_buffer():

    global buffer
    global window_number

    updated = False

    while not audio_queue.empty():

        chunk = audio_queue.get()

        # Move old audio to left
        buffer[:-len(chunk)] = buffer[len(chunk):]

        # Add new audio
        buffer[-len(chunk):] = chunk

        window_number += 1

        updated = True

    return updated


# ==========================================
# LIVE WAVEFORM
# ==========================================

fig, ax = plt.subplots()

time_axis = np.linspace(
    -WINDOW_SECONDS,
    0,
    WINDOW_SIZE
)

line, = ax.plot(
    time_axis,
    buffer
)

ax.set_title(
    "SatyaVaani - Live Microphone Audio"
)

ax.set_xlabel(
    "Time (seconds)"
)

ax.set_ylabel(
    "Amplitude"
)

ax.set_ylim(
    -0.5,
    0.5
)

ax.set_xlim(
    -WINDOW_SECONDS,
    0
)

ax.grid(True)


# ==========================================
# LIVE UPDATE FUNCTION
# ==========================================

def update_plot(frame):

    update_buffer()

    line.set_ydata(buffer)

    rms = np.sqrt(
        np.mean(buffer ** 2)
    )

    ax.set_title(
        f"SatyaVaani - Live Microphone Audio | "
        f"Window: {window_number} | "
        f"RMS: {rms:.4f}"
    )

    return line,


# ==========================================
# START MICROPHONE
# ==========================================

print("=" * 50)
print("       SATYAVAANI MICROPHONE")
print("=" * 50)

print("Sample Rate : 16000 Hz")
print("Channels    : Mono")
print("Window      : 2 seconds")
print("Hop         : 0.5 seconds")

print("\n🎙️ Microphone started.")
print("Speak into the microphone.")
print("Close the graph window to stop.\n")


stream = sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    blocksize=CHUNK_SIZE,
    dtype="float32",
    callback=audio_callback
)

stream.start()


# ==========================================
# START LIVE GRAPH
# ==========================================

animation = FuncAnimation(
    fig,
    update_plot,
    interval=100,
    blit=True,
    cache_frame_data=False
)

try:

    plt.show()

finally:

    stream.stop()
    stream.close()

    print("\n🎙️ Microphone stopped.")