from api import clef_api_deepgram
import sounddevice as sd
from scipy.io.wavfile import write
from audio_record import record_audio

api_deepgram = clef_api_deepgram()

from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
# creer la fonction pour transformer l'audio en texte
def speech2text(audio_file):
    try:
        # creer le client deepgram a partir de la clef api
        deepgram = DeepgramClient(api_key=api_deepgram)
        # ouvrir le fichier audio
        with open(audio_file, "rb") as file:
            buffer_data = file.read()
        # definir la source des données et le modele utilisé pour transcrire l'audio
        payload: FileSource = {
            
            "buffer": buffer_data,
        }

        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )
        # definir la requete a l'api de deepgram en envoyant les données du fichier audio ainsi
        # que les parametres du modele utilisé 
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        # extraction de la transcription audio recu de l'api 
        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
        return(transcript)

    except Exception as e:
        print(f"Exception: {e}")

# verification de l'execution et print() du resultat de la fonction speech2text() sur l'audio enregistré
if __name__ == "__main__":
    print(speech2text("output.wav"))
