# Basic Chatbot with Streamlit, LangChain, and Groq

A lightweight, interactive web-based chat application built using **Streamlit**, **LangChain**, and **Groq**'s lightning-fast language models. This application maintains conversational history during the session and provides a clean, user-friendly chat interface.

---

## 🚀 Features

* **Interactive UI:** Powered by Streamlit's native chat components (`st.chat_input` and `st.chat_message`).
* **Session State Management:** Retains chat history across interactions within the active browser session.
* **High-Performance LLM:** Utilizes Groq's integration with LangChain for rapid response generation using the `qwen/qwen3.8-27b` model.
* **Environment Security:** Securely manages sensitive credentials like API keys using `python-dotenv`.

---

## 📋 Prerequisites

Before running the application, ensure you have:
* Python 3.8 or higher installed on your system.
* A valid Groq API Key (you can create one at [Groq Console](https://console.groq.com/)).

---

## ⚙️ Installation & Setup

### 1. Project Directory
Ensure your project files are organized in a single folder with the following structure:

```text
├── app.py          # Main application file
├── .env            # Environment file storing API keys
└── README.md       # Project documentation
```

### 2. Install Required Dependencies
Run the following command to install the required Python packages:

```bash
pip install streamlit langchain-groq python-dotenv
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory of the project and add your Groq API key:

```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

---

## 🏃‍♂️ Running the Application

Execute the following command in your terminal to launch the Streamlit app:

```bash
streamlit run app.py
```

> **Note:** If your script is named differently than `app.py`, replace it with your file's name in the command above.

Once launched, the app will automatically open in your default web browser (typically at `http://localhost:8501`).

---

## 🛠️ Code Overview

| Component | Description |
| :--- | :--- |
| **`load_dotenv()`** | Loads environment variables from the `.env` file into python environment. |
| **`ChatGroq`** | Initializes the LLM instance with `qwen/qwen3.8-27b`. |
| **`st.session_state`** | Preserves chat history (`messages`) across Streamlit rerenders. |
| **`st.chat_message`** | Displays chat messages formatted cleanly according to the speaker's role (`user` or `assistant`). |
| **`st.chat_input`** | Accepts text input from the user and triggers model invocation. |

---

## 💡 Future Enhancements

* Add a sidebar to configure parameters like model selection, `temperature`, or system instructions.
* Implement a **Clear Chat** button to reset `st.session_state.messages`.
* Enable streaming responses using LangChain's streaming capabilities for real-time output.