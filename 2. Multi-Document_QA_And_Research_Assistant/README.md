# Ask Your Document: Multi-Document QA & Research Assistant

A lightweight, interactive web app built with **Streamlit**, **LangChain**, and **Groq**. Upload PDF, TXT, or Markdown files and ask questions about them in a chat interface. Answers are grounded strictly in the uploaded documents, and responses stream in token by token for a fast, responsive feel.

---

## 🚀 Features

* **Document Upload:** Supports `.pdf`, `.txt`, and `.md` files (up to 10 MB each) via `st.file_uploader`.
* **Multi-Document Context:** Every file you upload during a session is kept and sent to the model together, so you can ask questions across several documents.
* **Grounded Answers:** The system prompt instructs the model to answer only from the provided documents and to say so when the answer isn't there, instead of inventing information.
* **Streaming Responses:** Replies are streamed live using LangChain's `.stream()` and Streamlit's `st.write_stream`.
* **Session State Management:** Chat history and loaded documents persist across Streamlit reruns within the active browser session.
* **Bounded Context:** Chat history is capped at the last 10 turns and each document at 60,000 characters, to keep requests within the model's context window.
* **Robust Error Handling:** Handles encrypted PDFs, scanned/image-only files, oversized uploads, and LLM failures with clear messages and logging.
* **Environment Security:** API keys are managed through `python-dotenv`.

---

## 📋 Prerequisites

Before running the application, ensure you have:
* Python 3.9 or higher installed on your system.
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
pip install streamlit langchain-groq langchain-core python-dotenv pypdf
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

## 🧭 How to Use

1. **Upload a document** using the file uploader (PDF, TXT, or MD, max 10 MB).
2. Wait for the "Reading document..." spinner to finish. The file name appears under **Loaded:**.
3. *(Optional)* Upload additional files one after another. All of them are included in the context.
4. **Ask a question** in the chat box. The answer streams in, based only on your documents.
5. Ask follow-ups. The last 10 turns of conversation are remembered.

---

## 🛠️ Code Overview

| Component | Description |
| :--- | :--- |
| **`load_dotenv(find_dotenv())`** | Loads environment variables (e.g., `GROQ_API_KEY`) from the `.env` file. |
| **Constants** | `MAX_FILE_MB` (10), `MAX_DOC_CHARS` (60,000), and `MAX_HISTORY_TURNS` (10) control upload size, per-document text length, and remembered chat turns. |
| **`SYSTEM_PROMPT`** | Instructs the model to act as a research assistant that answers only from the supplied documents. |
| **`get_llm()`** | Cached (`@st.cache_resource`) `ChatGroq` client using `qwen/qwen3.8-27b` with streaming, a 30s timeout, 2 retries, and a 1,500-token output limit. |
| **`extract_text()`** | Extracts text from PDFs via `pypdf` (rejecting encrypted files) or decodes TXT/MD files; raises an error if no text is found. |
| **`st.session_state`** | Holds `messages` (user/assistant turns) and `docs` (loaded documents keyed by file name and size). |
| **`st.file_uploader`** | Accepts uploads, validates size, extracts text, and truncates overly long documents. |
| **Prompt assembly** | Wraps each document in `<document name="...">` tags, injects them into the system prompt, and appends recent chat history as `HumanMessage` / `AIMessage` objects. |
| **`st.write_stream`** | Streams the model's response into the chat UI as it is generated. |

---

## 🔄 How It Works

```text
Upload file → extract_text() → truncate to 60k chars → store in session_state.docs
                                                              │
User question → build <document> blocks → SystemMessage + last 10 turns
                                                              │
                                   ChatGroq (streaming) → answer shown in chat
```

This is a **context-stuffing** approach: the full text of every loaded document is placed directly in the system prompt on each question. It is simple and works well for a handful of small-to-medium documents, but it does not scale to large files or large collections (see limitations below).

---

## ⚠️ Current Limitations

* **No retrieval layer:** There is no chunking, embedding, or vector store yet. Large documents are simply truncated at 60,000 characters (the end of the document is lost).
* **Context budget is per document:** The 60,000-character limit applies to each file individually, so many documents together can still exceed the model's context window.
* **No source citations:** Answers don't yet indicate which document or page they came from.
* **Limited file types:** DOCX and CSV are not supported yet.
* **Single-file uploader:** Files are added one at a time, and there is currently no button to remove a loaded document or clear the chat.
* **Scanned PDFs:** Image-only PDFs aren't supported because there is no OCR step.
* **Session-only memory:** Documents and chat history are lost when the browser session ends.

---

## 💡 Roadmap: Toward Advanced RAG

The original vision for this project is a full multi-document research assistant built on Retrieval-Augmented Generation. Planned enhancements:

* **Retrieval pipeline:** Load documents with `PyPDFLoader`, split them with `RecursiveCharacterTextSplitter`, embed the chunks, and store them in a vector database (`FAISS` or `Chroma`) so only the most relevant passages are sent to the model.
* **Source citations:** Show exactly which document and page each answer came from, using chunk metadata.
* **Document comparison:** Support queries such as "Compare the financial metrics in the Q2 vs. Q3 report" by retrieving from each document separately and synthesizing the results.
* **More file formats:** Add DOCX and CSV support alongside PDF, TXT, and MD.
* **Multi-file upload:** Enable `accept_multiple_files=True` and a sidebar listing loaded documents with remove buttons.
* **Conversational retrieval:** Use a conversational retrieval chain (e.g., `ConversationalRetrievalChain` or the newer LangChain retrieval/LCEL equivalents) so follow-up questions are rewritten with chat context before retrieval.
* **UI controls:** Add a sidebar to configure model selection, `temperature`, and system instructions, plus a **Clear Chat** button to reset `st.session_state.messages`.
* **OCR support:** Handle scanned PDFs with an OCR step.

---

## 🔧 Troubleshooting

| Problem | Likely Cause / Fix |
| :--- | :--- |
| `GROQ_API_KEY` not found / authentication error | Make sure `.env` exists in the project root and contains a valid key, then restart Streamlit. |
| "This PDF is encrypted." | Remove the password protection from the PDF and re-upload. |
| "No extractable text found" | The file is likely a scanned image. Use an OCR tool first. |
| "Document is long; truncating..." | The file exceeds 60,000 characters; only the beginning is used. Consider splitting the file, or wait for the RAG upgrade. |
| Model not found error | Verify the model ID in `get_llm()` against the models currently available in the [Groq Console](https://console.groq.com/). |
| "Something went wrong generating a response" | Check the terminal logs for the underlying exception (rate limit, timeout, or network issue) and try again. |

---

## 📦 Tech Stack

* [Streamlit](https://streamlit.io/): UI and session management
* [LangChain](https://www.langchain.com/) (`langchain-groq`, `langchain-core`): LLM integration and message types
* [Groq](https://groq.com/): fast LLM inference
* [pypdf](https://pypdf.readthedocs.io/): PDF text extraction
* [python-dotenv](https://pypi.org/project/python-dotenv/): environment variable loading