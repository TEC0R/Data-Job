import tempfile
from text3speech import text2speech
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from playsound import playsound
from audio_record import record_audio
from speech2text import speech2text
from api import clef_api_groq 
api_groq = clef_api_groq()
# fonction pour lire le fichier txt du prompt
def read_system_prompt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
# chemin du fichier du prompt systeme
file_path = 'system_prompt.txt'

# lecture du prompt systeme
system_prompt = read_system_prompt(file_path)

# creer un objet pour appeler le modele, avec le parametre de temperature
chat = ChatGroq(temperature=0.5, groq_api_key=api_groq, model_name="llama3-70b-8192")
# definir le contexte du modele, pour le template du chat, je defini le prompt du system
# sur le fichier txt qui contient le prompt
human = "{text}"
prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human)])
chain = prompt | chat
# stocker la fonction speech2text qui permet d'enregistrer un message qui sera transcrit en texte et     
# utilisé en tant que prompt pour communiquer avec le modele
texte = speech2text(r"C:\Users\quent\Documents\GitHub\Data_job\audios\human.wav")
# je defini la reponse en invoquant la chaine avec le texte issus de l'audio
reponse = chain.invoke({"text": texte})
# la fonction text2speech va convertir la reponse du modele en audio
text2speech(reponse.content)
# poour finir j'utilise la librairie playsound qui permet de lire automatiquement le fichier 
# audio transcrit du texte de la reponse du modele
playsound(r"C:\Users\quent\Documents\GitHub\Data_job\audios\system.wav")