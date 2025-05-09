import streamlit as st
from cheese_chatbot import FoodChatbot
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Cheese Product Assistant",
    page_icon="🧀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_json" not in st.session_state:
    st.session_state.show_json = False
if "relevant_products" not in st.session_state:
    st.session_state.relevant_products = "I'm a chatbot."

# Custom CSS
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #f5f5f5;
        padding: 2rem;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .chat-message.user {
        background-color: white;
        color: black;
        margin-left: 20%;
        border-bottom-right-radius: 0.5rem;
    }
    
    .chat-message.assistant {
        background-color: white;
        margin-right: 20%;
        border-bottom-left-radius: 0.5rem;
        border: 1px solid #e0e0e0;
    }
    
    .chat-message .content {
        display: flex;
        flex-direction: row;
        align-items: flex-start;
    }
    
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    /* JSON viewer styling */
    .json-viewer {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        max-height: 600px;
        overflow-y: auto;
        font-family: monospace;
        font-size: 0.9rem;
    }
    
    /* Updated Input box styling */
    .stTextInput>div>div>input {
        background-color: white !important;
        color: black !important;
        border-radius: 1rem;
        padding: 1rem;
        border: 1px solid #e0e0e0;
    }
    
    /* Style for the input placeholder */
    .stTextInput>div>div>input::placeholder {
        color: #666 !important;
    }
    
    /* Style for the input when focused */
    .stTextInput>div>div>input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 1px #4CAF50;
    }
    
    /* Style for the input container */
    .stTextInput>div>div {
        background-color: white !important;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 1rem;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 1rem;
        color: #666;
        font-size: 0.8rem;
    }
    
    /* Product card styling */
    .product-card {
        background-color: white;
        border-radius: 1rem;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Animation for new messages */
    @keyframes slideIn {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .chat-message {
        animation: slideIn 0.3s ease-out;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize chatbot
@st.cache_resource
def get_chatbot():
    return FoodChatbot()

chatbot = get_chatbot()

# Header
st.markdown("""
    <div class="header">
        <h1>🧀 Cheese Product Assistant</h1>
        <p>Your personal guide to the world of fine cheeses</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2>About</h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        This assistant helps you discover and learn about our premium cheese selection.
        Features:
        - Detailed product information
        - Video demonstrations
        - Storage recommendations
        - Pairing suggestions
        - Expert advice
    """)
    
    st.markdown("""
        <div style='margin-top: 2rem;'>
            <h3>Example Questions</h3>
            <ul>
                <li>What kind of cheddar do you have?</li>
                <li>Can you recommend a cheese for my wine?</li>
                <li>How should I store this cheese?</li>
                <li>Tell me about your artisanal cheeses</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    # Add JSON viewer toggle
    st.markdown("---")
    if st.button("Toggle Raw JSON Data"):
        st.session_state.show_json = not st.session_state.show_json
    
    if st.session_state.show_json:
        st.markdown("### Raw JSON Data")
        st.markdown('<div class="json-viewer">', unsafe_allow_html=True)
        st.markdown(st.session_state.relevant_products)
        st.markdown('</div>', unsafe_allow_html=True)

# Chat interface
def display_chat_message(role, content):
    if role == "user":
        st.markdown(f"""
            <div class="chat-message user">
                <div class="content">
                    <div class="avatar">👤</div>
                    <div>{content}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="chat-message assistant">
                <div class="content">
                    <div class="avatar">🧀</div>
                    <div>{content}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Display chat history
for message in st.session_state.messages:
    display_chat_message(message["role"], message["content"])

# Chat input
user_input = st.chat_input("Ask about our cheeses...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    display_chat_message("user", user_input)
    
    # Get chatbot response
    with st.spinner("Thinking..."):
        try:
            response = chatbot.chat(user_input)
            print(response)
            st.session_state.relevant_products = response[1]
            response = response[0]
            # Add assistant message to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            display_chat_message("assistant", response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please try again or rephrase your question.")

# Footer
st.markdown("""
    <div class="footer">
        <p>Powered by OpenAI GPT-4 and Pinecone Vector Database</p>
        <p>© 2024 The Cheese Market. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)

# Add a clear chat button in the sidebar
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()