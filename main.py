import datetime
import speech as spc
from spotify_filexp_yt import Spotify, YouTube, open_local_files
from speech import speak, takecommand, wish

# Initialize the TTS engine
# engine = pyttsx3.init('sapi5')
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[0].id)

spotify_instance = Spotify()
youtube_instance = YouTube()

def wish():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good morning sir!")
    elif 12 <= hour < 18:
        speak("Good afternoon sir!")
    else:
        speak("Good evening sir!")
    speak("Hello, I am Lodu. How can I assist you today?")
 
def continue_or_not():
    print("Please say 'Goodbye' if you want to exit")
    speak("Say \"continue\" to continue.")
    query = takecommand().lower()
    if any(word in query for word in ["good", "bye", "goodbye"]):
        speak("Okay, bye bye. Have a nice day!")
        return False
    elif query == "continue":
        return True

if __name__ == "__main__":
    wish()
    while True:
        query = takecommand()

        if "open" and "file explorer" in query:
            open_local_files()
        elif "open" and "spotify" in query:
            spotify_instance.open_spotify()
            spotify_instance.forward()
        elif "open" and "youtube" in query:
            youtube_instance.open_youtube()
            youtube_instance.forward()
        
        want_answer = continue_or_not()
        if not want_answer:
            break
        elif want_answer:
            speak("What else shall I do?")