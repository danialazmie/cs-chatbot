import streamlit as st
import time
from bot.chatbot import Chatbot
import logging

logger = logging.getLogger(st.__name__)

model_map = {
    'X': 'Gemini',
    'Y': 'OpenAI'
}

st.markdown("""
<style>
    div.stSpinner > div {
        text-align:center;
        align-items: center;
        justify-content: center;
    }
</style>""", unsafe_allow_html=True)

st.title('Tonton Chatbot')
st.caption('Version 2.4.5')
st.caption('If you find any issues or have ideas for improvement, feel free to reach out to Data Science and Analytics team at koonfoong@revmedia.my, danial.azmi@revmedia.my, faris.omar@revmedia.my')
st.caption('Please give your feedback [here](https://docs.google.com/forms/d/e/1FAIpQLSfCQrfMxhSffbXmC-3FfWTV5_frTm-4YVKDpB_dju7OOdoPGQ/viewform) or if the chatbot is giving inaccurate responses, report them [here](https://docs.google.com/spreadsheets/d/19PUcIGXNIkx98M5tJRs4zXfnuOxDacGmYD6ws-xNTq8/edit?usp=sharing)')

if "messages" not in st.session_state:
    st.session_state.messages = []

if 'model' not in st.session_state:
    st.session_state.model = 'X'

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = Chatbot(model_map[st.session_state.model])

def reset_conversation():
    st.session_state.messages = []
    st.session_state.chatbot = Chatbot(model_map[st.session_state.model])

option = st.selectbox(
    'Model:',
    ('X', 'Y'),
    index=0,
    key='model',
    on_change=reset_conversation
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type something here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner(''):
        response = st.session_state.chatbot.prompt(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message('assistant'):
        st.markdown(response)
