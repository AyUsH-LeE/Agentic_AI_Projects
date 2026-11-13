# ==============================================================================
# 1. Imports & Logging Configuration
# ==============================================================================
import logging
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import streamlit as st
from pypdf import PdfReader

# Load environment variables (e.g., API keys) from a .env file
load_dotenv(find_dotenv())

# Configure logging to track app events and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================================================================
# 2. Global Constants & System Prompt
# ==============================================================================
MAX_FILE_MB = 10
MAX_DOC_CHARS = 60_000      # Crude guard until you add chunking/retrieval
MAX_HISTORY_TURNS = 10

# Define the core system instructions for the research assistant LLM
SYSTEM_PROMPT = (
    "You are a research assistant. Answer using only the documents provided. "
    "If the answer is not in the documents, say so. Do not invent information.\n\n"
    "Documents:\n{docs}"
)

# ==============================================================================
# 3. LLM Initialization (Cached)
# ==============================================================================
@st.cache_resource
def get_llm():
    """Initialize and cache the ChatGroq model client."""
    return ChatGroq(
        model="qwen/qwen3.8-27b",
        max_tokens=1500,
        timeout=30,
        max_retries=2,
        streaming=True,
    )

# ==============================================================================
# 4. Helper Functions for Document Extraction
# ==============================================================================
def extract_text(f) -> str:
    """Extract text from an uploaded PDF, TXT, or Markdown file."""
    if f.type == "application/pdf":
        reader = PdfReader(f)
        if reader.is_encrypted:
            raise ValueError("This PDF is encrypted.")
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = f.getvalue().decode("utf-8", errors="replace")
    if not text.strip():
        raise ValueError("No extractable text found (the file may be a scanned image).")
    return text

# ==============================================================================
# 5. Streamlit UI Header & State Initialization
# ==============================================================================
st.title("Ask your document")
st.markdown("Multi-Document QA & Research Assistant")

# Initialize session state variables for chat history and loaded documents
st.session_state.setdefault("messages", [])   # only user/assistant chat turns
st.session_state.setdefault("docs", {})       # {file_key: (name, text)}

# ==============================================================================
# 6. File Upload & Processing Section
# ==============================================================================
# Accept document uploads from the user
file = st.file_uploader("Upload a file", type=["pdf", "txt", "md"])
if file:
    if file.size > MAX_FILE_MB * 1024 * 1024:
        st.error(f"File too large (max {MAX_FILE_MB} MB).")
    else:
        key = (file.name, file.size)
        if key not in st.session_state.docs:
            try:
                with st.spinner("Reading document..."):
                    text = extract_text(file)
                if len(text) > MAX_DOC_CHARS:
                    st.warning("Document is long; truncating to fit the model context.")
                    text = text[:MAX_DOC_CHARS]
                st.session_state.docs[key] = (file.name, text)
            except Exception as e:
                logger.exception("Extraction failed")
                st.error(f"Could not read the file: {e}")

# Display currently loaded files if any exist
if st.session_state.docs:
    st.caption("Loaded: " + ", ".join(n for n, _ in st.session_state.docs.values()))

# ==============================================================================
# 7. Render Conversation History
# ==============================================================================
# Render all past messages in the chat interface
for m in st.session_state.messages:
    st.chat_message(m["role"]).markdown(m["content"])

# ==============================================================================
# 8. User Input & QA Processing Loop
# ==============================================================================
# Accept input query from the user
question = st.chat_input("Ask anything?")
if question:
    # Ensure at least one document is loaded before allowing questions
    if not st.session_state.docs:
        st.warning("Please upload a document first.")
        st.stop()

    # Display user's question and save it to session history
    st.chat_message("user").markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # Format all loaded documents into an XML-like structure for the prompt
    docs = "\n\n".join(
        f'<document name="{name}">\n{text}\n</document>'
        for name, text in st.session_state.docs.values()
    )
    
    # Slice the recent conversation history up to the allowed maximum turns
    history = st.session_state.messages[-MAX_HISTORY_TURNS * 2:]    # Using *2 because one full conversation "turn" consists of two messages: a user prompt and an assistant response. If MAX_HISTORY_TURNS is set to 10, this slices the last 20 messages (10 user + 10 assistant turns).
    
    # Construct the message payload including system prompt and chat history
    messages = [SystemMessage(SYSTEM_PROMPT.format(docs=docs))] + [
        HumanMessage(m["content"]) if m["role"] == "user" else AIMessage(m["content"])
        for m in history
    ]

    # Stream the LLM response and handle potential execution errors
    try:
        with st.chat_message("assistant"):
            answer = st.write_stream(
                chunk.content for chunk in get_llm().stream(messages)
            )
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception:
        logger.exception("LLM call failed")
        st.error("Something went wrong generating a response. Please try again.")
        st.session_state.messages.pop()  # drop the unanswered question