# Importing Libraries
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import streamlit as st

# Loading Environment Variables
load_dotenv()
llm = ChatGroq(model="qwen/qwen3.8-27b")

# StreamlitUI

st.title("Basic Chatbot")
st.markdown("My QnA Bot with LangChain and Groq.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)

query = st.chat_input("Ask anything?")
if query:
    st.chat_message("user").markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})
    
    res = llm.invoke(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": res.content})
    st.chat_message("assistant").markdown(res.content)
