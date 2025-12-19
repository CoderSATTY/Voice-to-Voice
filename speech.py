import speech_recognition as sr
import datetime
import os
import uuid
import base64
import time
from gtts import gTTS 
import io             

_socketio = None

def set_socketio_instance(sio):
    global _socketio
    _socketio = sio

def speak(audio_text):

    if not _socketio:
        print(f"(No client) Assistant would say: {audio_text}")
        return

    def generate_and_send_utterance():
        print(f"-> Generating TTS for: '{audio_text}'")
        try:
            tts = gTTS(text=audio_text, lang='en', slow=False)
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0) 
            

            audio_data = mp3_fp.read()
            b64_audio = base64.b64encode(audio_data).decode('utf-8')
     
            payload = {
                'text': audio_text,
                'audio': b64_audio
            }
            

            print(f"-> Sending combined utterance for: '{audio_text}'")
            _socketio.emit('assistant_utterance', payload)

        except Exception as e:
            print(f"[ERROR] An exception occurred in the gTTS background task: {e}")

    _socketio.start_background_task(target=generate_and_send_utterance)


def takecommand():

    r = sr.Recognizer()
    with sr.Microphone() as source:
        if _socketio: 
            _socketio.emit('status_update', {'data': 'Listening...'})
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=15, phrase_time_limit=10)
            if _socketio: 
                _socketio.emit('status_update', {'data': 'Recognizing...'})
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            
            print(f"User said: {query}")
            if _socketio: 
                _socketio.emit('user_query', {'data': query})
            return query.lower()
        except Exception as e:
            print(f"STT Error: {e}")
            return None

def wish():
    hour = datetime.datetime.now().hour
    greet="Hello"
    if 0 <= hour < 12:
        greet = "Good morning"
    elif 12 <= hour < 18:
        greet = "Good afternoon"
    else:
        greet = "Good evening"
    speak(f"{greet}! I am Voiz AI. How can I assist you today?")
