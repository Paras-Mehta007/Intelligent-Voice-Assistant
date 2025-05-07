import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import datetime
import math
import time
import os
import sys
from PIL import Image, ImageTk, ImageDraw, ImageFont
import numpy as np
import io
import requests



# Import the VoiceAssistant class from your existing file
from quickstart import VoiceAssistant

class AssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Assistant")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Set theme colors
        self.bg_color = "#1E1E2E"
        self.text_color = "#CDD6F4"
        self.accent_color = "#89B4FA"
        self.secondary_accent = "#F5C2E7"
        self.panel_color = "#313244"
        self.highlight_color = "#F38BA8"
        
        # Configure the root window
        self.root.configure(bg=self.bg_color)
        
        # Initialize state variables
        self.is_listening = False
        self.is_speaking = False
        self.animation_id = None
        
        # Create and place the GUI components
        self.create_widgets()
        
        # Initialize the assistant in a separate thread
        self.assistant = None
        self.assistant_thread = threading.Thread(target=self.initialize_assistant)
        self.assistant_thread.daemon = True
        self.assistant_thread.start()
        
        # Start the idle animation
        self.animate_idle()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container frame with padding
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Top section - Title and assistant visualization
        top_frame = tk.Frame(main_frame, bg=self.bg_color)
        top_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(top_frame, text="Voice Assistant", 
                              font=("Helvetica", 24, "bold"), 
                              bg=self.bg_color, fg=self.accent_color)
        title_label.pack(pady=(0, 10))
        
        # Assistant visualization canvas
        self.canvas_frame = tk.Frame(top_frame, bg=self.bg_color)
        self.canvas_frame.pack(pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=200, height=200, 
                               bg=self.bg_color, highlightthickness=0)
        self.canvas.pack()
        
        # Create the visualization
        self.create_visualization()
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Initializing...")
        self.status_label = tk.Label(top_frame, textvariable=self.status_var, 
                                    font=("Helvetica", 12), 
                                    bg=self.bg_color, fg=self.text_color)
        self.status_label.pack(pady=5)
        
        # Middle section - Conversation history
        mid_frame = tk.Frame(main_frame, bg=self.bg_color)
        mid_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Conversation history label
        history_label = tk.Label(mid_frame, text="Conversation History", 
                                font=("Helvetica", 14), 
                                bg=self.bg_color, fg=self.accent_color)
        history_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Conversation text area with custom styling
        self.conversation_text = scrolledtext.ScrolledText(
            mid_frame, 
            wrap=tk.WORD, 
            font=("Helvetica", 11),
            bg=self.panel_color, 
            fg=self.text_color,
            insertbackground=self.text_color,
            selectbackground=self.accent_color,
            selectforeground=self.panel_color,
            padx=10,
            pady=10
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True)
        self.conversation_text.config(state=tk.DISABLED)
        
        # Bottom section - User input and controls
        bottom_frame = tk.Frame(main_frame, bg=self.bg_color)
        bottom_frame.pack(fill=tk.X, pady=(20, 0))
        
        # User input label
        input_label = tk.Label(bottom_frame, text="Type your command:", 
                              font=("Helvetica", 12), 
                              bg=self.bg_color, fg=self.accent_color)
        input_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Input and buttons container
        input_container = tk.Frame(bottom_frame, bg=self.bg_color)
        input_container.pack(fill=tk.X)
        
        # Text input field
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(
            input_container, 
            textvariable=self.input_var, 
            font=("Helvetica", 12),
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", lambda event: self.send_text_command())
        
        # Create a custom style for the buttons
        self.style = ttk.Style()
        self.style.configure(
            "Custom.TButton",
            background=self.accent_color,
            foreground=self.bg_color,
            font=("Helvetica", 11),
            padding=5
        )
        
        # Send button
        self.send_button = ttk.Button(
            input_container, 
            text="Send", 
            command=self.send_text_command,
            style="Custom.TButton"
        )
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        # Microphone button
        self.mic_button = ttk.Button(
            input_container, 
            text="🎤 Listen", 
            command=self.toggle_listening,
            style="Custom.TButton"
        )
        self.mic_button.pack(side=tk.LEFT, padx=5)
        
        # Help button
        self.help_button = ttk.Button(
            input_container, 
            text="❓ Help",
            command=self.show_help,
            style="Custom.TButton"
        )
        self.help_button.pack(side=tk.LEFT, padx=5)
        
        # Exit button
        self.exit_button = ttk.Button(
            input_container, 
            text="🚪 Exit",
            command=self.exit_application,
            style="Custom.TButton"
        )
        self.exit_button.pack(side=tk.LEFT, padx=5)
        
        # Footer with credits
        footer_frame = tk.Frame(main_frame, bg=self.bg_color)
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        footer_text = tk.Label(
            footer_frame, 
            text="Voice Assistant - Created for PBL Project", 
            font=("Helvetica", 9), 
            bg=self.bg_color, 
            fg="#7F849C"
        )
        footer_text.pack(side=tk.RIGHT)
    
    def create_visualization(self):
        """Create the animated visualization for the assistant"""
        # Main circle parameters
        self.circle_radius = 80
        self.circle_x = 100
        self.circle_y = 100
        
        # Create outer circle
        self.outer_circle = self.canvas.create_oval(
            self.circle_x - self.circle_radius, 
            self.circle_y - self.circle_radius,
            self.circle_x + self.circle_radius, 
            self.circle_y + self.circle_radius,
            outline=self.accent_color, 
            width=3, 
            fill=self.panel_color
        )
        
        # Create inner circle
        self.inner_radius = self.circle_radius - 15
        self.inner_circle = self.canvas.create_oval(
            self.circle_x - self.inner_radius, 
            self.circle_y - self.inner_radius,
            self.circle_x + self.inner_radius, 
            self.circle_y + self.inner_radius,
            outline=self.accent_color, 
            width=2, 
            fill=self.bg_color
        )
        
        # Create wave points for animation
        self.wave_points = []
        self.num_points = 30
        for i in range(self.num_points):
            angle = 2 * math.pi * i / self.num_points
            x = self.circle_x + self.inner_radius * math.cos(angle)
            y = self.circle_y + self.inner_radius * math.sin(angle)
            point = self.canvas.create_oval(
                x-2, y-2, x+2, y+2, 
                fill=self.accent_color, 
                outline=""
            )
            self.wave_points.append((point, angle))
    
    def animate_idle(self):
        """Animate the assistant visualization in idle state"""
        # Subtle pulsing animation
        scale = 0.05 * math.sin(time.time() * 2) + 1.0
        
        for point, angle in self.wave_points:
            x = self.circle_x + self.inner_radius * scale * math.cos(angle)
            y = self.circle_y + self.inner_radius * scale * math.sin(angle)
            self.canvas.coords(point, x-2, y-2, x+2, y+2)
        
        self.animation_id = self.root.after(50, self.animate_idle)
    
    def animate_listening(self):
        """Animate the assistant visualization when listening"""
        # More active animation with multiple wave patterns
        amplitudes = [0.1 * math.sin(time.time() * 8 + i * 0.5) + 1.0 for i in range(4)]
        
        for i, (point, angle) in enumerate(self.wave_points):
            # Use different amplitudes for different sections
            section = int(4 * i / self.num_points)
            scale = amplitudes[section]
            
            x = self.circle_x + (self.inner_radius * (1 + 0.2 * scale)) * math.cos(angle)
            y = self.circle_y + (self.inner_radius * (1 + 0.2 * scale)) * math.sin(angle)
            self.canvas.coords(point, x-3, y-3, x+3, y+3)
            
            # Change color to indicate listening
            self.canvas.itemconfig(point, fill=self.secondary_accent)
        
        self.animation_id = self.root.after(50, self.animate_listening)
    
    def animate_speaking(self):
        """Animate the assistant visualization when speaking"""
        # Animation when the assistant is speaking
        amplitudes = [0.3 * math.sin(time.time() * 10 + i * 1.0) + 1.0 for i in range(self.num_points)]
        
        for i, (point, angle) in enumerate(self.wave_points):
            scale = amplitudes[i % len(amplitudes)]
            x = self.circle_x + (self.inner_radius * scale) * math.cos(angle)
            y = self.circle_y + (self.inner_radius * scale) * math.sin(angle)
            self.canvas.coords(point, x-3, y-3, x+3, y+3)
            
            # Change color to indicate speaking
            self.canvas.itemconfig(point, fill=self.highlight_color)
        
        self.animation_id = self.root.after(50, self.animate_speaking)
    
    def update_animation_state(self):
        """Update the animation based on current state"""
        # Cancel any existing animation
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
        
        # Start the appropriate animation based on current state
        if self.is_speaking:
            self.status_var.set("Speaking...")
            self.animate_speaking()
        elif self.is_listening:
            self.status_var.set("Listening...")
            self.animate_listening()
        else:
            self.status_var.set("Ready")
            self.animate_idle()
            
            # Reset point colors to default
            for point, _ in self.wave_points:
                self.canvas.itemconfig(point, fill=self.accent_color)
    
    def initialize_assistant(self):
        """Initialize the voice assistant"""
        try:
            # Create a custom VoiceAssistant that will work with our GUI
            self.assistant = EnhancedVoiceAssistant("Assistant", self)
            self.status_var.set("Ready")
        except Exception as e:
            self.status_var.set(f"Error initializing: {str(e)}")
            self.add_to_conversation(f"Error initializing assistant: {str(e)}")
    
    def toggle_listening(self):
        """Toggle the listening state"""
        if not self.assistant:
            self.add_to_conversation("Assistant not initialized yet. Please wait.")
            return
        
        if not self.is_listening:
            # Start listening
            self.is_listening = True
            self.mic_button.config(text="🛑 Stop")
            self.update_animation_state()
            
            # Start listening in a separate thread
            threading.Thread(target=self.start_listening).start()
        else:
            # Stop listening (note: this is a bit tricky with speech_recognition)
            self.is_listening = False
            self.mic_button.config(text="🎤 Listen")
            self.update_animation_state()
    
    def start_listening(self):
        """Start the listening process"""
        if self.assistant:
            command = self.assistant.listen()
            self.is_listening = False
            self.mic_button.config(text="🎤 Listen")
            self.update_animation_state()
            
            if command:
                self.add_to_conversation(f"You: {command}")
                self.process_command(command)
    
    def send_text_command(self):
        """Process a text command from the input field"""
        command = self.input_var.get().strip()
        if command:
            self.input_var.set("")  # Clear the input field
            self.add_to_conversation(f"You: {command}")
            self.process_command(command)
    
    def process_command(self, command):
        """Process a command through the assistant"""
        if self.assistant:
            # Process the command in a separate thread
            threading.Thread(target=self.process_command_thread, args=(command,)).start()
    
    def process_command_thread(self, command):
        """Thread function to process commands"""
        if self.assistant:
            response = self.assistant.process_command(command)
            self.is_speaking = True
            self.update_animation_state()
            self.assistant.speak(response)
            self.is_speaking = False
            self.update_animation_state()
    
    def add_to_conversation(self, message):
        """Add a message to the conversation history"""
        # Enable text widget for editing
        self.conversation_text.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Add the message with appropriate formatting
        if message.startswith("You: "):
            self.conversation_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.conversation_text.insert(tk.END, "You: ", "user")
            self.conversation_text.insert(tk.END, message[5:] + "\n", "user_message")
        else:
            self.conversation_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.conversation_text.insert(tk.END, "Assistant: ", "assistant")
            self.conversation_text.insert(tk.END, message + "\n", "assistant_message")
        
        # Apply tags for styling
        self.conversation_text.tag_config("timestamp", foreground="#7F849C")
        self.conversation_text.tag_config("user", foreground=self.accent_color, font=("Helvetica", 11, "bold"))
        self.conversation_text.tag_config("user_message", foreground=self.text_color)
        self.conversation_text.tag_config("assistant", foreground=self.secondary_accent, font=("Helvetica", 11, "bold"))
        self.conversation_text.tag_config("assistant_message", foreground=self.text_color)
        
        # Scroll to the bottom
        self.conversation_text.see(tk.END)
        
        # Disable editing
        self.conversation_text.config(state=tk.DISABLED)
    
    def show_help(self):
        """Show help information"""
        help_text = (
            "Voice Assistant Help:\n\n"
            "• Ask for the time: 'What time is it?'\n"
            "• Ask for the date: 'What is today's date?'\n"
            "• Open applications: 'Open Chrome'\n"
            "• Search the web: 'Search for pizza recipes'\n"
            "• Check weather: 'What's the weather in New York?'\n"
            "• View calendar: 'Show my calendar events'\n"
            "• Exit: 'Goodbye' or click the Exit button\n\n"
            "You can type commands in the text box or click the microphone button to speak."
        )
        self.add_to_conversation(help_text)
    
    def exit_application(self):
        """Exit the application"""
        if self.assistant:
            self.assistant.speak("Goodbye! Have a great day!")
        self.root.after(1000, self.root.destroy)


class EnhancedVoiceAssistant(VoiceAssistant):
    """Extended VoiceAssistant class with enhanced features"""
    def __init__(self, name, gui):
        self.gui = gui
        self.weather_api_key = "YOUR_API_KEY"  # Replace with your OpenWeatherMap API key
        super().__init__(name)
    
    def speak(self, text):
        """Override speak method to update GUI"""
        print(f"{self.name}: {text}")
        
        # Add to conversation in GUI
        if self.gui:
            self.gui.add_to_conversation(text)
        
        # Use the original speak method for TTS
        super().speak(text)
    
    def get_weather(self, city):
        """Get weather information for a city using OpenWeatherMap API"""
        try:
            # If you have an API key, use it
            if hasattr(self, 'weather_api_key') and self.weather_api_key != "YOUR_API_KEY":
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
                response = requests.get(url)
                data = response.json()
                
                if response.status_code == 200:
                    # Extract weather information
                    weather_desc = data['weather'][0]['description']
                    temperature = data['main']['temp']
                    humidity = data['main']['humidity']
                    wind_speed = data['wind']['speed']
                    
                    return (f"The weather in {city} is {weather_desc}. "
                            f"The temperature is {temperature:.1f}°C with {humidity}% humidity. "
                            f"Wind speed is {wind_speed} meters per second.")
                else:
                    # If city not found or other error
                    return f"I couldn't find weather information for {city}. Please try another city."
            else:
                # Fallback if no API key
                return f"The weather in {city} is currently unavailable. To get real weather data, please add an OpenWeatherMap API key."
        except Exception as e:
            return f"I encountered an error getting weather for {city}: {str(e)}"
    
    def process_command(self, command):
        """Process commands but don't exit directly"""
        if not command:
            return "I didn't catch that. Can you please repeat?"
        
        # Handle exit command differently
        if any(phrase in command for phrase in ["exit", "quit", "goodbye", "bye"]):
            return "Goodbye! Have a great day!"
        
        # Use the original process_command for other commands
        return super().process_command(command)


def main():
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

