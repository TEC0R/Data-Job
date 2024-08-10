import sounddevice as sd
import numpy as np
import wave
import threading

def record_audio(filename="human.wav", samplerate=44100, channels=2):
    # declarer une variable pour stocker l'audio 
    audio_data = []

    # creer une fonction pour recuperer l'audio en chunck et les mettre dans la liste
    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_data.append(indata.copy())

    # fonction pour definir la fin de l'enregistrement 
    def stop_recording():
        input("Je t'ecoute.... appuis sur entrée pour que je te reponde")
        nonlocal recording
        recording = False

    # demarrer un thread qui va target le declenchement de la fonction stop recording
    threading.Thread(target=stop_recording).start()

    # demarrer l'enregistrement
    recording = True
    try:
        with sd.InputStream(samplerate=samplerate, channels=channels, dtype='int16', callback=callback):
            while recording:
                sd.sleep(100)
    except Exception as e:
        print(f"An error occurred: {e}")
        return
    
    # convertir la liste de l'audio en array numpy
    audio_data = np.concatenate(audio_data, axis=0)

    # enregistrer l'audio dans un fichier .wav (meilleure qualité et rapidité de traitement)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # nombre de byte par sample
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    
    #print(f"Recording saved as {filename}")

# appeler la fonction qui va debuter l'enregistrement
record_audio()
