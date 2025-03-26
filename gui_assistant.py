import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import datetime
import math
import time
from PIL import Image, ImageTk
from quickstart import VoiceAssistant

class AssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Assistant")
        self.root.geometry("900x700")
      
        # Theme colors
        self.bg_color = "#1E1E2E"
        self.text_color = "#CDD6F4"
        self.accent_color = "#89B4FA"
        self.secondary_accent = "#F5C2E7"
        self.root.configure(bg=self.bg_color)
        
        # State variables
        self.is_listening = False
        self.is_speaking = False
        self.assistant = None
        
        # Create main UI components
        self.create_widgets()
        
        # Initialize assistant in background
        threading.Thread(target=self.initialize_assistant, daemon=True).start()
    
    def create_widgets(self):
        # Main container with title
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title and visualization area
        tk.Label(main_frame, text="Voice Assistant", font=("Helvetica", 24, "bold"), 
                bg=self.bg_color, fg=self.accent_color).pack(pady=10)
        
        # Create visualization canvas
        self.canvas = tk.Canvas(main_frame, width=200, height=200, 
                               bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # Create simple visualization
        self.circle = self.canvas.create_oval(50, 50, 150, 150, 
                                            outline=self.accent_color, 
                                            width=3, fill="#313244")
        
        # Status indicator
        self.status_var = tk.StringVar(value="Initializing...")
        tk.Label(main_frame, textvariable=self.status_var, bg=self.bg_color, 
                fg=self.text_color, font=("Helvetica", 12)).pack(pady=5)
        
        # Conversation history
        self.conversation_text = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, font=("Helvetica", 11),
            bg="#313244", fg=self.text_color, padx=10, pady=10
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # User input area
        input_frame = tk.Frame(main_frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, pady=10)
        
        self.input_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_var, 
                 font=("Helvetica", 12)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(input_frame, text="Send", 
                  command=self.send_text_command).pack(side=tk.LEFT, padx=5)
        
        self.mic_button = ttk.Button(input_frame, text="🎤 Listen", 
                                    command=self.toggle_listening)
        self.mic_button.pack(side=tk.LEFT, padx=5)
    
    def initialize_assistant(self):
        try:
            self.assistant = EnhancedVoiceAssistant("Assistant", self)
            self.status_var.set("Ready")
            self.add_to_conversation("Hello! I'm your voice assistant. How can I help you today?")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def toggle_listening(self):
        if not self.assistant:
            self.add_to_conversation("Assistant not initialized yet. Please wait.")
            return
        
        if not self.is_listening:
            # Start listening
            self.is_listening = True
            self.mic_button.config(text="🛑 Stop")
            self.status_var.set("Listening...")
            self.canvas.itemconfig(self.circle, fill=self.secondary_accent)
            
            # Start listening in a separate thread
            threading.Thread(target=self.start_listening).start()
        else:
            # Stop listening
            self.is_listening = False
            self.mic_button.config(text="🎤 Listen")
            self.status_var.set("Ready")
            self.canvas.itemconfig(self.circle, fill="#313244")
    
    def start_listening(self):
        if self.assistant:
            command = self.assistant.listen()
            self.is_listening = False
            self.mic_button.config(text="🎤 Listen")
            self.status_var.set("Ready")
            self.canvas.itemconfig(self.circle, fill="#313244")
            
            if command:
                self.add_to_conversation(f"You: {command}")
                self.process_command(command)
    
    def send_text_command(self):
        command = self.input_var.get().strip()
        if command:
            self.input_var.set("")  # Clear the input field
            self.add_to_conversation(f"You: {command}")
            self.process_command(command)
    
    def process_command(self, command):
        if self.assistant:
            threading.Thread(target=self.process_command_thread, args=(command,)).start()
    
    def process_command_thread(self, command):
        if self.assistant:
            self.is_speaking = True
            self.status_var.set("Processing...")
            response = self.assistant.process_command(command)
            self.status_var.set("Speaking...")
            self.canvas.itemconfig(self.circle, fill="#F38BA8")
            self.assistant.speak(response)
            self.is_speaking = False
            self.status_var.set("Ready")
            self.canvas.itemconfig(self.circle, fill="#313244")
    
    def add_to_conversation(self, message):
        # Enable text widget for editing
        self.conversation_text.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.conversation_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        # Scroll to the bottom
        self.conversation_text.see(tk.END)
        
        # Disable editing
        self.conversation_text.config(state=tk.DISABLED)

class EnhancedVoiceAssistant(VoiceAssistant):
    def __init__(self, name, gui):
        self.gui = gui
        super().__init__(name)
    
    def speak(self, text):
        if self.gui:
            self.gui.add_to_conversation(f"Assistant: {text}")
        super().speak(text)

def main():
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
