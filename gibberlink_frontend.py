import streamlit as st
import sounddevice as sd
import queue
import numpy as np
import ggwave
import google.generativeai as genai

# אתחול המערכות
try:
    wave = ggwave.init()
except Exception as e:
    st.error(f"Error initializing ggwave: {e}")
    st.stop()

try:
    genai.configure(api_key="your_gemini_api_key")
except Exception as e:
    st.error(f"Error initializing Gemini API: {e}")
    st.stop()

# תור לאודיו
audio_queue = queue.Queue()

def decode_audio(audio_data):
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

def callback(indata, frames, time, status):
    if status:
        st.warning(f"Stream status: {status}")
    audio_queue.put(indata.copy())

st.title("GibberLink Translator")
st.subheader("Listen to AI Agents' Communication and Translate")

listening = st.button("Start Listening")
stop_listening = st.button("Stop Listening")

if listening:
    with sd.InputStream(callback=callback, samplerate=44100, channels=1, dtype='int16'):
        st.write("Listening...")
        while not stop_listening:
            if not audio_queue.empty():
                audio_data = audio_queue.get()
                decoded_msg = decode_audio(audio_data)
                if decoded_msg:
                    translation = translate_message(decoded_msg)
                    st.write(f"**AI:** {decoded_msg}")
                    st.write(f"**Translated:** {translation}")
