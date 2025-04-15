import streamlit as st
from textblob import TextBlob
from dotenv import load_dotenv
import asyncio
import os

import xai_sdk

# Load .env variables
load_dotenv()

# Streamlit UI Setup
st.set_page_config(page_icon="🏥", layout="wide", page_title="Virtual Doc!")

def icon(emoji: str):
    st.write(f'<span style="font-size: 78px; line-height: 1">{emoji}</span>', unsafe_allow_html=True)

icon("🧑‍⚕")
st.subheader("Your Personal Doctor")

# xAI Grok SDK Setup
api_key = os.getenv("XAI_API_KEY")  # Updated environment variable name
if not api_key:
    st.error("Missing API key! Please set XAI_API_KEY in your .env file.")
    st.stop()

client = xai_sdk.Client(api_key=os.getenv("XAI_API_KEY"))

# Session state for conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mood analyzer
def analyze_mood(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# UI
st.header("Welcome to the AI-Powered Mental Health Companion!")
st.write("Track your mood, get personalized mindfulness exercises, and receive real-time emotional support.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input
if prompt := st.chat_input("Talk to the AI"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    system_prompt = (
        "You are a virtual doctor named DocOuc. Your role is to diagnose and provide medical advice to patients "
        "while asking as few questions as possible. Your approach should be friendly, empathetic, and supportive, "
        "offering not only medical insights but also emotional and moral support. Engage with the patient in a kind "
        "and understanding manner, making them feel comfortable and cared for. Analyze the problem and provide the "
        "solution in a clear and concise manner. The response must be broken down into points."
    )

    final_prompt = f"{system_prompt}\n\nPatient: {prompt}\nDocOuc:"

    try:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response_tokens = []  # Using a list to collect tokens

            async def display_response():
                async for token in client.grok.stream(final_prompt, max_len=512):
                    full_response_tokens.append(token.token_str)
                    # Update the placeholder with the joined tokens
                    placeholder.markdown("".join(full_response_tokens))

            asyncio.run(display_response())
            # Once done, join tokens into a single string
            full_response = "".join(full_response_tokens)
            mood_analysis = analyze_mood(prompt)
            st.write("Mood Analysis:", mood_analysis)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"An error occurred: {str(e)}", icon="🚨")
        st.info("Please try again or check your internet connection.")
