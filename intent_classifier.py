import openai
from dotenv import load_dotenv
import os
import anthropic
import json

load_dotenv()


# Initialize the Anthropic client
client = anthropic.Anthropic(
    api_key=os.getenv("CLAUDE_API_KEY")
  # Replace with your key
)

# System prompt (same structure as GPT-4 example)
system_prompt = """
You are a task automation assistant. Your job is to:
1. Classify intents in the user's query (e.g., App_Launch, Media_Play, Volume_Adjust, App_Close).
2. Extract parameters (e.g., app names, song titles, volume levels).
3. Return a VALID JSON array where each object has:
   - "intent" (the classified action)
   - "parameters" (key-value pairs for execution)

Rules:
- Be concise. No explanations.
- Use this intent taxonomy:
  - App_Launch: Opening apps (e.g., "Open Spotify")
  - Media_Play: Playing media (e.g., "Play Fein")
  - Volume_Adjust: Changing volume (e.g., "Set volume to 80")
  - App_Close: Closing apps (e.g., "Close Spotify")
"""

# User query (multi-task example)
user_query = "open spotify play fein on a volume level of 80 and then close the app"

# Call Claude Haiku (free tier)
try:

    response = client.messages.create(
        model="claude-3-haiku-20240307",  # Free model
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_query}
        ]
    )
# Parse and execute tasks
    tasks = json.loads(response.content[0].text.strip())
    
    if not isinstance(tasks, list):
        raise ValueError("Expected a JSON array")
        
    print("Structured Tasks:")
    print(json.dumps(tasks, indent=2))
    
    print("\nExecution:")
    for task in tasks:
        intent = task.get("intent", "").lower()
        params = task.get("parameters", {})

        try:
            if intent == "app_launch":
                app = params.get("app_name")
                if not app:
                    raise KeyError("Missing 'app_name' in parameters")
                print(f"EXECUTING: Launching {app}...")
                # subprocess.run(["open", "-a", app])  # Uncomment for macOS
                
            elif intent == "media_play":
                song = params.get("song_name")
                if not song:
                    raise KeyError("Missing 'song_name' in parameters")
                print(f"EXECUTING: Playing '{song}'...")
                
            elif intent == "volume_adjust":
                volume = params.get("volume_level")
                if volume is None:
                    raise KeyError("Missing 'volume_level' in parameters")
                print(f"EXECUTING: Setting volume to {volume}%...")
                
            elif intent == "app_close":
                app = params.get("app_name")
                if not app:
                    raise KeyError("Missing 'app_name' in parameters")
                print(f"EXECUTING: Closing {app}...")
                # subprocess.run(["pkill", "-x", app])  # Uncomment for macOS/Linux
                
            else:
                print(f"Unknown intent: {intent}")
                
        except KeyError as e:
            print(f"SKIPPING {intent}: {e}")
            continue
            
except json.JSONDecodeError:
    print("Failed to parse Claude's response as JSON")
    print("Raw output:", response.content[0].text)
except Exception as e:
    print(f"Error: {str(e)}")