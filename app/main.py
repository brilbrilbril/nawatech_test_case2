import sys, os
import streamlit as st
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
 
from config.setting import env
from controller.instance import RAG

# configuration
session_id_1 = "user_1"
inactive_limit = timedelta(minutes=5)
max_len = 20

st.title("Nawatech FAQ Chatbot")

# define the session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_interaction" not in st.session_state:
    st.session_state["last_interaction"] = datetime.now()

# a button to clear the chat history from screen and RAM
if st.button("Clear session"):
    RAG._clear_session(session_id=session_id_1)
    st.session_state["messages"] = []
    st.session_state["last_interaction"] = datetime.now()

# display the past chat
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# user input
if prompt:=st.chat_input("Type here.."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # model will stop generating resposne if the user is inactive for more than 5 minutes
    # or the length of the chat is more than 20
    if datetime.now() - st.session_state["last_interaction"] > inactive_limit or len(st.session_state["messages"]) > 20:
        with st.chat_message("assistant"):
            response = "Your session is expired, please click clear session button above"
            st.write(response)
    else:
        with st.chat_message("assistant"):
            response=st.write_stream(RAG.run(prompt, session_id_1))
            st.session_state["last_interaction"] = datetime.now()
    st.session_state.messages.append({"role": "assistant", "content": response})
    
