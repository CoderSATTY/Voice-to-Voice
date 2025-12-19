import pyautogui
import screen_brightness_control as sbc
import os
import subprocess
import time
import platform
from speech import speak
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import webbrowser
import urllib.parse
import requests

class SystemControl:
    def __init__(self):
        self.os = platform.system()
        if self.os == "Windows":
            self._initialize_volume_control()

    def _initialize_volume_control(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

    def take_screenshot(self, filename="screenshot.png"):
        pyautogui.screenshot(filename)
        speak(f"[INFO] Screenshot saved as {filename}")

    def set_volume(self, level):
        if self.os=="Windows":
            level = max(0, min(100,level))/100
            self.volume.SetMasterVolumeLevelScalar(level, None)
            speak(f"[INFO] Volume set to {int(level*100)}%")
        else:
            speak("[ERROR] Volume control not implemented..")
    
    def mute_volume(self):
        if self.os == "Windows":
            speak("[INFO] Muting Volume..")
            self.volume.SetMute(1,None)
    
    def unmute_volume(self):
        if self.os=="Windows":
            self.volume.SetMute(0,None)
            speak("[INFO] Volume unmuted..")

    def set_brightness(self,level):
        level = max(0, min(100,level))
        sbc.set_brightness(level)
        speak(f"[INFO] Brightness set to {level}%")
 
    def toggle_gui(self):
        pyautogui.hotkey('win','a')
        time.sleep(1)
        pyautogui.moveTo(1800,800, duration=0.2)
        pyautogui.click()
        time.sleep(0.5)
        pyautogui.hotkey('win','a')
    def forward(self, intent, params):
        intent = intent.lower()
        params = params
        print("Parameters received:", params)
        if intent == "set_volume":
            level = params.get("volume_level", 50)  # Default volume level is 50%
            self.set_volume(level)

        elif intent == "mute_volume":
            self.mute_volume()

        elif intent == "unmute_volume":
            self.unmute_volume()

        elif intent == "adjust_brightness":
            level = params.get("brightness_level", 50)  # Default brightness level is 50%
            self.set_brightness(level)

        elif intent == "take_screenshot":
            filename = params.get("filename", "screenshot.png")  # Default filename
            self.take_screenshot(filename)
        else:
            print(f"[ERROR] Unknown intent: {intent}")
# s = SystemControl()
# s.set_volume(60)
# s.mute_volume()
# s.unmute_volume()
# s.take_screenshot()
# s.toggle_gui()
# s.set_brightness(10)

class BrowserAssistant:
    def __init__(self):
        self.sites = {
            "chatgpt" : "chat.openai",
            "colab" : "colab.research.google",
            "twitter" : "x",
            "google maps" : "maps.google",
            "gmail" : "mail.google",
            "google drive" : "drive.google",
            "google docs" : "docs.google",
            "stack overflow" : "stackoverflow",
            "telegram" : "web.telegram",
            "wikipedia" : "en.wikipedia",

        }
        self.browser = webbrowser.get(using='windows-default')

    def open(self, site):
        site = site.lower()
        guessed_url = f"https://www.{site}.com"
        try:
            r  = requests.head(guessed_url, timeout = 3)
            if r.status_code < 400:
                print(f"Guessed and opened: {guessed_url}")
                speak(f"Opening {site}...")
                self.browser.open(guessed_url)
                return
        except requests.RequestException:
            if site in self.sites.keys():
                try:
                    url = f"https://{self.sites[site]}.com"
                    self.browser.open(url)
                    return
                except Exception as e:
                    speak("Not found in directories... ")
            else:
                self.search(site)

    def search(self,phrase):
        try:
            url = f"https://www.google.com/search?q={phrase}"
            speak(f"Searching for {phrase} on Google...")
            self.browser.open(url)
        except Exception as e:
            speak(f"Error found, cant execute: {e}")
    def forward(self, intent, params):
        if intent == "open_website":
            site = params.get("site_name", "")
            self.open(site)
        elif intent == "search_web":
            phrase = params.get("search_query", "")
            self.search(phrase)
        else:
            speak(f"[ERROR] Unknown intent: {intent}")

# br = BrowserAssistant()
# br.open("Twitter")
# br.search("Python programming")
# br.open("Colab")
# br.open("Linkedin")
# br.open("Whatsapp")
# br.open("Telegram")
