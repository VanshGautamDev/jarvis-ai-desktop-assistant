#!/usr/bin/env python3
"""
GUI Interface Module for JARVIS
Creates a futuristic Iron Man-style interface
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime
import logging
import json
from collections import deque

class JarvisGUI:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.root = None
        self.running = False
        
        # GUI elements
        self.status_label = None
        self.command_history = None
        self.response_history = None
        self.system_info_frame = None
        
        # Data storage
        self.commands = deque(maxlen=50)
        self.responses = deque(maxlen=50)
        self.current_status = "Initializing..."
        
        # Colors (Iron Man theme)
        self.colors = {
            'bg': '#0a0a0a',           # Dark background
            'primary': '#00d4ff',       # Cyan blue
            'secondary': '#ff6b35',     # Orange/red
            'text': '#ffffff',          # White text
            'accent': '#1a1a1a',       # Darker accent
            'success': '#00ff88',       # Green
            'warning': '#ffaa00',       # Orange
            'error': '#ff3333'          # Red
        }
        
        self.logger.info("GUI interface initialized")
    
    def create_gui(self):
        """Create the main GUI window"""
        self.root = tk.Tk()
        self.root.title("JARVIS - AI Desktop Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg=self.colors['bg'])
        self.root.resizable(True, True)
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap('jarvis_icon.ico')
        except:
            pass
        
        # Configure styles
        self.setup_styles()
        
        # Create main layout
        self.create_main_layout()
        
        # Start update thread
        self.start_update_thread()
        
        self.logger.info("GUI created successfully")
    
    def setup_styles(self):
        """Setup custom styles for ttk widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['primary'],
                       font=('Arial', 24, 'bold'))
        
        style.configure('Status.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['success'],
                       font=('Arial', 12, 'bold'))
        
        style.configure('Header.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['secondary'],
                       font=('Arial', 14, 'bold'))
        
        style.configure('Info.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['text'],
                       font=('Arial', 10))
    
    def create_main_layout(self):
        """Create the main GUI layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="J.A.R.V.I.S.", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, 
                                  text="Just A Rather Very Intelligent System", 
                                  style='Info.TLabel')
        subtitle_label.pack(pady=(0, 30))
        
        # Status section
        self.create_status_section(main_frame)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Left panel - Commands and Responses
        self.create_interaction_panel(content_frame)
        
        # Right panel - System Information
        self.create_system_panel(content_frame)
        
        # Bottom panel - Controls
        self.create_control_panel(main_frame)
    
    def create_status_section(self, parent):
        """Create status display section"""
        status_frame = tk.Frame(parent, bg=self.colors['accent'], relief=tk.RAISED, bd=2)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        status_header = ttk.Label(status_frame, text="SYSTEM STATUS", style='Header.TLabel')
        status_header.pack(pady=5)
        
        self.status_label = ttk.Label(status_frame, 
                                     text=self.current_status, 
                                     style='Status.TLabel')
        self.status_label.pack(pady=(0, 5))
    
    def create_interaction_panel(self, parent):
        """Create command and response interaction panel"""
        # Left panel
        left_frame = tk.Frame(parent, bg=self.colors['bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Commands section
        cmd_header = ttk.Label(left_frame, text="VOICE COMMANDS", style='Header.TLabel')
        cmd_header.pack(anchor=tk.W, pady=(0, 5))
        
        # Commands listbox with scrollbar
        cmd_frame = tk.Frame(left_frame, bg=self.colors['bg'])
        cmd_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.command_history = tk.Listbox(cmd_frame,
                                         bg=self.colors['accent'],
                                         fg=self.colors['text'],
                                         selectbackground=self.colors['primary'],
                                         font=('Consolas', 10),
                                         height=12)
        
        cmd_scrollbar = tk.Scrollbar(cmd_frame, orient=tk.VERTICAL)
        self.command_history.config(yscrollcommand=cmd_scrollbar.set)
        cmd_scrollbar.config(command=self.command_history.yview)
        
        self.command_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cmd_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Responses section
        resp_header = ttk.Label(left_frame, text="JARVIS RESPONSES", style='Header.TLabel')
        resp_header.pack(anchor=tk.W, pady=(0, 5))
        
        # Responses text area
        resp_frame = tk.Frame(left_frame, bg=self.colors['bg'])
        resp_frame.pack(fill=tk.BOTH, expand=True)
        
        self.response_history = scrolledtext.ScrolledText(resp_frame,
                                                         bg=self.colors['accent'],
                                                         fg=self.colors['text'],
                                                         insertbackground=self.colors['primary'],
                                                         font=('Consolas', 10),
                                                         height=12,
                                                         state=tk.DISABLED)
        self.response_history.pack(fill=tk.BOTH, expand=True)
    
    def create_system_panel(self, parent):
        """Create system information panel"""
        # Right panel
        right_frame = tk.Frame(parent, bg=self.colors['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # System info header
        sys_header = ttk.Label(right_frame, text="SYSTEM METRICS", style='Header.TLabel')
        sys_header.pack(anchor=tk.W, pady=(0, 10))
        
        # System info frame
        self.system_info_frame = tk.Frame(right_frame, 
                                         bg=self.colors['accent'], 
                                         relief=tk.RAISED, 
                                         bd=2,
                                         width=300)
        self.system_info_frame.pack(fill=tk.BOTH, expand=True)
        self.system_info_frame.pack_propagate(False)
        
        # System info labels
        self.create_system_info_labels()
        
        # AI Status section
        ai_header = ttk.Label(right_frame, text="AI STATUS", style='Header.TLabel')
        ai_header.pack(anchor=tk.W, pady=(20, 5))
        
        ai_frame = tk.Frame(right_frame, 
                           bg=self.colors['accent'], 
                           relief=tk.RAISED, 
                           bd=2)
        ai_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.ai_status_label = ttk.Label(ai_frame, 
                                        text="Claude AI: Online\nOpenAI: Standby", 
                                        style='Info.TLabel',
                                        justify=tk.LEFT)
        self.ai_status_label.pack(pady=10)
    
    def create_system_info_labels(self):
        """Create system information display labels"""
        info_labels = [
            ("Time:", ""),
            ("CPU Usage:", "0%"),
            ("Memory:", "0%"),
            ("Disk Space:", "0%"),
            ("Network:", "Connected"),
            ("Uptime:", "00:00:00")
        ]
        
        self.info_labels = {}
        
        for label_text, default_value in info_labels:
            frame = tk.Frame(self.system_info_frame, bg=self.colors['accent'])
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            label = tk.Label(frame, 
                           text=label_text, 
                           bg=self.colors['accent'], 
                           fg=self.colors['secondary'],
                           font=('Arial', 10, 'bold'),
                           anchor=tk.W)
            label.pack(side=tk.LEFT)
            
            value_label = tk.Label(frame, 
                                 text=default_value, 
                                 bg=self.colors['accent'], 
                                 fg=self.colors['text'],
                                 font=('Arial', 10),
                                 anchor=tk.E)
            value_label.pack(side=tk.RIGHT)
            
            self.info_labels[label_text] = value_label
    
    def create_control_panel(self, parent):
        """Create control buttons panel"""
        control_frame = tk.Frame(parent, bg=self.colors['bg'])
        control_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Control buttons
        buttons = [
            ("Clear History", self.clear_displays),
            ("Save Log", self.save_interaction_log),
            ("Settings", self.open_settings),
            ("Exit", self.close_application)
        ]
        
        for button_text, command in buttons:
            btn = tk.Button(control_frame,
                           text=button_text,
                           command=command,
                           bg=self.colors['primary'],
                           fg=self.colors['bg'],
                           font=('Arial', 10, 'bold'),
                           relief=tk.FLAT,
                           padx=20,
                           pady=5)
            btn.pack(side=tk.LEFT, padx=5)
            
            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.colors['secondary']))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors['primary']))
    
    def start_update_thread(self):
        """Start the GUI update thread"""
        def update_loop():
            while self.running:
                try:
                    self.update_displays()
                    time.sleep(1)  # Update every second
                except Exception as e:
                    self.logger.error(f"Error in GUI update loop: {e}")
                    time.sleep(5)
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def update_displays(self):
        """Update all GUI displays"""
        if not self.root or not self.running:
            return
        
        try:
            # Update time
            current_time = datetime.now().strftime("%H:%M:%S")
            if "Time:" in self.info_labels:
                self.info_labels["Time:"].config(text=current_time)
            
            # Update system metrics (placeholder - would integrate with system_controller)
            # This would normally get real system data
            import random
            if "CPU Usage:" in self.info_labels:
                cpu_usage = f"{random.randint(10, 80)}%"
                self.info_labels["CPU Usage:"].config(text=cpu_usage)
            
            if "Memory:" in self.info_labels:
                mem_usage = f"{random.randint(30, 90)}%"
                self.info_labels["Memory:"].config(text=mem_usage)
                
        except Exception as e:
            self.logger.error(f"Error updating displays: {e}")
    
    def add_command(self, command):
        """Add a command to the display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        display_text = f"[{timestamp}] {command}"
        
        self.commands.append(display_text)
        
        if self.command_history:
            self.command_history.insert(tk.END, display_text)
            self.command_history.see(tk.END)
    
    def add_response(self, response):
        """Add a response to the display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        display_text = f"[{timestamp}] JARVIS: {response}\n"
        
        self.responses.append(display_text)
        
        if self.response_history:
            self.response_history.config(state=tk.NORMAL)
            self.response_history.insert(tk.END, display_text)
            self.response_history.see(tk.END)
            self.response_history.config(state=tk.DISABLED)
    
    def update_status(self, status):
        """Update the status display"""
        self.current_status = status
        if self.status_label:
            self.status_label.config(text=status)
    
    def clear_displays(self):
        """Clear command and response displays"""
        if self.command_history:
            self.command_history.delete(0, tk.END)
        
        if self.response_history:
            self.response_history.config(state=tk.NORMAL)
            self.response_history.delete(1.0, tk.END)
            self.response_history.config(state=tk.DISABLED)
        
        self.commands.clear()
        self.responses.clear()
    
    def save_interaction_log(self):
        """Save interaction history to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jarvis_log_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("JARVIS Interaction Log\n")
                f.write("=" * 50 + "\n\n")
                
                f.write("Commands:\n")
                for cmd in self.commands:
                    f.write(f"{cmd}\n")
                
                f.write("\nResponses:\n")
                for resp in self.responses:
                    f.write(f"{resp}")
            
            self.add_response(f"Interaction log saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving log: {e}")
            self.add_response("Failed to save interaction log")
    
    def open_settings(self):
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("JARVIS Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.colors['bg'])
        
        # Settings content (placeholder)
        settings_label = ttk.Label(settings_window, 
                                  text="Settings Panel", 
                                  style='Header.TLabel')
        settings_label.pack(pady=20)
        
        # Voice settings
        voice_frame = tk.LabelFrame(settings_window, 
                                   text="Voice Settings", 
                                   bg=self.colors['bg'], 
                                   fg=self.colors['text'])
        voice_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Volume slider
        tk.Label(voice_frame, 
                text="Voice Volume:", 
                bg=self.colors['bg'], 
                fg=self.colors['text']).pack(anchor=tk.W)
        
        volume_scale = tk.Scale(voice_frame, 
                               from_=0, 
                               to=100, 
                               orient=tk.HORIZONTAL,
                               bg=self.colors['bg'], 
                               fg=self.colors['text'])
        volume_scale.set(90)
        volume_scale.pack(fill=tk.X, padx=10, pady=5)
        
        # Speech rate slider
        tk.Label(voice_frame, 
                text="Speech Rate:", 
                bg=self.colors['bg'], 
                fg=self.colors['text']).pack(anchor=tk.W)
        
        rate_scale = tk.Scale(voice_frame, 
                             from_=100, 
                             to=300, 
                             orient=tk.HORIZONTAL,
                             bg=self.colors['bg'], 
                             fg=self.colors['text'])
        rate_scale.set(180)
        rate_scale.pack(fill=tk.X, padx=10, pady=5)
    
    def close_application(self):
        """Close the application"""
        self.running = False
        if self.root:
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Run the GUI main loop"""
        self.running = True
        self.create_gui()
        
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error in GUI main loop: {e}")
        finally:
            self.running = False

# Test function
if __name__ == "__main__":
    gui = JarvisGUI()
    
    # Test the GUI
    def test_gui():
        import time
        time.sleep(2)
        gui.add_command("open calculator")
        gui.add_response("Opening calculator, sir.")
        gui.update_status("Ready for commands")
    
    # Start test in separate thread
    test_thread = threading.Thread(target=test_gui, daemon=True)
    test_thread.start()
    
    gui.run()