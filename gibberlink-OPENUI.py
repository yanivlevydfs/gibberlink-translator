import streamlit as st
import sounddevice as sd
import queue
import numpy as np
import ggwave
import google.generativeai as genai
from openai import OpenAI
import threading
import time

# ============================================================
# INITIALIZATION
# ============================================================

def initialize_systems():
    """Initialize ggwave and Gemini systems."""
    try:
        wave = ggwave.init()
    except Exception as e:
        st.error(f"❌ Error initializing ggwave: {e}")
        return None

    # Try to configure Gemini if available
    try:
        gemini_key = st.secrets.get("GEMINI_API_KEY", None)
        if gemini_key:
            genai.configure(api_key=gemini_key)
        else:
            st.warning("⚠️ Gemini API key not found in secrets.")
    except Exception as e:
        st.error(f"Error initializing Gemini API: {e}")

    return wave


# ============================================================
# DECODING AND TRANSLATION
# ============================================================

def decode_audio(audio_data, wave):
    """Decode ultrasonic or encoded AI signal using ggwave."""
    try:
        return ggwave.decode(wave, audio_data.tobytes())
    except Exception as e:
        st.error(f"Error decoding audio: {e}")
        return None


def translate_with_gemini(message: str) -> str:
    """Translate message using Google Gemini."""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Translate AI communication to human language: {message}")
        return response.text.strip()
    except Exception as e:
        st.error(f"Error translating with Gemini: {e}")
        return "[Gemini Translation Error]"


def translate_with_chatgpt(message: str) -> str:
    """Translate message using OpenAI GPT-4 or GPT-4o."""
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # use "gpt-4-turbo" or "gpt-4o" if you have access
            messages=[
                {"role": "system", "content": "You are a translator between AI signals and human language."},
                {"role": "user", "content": f"Translate this AI communication into human language: {message}"}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error translating with ChatGPT: {e}")
        return "[ChatGPT Translation Error]"


# ============================================================
# AUDIO STREAM HANDLING
# ============================================================

def callback(indata, frames, time, status, audio_queue):
    """Capture microphone data via callback."""
    if status:
        st.warning(f"Stream status: {status}")
    audio_queue.put(indata.copy())


def listen_loop(audio_queue, wave, engine: str):
    """Background thread to continuously decode and translate."""
    with sd.InputStream(
        callback=lambda indata, frames, time, status: callback(indata, frames, time, status, audio_queue),
        samplerate=44100,
        channels=1,
        dtype='int16'
    ):
        while st.session_state.listening:
            if not audio_queue.empty():
                audio_data = audio_queue.get()
                decoded_msg = decode_audio(audio_data, wave)
                if decoded_msg:
                    if engine == "Gemini":
                        translation = translate_with_gemini(decoded_msg)
                    else:
                        translation = translate_with_chatgpt(decoded_msg)

                    st.session_state.messages.append((decoded_msg, translation))
            time.sleep(0.1)  # Prevent CPU overuse


# ============================================================
# STREAMLIT INTERFACE
# ============================================================

def main():
    st.set_page_config(page_title="GibberLink Translator", page_icon="🎧", layout="wide")

    st.title("🎧 GibberLink Translator")
    st.caption("Decode AI-to-AI acoustic messages into human-readable text using Gemini or ChatGPT.")

    # --- Initialize session state ---
    if "listening" not in st.session_state:
        st.session_state.listening = False
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # --- Setup systems ---
    wave = initialize_systems()
    if not wave:
        st.stop()

    audio_queue = queue.Queue()

    # --- Sidebar: Settings ---
    with st.sidebar:
        st.header("⚙️ Settings")
        engine = st.radio("Choose AI Model:", ["Gemini", "ChatGPT"], horizontal=False)
        st.info("Gemini uses Google's Generative AI.\nChatGPT uses OpenAI's GPT models.")

        st.divider()
        st.markdown("🪪 **API Keys:**")
        st.write(f"Gemini Key: {'✅' if st.secrets.get('GEMINI_API_KEY') else '❌ Not Found'}")
        st.write(f"OpenAI Key: {'✅' if st.secrets.get('OPENAI_API_KEY') else '❌ Not Found'}")

        st.divider()
        st.markdown("Developed by **Yaniv Levy** — 2025 ©")

    # --- Main UI ---
    col1, col2 = st.columns([3, 1])
    with col1:
        start = st.button("▶️ Start Listening", disabled=st.session_state.listening)
        stop = st.button("⏹️ Stop Listening", disabled=not st.session_state.listening)
    with col2:
        st.image("your_icon_path.png", width=100)

    # --- Handle button logic ---
    if start:
        st.session_state.listening = True
        thread = threading.Thread(target=listen_loop, args=(audio_queue, wave, engine), daemon=True)
        thread.start()
        st.success("Listening started! 🟢")

    if stop:
        st.session_state.listening = False
        st.warning("Listening stopped. 🛑")

    # --- Show messages ---
    if st.session_state.messages:
        st.markdown("### 💬 Recent Translations")
        for i, (raw, translated) in enumerate(reversed(st.session_state.messages[-10:]), 1):
            st.markdown(f"**AI #{i}:** {raw}")
            st.markdown(f"**Translated:** {translated}")
            st.divider()
    else:
        st.info("Press 'Start Listening' to begin decoding AI acoustic signals.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
