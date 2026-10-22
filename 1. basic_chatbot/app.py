"""
Basic Chatbot Application
A simple interactive Q&A chatbot built with Streamlit, LangChain, and Groq.
"""

# ==============================================================================
# 1. Imports
# ==============================================================================
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import streamlit as st

# ==============================================================================
# 2. Configuration & Model Initialization
# ==============================================================================
# Load environment variables from the .env file (e.g., GROQ_API_KEY)
load_dotenv()

# Initialize the Groq LLM client using LangChain
llm = ChatGroq(model="qwen/qwen3.8-27b")

# ==============================================================================
# 3. Streamlit UI Header
# ==============================================================================
st.title("Basic Chatbot")
st.markdown("My QnA Bot with LangChain and Groq.")

# ==============================================================================
# 4. Session State Initialization
# ==============================================================================
# Initialize chat history in Streamlit session state to preserve messages across reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================================================================
# 5. Display Conversation History
# ==============================================================================
# Render all previously exchanged messages
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)

# ==============================================================================
# 6. User Input & Response Handling
# ==============================================================================
# Accept input prompt from the user
query = st.chat_input("Ask anything?")
if query:
    # Display the user's message in the chat container and record it in session state
    st.chat_message("user").markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Query the LLM with the full conversation history to maintain context
    res = llm.invoke(st.session_state.messages)
    
    # Save assistant's reply to session history and display it in the chat interface
    st.session_state.messages.append({"role": "assistant", "content": res.content})
    st.chat_message("assistant").markdown(res.content)
