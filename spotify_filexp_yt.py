import speech_recognition as sr
import datetime
import os
import webbrowser
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pywhatkit
from googleapiclient.discovery import build
from typing import Optional
from dotenv import load_dotenv
from speech import speak, takecommand
load_dotenv() 

# Spotify Class (unchanged)
class Spotify:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri="http://localhost:8888/callback",
            scope="user-modify-playback-state user-read-playback-state"
        ))
        self.spotify_process = None
    

    def open_spotify(self):
        speak("Opening Spotify. What would you like to listen to?")

        try:
            webbrowser.open("https://open.spotify.com")
            print("Opened Spotify successfully!")
            return True
        except Exception as e:
                print(f"Failed to open Spotify: {e}")
                return False

    def close_spotify(self):
        try:
            speak("Spotify closed.")
        except Exception as e:
            speak(f"Error closing Spotify: {e}")

    def play_on_spotify(self, song_name):
        try:
            results = self.sp.search(q=song_name, limit=1)
            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                self.sp.start_playback(uris=[track_uri])
                speak(f"Playing {song_name} on Spotify.")
            else:
                speak(f"Sorry, I couldn't find {song_name} on Spotify.")
        except Exception as e:
            print(f"Error playing song: {song_name}")
            speak(f"Sorry, there was an error playing your song. Can you repeat?")
    def pause_spotify(self):
        # Pause the playback
        self.sp.pause_playback()
        time.sleep(0.5)  # Small delay to ensure yt_query registers    
        # Verify it was paused
        current_playback = self.sp.current_playback()
        if current_playback and current_playback['is_playing']:
            speak("Couldn't pause the music. Trying again...")
            self.sp.pause_playback()  # Try one more time
            time.sleep(0.5)
        else:
            speak("Music paused.")

    def resume_spotify(self):
        try:
            self.sp.start_playback()
            speak("Music resumed.")
        except Exception as e:
            speak(f"Error resuming music: {e}")

    def next_song(self):
        try:
            self.sp.next_track()
            speak("Skipping to the next track.")
        except Exception as e:
            speak(f"Error skipping track: {e}")

    def set_volume(self, level):
        try:
            if 0 <= level <= 100:
                self.sp.volume(level)
                speak(f"Volume set to {level}%.")
            else:
                speak("Please set volume between 0 and 100.")
        except Exception as e:
            speak(f"Error setting volume: {e}")

    def forward(self):
        while True:
            song_query = takecommand()
            try:   
                if "play" in song_query:
                    song_name = song_query.replace("play", "").strip()
                    self.play_on_spotify(song_name)

                elif "pause" in  song_query and song_query:
                    self.pause_spotify()
                elif "resume" in  song_query and song_query:
                    self.resume_spotify()
                elif "next" in song_query and "song" in  song_query:
                    self.next_song()
                elif "volume" in song_query in song_query:
                    try:
                        level = int(song_query.split()[-1])
                        self.set_volume(level)
                    except:
                        speak("Please specify a volume level between 0 and 100")
                elif "close" and "spotify" in song_query:
                    self.close_spotify()
                    break
                else:
                    print("Command not recognized")
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that")
            except sr.RequestError:
                print("Speech service unavailable")
            except Exception as e:
                print(f"Error: {e}")


# Updated YouTube Class using google-api-python-client
class YouTube:
    def __init__(self):
        """
        Initialize YouTube controller with Google API client
        """
        api_key = os.getenv("YOUTUBE_API_KEY")
        if api_key:
            self.youtube = build('youtube', 'v3', developerKey=api_key)
        else:
            self.youtube = None
        self.current_video = None
        
    def open_youtube(self):
        speak("Opening YouTube. What would you like me to do?")
        try:
            webbrowser.open("https://www.youtube.com")
            print("Opened YouTube successfully!")
            return True
        except Exception as e:
            print(f"Failed to open YouTube: {e}")
            return False
    
    def play_video(self, video_name):
        try:
            speak(f"Now playing {video_name}.")
            pywhatkit.playonyt(video_name)
            self.current_video = video_name
            return True
        except Exception as e:
            print(f"Error playing video: {e}")
            return False
    
    def search_videos(self, query: str, max_results: int = 5) -> list:
        """
        Search for videos using YouTube API
        Returns list of video results
        """
        if not self.youtube:
            print("YouTube API not initialized")
            return []
            
        try:
            speak(f"Searching for {query}.")
            request = self.youtube.search().list(
                q=query,
                part="id,snippet",
                maxResults=max_results,
                type="video"
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                videos.append({
                    'title': item['snippet']['title'],
                    'id': video_id,
                    'url': f"https://youtube.com/watch?v={video_id}",
                    'channel': item['snippet']['channelTitle']
                })
            return videos
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_trending_videos(self, region_code: str = "US", max_results: int = 10) -> list:
        """
        Get trending videos using YouTube API
        """
        if not self.youtube:
            print("YouTube API not initialized")
            return []
            
        try:
            speak("These are the current Trending YouTube Videos")
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                chart="mostPopular",
                regionCode=region_code,
                maxResults=max_results
            )
            response = request.execute()
            
            trending = []
            for item in response.get('items', []):
                trending.append({
                    'title': item['snippet']['title'],
                    'id': item['id'],
                    'url': f"https://youtube.com/watch?v={item['id']}",
                    'views': item['statistics'].get('viewCount', 'N/A'),
                    'channel': item['snippet']['channelTitle']
                })
            return trending
        except Exception as e:
            print(f"Error getting trending videos: {e}")
            return []
    
    def close_youtube(self):
        try:
            speak("YouTube closed.")
        except Exception as e:
            speak(f"Error closing YouTube: {e}")
    
    def forward(self):
        while True:
            yt_query = takecommand()
            try:
                if "play" in yt_query:
                    video_name = yt_query.replace("play", "").strip()
                    self.play_video(video_name)

                elif "search" in yt_query:
                    query = yt_query.replace("search", "").strip()
                    results = self.search_videos(query)
                    for i, video in enumerate(results[:3], 1):
                        print(f"{i}. {video['title']}")

                elif "trending" in yt_query:
                    videos = self.get_trending_videos()
                    for i, video in enumerate(videos[:5], 1):
                        print(f"{i}. {video['title']}")

                elif "close" in yt_query:
                    self.close_youtube()
                    print("Closing YouTube")
                    break
                else:
                    print("Command not recognized")
                        
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that")
            except sr.RequestError:
                print("Speech service unavailable")
            except Exception as e:
                print(f"Error: {e}")
                

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
# Class FileExplorer
def open_local_files():
    speak("Opening File Explorer.")
    os.system("explorer")




