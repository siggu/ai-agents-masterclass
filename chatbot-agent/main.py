import time

import streamlit as st

st.header("Hello world!")

st.button("Click me please")

st.text_input(
    "Write your API Key",
    max_chars=20,
)

st.feedback("faces")

with st.sidebar:
    st.badge("Badge 1")


tab1, tab2, tab3 = st.tabs(["Agent", "Chat", "Output"])

with tab1:
    st.header("Agent 1")
with tab2:
    st.header("Agent 2")
with tab3:
    st.header("Agent 3")


time.sleep(2)
with st.chat_message("human"):
    st.text("안녕! 지금 한국의 날씨는 어때?")

time.sleep(3)
with st.chat_message("ai"):
    st.text("...")
    with st.status("Agent is using tool") as status:
        time.sleep(2)
        status.update(label="Agent is searching the web")
        time.sleep(2)
        status.update(label="Agent is reading the web")
        time.sleep(3)
        status.update(label="30도")
        status.update(state="complete")

st.chat_input(
    "Write a message for the assistant.",
    accept_file=True,
)
