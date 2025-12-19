import speech_recognition as sr
import datetime
import time
import os
import webbrowser
import platform
import subprocess
import psutil 
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pywhatkit
from googleapiclient.discovery import build
from typing import Optional
from dotenv import load_dotenv
from speech import speak
import cv2
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
load_dotenv() 

class Spotify:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri="http://localhost:8888/callback",
            scope="user-modify-playback-state user-read-playback-state user-read-currently-playing"
        ))
        self.spotify_process = None

    def open_spotify(self):
        speak("Opening Spotify.")
        try:
            system = platform.system()
            if system == "Windows":
                os.system("start spotify:")
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", "Spotify"])
            elif system == "Linux":
                subprocess.Popen(["spotify"])
            else:
                raise Exception("Unsupported OS")
            
            print("Opened Spotify app.")
            return True
        except Exception as e:
            print(f"Failed to open Spotify app locally: {e}")
            print("Opening Spotify in browser...")
            webbrowser.open("https://open.spotify.com")
            return False
    def close_spotify(self):
        """
        Close Spotify app (Windows only for now).
        """
        try:
            closed = False
            for proc in psutil.process_iter(['pid', 'name']):
                if "spotify" in proc.info['name'].lower():
                    proc.kill()
                    closed = True
            if closed:
                print("Spotify closed.")
            else:
                print("Spotify app not running.")
        except Exception as e:
            print(f"Error closing Spotify: {e}")        
    def wait_for_active_device(self, timeout=10):
        """
        Waits for an active Spotify device.
        """
        for _ in range(timeout):
            devices = self.sp.devices()
            if devices['devices']:
                return devices['devices'][0]['id']
            print("Waiting for Spotify device to activate...")
            time.sleep(5)
        print("No active device found.")
        return None
    
    def close_spotify(self):
        try:
            speak("Spotify closed.")
        except Exception as e:
            speak(f"Error closing Spotify: {e}")

    def play_on_spotify(self, song_name, artist_name, album_name):

        try:
            device_id = self.wait_for_active_device()

            if not device_id:
                print("No active device found. Please start Spotify manually.")
                return

            query = song_name
            if artist_name != "None":
                query += f' by {artist_name}'
            if album_name != "None":
                query += f' from {album_name}'

            print(f"query: {query}")
            results = self.sp.search(q=query, type='track', limit=1)

            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                self.sp.start_playback(device_id=device_id, uris=[track_uri])
                print(f"Playing '{song_name}' by {artist_name or 'Unknown Artist'} on Spotify.")
            else:
                print(f"Song '{song_name}' not found.")
        except Exception as e:
            print(f"Error playing song '{song_name}': {e}")

    def pause_spotify(self):
        self.sp.pause_playback()
        time.sleep(0.5)   
       
        current_playback = self.sp.current_playback()
        if current_playback and current_playback['is_playing']:
            speak("Couldn't pause the music. Trying again...")
            self.sp.pause_playback() 
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

    def forward(self, intent, params):
        
        try:
            intent, params = intent.lower(), params 
            print(f" Parameters: {params}")
            if intent == "open_app":
                self.open_spotify()

            elif intent == "play_spotify":
                song = params.get("media_name", "")
                artist = params.get("artist_name", "")
                album = params.get("album_name", "")
                print(f" Song: {song}")
                if song:
                    self.play_on_spotify(song, artist_name=artist, album_name=album)
                else:
                    speak("Please specify a song name to play.")
            elif intent == "pause_spotify":
                self.pause_spotify()
            elif intent == "resume_spotify":
                self.resume_spotify()
            elif intent == "next_song":
                self.next_song()
            elif intent == "app_close":
                self.close_spotify()
        except Exception as e:
            print(f"Error in tool_name: {e}")
            return


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
        speak("Opening YouTube.")
        try:
            webbrowser.open("https://www.youtube.com")
            print("Opened YouTube successfully!")
            return True
        except Exception as e:
            print(f"Failed to open YouTube: {e}")
            return False
    
    def open_and_play_video(self, video_name, cc_name):
        input_video = f"{video_name} by {cc_name}"
        try:
            speak(f"Opening Youtube and playing {input_video}.")
            pywhatkit.playonyt(input_video)
            self.current_video = input_video
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
    
    def get_trending_videos(self, region_code: str = "IND", max_results: int = 10) -> list:
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
    
    def forward(self, intent, params):
        try:
            intent, params = intent.lower(), params 
            print(f" Parameters: {params}")
            if intent == "open_app":
                self.open_youtube()
            elif intent == "open_and_play_media":
                video = params.get("media_name", "")
                cc = params.get("content_creator", "")
                print(f" Media: {video}")
                if video:
                    self.open_and_play_video(video, cc_name=cc)
                else:
                    speak("Please specify a song name to play.")
            elif intent == "search_youtube":
                query = params.get("query", "")
                self.search_videos(query)
            elif intent == "get_trending_media":
                self.get_trending_videos()
            elif intent == "app_close":
                self.close_youtube()
        except Exception as e:
            print(f"Error in tool_name: {e}")
            return


class Camera:
    def __init__(self, camera_index=0, output_dir="captures"):
        self.camera_index = camera_index
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.cap = None

    def click_picture(self, filename="capture.png"):
        self.cap = cv2.VideoCapture(self.camera_index)
        ret, frame = self.cap.read()
        if ret:
            filepath = os.path.join(self.output_dir, filename)
            cv2.imwrite(filepath, frame)
            speak(f"Picture saved as {filename}")
        else:
            speak("Failed to access camera.")
        self.cap.release()

    def close_camera(self):
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            speak("Camera closed.")

    def forward(self, intent, params):
        try:
            intent = intent.lower()
            print(f" Parameter: {params}")

            if intent == "click_picture":
                filename = params.get("filename", "capture.png")
                self.click_picture(filename)

            elif intent == "close_camera":
                self.close_camera()

        except Exception as e:
            speak(f"Error in Camera forward(): {e}")


class Calendar:
    def get_today(self):
        today = datetime.datetime.now()
        return today.strftime("%d %B %Y")  

    def get_day_for_date(self, date_str):
        date_str = date_str.strip().lower()
        date_str = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)  

        possible_formats = [
            "%Y-%m-%d",
            "%d %B %Y",
            "%d %b %Y",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%d/%m/%y",
            "%d-%m-%y",
            "%B %d %Y",
            "%b %d %Y",
            "%d %B, %Y",
        ]

        for fmt in possible_formats:
            try:
                parsed_date = datetime.datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%A") 
            except ValueError:
                continue
        return "Invalid date format. Try formats like '8 June 2025' or '08-06-25'."

    def forward(self, intent, params):
        try:
            intent = intent.lower()
            print(f" Parameter: {params}")

            if intent == "get_today":
                formatted_date = self.get_today()
                speak(f"Today's date is {formatted_date}")

            elif intent == "get_day_for_date":
                date_str = params.get("date", "")
                day = self.get_day_for_date(date_str)
                speak(f"The day for {date_str} is {day}")

        except Exception as e:
            speak(f"Error in Calendar forward(): {e}")


class Clock:
    def __init__(self):
        pass

    def tell_time(self):
        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M %p")
        speak(f"The current time is {current_time}")

    def forward(self, intent, params):
        intent = intent.lower()
        try:
            if intent == "get_time":
                self.tell_time()
            else:
                speak("Sorry, I don't recognize that clock command.")
        except Exception as e:
            speak(f"Error in Clock forward: {e}")

#Webcam

class Webcam:
    def __init__(self,camera_index=0, output_dir="captures"):
        self.camera_index = camera_index
        self.output_dir = output_dir
        self.cap = None
        os.makedirs(self.output_dir, exist_ok=True)

    def open(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                speak("Webcam could not be opened")
                raise Exception("Webcam could not be opened")
            else:
                speak("Opening Webcam...")
    def close(self):
        if self.cap:
            self.cap.release()
            self.cap= None
            speak("Closing Webcam...")            
    def take_picture(self, delay=3, filename=None):
        self.open()        
        if delay>0:
            speak(f"[INFO] Waiting {delay} seconds before taking picture")
            time.sleep(delay)
        ret, frame = self.cap.read()
        if ret:
            filename = filename or f"{self.output_dir}/photo_{self._timestamp()}.jpg"
            cv2.imwrite(filename, frame)
            speak(f"[INFO] Picture saved at {filename}")
            self.close()
            return filename 
        else:
            speak("Failed to capture images.")
            raise Exception("Failed to capture images.")
        
        self.close()
        
    def record_video(self, delay=3, filename=None, fps=30.0):
        self.open()
        if delay>0:
            speak(f"[INFO] Waiting {delay} seconds before recording video.")
            time.sleep(delay)

        filename = filename or f"{self.output_dir}/video_{self._timestamp()}.avi"
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(filename, fourcc, fps, (width,height))

        speak(f"[INFO] Recording.... Press any key to stop")  

        while True:
            ret, frame = self.cap.read()
            if ret:
                out.write(frame)
                cv2.imshow("Recording... ", frame)

                if cv2.waitKey(1) != -1:
                    speak("[INFO] Key pressed. Ending Recording")
                    break
            else:
                speak("[WARNING] Frame capture failed.")
                break
        
        out.release()
        cv2.destroyAllWindows()
        self.close()
        speak(f"[INFO] Video saved at {filename}")
        return filename 
    

    
    def _timestamp(self):
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    def forward(self, intent, params):
        try:
            intent = intent.lower()
            print(f" Parameters: {params}")

            if intent == "take_picture":
                delay = params.get("delay_seconds", 3)
                filename = params.get("filename", None)
                self.take_picture(delay=delay, filename=filename)

            elif intent == "take_video":
                delay = params.get("delay_seconds", 3)
                filename = params.get("filename", None)
                fps = params.get("fps", 30.0)
                self.record_video(delay=delay, filename=filename, fps=fps)

        except Exception as e:
            print(f"Error in Webcam forward(): {e}")






