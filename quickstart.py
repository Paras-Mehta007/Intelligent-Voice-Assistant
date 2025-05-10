
import speech_recognition as sr
import os
import subprocess
import webbrowser
import datetime
import random
import platform
from gtts import gTTS
import playsound
import re

# Google Calendar API   imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Google Calendar API scope
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

class VoiceAssistant:
    def __init__(self, name="Assistant"):
        self.name = name
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.calendar_creds = None
        self._init_calendar()
        self.speak(f"Hello, I am {self.name}. How can I help you?")


    
    def _init_calendar(self):
        if os.path.exists("token.json"):
            self.calendar_creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not self.calendar_creds or not self.calendar_creds.valid:
            if self.calendar_creds and self.calendar_creds.expired and self.calendar_creds.refresh_token:
                self.calendar_creds.refresh(Request())
            else:
                if os.path.exists("credentials.json"):
                    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                    self.calendar_creds = flow.run_local_server(port=0)
                    with open("token.json", "w") as token:
                        token.write(self.calendar_creds.to_json())
    
    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = self.recognizer.listen(source)
        try:
            print("Recognizing...")
            command = self.recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except (sr.UnknownValueError, sr.RequestError):
            print("Sorry, I couldn't understand that.")
            return ""
    




    def speak(self, text):
        print(f"{self.name}: {text}")
        tts = gTTS(text=text, lang='en')
        temp_file = "temp_voice.mp3"
        tts.save(temp_file)
        playsound.playsound(temp_file)
        os.remove(temp_file)
    
    def get_calendar_events(self, max_results=3):
        if not self.calendar_creds:
            return "Calendar not available. Please set up credentials."
        try:
            service = build("calendar", "v3", credentials=self.calendar_creds)
            now = datetime.datetime.utcnow().isoformat() + "Z"
            events_result = service.events().list(calendarId="primary", timeMin=now,
                                                 maxResults=max_results, singleEvents=True,
                                                 orderBy="startTime").execute()
            events = events_result.get("items", [])
            if not events:
                return "No upcoming events found."
            response = "Here are your upcoming events: "
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                if "T" in start:
                    start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                    formatted_date = start_dt.strftime("%A, %B %d at %I:%M %p")
                else:
                    start_dt = datetime.datetime.fromisoformat(start)
                    formatted_date = start_dt.strftime("%A, %B %d")
                response += f"{event['summary']} on {formatted_date}. "
            return response
        except HttpError as error:
            return f"Calendar error: {error}"
    
    def process_command(self, command):
        if not command:
            return "I didn't catch that. Please repeat?"
        
        if any(word in command for word in ["hello", "hi", "hey"]):
            return random.choice(["Hello! How can I help?", "Hi there!", "Hey! I'm listening."])
        elif "time" in command:
            return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}"
        elif "date" in command or "day" in command:
            return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}"
        elif "open" in command:
            app = re.search(r'open\s+(.*)', command).group(1).strip() if re.search(r'open\s+(.*)', command) else None
            if app:
                system = platform.system()
                try:
                    if system == "Windows": os.startfile(app)
                    elif system == "Darwin": subprocess.call(["open", "-a", app])
                    elif system == "Linux": subprocess.call([app])
                    return f"Opening {app}"
                except Exception as e:
                    return f"Couldn't open {app}: {e}"
            return "What application should I open?"
        elif "search" in command or "google" in command:
            query = re.search(r'search\s+(?:for\s+)?(.*)', command).group(1).strip() if re.search(r'search\s+(?:for\s+)?(.*)', command) else None
            if query:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                return f"Searching for {query}"
            return "What should I search for?"
        elif "calendar" in command or "events" in command or "schedule" in command:
            return self.get_calendar_events()
        elif any(word in command for word in ["exit", "quit", "goodbye", "bye"]):
            self.speak("Goodbye! Have a great day!")
            exit()
        else:
            return "I'm not sure how to help with that. Try asking for help."
    
    def run(self):
        while True:
            command = self.listen()
            response = self.process_command(command)
            self.speak(response)




if __name__ == "__main__":
    assistant = VoiceAssistant("Assistant")
    assistant.run()
