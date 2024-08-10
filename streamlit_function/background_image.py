import base64
import streamlit as st
import os

# création définition pour charger les affiches en local:
def load_image_as_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def background_image():
    # Charger l'image de fond
    image_path = "./streamlit_function/background.png"
    image_base64 = load_image_as_base64(image_path)
    # Définir le style CSS pour l'image de fond
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{image_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            height: 100vh;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )