// --- START OF FILE r1.js ---

let socket;
let isListening = false;
let audioQueue = [];
let isPlayingAudio = false;

// --- Functions called from HTML ---

function startAssistant(event) {
    if (event) { event.preventDefault(); }
    const silentAudio = 'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=';
    const audio = new Audio(silentAudio);
    const onAudioUnlocked = () => {
        audio.removeEventListener('ended', onAudioUnlocked);
        console.log("Audio context unlocked successfully.");
        document.getElementById('introPage').classList.add('hidden');
        document.getElementById('mainInterface').classList.add('visible');
        document.getElementById('instructionsSection').classList.remove('hidden');
        document.querySelector('.new-session-btn').classList.remove('hidden');
        document.getElementById('messagesContainer').innerHTML = '';
        socket.emit('start_assistant');
    };
    audio.addEventListener('ended', onAudioUnlocked);
    audio.play().catch(e => { onAudioUnlocked(); });
}

function newSession() { location.reload(); }

function toggleSpeaking() {
    if (isListening || isPlayingAudio) { return; }
    isListening = true;
    const speakBtn = document.getElementById('speakBtn');
    const speakBtnText = document.getElementById('speakBtnText');
    speakBtn.classList.add('active');
    speakBtnText.textContent = 'Listening...';
    socket.emit('trigger_take_command');
}

document.addEventListener('DOMContentLoaded', () => {
    socket = io('http://127.0.0.1:5000');
    socket.on('connect', () => console.log('Successfully connected to the backend.'));
    socket.on('user_query', (msg) => {
        // First reset the listening state and UI
        isListening = false;
        const speakBtn = document.getElementById('speakBtn');
        const speakBtnText = document.getElementById('speakBtnText');
        speakBtn.classList.remove('active');
        speakBtnText.textContent = 'Speak';
        
        // Then add the message to the container
        addMessage('user', msg.data);
    });

    socket.on('assistant_utterance', (payload) => {
        console.log("Received combined utterance from backend.");
        
        // 1. Display the text from the payload
        addMessage('assistant', payload.text);
        
        // 2. Add the audio from the payload to the queue
        audioQueue.push(payload.audio);
        isListening = false;
        const speakBtn = document.getElementById('speakBtn');
        const speakBtnText = document.getElementById('speakBtnText');
        speakBtn.classList.remove('active');
        speakBtnText.textContent = 'Speak';       
        // 3. Start the playback loop if it's not already running
        if (!isPlayingAudio) {
            playNextInQueue();
        }
    });

    socket.on('disconnect', () => {
        addMessage('assistant', '[ERROR] Disconnected. Please reload.');
        document.getElementById('speakBtn').disabled = true;
    });
});

function addMessage(sender, text) {
    const messagesContainer = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    const label = sender === 'user' ? 'You' : 'Voiz AI';
    messageDiv.innerHTML = `<div class="message-label">${label}</div><div class="message-text">${text}</div>`;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function playNextInQueue() {
    if (audioQueue.length === 0) {
        isPlayingAudio = false;
        return;
    }
    isPlayingAudio = true;
    const base64Audio = audioQueue.shift();
    const audioSrc = `data:audio/mpeg;base64,${base64Audio}`;
    const audio = new Audio(audioSrc);
    audio.onended = () => { playNextInQueue(); };
    audio.play().catch(e => {
        console.error("Error playing audio:", e);
        isPlayingAudio = false;
        playNextInQueue();
    });
}
