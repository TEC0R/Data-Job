import streamlit as st
from typing import Generator
from groq import Groq
import json


def chat():
    profil_authen = st.session_state["config"]["credentials"]["usernames"][st.session_state["username"]]

    def read_system_prompt(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    # File path to the system prompt
    file_path = './streamlit_function/pages/prompt_tool_reco_skill.txt'
    system_prompt = read_system_prompt(file_path)

    profile_str = json.dumps(profil_authen, ensure_ascii=False, indent=4)

    client = Groq(
        api_key=st.secrets['GROQ_API_KEY'],
    )

    machine_prompt = {
        "role": "system",
        "content": f"{system_prompt} {profile_str}"
    }

    # Initialize chat history, selected model, and automatic response flag
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add machine prompt
        st.session_state.messages.append(machine_prompt)

    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None

    if "auto_response_sent" not in st.session_state:
        st.session_state.auto_response_sent = False  # Initialize the auto_response_sent variable

    # Display chat messages from history on app rerun
    for message in st.session_state.messages[2:]:
        avatar = '🤖' if message["role"] == "assistant" else '👨‍💻'
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
        """Yield chat response content from the Groq API response."""
        for chunk in chat_completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    # Automatic response logic
    if not st.session_state.auto_response_sent:
        # Add the pre-message
        pre_message = {"role": "user", "content": "Je souhaite que tu me donne des conseilles pour optimiser mes chances d'être recruter"}
        st.session_state.messages.append(pre_message)
        
        try:
            chat_completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": m["role"],
                        "content": m["content"]
                    }
                    for m in st.session_state.messages
                ],
                stream=True
            )

            # Use the generator function with st.write_stream
            with st.chat_message("assistant", avatar="🤖"):
                chat_responses_generator = generate_chat_responses(chat_completion)
                full_response = st.write_stream(chat_responses_generator)

            # Append the full response to session_state.messages
            if isinstance(full_response, str):
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response})
            else:
                # Handle the case where full_response is not a string
                combined_response = "\n".join(str(item) for item in full_response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": combined_response})
            
            # Mark the automatic response as sent
            st.session_state.auto_response_sent = True
        except Exception as e:
            st.error(e, icon="🚨")

    if prompt := st.chat_input("Enter your prompt here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar='👨‍💻'):
            st.markdown(prompt)

        # Fetch response from Groq API
        try:
            chat_completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": m["role"],
                        "content": m["content"]
                    }
                    for m in st.session_state.messages
                ],
                stream=True
            )

            # Use the generator function with st.write_stream
            with st.chat_message("assistant", avatar="🤖"):
                chat_responses_generator = generate_chat_responses(chat_completion)
                full_response = st.write_stream(chat_responses_generator)
        except Exception as e:
            st.error(e, icon="🚨")

        # Append the full response to session_state.messages
        if isinstance(full_response, str):
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response})
        else:
            # Handle the case where full_response is not a string
            combined_response = "\n".join(str(item) for item in full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": combined_response})
        st.experimental_rerun()

