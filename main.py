import tkinter as tk
import cv2
import threading
import time
import os
import datetime 
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

# Import our modules
from face_recognition_module import FaceRecognition
from gui_assistant import AssistantGUI


class AuthenticationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Assistant Authentication")
        self.root.geometry("800x600")
        
        # Set theme colors (matching the GUI assistant)
        self.bg_color = "#1E1E2E"
        self.text_color = "#CDD6F4"
        self.accent_color = "#89B4FA"
        self.secondary_accent = "#F5C2E7"
        self.panel_color = "#313244"
        self.highlight_color = "#F38BA8"
        self.success_color = "#94E2D5"  # Light teal for success
        
        # Configure the root window
        self.root.configure(bg=self.bg_color)
        
        # Initialize face recognition system
        self.face_system = FaceRecognition()
        
        # Check if face data exists
        self.has_registered_users = len(self.face_system.face_data) > 0
        
        # Initialize animation ID
        self.animation_id = None
        
        # Create security logs directory
        self.log_dir = "security_logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # Create and place the GUI components
        self.create_widgets()
        
        # Start camera if we have registered users
        if self.has_registered_users:
            self.start_camera()
    
    def create_widgets(self):
        """Create all GUI widgets for authentication"""
        # Main container frame with padding
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Voice Assistant Authentication", 
                              font=("Helvetica", 24, "bold"), 
                              bg=self.bg_color, fg=self.accent_color)
        title_label.pack(pady=(0, 20))
        
        # Camera frame
        self.camera_frame = tk.Frame(main_frame, bg=self.bg_color)
        self.camera_frame.pack(pady=10)
        
        # Camera canvas
        self.canvas = tk.Canvas(self.camera_frame, width=640, height=480, 
                               bg="black", highlightthickness=0)
        self.canvas.pack()
        
        # Create authentication status indicator (circle)
        self.outer_circle = self.canvas.create_oval(
            290, 430, 350, 470,  # Position at bottom center of canvas
            outline=self.accent_color, 
            width=3, 
            fill=self.panel_color
        )
        
        # Status label
        self.status_var = tk.StringVar()
        
        if self.has_registered_users:
            self.status_var.set("Looking for a registered face...")
        else:
            self.status_var.set("No registered users found. Please register a user first.")
        
        self.status_label = tk.Label(main_frame, textvariable=self.status_var, 
                                    font=("Helvetica", 12), 
                                    bg=self.bg_color, fg=self.text_color)
        self.status_label.pack(pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg=self.bg_color)
        buttons_frame.pack(pady=20)
        
        # Register button
        self.register_button = tk.Button(
            buttons_frame, 
            text="Register New User", 
            font=("Helvetica", 12),
            bg=self.accent_color,
            fg=self.bg_color,
            padx=10,
            pady=5,
            command=self.register_new_user
        )
        self.register_button.pack(side=tk.LEFT, padx=10)
        
        # Manage Users button
        self.manage_button = tk.Button(
            buttons_frame, 
            text="Manage Users", 
            font=("Helvetica", 12),
            bg=self.secondary_accent,
            fg=self.bg_color,
            padx=10,
            pady=5,
            command=self.manage_users
        )
        self.manage_button.pack(side=tk.LEFT, padx=10)
        
        # Skip authentication button (for development/testing)
        self.skip_button = tk.Button(
            buttons_frame, 
            text="Skip Authentication", 
            font=("Helvetica", 12),
            bg=self.panel_color,
            fg=self.text_color,
            padx=10, 
            pady=5,
            command=self.skip_authentication
        )
        self.skip_button.pack(side=tk.LEFT, padx=10)
        
        # Exit button
        self.exit_button = tk.Button(
            buttons_frame, 
            text="Exit", 
            font=("Helvetica", 12),
            bg=self.highlight_color,
            fg=self.bg_color,
            padx=10,
            pady=5,
            command=self.root.destroy
        )
        self.exit_button.pack(side=tk.LEFT, padx=10)
        
        # View logs button
        self.logs_button = tk.Button(
            main_frame, 
            text="View Security Logs", 
            font=("Helvetica", 10),
            bg=self.panel_color,
            fg=self.text_color,
            padx=5,
            pady=2,
            command=self.view_security_logs
        )
        self.logs_button.pack(side=tk.BOTTOM, pady=10, anchor=tk.SE)
    
    def start_camera(self):
        """Start the camera for face recognition"""
        self.cap = cv2.VideoCapture(0)
        self.is_running = True
        
        # Start camera thread
        self.camera_thread = threading.Thread(target=self.update_camera)
        self.camera_thread.daemon = True
        self.camera_thread.start()
        
        # Start recognition thread
        self.recognition_thread = threading.Thread(target=self.perform_recognition)
        self.recognition_thread.daemon = True
        self.recognition_thread.start()
    
    def update_camera(self):
        """Update camera feed on canvas"""
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                # Convert frame to RGB for tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize if needed
                frame_rgb = cv2.resize(frame_rgb, (640, 480))
                
                # Convert to PhotoImage
                self.photo = tk.PhotoImage(
                    data=cv2.imencode('.png', frame_rgb)[1].tobytes()
                )
                
                # Update canvas
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            
            time.sleep(0.03)  # ~30 FPS
    
   
    def perform_recognition(self):
        """Perform face recognition on camera feed"""
        # Wait a moment for camera to initialize
        time.sleep(1)
        
        recognition_interval = 1.0  # seconds between recognition attempts
        last_recognition_time = 0
        
        # Authentication parameters
        max_attempts = 10  # Maximum number of recognition attempts
        confidence_threshold = 60  # Confidence threshold for authentication (lower is better)
        attempt_count = 0
        
        while self.is_running and attempt_count < max_attempts:
            current_time = time.time()
            
            # Only perform recognition at intervals
            if current_time - last_recognition_time >= recognition_interval:
                last_recognition_time = current_time
                attempt_count += 1
                
                ret, frame = self.cap.read()
                if ret:
                    # Perform face recognition
                    results = self.face_system.recognize_face(frame,confidence_threshold)
                    
                    # Check if any faces were detected
                    if not results:
                        # No faces detected
                        self.status_var.set(f"No face detected. Attempt {attempt_count}/{max_attempts}")
                    else:
                        # Process all detected faces
                        valid_matches = [r for r in results if r['valid']]
                        
                        if valid_matches:
                            # Get the user with highest confidence (lowest value) among valid matches
                            best_match = min(valid_matches, key=lambda x: x['confidence'])
                            
                            # Authentication successful
                            self.is_running = False
                            
                            # Update status and show success animation
                            self.status_var.set(f"Authentication successful! Welcome, {best_match['name']}!")
                            self.show_authentication_result(True, best_match['name'])
                            
                            # Log successful authentication
                            self.log_authentication_attempt(True, best_match['name'])
                            
                            # Schedule launching the main application
                            self.root.after(1500, lambda: self.launch_assistant(best_match['name']))
                            return
                        else:
                            # Face detected but not recognized as a registered user
                            self.status_var.set(f"Unrecognized face. Attempt {attempt_count}/{max_attempts}")
            
            time.sleep(0.1)
        
        # If we reach here, authentication has failed
        if self.is_running:
            self.is_running = False
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()
            
            # Update status and show failure animation
            self.status_var.set("Authentication failed. Access denied.")
            self.show_authentication_result(False)
            
            # Log failed authentication
            self.log_authentication_attempt(False)
            
            # Show message box
            self.root.after(500, lambda: messagebox.showerror("Authentication Failed", 
                                                            "Face not recognized. Please register or try again."))

    def show_authentication_result(self, success, user_name=None):
        """Show a visual indication of authentication success/failure"""
        # Clear existing animation
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
        
        # Change the circle color based on result
        if success:
            result_color = self.success_color  # Success color (light teal)
            self.canvas.itemconfig(self.outer_circle, outline=result_color, width=5)
            self.status_var.set(f"Welcome, {user_name}! Access granted.")
        else:
            result_color = self.highlight_color  # Failure color (light red)
            self.canvas.itemconfig(self.outer_circle, outline=result_color, width=5)
            self.status_var.set("Authentication failed. Access denied.")
        
        # Flash animation
        self.root.update()
    
    def log_authentication_attempt(self, success, user_name=None):
        """Log authentication attempts for security purposes"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = os.path.join(self.log_dir, "auth_log.txt")
        
        with open(log_file, "a") as f:
            if success:
                f.write(f"{timestamp} - SUCCESSFUL LOGIN: {user_name}\n")
            else:
                f.write(f"{timestamp} - FAILED LOGIN ATTEMPT\n")
    
    def view_security_logs(self):
        """Open a window to view security logs"""
        log_file = os.path.join(self.log_dir, "auth_log.txt")
        
        if not os.path.exists(log_file):
            messagebox.showinfo("Logs", "No security logs found.")
            return
        
        # Create logs window
        logs_window = tk.Toplevel(self.root)
        logs_window.title("Security Logs")
        logs_window.geometry("600x400")
        logs_window.configure(bg=self.bg_color)
        
        # Create a frame for the logs
        logs_frame = tk.Frame(logs_window, bg=self.bg_color)
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(logs_frame, text="Authentication Security Logs", 
                font=("Helvetica", 16, "bold"), 
                bg=self.bg_color, fg=self.accent_color).pack(pady=(0, 10))
        
        # Create a text widget to display logs
        log_text = tk.Text(logs_frame, wrap=tk.WORD, bg=self.panel_color, 
                          fg=self.text_color, font=("Courier", 10))
        log_text.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=log_text.yview)
        
        # Read and display logs
        with open(log_file, "r") as f:
            logs = f.readlines()
        
        for log in logs:
            if "SUCCESSFUL" in log:
                log_text.insert(tk.END, log, "success")
            else:
                log_text.insert(tk.END, log, "failure")
        
        # Configure tags
        log_text.tag_config("success", foreground=self.success_color)
        log_text.tag_config("failure", foreground=self.highlight_color)
        
        # Make text read-only
        log_text.config(state=tk.DISABLED)
        
        # Add clear logs button
        tk.Button(logs_frame, text="Clear Logs", 
                 bg=self.highlight_color, fg=self.bg_color,
                 command=lambda: self.clear_logs(log_text)).pack(pady=10)
    
    def clear_logs(self, log_text):
        """Clear the security logs"""
        log_file = os.path.join(self.log_dir, "auth_log.txt")
        
        # Confirm before clearing
        if messagebox.askyesno("Clear Logs", "Are you sure you want to clear all security logs?"):
            # Clear the file
            open(log_file, "w").close()
            
            # Clear the text widget
            log_text.config(state=tk.NORMAL)
            log_text.delete(1.0, tk.END)
            log_text.config(state=tk.DISABLED)
            
            messagebox.showinfo("Logs", "Security logs have been cleared.")
    
    def register_new_user(self):
        """Register a new user"""
        # Stop camera if running
        if hasattr(self, 'is_running') and self.is_running:
            self.is_running = False
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()
            time.sleep(0.5)  # Give time for threads to stop
        
        # Create a simple dialog for name input
        register_window = tk.Toplevel(self.root)
        register_window.title("Register New User")
        register_window.geometry("400x200")
        register_window.configure(bg=self.bg_color)
        
        # Name label and entry
        name_label = tk.Label(
            register_window, 
            text="Enter your name:", 
            font=("Helvetica", 12),
            bg=self.bg_color,
            fg=self.text_color
        )
        name_label.pack(pady=(20, 10))
        
        name_entry = tk.Entry(
            register_window,
            font=("Helvetica", 12),
            width=30
        )
        name_entry.pack(pady=10)
        name_entry.focus()
        
        # Submit button
        submit_button = tk.Button(
            register_window,
            text="Start Registration",
            font=("Helvetica", 12),
            bg=self.accent_color,
            fg=self.bg_color,
            command=lambda: self.start_registration(name_entry.get(), register_window)
        )
        submit_button.pack(pady=20)
    
    def start_registration(self, name, register_window):
        """Start the registration process"""
        if not name.strip():
            messagebox.showerror("Error", "Please enter a name")
            return
        
        # Close the registration window
        register_window.destroy()
        
        # Update status
        self.status_var.set(f"Registering {name}... Look at the camera and follow instructions")
        self.root.update()
        
        # Start registration process
        try:
            user_id = self.face_system.register_new_user(name)
            messagebox.showinfo("Success", f"Registration successful for {name}!")
            
            # Log the registration
            self.log_registration(name)
            
            # Update status and restart camera
            self.status_var.set("Looking for a registered face...")
            self.has_registered_users = True
            self.start_camera()
            
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")
            self.status_var.set("Registration failed. Please try again.")
    
    def log_registration(self, name):
        """Log user registration"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = os.path.join(self.log_dir, "auth_log.txt")
        
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - NEW USER REGISTERED: {name}\n")
    
    def manage_users(self):
        """Open a window to manage registered users"""
        # Stop camera if running
        if hasattr(self, 'is_running') and self.is_running:
            self.is_running = False
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()
            time.sleep(0.5)  # Give time for threads to stop
        
        # Create user management window
        manage_window = tk.Toplevel(self.root)
        manage_window.title("User Management")
        manage_window.geometry("500x400")
        manage_window.configure(bg=self.bg_color)
        
        # Create a frame for the user management
        users_frame = tk.Frame(manage_window, bg=self.bg_color)
        users_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(users_frame, text="Registered Users", 
                font=("Helvetica", 16, "bold"), 
                bg=self.bg_color, fg=self.accent_color).pack(pady=(0, 10))
        
        # Create a listbox with all users
        users_listbox = tk.Listbox(
            users_frame, 
            bg=self.panel_color, 
            fg=self.text_color,
            font=("Helvetica", 12), 
            width=40, 
            height=10
        )
        users_listbox.pack(pady=10)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(users_listbox)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        users_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=users_listbox.yview)
        
        # Populate the listbox
        for user_id, user_data in self.face_system.face_data.items():
            users_listbox.insert(tk.END, f"{user_data['name']} (ID: {user_id})")
        
        # Buttons frame
        buttons_frame = tk.Frame(users_frame, bg=self.bg_color)
        buttons_frame.pack(pady=10)
        
        # Add buttons for user management
        tk.Button(
            buttons_frame, 
            text="Add New User", 
            bg=self.accent_color, 
            fg=self.bg_color,
            command=lambda: (manage_window.destroy(), self.register_new_user())
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame, 
            text="Delete User", 
            bg=self.highlight_color, 
            fg=self.bg_color,
            command=lambda: self.delete_user(users_listbox, manage_window)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame, 
            text="Close", 
            bg=self.panel_color, 
            fg=self.text_color,
            command=manage_window.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        # When window is closed, restart camera
        manage_window.protocol("WM_DELETE_WINDOW", 
                              lambda: (manage_window.destroy(), self.start_camera()))
    
    def delete_user(self, users_listbox, manage_window):
        """Delete a selected user"""
        selection = users_listbox.curselection()
        
        if not selection:
            messagebox.showerror("Error", "Please select a user to delete")
            return
        
        # Get the selected user
        user_text = users_listbox.get(selection[0])
        user_id = int(user_text.split("ID: ")[1].strip(")"))
        user_name = self.face_system.face_data[user_id]['name']
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {user_name}?"):
            # Delete the user
            del self.face_system.face_data[user_id]
            
            # Save the updated face data
            self.face_system.save_face_data()
            
            # Retrain the model if there are still users
            if self.face_system.face_data:
                # This is a simplified approach - in a real app, you'd need to retrain with all remaining users' face data
                messagebox.showinfo("Info", "User deleted. You may need to retrain the model.")
            else:
                # No more users
                self.has_registered_users = False
            
            # Log the deletion
            self.log_user_deletion(user_name)
            
            # Close the management window and restart
            manage_window.destroy()
            self.start_camera()
    
    def log_user_deletion(self, name):
        """Log user deletion"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = os.path.join(self.log_dir, "auth_log.txt")
        
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - USER DELETED: {name}\n")
    
    def skip_authentication(self):
        """Skip authentication (for development/testing)"""
        # Log the skipped authentication
        self.log_authentication_attempt(True, "Developer (Skipped)")
        self.launch_assistant("Developer")
    
    def launch_assistant(self, user_name):
        """Launch the main voice assistant application"""
        # Stop camera if running
        if hasattr(self, 'is_running') and self.is_running:
            self.is_running = False
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()
        
        # Hide the authentication window
        self.root.withdraw()
        
        # Create a new window for the assistant
        assistant_window = tk.Toplevel(self.root)
        assistant_window.protocol("WM_DELETE_WINDOW", self.root.destroy)  # Close both windows on exit
        
        # Initialize the assistant GUI
        app = AssistantGUI(assistant_window)
        
        # Add welcome message with authenticated user
        app.add_to_conversation(f"Welcome, {user_name}! Authentication successful.")
        
        # When assistant window is closed, close the entire application
        assistant_window.protocol("WM_DELETE_WINDOW", self.root.destroy)

def main():
    root = tk.Tk()
    app = AuthenticationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
