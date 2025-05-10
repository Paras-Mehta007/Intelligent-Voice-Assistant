import speech_recognition as sr
import os
import subprocess
import webbrowser
import datetime
import random
import platform
from gtts import gTTS
import playsound
import time
import json
import requests
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import wikipedia
import psutil
import pyjokes
import pyautogui
import wolframalpha
from newsapi import NewsApiClient
import socket
from geopy.geocoders import Nominatim
# from timezonefinder import TimezoneFinder
import pytz
import yfinance as yf
import threading
from pytube import YouTube
import speedtest
import cv2

# Import Google Calendar functionality
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Calendar API scopes
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

class VoiceAssistant:
    def __init__(self, name="Assistant"):
        self.name = name
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000  # Adjust based on your environment
        self.recognizer.dynamic_energy_threshold = True
        
        # API keys (you'll need to replace these with your own)
        self.weather_api_key = "YOUR_OPENWEATHERMAP_API_KEY"
        self.news_api_key = "YOUR_NEWS_API_KEY"
        self.wolfram_app_id = "YOUR_WOLFRAM_ALPHA_APP_ID"
        
        # Email configuration
        self.email = None
        self.email_password = None
        
        # Initialize APIs
        self.news_api = None
        if self.news_api_key != "YOUR_NEWS_API_KEY":
            self.news_api = NewsApiClient(api_key=self.news_api_key)
        
        self.wolfram_client = None
        if self.wolfram_app_id != "YOUR_WOLFRAM_ALPHA_APP_ID":
            self.wolfram_client = wolframalpha.Client(self.wolfram_app_id)
        
        # Initialize Google Calendar credentials
        self.calendar_creds = None
        self.initialize_calendar_creds()
        
        # Settings
        self.wake_word = name.lower()
        self.is_active = True
        self.is_listening = False
        self.continuous_listening = False
        self.volume = 1.0  # Default volume level
        
        # Command history
        self.command_history = []
        self.max_history = 10
        
        # Reminders
        self.reminders = []
        self.reminder_thread = None
        self.start_reminder_checker()
        
        # Greet the user
        self.speak(f"Hello, I am {self.name}, your voice assistant. How can I help you today?")
    
    def initialize_calendar_creds(self):
        """Initialize Google Calendar credentials"""
        if os.path.exists("token.json"):
            self.calendar_creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
        if not self.calendar_creds or not self.calendar_creds.valid:
            if self.calendar_creds and self.calendar_creds.expired and self.calendar_creds.refresh_token:
                self.calendar_creds.refresh(Request())
            else:
                # Adjust the path to your credentials file as needed
                credentials_path = "credentials.json"
                if os.path.exists(credentials_path):
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    self.calendar_creds = flow.run_local_server(port=0)
                    # Save the credentials for the next run
                    with open("token.json", "w") as token:
                        token.write(self.calendar_creds.to_json())
                else:
                    print("Google Calendar credentials file not found.")
    
    def listen(self):
        """Listen for voice commands"""
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = self.recognizer.listen(source)
            
        try:
            print("Recognizing...")
            command = self.recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            
            # Store command in history
            self.command_history.append(command)
            if len(self.command_history) > self.max_history:
                self.command_history.pop(0)
                
            return command
        except sr.UnknownValueError:
            print("Sorry, I didn't understand that.")
            return ""
        except sr.RequestError:
            print("Sorry, my speech service is down.")
            return ""
    
    def speak(self, text):
        """Convert text to speech and play it"""
        print(f"{self.name}: {text}")
        tts = gTTS(text=text, lang='en')
        temp_file = "temp_voice.mp3"
        tts.save(temp_file)
        
        # Play the audio file with adjusted volume
        playsound.playsound(temp_file, block=True)
        
        # Clean up the temporary file
        os.remove(temp_file)
    
    def get_time(self):
        """Get current time"""
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}"
    
    def get_date(self):
        """Get current date"""
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {current_date}"
    
    def open_application(self, app_name):
        """Open an application based on the operating system"""
        system = platform.system()
        
        # Common application names and their executable names
        app_dict = {
            "chrome": "chrome" if system == "Windows" else "Google Chrome",
            "firefox": "firefox",
            "word": "winword" if system == "Windows" else "Microsoft Word",
            "excel": "excel" if system == "Windows" else "Microsoft Excel",
            "powerpoint": "powerpnt" if system == "Windows" else "Microsoft PowerPoint",
            "notepad": "notepad" if system == "Windows" else "TextEdit",
            "calculator": "calc" if system == "Windows" else "Calculator",
            "spotify": "spotify",
            "vlc": "vlc",
            "vscode": "code" if system == "Windows" else "Visual Studio Code"
        }
        
        # Check if app name is in our dictionary
        for key in app_dict:
            if key in app_name.lower():
                app_name = app_dict[key]
                break
        
        try:
            if system == "Windows":
                os.startfile(app_name)
            elif system == "Darwin":  # macOS
                subprocess.call(["open", "-a", app_name])
            elif system == "Linux":
                subprocess.call([app_name])
            return f"Opening {app_name}"
        except Exception as e:
            return f"Sorry, I couldn't open {app_name}. Error: {str(e)}"
    
    def search_web(self, query):
        """Search the web for a query"""
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Here are the search results for {query}"
    
    def get_weather(self, city):
        """Get weather information for a city using OpenWeatherMap API"""
        if self.weather_api_key == "YOUR_OPENWEATHERMAP_API_KEY":
            return "Weather functionality is not available. Please set up your OpenWeatherMap API key."
        
        try:
            # Get coordinates for the city
            geolocator = Nominatim(user_agent="geoapiExercises")
            location = geolocator.geocode(city)
            
            if not location:
                return f"Sorry, I couldn't find the location for {city}."
            
            # Get weather data
            base_url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': location.latitude,
                'lon': location.longitude,
                'appid': self.weather_api_key,
                'units': 'metric'  # Use 'imperial' for Fahrenheit
            }
            
            response = requests.get(base_url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                # Extract weather information
                weather_desc = data['weather'][0]['description']
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']
                
                return (f"Weather in {city}: {weather_desc}. "
                       f"Temperature is {temp}°C, feels like {feels_like}°C. "
                       f"Humidity is {humidity}% and wind speed is {wind_speed} meters per second.")
            else:
                return f"Sorry, I couldn't get weather information for {city}. Error code: {response.status_code}"
        
        except Exception as e:
            return f"An error occurred while getting weather for {city}: {str(e)}"
    
    def get_calendar_events(self, max_results=5):
        """Get upcoming calendar events"""
        if not self.calendar_creds:
            return "Calendar functionality is not available. Please set up Google Calendar credentials."
        
        try:
            service = build("calendar", "v3", credentials=self.calendar_creds)
            
            # Get the upcoming events
            now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
            
            if not events:
                return "You have no upcoming events scheduled."
            
            response = "Here are your upcoming events: "
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                # Format the date and time for better speech
                if "T" in start:  # This is a datetime
                    start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                    formatted_date = start_dt.strftime("%A, %B %d at %I:%M %p")
                else:  # This is a date
                    start_dt = datetime.datetime.fromisoformat(start)
                    formatted_date = start_dt.strftime("%A, %B %d")
                
                response += f"{event['summary']} on {formatted_date}. "
            
            return response
            
        except HttpError as error:
            return f"An error occurred with the calendar: {error}"
    
    def send_email(self, recipient, subject, message):
        """Send an email"""
        if not self.email or not self.email_password:
            return "Email functionality is not set up. Please configure your email credentials."
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            
            # Setup the server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email, self.email_password)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            return f"Email has been sent to {recipient}."
        
        except Exception as e:
            return f"Failed to send email: {str(e)}"
    
    def set_reminder(self, reminder_text, time_str):
        """Set a reminder for a specific time"""
        try:
            # Parse the time string to get a datetime object
            current_date = datetime.datetime.now().date()
            
            # Handle "in X minutes/hours" format
            in_time_match = re.search(r'in (\d+) (minute|minutes|hour|hours)', time_str)
            if in_time_match:
                amount = int(in_time_match.group(1))
                unit = in_time_match.group(2)
                
                reminder_time = datetime.datetime.now()
                if 'minute' in unit:
                    reminder_time += datetime.timedelta(minutes=amount)
                elif 'hour' in unit:
                    reminder_time += datetime.timedelta(hours=amount)
            else:
                # Try to parse a specific time
                time_formats = ["%I:%M %p", "%H:%M"]
                parsed_time = None
                
                for fmt in time_formats:
                    try:
                        parsed_time = datetime.datetime.strptime(time_str, fmt).time()
                        break
                    except ValueError:
                        continue
                
                if not parsed_time:
                    return "I couldn't understand the time format. Please try again with a format like '3:30 PM' or 'in 30 minutes'."
                
                reminder_time = datetime.datetime.combine(current_date, parsed_time)
                
                # If the time is in the past, assume it's for tomorrow
                if reminder_time < datetime.datetime.now():
                    reminder_time += datetime.timedelta(days=1)
            
            # Add the reminder to the list
            self.reminders.append({
                "text": reminder_text,
                "time": reminder_time
            })
            
            # Sort reminders by time
            self.reminders.sort(key=lambda x: x["time"])
            
            formatted_time = reminder_time.strftime("%I:%M %p")
            return f"I'll remind you to {reminder_text} at {formatted_time}."
        
        except Exception as e:
            return f"Failed to set reminder: {str(e)}"
    
    def check_reminders(self):
        """Check for due reminders and announce them"""
        while self.is_active:
            current_time = datetime.datetime.now()
            due_reminders = []
            
            # Check for due reminders
            for reminder in self.reminders:
                if reminder["time"] <= current_time:
                    due_reminders.append(reminder)
            
            # Remove due reminders from the list
            for reminder in due_reminders:
                self.reminders.remove(reminder)
                self.speak(f"Reminder: {reminder['text']}")
            
            # Sleep for a short time before checking again
            time.sleep(10)  # Check every 10 seconds
    
    def start_reminder_checker(self):
        """Start the reminder checker thread"""
        self.reminder_thread = threading.Thread(target=self.check_reminders)
        self.reminder_thread.daemon = True
        self.reminder_thread.start()
    
    def get_news(self, category="general", count=3):
        """Get the latest news headlines"""
        if not self.news_api:
            return "News functionality is not available. Please set up your News API key."
        
        try:
            news = self.news_api.get_top_headlines(category=category, language='en', country='us')
            
            if news['totalResults'] > 0:
                response = f"Here are the top {min(count, len(news['articles']))} {category} news headlines: "
                
                for i, article in enumerate(news['articles'][:count]):
                    response += f"{i+1}. {article['title']}. "
                
                return response
            else:
                return f"Sorry, I couldn't find any {category} news headlines."
        
        except Exception as e:
            return f"An error occurred while getting news: {str(e)}"
    
    def get_wikipedia_info(self, query):
        """Get information from Wikipedia"""
        try:
            # Set the language to English
            wikipedia.set_lang("en")
            
            # Get a summary of the topic
            result = wikipedia.summary(query, sentences=3)  # Limit to 3 sentences
            return result
        except wikipedia.exceptions.DisambiguationError as e:
            options = e.options[:5]  # Limit options to first 5
            return f"There are multiple results for {query}. Did you mean: {', '.join(options)}?"
        except wikipedia.exceptions.PageError:
            return f"Sorry, I couldn't find any information about {query} on Wikipedia."
        except Exception as e:
            return f"An error occurred while searching Wikipedia: {str(e)}"
    
    def get_system_info(self):
        """Get system information"""
        try:
            # Get CPU, memory, and disk information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Format information
            info = (f"System information: CPU usage is {cpu_percent}%. "
                   f"Memory usage: {memory.percent}% used, {memory.available / (1024**3):.2f} GB available. "
                   f"Disk usage: {disk.percent}% used, {disk.free / (1024**3):.2f} GB free.")
            
            # Add battery information if available
            if hasattr(psutil, "sensors_battery") and psutil.sensors_battery():
                battery = psutil.sensors_battery()
                info += f" Battery: {battery.percent}%"
                if battery.power_plugged:
                    info += ", plugged in."
                else:
                    info += f", {battery.secsleft // 60} minutes remaining."
            
            return info
        except Exception as e:
            return f"An error occurred while getting system information: {str(e)}"
    
    def tell_joke(self):
        """Tell a random joke"""
        try:
            joke = pyjokes.get_joke()
            return joke
        except Exception as e:
            return f"Sorry, I couldn't think of a joke right now. Error: {str(e)}"
    
    def take_screenshot(self):
        """Take a screenshot"""
        try:
            screenshot_path = os.path.join(os.path.expanduser("~"), "Desktop", f"screenshot_{int(time.time())}.png")
            img = pyautogui.screenshot()
            img.save(screenshot_path)
            return f"Screenshot saved to {screenshot_path}"
        except Exception as e:
            return f"Failed to take screenshot: {str(e)}"
    
    def set_volume(self, level):
        """Set the assistant's volume level (0.0 to 1.0)"""
        try:
            if 0.0 <= level <= 1.0:
                self.volume = level
                return f"Volume set to {int(level * 100)}%"
            else:
                return "Volume must be between 0 and 100%"
        except Exception as e:
            return f"Failed to set volume: {str(e)}"
    
    def get_ip_address(self):
        """Get the device's IP address"""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Get public IP
            public_ip = requests.get('https://api.ipify.org').text
            
            return f"Your local IP address is {local_ip} and your public IP is {public_ip}"
        except Exception as e:
            return f"Failed to retrieve IP address: {str(e)}"
    
    def translate_text(self, text, target_language):
        """Translate text to another language (requires an API key)"""
        # This is a placeholder - you would need to implement a translation API
        return f"Translation functionality is not implemented yet."
    
    def get_stock_price(self, symbol):
        """Get stock price information"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            if 'regularMarketPrice' in info:
                price = info['regularMarketPrice']
                company_name = info.get('shortName', symbol)
                previous_close = info.get('regularMarketPreviousClose', None)
                
                response = f"The current price of {company_name} ({symbol}) is ${price:.2f}."
                
                if previous_close:
                    change = price - previous_close
                    percent_change = (change / previous_close) * 100
                    direction = "up" if change > 0 else "down"
                    response += f" That's {direction} ${abs(change):.2f} or {abs(percent_change):.2f}% from yesterday's close."
                
                return response
            else:
                return f"Sorry, I couldn't find stock information for {symbol}."
        
        except Exception as e:
            return f"An error occurred while getting stock information: {str(e)}"
    
    # def get_time_in_city(self, city):
    #     """Get the current time in a specific city"""
    #     try:
    #         # Get location coordinates
    #         geolocator = Nominatim(user_agent="geoapiExercises")
    #         location = geolocator.geocode(city)
            
    #         if not location:
    #             return f"Sorry, I couldn't find the location for {city}."
            
    #         # Get timezone from coordinates
    #         tf = TimezoneFinder()
    #         timezone_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
            
    #         if not timezone_str:
    #             return f"Sorry, I couldn't determine the timezone for {city}."
            
    #         # Get current time in that timezone
    #         timezone = pytz.timezone(timezone_str)
    #         city_time = datetime.datetime.now(timezone)
    #         formatted_time = city_time.strftime("%I:%M %p on %A, %B %d")
            
    #         return f"It's currently {formatted_time} in {city}."
        
    #     except Exception as e:
    #         return f"An error occurred while getting time for {city}: {str(e)}"
    
    def answer_question(self, question):
        """Answer general knowledge questions using Wolfram Alpha"""
        if not self.wolfram_client:
            return "I can't answer that question. Wolfram Alpha API is not configured."
        
        try:
            res = self.wolfram_client.query(question)
            if res['@success'] == 'true':
                # Try to get a short answer
                for pod in res.pods:
                    if pod['@title'] == 'Result' or pod['@title'] == 'Definition':
                        for sub in pod.subpods:
                            if hasattr(sub, 'plaintext'):
                                return sub.plaintext
                
                # If no specific result found, get the first available answer
                for pod in res.pods:
                    for sub in pod.subpods:
                        if hasattr(sub, 'plaintext') and sub.plaintext:
                            return f"{pod['@title']}: {sub.plaintext}"
                
                return "I found information, but couldn't extract a clear answer."
            else:
                return "I don't have an answer for that question."
        
        except Exception as e:
            # If Wolfram Alpha fails, try a general response
            return f"I'm not sure about that. Error: {str(e)}"
    
    def download_youtube_audio(self, url):
        """Download audio from a YouTube video"""
        try:
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Assistant_Downloads")
            os.makedirs(output_dir, exist_ok=True)
            
            # Get YouTube video
            yt = YouTube(url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            if not audio_stream:
                return "Sorry, I couldn't find an audio stream for this video."
            
            # Download the audio
            output_file = audio_stream.download(output_path=output_dir)
            
            # Rename to MP3
            base, ext = os.path.splitext(output_file)
            new_file = base + '.mp3'
            os.rename(output_file, new_file)
            
            return f"Audio downloaded from '{yt.title}' and saved to {new_file}"
        
        except Exception as e:
            return f"Failed to download YouTube audio: {str(e)}"
    
    def check_internet_speed(self):
        """Check internet connection speed"""
        try:
            self.speak("Testing your internet speed. This might take a moment...")
            
            st = speedtest.Speedtest()
            st.get_best_server()
            
            # Get download speed
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            
            # Get upload speed
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            
            return f"Your internet speed: Download: {download_speed:.2f} Mbps, Upload: {upload_speed:.2f} Mbps"
        
        except Exception as e:
            return f"Failed to test internet speed: {str(e)}"
    
    def take_photo(self):
        """Take a photo using the webcam"""
        try:
            # Initialize camera
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                return "Sorry, I couldn't access the webcam."
            
            # Wait a moment for the camera to initialize
            self.speak("Taking a photo in 3... 2... 1...")
            time.sleep(3)
            
            # Capture frame
            ret, frame = cap.read()
            
            if not ret:
                cap.release()
                return "Failed to capture image."
            
            # Save the image
            photo_path = os.path.join(os.path.expanduser("~"), "Desktop", f"photo_{int(time.time())}.jpg")
            cv2.imwrite(photo_path, frame)
            
            # Release camera
            cap.release()
            
            return f"Photo taken and saved to {photo_path}"
        
        except Exception as e:
            return f"Failed to take photo: {str(e)}"
    
    def configure_email(self, email, password):
        """Configure email settings"""
        self.email = email
        self.email_password = password
        return "Email configuration saved. You can now send emails."
    
    def show_command_history(self):
        """Show command history"""
        if not self.command_history:
            return "You haven't issued any commands yet."
        
        response = "Here are your recent commands: "
        for i, cmd in enumerate(self.command_history[-5:], 1):  # Show last 5 commands
            response += f"{i}. {cmd}. "
        
        return response
    
    def process_command(self, command):
        """Process voice commands"""
        if not command:
            return "I didn't catch that. Can you please repeat?"
        
        # Greeting
        if any(phrase in command for phrase in ["hello", "hi", "hey"]):
            responses = [
                f"Hello! How can I help you?",
                f"Hi there! What can I do for you?",
                f"Hey! I'm listening."
            ]
            return random.choice(responses)
        
        # Time
        elif "time" in command and not any(x in command for x in ["timer", "remind", "set", "in city"]):
            return self.get_time()
        
        # Date
        elif "date" in command or "day" in command:
            return self.get_date()
        
        # Open application
        elif "open" in command:
            app_match = re.search(r'open\s+(.*)', command)
            if app_match:
                app_name = app_match.group(1).strip()
                return self.open_application(app_name)
            else:
                return "What application would you like me to open?"
        
        # Web search
        elif "search" in command or "google" in command:
            search_match = re.search(r'search\s+(?:for\s+)?(.*)', command)
            if search_match:
                query = search_match.group(1).strip()
                return self.search_web(query)
            else:
                return "What would you like me to search for?"
        
        # Weather
        elif "weather" in command:
            city_match = re.search(r'weather\s+(?:in\s+)?(.*)', command)
            if city_match:
                city = city_match.group(1).strip()
                return self.get_weather(city)
            else:
                return "For which city would you like the weather?"
        
        # Calendar events
        elif "calendar" in command or "events" in command or "schedule" in command:
            return self.get_calendar_events()
        
        # Send email
        elif "email" in command or "send mail" in command:
            if "configure" in command or "setup" in command:
                return "To configure email, please say 'set email' followed by your email address, then I'll ask for your password."
            elif "set email" in command:
                email_match = re.search(r'set email\s+(.*)', command)
                if email_match:
                    email = email_match.group(1).strip()
                    self.speak("Please say your email password.")
                    password = self.listen()
                    return self.configure_email(email, password)
                else:
                    return "Please say 'set email' followed by your email address."
            else:
                # Extract recipient, subject, and message
                self.speak("Who would you like to send an email to?")
                recipient = self.listen()
                
                self.speak("What should the subject be?")
                subject = self.listen()
                
                self.speak("What message would you like to send?")
                message = self.listen()
                
                return self.send_email(recipient, subject, message)
        
        # Set a reminder
        elif "remind" in command or "reminder" in command:
            if "set" in command or "create" in command:
                remind_match = re.search(r'remind\s+(?:me\s+)?(?:to\s+)?(.*?)(?:at|in)(.*)', command)
                if remind_match:
                    reminder_text = remind_match.group(1).strip()
                    time_str = remind_match.group(2).strip()
                    return self.set_reminder(reminder_text, time_str)
                else:
                    self.speak("What would you like me to remind you about?")
                    reminder_text = self.listen()
                    
                    self.speak("When should I remind you? You can say something like '3:30 PM' or 'in 30 minutes'.")
                    time_str = self.listen()
                    
                    return self.set_reminder(reminder_text, time_str)
            elif "list" in command or "show" in command:
                if not self.reminders:
                    return "You don't have any active reminders."
                
                response = "Here are your active reminders: "
                for i, reminder in enumerate(self.reminders, 1):
                    formatted_time = reminder["time"].strftime("%I:%M %p")
                    response += f"{i}. {reminder['text']} at {formatted_time}. "
                
                return response
        
        # News
        elif "news" in command:
            category_match = re.search(r'(?:(\w+)\s+news|news\s+about\s+(\w+))', command)
            category = "general"
            
            if category_match:
                cat1, cat2 = category_match.groups()
                if cat1:
                    category = cat1
                elif cat2:
                    category = cat2
            
            return self.get_news(category=category)
        
        # Wikipedia
        elif "wiki" in command or "wikipedia" in command:
            wiki_match = re.search(r'(?:wiki|wikipedia)\s+(.*)', command)
            if wiki_match:
                query = wiki_match.group(1).strip()
                return self.get_wikipedia_info(query)
            else:
                return "What would you like me to look up on Wikipedia?"
        
        # System information
        elif "system" in command and ("info" in command or "status" in command):
            return self.get_system_info()
        
        # Tell a joke
        elif "joke" in command:
            return self.tell_joke()
        
        # Take a screenshot
        elif "screenshot" in command:
            return self.take_screenshot()
        
        # Set volume
        elif "volume" in command:
            volume_match = re.search(r'volume\s+(\d+)', command)
            if volume_match:
                volume_level = int(volume_match.group(1).strip()) / 100.0
                return self.set_volume(volume_level)
            else:
                return "Please specify a volume level between 0 and 100."
        
        # Get IP address
        elif "ip address" in command or "network" in command:
            return self.get_ip_address()
        
        # Translate
        elif "translate" in command:
            translate_match = re.search(r'translate\s+(.*?)(?:\s+to\s+|into\s+)(\w+)', command)
            if translate_match:
                text = translate_match.group(1).strip()
                target_language = translate_match.group(2).strip()
                return self.translate_text(text, target_language)
            else:
                return "Please specify what to translate and to which language."
        
        # Stock price
        elif "stock" in command or "price of" in command:
            stock_match = re.search(r'(?:stock|price of)\s+(\w+)', command)
            if stock_match:
                symbol = stock_match.group(1).strip().upper()
                return self.get_stock_price(symbol)
            else:
                return "Which stock would you like information about?"
        
        # Time in city
        elif "time in" in command:
            city_match = re.search(r'time in\s+(.*)', command)
            if city_match:
                city = city_match.group(1).strip()
                return self.get_time_in_city(city)
            else:
                return "For which city would you like to know the time?"
        
        # Answer a question (using Wolfram Alpha)
        elif any(q in command for q in ["what is", "who is", "when did", "where is", "why does", "how many", "calculate"]):
            return self.answer_question(command)
        
        # Download YouTube audio
        elif "download" in command and ("youtube" in command or "video" in command):
            self.speak("Please say or paste the YouTube URL.")
            url = self.listen()
            if "youtube.com" in url or "youtu.be" in url:
                return self.download_youtube_audio(url)
            else:
                return "That doesn't appear to be a valid YouTube URL."
        
        # Internet speed test
        elif "internet speed" in command or "speed test" in command:
            return self.check_internet_speed()
        
        # Take photo
        elif "take photo" in command or "take picture" in command or "take a photo" in command:
            return self.take_photo()
        
        # Show command history
        elif "history" in command or "previous commands" in command:
            return self.show_command_history()
        
        # Exit
        elif any(phrase in command for phrase in ["exit", "quit", "goodbye", "bye"]):
            self.speak("Goodbye! Have a great day!")
            self.is_active = False
            exit()
        
        # Help
        elif "help" in command:
            return (
                "I can help you with: "
                "time, date, weather, calendar events, reminders, "
                "send emails, news updates, web searches, Wikipedia info, "
                "system information, jokes, screenshots, stock prices, "
                "translations, internet speed tests, general knowledge questions, "
                "and more. Just ask!"
            )
        
        # Default response
        else:
            return "I'm not sure how to help with that yet. Try asking for help to see what I can do."
        
    def run(self):
        """Main loop for the voice assistant"""
        while True:
            command = self.listen()
            response = self.process_command(command)
            self.speak(response)

if __name__ == "__main__":
    assistant = VoiceAssistant("Assistant")  # You can change the name
    assistant.run()