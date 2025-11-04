import streamlit as st
import sounddevice as sd
import queue
import numpy as np
import ggwave
import google.generativeai as genai
import threading
import time

# --- Initialization ---
def initialize_systems():
    try:
        wave = ggwave.init()
    except Exception as e:
        st.error(f"Error initializing ggwave: {e}")
        return None
    try:
        genai.configure(api_key=st.secrets.get("GEMINI_API_KEY", "your_gemini_api_key"))
    except Exception as e:
        st.error(f"Error initializing Gemini API: {e}")
        return None
    return wave


def decode_audio(audio_data, wave):
    try:
        return ggwave.decode(wave, audio_data.tobytes())
    except Exception as e:
        st.error(f"Error decoding audio: {e}")
        return None


def translate_message(message):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Translate AI communication to human language: {message}")
        return response.text
    except Exception as e:
        st.error(f"Error translating message: {e}")
        return "[Translation Error]"


def callback(indata, frames, time, status, audio_queue):
    if status:
        st.warning(f"Stream status: {status}")
    audio_queue.put(indata.copy())


# --- Listening Thread ---
def listen_loop(audio_queue, wave):
    """Background thread: continuously read from audio queue."""
    with sd.InputStream(callback=lambda indata, frames, time, status:
                        callback(indata, frames, time, status, audio_queue),
                        samplerate=44100, channels=1, dtype='int16'):
        while st.session_state.listening:
            if not audio_queue.empty():
                audio_data = audio_queue.get()
                decoded_msg = decode_audio(audio_data, wave)
                if decoded_msg:
                    translation = translate_message(decoded_msg)
                    st.session_state.messages.append(
                        (decoded_msg, translation)
                    )
            time.sleep(0.1)  # avoid CPU overuse


# --- Streamlit UI ---
def main():
    st.title("🎧 GibberLink Translator")
    st.subheader("Listen to AI Agents' Communication and Translate")

    # Initialize session state
    if "listening" not in st.session_state:
        st.session_state.listening = False
    if "messages" not in st.session_state:
        st.session_state.messages = []

    wave = initialize_systems()
    if not wave:
        st.stop()

    audio_queue = queue.Queue()

    # --- UI buttons ---
    col1, col2 = st.columns([3, 1])
    with col1:
        start = st.button("▶️ Start Listening", disabled=st.session_state.listening)
        stop = st.button("⏹️ Stop Listening", disabled=not st.session_state.listening)
    with col2:
        st.image("your_icon_path.png", width=100)

    # --- Button logic ---
    if start:
        st.session_state.listening = True
        thread = threading.Thread(target=listen_loop, args=(audio_queue, wave), daemon=True)
        thread.start()
        st.success("Listening started! 🟢")

    if stop:
        st.session_state.listening = False
        st.warning("Listening stopped. 🛑")

    # --- Display messages dynamically ---
    if st.session_state.messages:
        st.markdown("### 💬 Translations")
        for i, (raw, translated) in enumerate(reversed(st.session_state.messages[-10:]), 1):
            st.write(f"**AI #{i}:** {raw}")
            st.write(f"**Translated:** {translated}")
            st.divider()


if __name__ == "__main__":
    main()
