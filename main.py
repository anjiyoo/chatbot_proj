from dotenv import load_dotenv
import os
from openai import OpenAI
from langchain_openai import ChatOpenAI

load_dotenv()
openai_api_key = os.getenv("openai_api_key")

# main.py
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI 
from langchain.schema import ChatMessage
import streamlit as st
import json

API_KEY = os.getenv("openai_api_key")
MODEL = "gpt-4-0125-preview"

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

# JSON 파일 경로
json_file_path = "breeds.json"

# JSON 파일을 로드하여 데이터를 가져옵니다.
content = load_json_file(json_file_path)

want_to = """너는 아래 내용을 기반으로 질의응답을 하는 로봇이야.
content
{}
"""

st.header("견종 가이드")
if "messages" not in st.session_state:
    st.session_state["messages"] = [ChatMessage(role="assistant", content="궁금한 견종을 입력해주세요.")]

for msg in st.session_state.messages:
    st.chat_message(msg.role).write(msg.content)

if prompt := st.chat_input():
    st.session_state.messages.append(ChatMessage(role="user", content=prompt))
    st.chat_message("user").write(prompt)

    if not API_KEY:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    with st.chat_message("assistant"):
        stream_handler = StreamHandler(st.empty())
        llm = ChatOpenAI(openai_api_key=API_KEY, streaming=True, callbacks=[stream_handler], model_name=MODEL)
        response = llm([ ChatMessage(role="system", content=want_to.format(content))]+st.session_state.messages)
        st.session_state.messages.append(ChatMessage(role="assistant", content=response.content))
