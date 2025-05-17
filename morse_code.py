import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

# Config
FREQ = 400  # Hz
AMPLITUDE = 0.25
WPM = 12
SAMPLE_RATE = 44100
DIT_DURATION = 1.2 / WPM  # in seconds
DAH_DURATION = 3 * DIT_DURATION
INTRA_CHAR_SPACE = DIT_DURATION
INTER_CHAR_SPACE = 3 * DIT_DURATION
INTER_WORD_SPACE = 7 * DIT_DURATION
INTER_SLASH_PAUSE = 1  # Custom pause for '/'
PAUSE_BETWEEN_REPEATS = 4  # seconds

# Input message 
message = "-·-· --- ··-· ··-· ·-· · / ····· ····· --···"

# Replace alternative morse symbols
def clean_morse(message):
    return message.replace('·', '.').replace('–', '-').replace('—', '-')

# Audio functions
def tone(duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return (AMPLITUDE * np.sin(2 * np.pi * FREQ * t)).astype(np.float32)

def silence(duration):
    return np.zeros(int(SAMPLE_RATE * duration), dtype=np.float32)

def generate_morse_audio(message):
    audio = []
    for symbol in clean_morse(message):
        if symbol == '.':
            audio.append(tone(DIT_DURATION))
            audio.append(silence(INTRA_CHAR_SPACE))
        elif symbol == '-':
            audio.append(tone(DAH_DURATION))
            audio.append(silence(INTRA_CHAR_SPACE))
        elif symbol == ' ':
            audio.append(silence(INTER_CHAR_SPACE))
        elif symbol == '/':
            audio.append(silence(INTER_SLASH_PAUSE))
    return np.concatenate(audio)

# Lecture en boucle
def loop_play():
    morse_audio = generate_morse_audio(message)
    pause = silence(PAUSE_BETWEEN_REPEATS)
    audio = np.concatenate([morse_audio, pause])
    while True:
        sd.play(audio, SAMPLE_RATE)
        sd.wait()

# Sauvegarde en .wav si besoin
def save_wav(filename="morse_output.wav"):
    morse_audio = generate_morse_audio(message)
    write(filename, SAMPLE_RATE, morse_audio)

# Exécution principale
if __name__ == "__main__":
    try:
        print("Lecture audio en boucle. Ctrl+C pour arrêter.")
        loop_play()
        # save_wav()  # Décommente pour exporter le fichier
    except KeyboardInterrupt:
        print("\nArrêt manuel")
