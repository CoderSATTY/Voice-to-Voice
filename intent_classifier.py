import anthropic
import json
from dotenv import load_dotenv
import os

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("CLAUDE_API_KEY")
)
with open("src/system_prompt.txt", "r", encoding="utf-8") as file:
    system_prompt = file.read()

def intent_identifier(query):
  user_query = query
  try:
      response = client.messages.create(
          model="claude-3-haiku-20240307",
          max_tokens=400,
          system=system_prompt,
          messages=[{"role": "user", "content": user_query}]
      )
      # print(response)
      raw_output = response.content[0].text
      tasks = json.loads(raw_output)

      print(json.dumps(tasks, indent=2))
      return tasks
  except json.JSONDecodeError:
      print("Failed to parse JSON from:")
  except Exception as e:
      print(f"Unexpected error: {str(e)}")

# intent_identifier("open spotify and play fein on a volume level of 80 and then close the app.")
# intent_identifier("Play the song 'Shape of You' on Spotify at 70% volume and then close Spotify.")
# intent_identifier("Open Youtube and play a video, then open Spotify and play a song at 50% volume.")
# intent_identifier("Play now you see me trailer on youtube at 50 percent volume and then open spotify and play chamak chalo.")
# intent_identifier("Open spotify and youtube on 50 percent volume.")
# intent_identifier("Open youtube and play meherbaan")
# intent_identifier("take picture only after camera is opened")
# intent_identifier("Open youtube and play vijay mallyas podcast , then open spotify and play chamak chalo at 50 percent volume.")
