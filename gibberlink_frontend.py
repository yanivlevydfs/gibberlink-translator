import streamlit as st
import sounddevice as sd
import queue
import numpy as np
import ggwave
import google.generativeai as genai

# Initialize systems with improved error handling and user-friendly messages
def initialize_systems():
    try:
        wave = ggwave.init()
    except Exception as e:
        st.error(f"Error initializing ggwave: {e}")
        return None
    try:
        genai.configure(api_key="your_gemini_api_key")
    except Exception as e:
        st.error(f"Error initializing Gemini API: {e}")
        return None
    return wave

# Decode audio with proper exception handling
def decode_audio(audio_data, wave):
    try:
        return ggwave.decode(wave, audio_data.tobytes())
    except Exception as e:
        st.error(f"Error decoding audio: {e}")
        return None

# Translate the decoded message using Gemini API
def translate_message(message):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Translate AI communication to human language: {message}")
        return response.text
    except Exception as e:
        st.error(f"Error translating message: {e}")
        return "[Translation Error]"

# Audio callback function for capturing audio data
def callback(indata, frames, time, status, audio_queue):
    if status:
        st.warning(f"Stream status: {status}")
    audio_queue.put(indata.copy())

# Streamlit interface setup
def main():
    # Initialize systems
    wave = initialize_systems()
    if not wave:
        st.stop()

    audio_queue = queue.Queue()

    st.title("GibberLink Translator")
    st.subheader("Listen to AI Agents' Communication and Translate")

    # Use columns for layout
    col1, col2 = st.columns([3, 1])

    with col1:
        listening = st.button("Start Listening")
        stop_listening = st.button("Stop Listening")
    
    with col2:
        st.image("your_icon_path.png", width=100)  # Add an icon or image for visual appeal

    if listening:
        with sd.InputStream(callback=lambda indata, frames, time, status: callback(indata, frames, time, status, audio_queue), 
                            samplerate=44100, channels=1, dtype='int16'):
            st.write("Listening... Please wait.")
            progress_bar = st.progress(0)
            while not stop_listening:
                if not audio_queue.empty():
                    audio_data = audio_queue.get()
                    decoded_msg = decode_audio(audio_data, wave)
                    if decoded_msg:
                        translation = translate_message(decoded_msg)
                        st.write(f"**AI:** {decoded_msg}")
                        st.write(f"**Translated:** {translation}")
                    progress_bar.progress(50)  # Update progress as per the task progress
                else:
                    st.write("Awaiting audio data...")
            progress_bar.progress(100)  # Complete progress bar when done
    else:
        st.write("Press 'Start Listening' to begin capturing audio.")

if __name__ == "__main__":
    main()
