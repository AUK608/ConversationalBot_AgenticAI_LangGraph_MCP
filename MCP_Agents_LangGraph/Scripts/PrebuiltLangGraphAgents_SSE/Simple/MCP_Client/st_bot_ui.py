import streamlit as st
import asyncio
from supervisor_lg_poc import initialize_supervisor  # Replace with actual path/module

import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import LoginError

with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Creating a login widget
try:
    authenticator.login()
except LoginError as e:
    st.error(e)

# Authenticating user
if st.session_state['authentication_status']:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}* ...')


    # Session state to store conversation
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "awaiting_confirmation" not in st.session_state:
        st.session_state.awaiting_confirmation = False

    if "pending_action" not in st.session_state:
        st.session_state.pending_action = None

    st.title("📊 Welcome to Conversational ChatBot")

    st.markdown("Predefined Prompts : ")
    st.markdown(""" 1) Look Up Cases in <Queue>,\n
    2) Look Up Cases in <Queue> and if Status <status> then Update with <Queue> and send Mail to corresponding IDs with correct subject, message content, else dont update and email,\n
    3) Look Up Case in <Queue> and if Status <status> then Mail to corresponding IDs\n""")

    # Display previous messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).markdown(msg["content"])

    # User input
    if prompt := st.chat_input("Say hi or give an instruction..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # If awaiting confirmation
        if st.session_state.awaiting_confirmation:
            if "yes" in prompt.lower():
                # Proceed with actual changes using original input
                with st.spinner("Executing tasks..."):
                    final_output = asyncio.run(initialize_supervisor(st.session_state.pending_action))
                st.chat_message("assistant").markdown(f"✅ Done:\n{final_output}")
                st.session_state.messages.append({"role": "assistant", "content": f"✅ Done:\n{final_output}"})
                st.session_state.awaiting_confirmation = False
                st.session_state.pending_action = None
            else:
                st.chat_message("assistant").markdown("❌ Cancelled the action. Let me know what to do next.")
                st.session_state.messages.append({"role": "assistant", "content": "❌ Cancelled the action. Let me know what to do next."})
                st.session_state.awaiting_confirmation = False
                st.session_state.pending_action = None

        else:
            # Step 1: only retrieve and show what will happen
            preview_prompt = prompt + "\nOnly retrieve data and tell me what actions will be taken, don't make changes yet."

            with st.spinner("Analyzing and retrieving data..."):
                preview_response = asyncio.run(initialize_supervisor(preview_prompt))

            st.chat_message("assistant").markdown(f"📋 Here's what will happen:\n{preview_response}")
            st.session_state.messages.append({"role": "assistant", "content": f"📋 Here's what will happen:\n{preview_response}"})

            st.chat_message("assistant").markdown("🟡 Shall I proceed with these actions? (yes/no)")
            st.session_state.messages.append({"role": "assistant", "content": "🟡 Shall I proceed with these actions? (yes/no)"})

            st.session_state.awaiting_confirmation = True
            st.session_state.pending_action = prompt

elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect!!!')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password!!!')
    
