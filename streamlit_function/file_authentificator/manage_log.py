import streamlit as st
from streamlit_authenticator.utilities.exceptions import CredentialsError, ForgotError, LoginError, RegisterError, ResetError, UpdateError 
from streamlit_function.file_authentificator.send_email import send_email


def login_page():

    # Creating tabs
    login, sign_in, forgot_password, forgot_username = st.tabs(['Login','Sign In','Forgot Password','Forgot Username'])

    with login :
        # Creating a login widget
        try:
            st.session_state.authenticator.login()
        except LoginError as e:
            st.error(e)



    with sign_in :
        # Creating a new user registration widget
        try:
            (email_of_registered_user,
                username_of_registered_user,
                name_of_registered_user) = st.session_state.authenticator.register_user(pre_authorization=False)
            if email_of_registered_user:
                st.session_state.config['credentials']['usernames'][st.session_state["username"]]["Forgot"] = False
                st.session_state.config['credentials']['usernames'][st.session_state["username"]]["hardskills"] = {}
                st.session_state.config['credentials']['usernames'][st.session_state["username"]]["softskills"] = {}
                st.success('User registered successfully')
        except RegisterError as e:
            st.error(e)

    with forgot_password :
        # Creating a forgot password widget
        try:
            (username_of_forgotten_password,
                email_of_forgotten_password,
                new_random_password) = st.session_state.authenticator.forgot_password()
            if username_of_forgotten_password:
                st.success('New password sent securely')
                send_email(email_of_forgotten_password, "Nouveau mot de passe", f"Bonjour {username_of_forgotten_password},\n\nVoici votre nouveau Mot de Passe : {new_random_password}")
                st.session_state.config['credentials']['usernames'][username_of_forgotten_password]['Forgot'] = True
            elif not username_of_forgotten_password:
                st.error('Username not found')
        except ForgotError as e:
            st.error(e)

    with forgot_username :
        # Creating a forgot username widget
        try:
            (username_of_forgotten_username,
                email_of_forgotten_username) = st.session_state.authenticator.forgot_username()
            if username_of_forgotten_username:
                st.success('Username sent securely')
                send_email(email_of_forgotten_password, "Oublie du username", f"Bonjour ,\n\nVoici votre username : {username_of_forgotten_username}")

                # Username to be transferred to the user securely
            elif not username_of_forgotten_username:
                st.error('Email not found')
        except ForgotError as e:
            st.error(e)

def reset_password():
    # Creating a password reset widget
    try:
        if st.session_state.authenticator.reset_password(st.session_state["username"]):
            st.success('Password modified successfully')
            st.session_state.config['credentials']['usernames'][st.session_state["username"]]["Forgot"] = False

    except ResetError as e:
        st.error(e)
    except CredentialsError as e:
        st.error(e)

