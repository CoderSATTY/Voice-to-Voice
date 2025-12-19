# Voiz AI

**Voiz AI** is an advanced conversational assistant designed with a modular client-server architecture. It bridges the gap between web-based interfaces and local system control, utilizing **WebSockets** for low-latency, real-time speech processing and command execution.

Unlike traditional assistants that rely heavily on generic cloud APIs, Voiz AI processes intents using **Anthropic's Claude 3** and executes dynamic system tasks—from launching applications to controlling hardware—instantly.

---

## 🏗 System Architecture

Voiz AI operates on a **Full-Duplex Communication** model:

1.  **Frontend (Client):** A lightweight web interface captures audio and manages the user state (Listening/Speaking).
2.  **Transport Layer:** Uses **Socket.IO** to maintain a persistent connection, streaming base64-encoded audio data and JSON command payloads bi-directionally.
3.  **Backend (Server):** A **Flask** server managed by **Eventlet** handles concurrent connections.
4.  **Core Logic:**
    * **STT/TTS Engine:** Uses Google Speech Recognition and gTTS for audio conversion.
    * **Intent Classifier:** Leveraging **Claude 3 Haiku** to intelligently map natural language queries to complex JSON task queues.
    * **Tool Manager:** Dynamically routes commands to specific modules (Spotify, System Control, Browser).

---

## 🛠 Tech Stack

| Component | Technologies Used |
| :--- | :--- |
| **Core Framework** | Python 3.10+, Flask |
| **Real-time Communication** | Flask-SocketIO, Eventlet |
| **AI & LLM** | **Anthropic Claude 3 Haiku** (Intent Classification) |
| **Speech Processing** | `SpeechRecognition`, `gTTS` (Google Text-to-Speech) |
| **System Automation** | `PyAutoGUI` (GUI Control), `Pycaw` (Audio/Volume), `Screen-Brightness-Control`, `Psutil` (Process Management) |
| **Web Automation** | `Selenium` (Chrome Automation), `Webbrowser`, `PyWhatKit` (YouTube) |
| **App Integrations** | `Spotipy` (Spotify Web API), `Google API Client` (YouTube Data), `OpenCV` (Webcam) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, Socket.IO Client |

---

## ⚙ Core Features

Voiz AI is built to be an "On-Demand" assistant, activating tools only when required:

* **Intelligent Intent Parsing** – Uses **Claude 3** to understand complex, multi-step commands (e.g., "Open YouTube and play a trailer, then open Spotify at 50% volume").
* **Voice-based System Control** – Adjust volume, screen brightness, and system settings hands-free.
* **Advanced App Control** – Full Spotify integration (Play/Pause/Volume) via **Spotipy** and Browser automation via **Selenium**.
* **Visual Capabilities** – Access and control the webcam using **OpenCV**.
* **Web Search** – Perform instant queries using Google APIs and direct browser automation.
* **Real-time Processing** – Server-side handling ensures consistent performance regardless of client hardware.
* **Natural Interaction** – Designed to minimize latency for a fluid, human-like conversational experience.

---

## 🚀 Installation & Setup

Follow these steps to run Voiz AI locally.

### Prerequisites
* **Operating System:** Windows 10/11 (Required for system audio control via `pycaw`).
* **Python:** Version 3.10 or higher.
* **Hardware:**
    * Microphone and Speakers.
    * Webcam (For computer vision features).
* **Software:**
    * **Google Chrome** (Required for browser automation commands).
* **API Keys:**
    * **Anthropic Account** (Claude API Key).
    * **Spotify Developer Account** (Client ID & Secret).

### 1. Clone the Repository
```bash
git clone https://github.com/CoderSATTY/Voice-to-Voice.git
cd Voice-to-Voice
```
### 2. Install Dependencies
It is recommended to use a virtual environment.
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```
### 3. Environment Variables
Create a .env file in the root directory to store your API keys (required for Spotify):
```bash
SPOTIFY_CLIENT_ID=your_id_here
SPOTIFY_CLIENT_SECRET=your_secret_here
FLASK_SECRET_KEY=voiz-ai-secret
YOUTUBE_API_KEY=your_yt_secret
CLAUDE_API_KEY=your_claude_secret
```
### 4. Run the Application
You need to run the backend server and then launch the frontend interface.
#### <u>Step A: Start the Backend Run the main Python script to initialize the Socket.IO server:</u>
```bash
python main.py
```
The terminal should indicate the server is running.


#### <u>Step B: Launch the Frontend You have two options to open the interface:</u>

**Option 1: Live Server (Recommended for Development)** Open the frontend folder in VS Code, right-click index.html, and select "Open with Live Server". This allows for hot-reloading changes.

**Option 2: Direct Port Access If you have configured** Flask to serve static files, simply open your browser and navigate to: http://127.0.0.1:5000

## 🚀 Demo Video
[![Project Demo Video](https://github.com/CoderSATTY/Voice-to-Voice/blob/main/src/voiz%20ai%20thumbnail.png?raw=true)](https://youtu.be/Raw870zI6Jg?si=ugINMgmyP3aeLUZV)


*Click the thumbnail above to watch the demo video for some insane outputs*


