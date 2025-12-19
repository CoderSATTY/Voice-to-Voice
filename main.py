from flask import Flask
from flask_socketio import SocketIO, emit
from agent_tools.app_tools import Spotify, YouTube, Webcam
from agent_tools.system_tools import SystemControl, BrowserAssistant
from intent_classifier import intent_identifier
import speech
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, 'agent_tools', '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
speech.set_socketio_instance(socketio)

tools = {
    "spotify": Spotify(),
    "youtube": YouTube(), 
    "systemcontrol": SystemControl(),
    "browserassistant": BrowserAssistant(), 
    "webcam": Webcam()
}
print("All backend tools initialized.")

def process_query(query):
    """Processes a recognized query, identifies intents, and executes tasks."""
    print(f"Processing query: '{query}'")
    try:
        task_list = intent_identifier(query)
        tool_list = task_list[-1].get("total_functions", "").split(", ")
            
        if not task_list:
            speech.speak("I'm sorry, I could not determine the task. Please try again.")
            return
 
        for i in range(len(tool_list)):
            task = task_list[i]
            intent = task.get("intent_function", "").lower()
            tool_name = task.get("tool_used", "").lower()
            params = task.get("parameters", {})
            
            tool_instance = tools.get(tool_name)
            if tool_instance:
                print(f"Executing: tool='{tool_name}', intent='{intent}', params={params}")
                tool_instance.forward(intent, params)
            else:
                continue 
    except Exception as e:
        print(f"[ERROR] An exception occurred during query processing: {e}")
        speech.speak("I encountered an error while processing your request.")

@socketio.on('connect')
def handle_connect():
    print("Client connected successfully.")

@socketio.on('start_assistant')
def handle_start_assistant():
    """Triggered by the 'Initialize System' button. This is non-blocking."""
    print("-> Event 'start_assistant' received. Running wish().")
    speech.wish()

@socketio.on('trigger_take_command')
def handle_take_command():
    """
    Triggered by the 'Speak' button.
    This handler now starts a background task and returns immediately,
    keeping the server responsive.
    """

    def listen_and_process():
        """This function will run in the background."""
        print("-> Background task started for STT and processing.")

        query = speech.takecommand()

        if query:
            process_query(query)
        else:
            speech.speak("I didn't quite catch that. Please try again.")

    print("-> Event 'trigger_take_command' received. Starting background task.")
    socketio.start_background_task(target=listen_and_process)


if __name__ == '__main__':
    print("Starting Voiz AI WebSocket server...")
    socketio.run(app, port=5000)