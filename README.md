# gibberlink-translator
GibberLink Translator is a Python-based AI communication listener and translator. It listens to AI agents communicating using the GibberLink protocol, decodes their messages, and translates them into human-readable text using Google Gemini API.

Features

✅ Listens to AI agent conversations in real-time✅ Decodes AI communication using ggwave✅ Translates messages into human language with Gemini AI✅ Provides a Streamlit web interface for easy interaction

Installation

Clone the repository:

git clone https://github.com/yourusername/gibberlink-translator.git
cd gibberlink-translator

Install dependencies:

pip install -r requirements.txt

Set up Gemini API Key:
Replace your_gemini_api_key in the src/backend.py file with your actual API key.

Usage

Run the backend listener:

python src/backend.py

Run the Streamlit web interface:

streamlit run src/frontend.py

Folder Structure

📂 gibberlink-translator  
│── 📂 src  
│   │── backend.py  # Audio listening, decoding & translating  
│   │── frontend.py  # Streamlit UI  
│── 📂 docs  
│   │── README.md  # Project documentation  
│── requirements.txt  # Required Python libraries  
│── .gitignore  # Ignore unnecessary files  

Requirements

Python 3.8+

ggwave

sounddevice

numpy

google-generativeai

streamlit

Contributing

Feel free to submit issues or pull requests to improve the project!

License

MIT License
