import streamlit as st
import yaml
from yaml.loader import SafeLoader
from cryptography.fernet import Fernet

def decrypt_yaml(file_path, key):
    cipher_suite = Fernet(key)
    
    # Charger les données chiffrées
    with open(file_path, 'rb') as enc_file:
        cipher_text = enc_file.read()

    # Déchiffrer les données
    decrypted_bytes = cipher_suite.decrypt(cipher_text)

    # Convertir les bytes déchiffrés en chaîne de caractères
    decrypted_str = decrypted_bytes.decode('utf-8')

    # Charger les données YAML à partir de la chaîne déchiffrée
    return yaml.safe_load(decrypted_str)




def encrypt_yaml(data, file_path, key):
    cipher_suite = Fernet(key)
    
    # Convertir les données YAML en une chaîne de caractères et encoder en bytes
    yaml_str = yaml.dump(data)
    yaml_bytes = yaml_str.encode('utf-8')

    # Chiffrer les données YAML
    cipher_text = cipher_suite.encrypt(yaml_bytes)

    # Enregistrer les données chiffrées dans un fichier
    with open(file_path, 'wb') as enc_file:
        enc_file.write(cipher_text)

