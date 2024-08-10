import streamlit as st
from streamlit_function.file_authentificator.manage_log import login_page, reset_password
from streamlit_function.background_image import background_image
from streamlit_function.pages.main_ap_auth import ap_auth
import streamlit_authenticator as stauth


background_image()

# Charger et déchiffrer le fichier YAML
st.session_state["config"] = {
    "cookie": {
        "expiry_days": 0,
        "key": "some_signature_key",
        "name": "some_cookie_name"
    },
    "credentials": {
        "usernames": {
            "nissou": {
                "Forgot": False,
                "email": "kacem.anissa@gmal.com",
                "failed_login_attempts": 0,
                "hardskills": {
                    "dashboard": ["Power BI", "Looker"],
                    "python": ["Scikit-learn"],
                    "sql": []
                },
                "logged_in": True,
                "name": "nissou",
                "password": "$2b$12$4T5UnmWVKheQNRxPjVYwX.GXA.zQgOt4Rss716GQLpsbHVHVNBjbq",
                "softskills": [],
                "ville": "Chennevières-sur-Marne (94)"
            },
            "quentin": {
                "Forgot": False,
                "email": "q.loumeau@googlemail.com",
                "failed_login_attempts": 0,
                "hardskills": {},
                "logged_in": True,
                "name": "quentin",
                "password": "$2b$12$eA/BFYq0Wa6I.7CADARqmuqdza5Lnqcc23hm0wXezegQIzDuEFd6C"
            },
            "tecor": {
                "Forgot": False,
                "contrat": ["ALTERNANCE"],
                "diplome": "Doctorat (PhD)",
                "email": "cornelusse.terry@gmail.com",
                "failed_login_attempts": 0,
                "hardskills": {
                    "dashboard": ["Power BI"],
                    "python": ["Pandas", "Numpy", "Scikit-learn", "Spacy"],
                    "sql": []
                },
                "logged_in": True,
                "name": "terry",
                "niveau": "SENIOR",
                "password": "$2b$12$pkd1xRnmaq/94x08KzOwHOjlVdNZLjb1mFT1IN9OPQwHqWrinqcvy",
                "softskills": ["Communication"],
                "ville": "Île-de-France"
            }
        }
    },
    "pre-authorized": {
        "emails": ["melsby@gmail.com"]
    }
}
        
# Creating the authenticator object
st.session_state.authenticator = stauth.Authenticate(
    st.session_state["config"]['credentials'],
    st.session_state["config"]['cookie']['name'],
    st.session_state["config"]['cookie']['key'],
    st.session_state["config"]['cookie']['expiry_days'],
    st.session_state["config"]['pre-authorized']
)


if not st.session_state["authentication_status"]:
    login_page()    

elif st.session_state["authentication_status"]: 
    #lieu personnel utilisateur
    ap_auth()


    if st.session_state["config"]['credentials']['usernames'][st.session_state["username"]]["Forgot"] :
        reset_password()
        

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')

elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')



