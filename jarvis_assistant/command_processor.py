
"""
Command Processor Module for JARVIS
Processes voice commands and routes them to appropriate modules
"""

import logging
import re
from datetime import datetime
import json

class CommandProcessor:
    def __init__(self, system_controller, ai_assistant, tts):
        self.logger = logging.getLogger(__name__)
        self.system_controller = system_controller
        self.ai_assistant = ai_assistant
        self.tts = tts
        
        # Command patterns and their handlers
        self.command_patterns = {
            # System control commands
            r'open\s+(.+)': self.handle_open_application,
            r'launch\s+(.+)': self.handle_open_application,
            r'start\s+(.+)': self.handle_open_application,
            r'run\s+(.+)': self.handle_open_application,
            
            r'close\s+(.+)': self.handle_close_application,
            r'quit\s+(.+)': self.handle_close_application,
            r'exit\s+(.+)': self.handle_close_application,
            
            # File operations
            r'open\s+file\s+(.+)': self.handle_open_file,
            r'open\s+folder\s+(.+)': self.handle_open_folder,
            r'create\s+folder\s+(.+)': self.handle_create_folder,
            r'create\s+a\s+folder\s+(.+)': self.handle_create_folder,
            r'make\s+folder\s+(.+)': self.handle_create_folder,
            r'new\s+folder\s+(.+)': self.handle_create_folder,
            r'delete\s+file\s+(.+)': self.handle_delete_file,
            r'search\s+for\s+(.+)': self.handle_search_files,
            
            # Media control - Updated patterns
            r'play\s+music\s*(.*)': self.handle_play_music,
            r'play\s+song\s*(.*)': self.handle_play_music,
            r'play\s+(.+)\s+on\s+youtube': self.handle_play_youtube,
            r'youtube\s+(.+)': self.handle_search_youtube,
            r'search\s+youtube\s+(.+)': self.handle_search_youtube,
            r'music\s*(.*)': self.handle_play_music,
            
            # Web commands
            r'open\s+website\s+(.+)': self.handle_open_website,
            r'go\s+to\s+(.+)': self.handle_open_website,
            r'browse\s+(.+)': self.handle_open_website,
            
            # System information
            r'system\s+info': self.handle_system_info,
            r'system\s+status': self.handle_system_info,
            r'how\s+is\s+the\s+system': self.handle_system_info,
            
            # Volume control - Fixed patterns
            r'set\s+volume\s+to\s+(\d+)': self.handle_set_volume,
            r'volume\s+(\d+)': self.handle_set_volume,
            r'set\s+volume\s+(\d+)': self.handle_set_volume,
            r'increase\s+volume': self.handle_increase_volume,
            r'decrease\s+volume': self.handle_decrease_volume,
            r'mute': self.handle_mute,
            
            # Screenshot
            r'take\s+screenshot': self.handle_screenshot,
            r'screenshot': self.handle_screenshot,
            r'capture\s+screen': self.handle_screenshot,
            
            # System power
            r'shutdown\s+system': self.handle_shutdown,
            r'restart\s+system': self.handle_restart,
            r'lock\s+screen': self.handle_lock_screen,
            
            # Time and date
            r'what\s+time\s+is\s+it': self.handle_time,
            r'current\s+time': self.handle_time,
            r'what\s+date\s+is\s+it': self.handle_date,
            r'current\s+date': self.handle_date,
            
            # Greetings and conversation
            r'hello\s*jarvis': self.handle_greeting,
            r'hi\s*jarvis': self.handle_greeting,
            r'hey\s*jarvis': self.handle_greeting,
            r'good\s+morning': self.handle_greeting,
            r'good\s+afternoon': self.handle_greeting,
            r'good\s+evening': self.handle_greeting,
            
            # JARVIS control
            r'clear\s+history': self.handle_clear_history,
            r'set\s+personality\s+(.+)': self.handle_set_personality,
            
            # Help
            r'help': self.handle_help,
            r'what\s+can\s+you\s+do': self.handle_help,
            r'commands': self.handle_help,
        }
        
        self.logger.info("Command processor initialized")
    
    def process_command(self, command):
        """Process a voice command and return response"""
        if not command:
            return "I didn't catch that, sir."
        
        command = command.lower().strip()
        self.logger.info(f"Processing command: {command}")
        
        # Try to match command patterns
        for pattern, handler in self.command_patterns.items():
            match = re.search(pattern, command)
            if match:
                try:
                    if match.groups():
                        response = handler(match.group(1))
                    else:
                        response = handler()
                    
                    self.logger.info(f"Command handled by {handler.__name__}")
                    return response
                    
                except Exception as e:
                    self.logger.error(f"Error handling command: {e}")
                    return "I encountered an error processing that command, sir."
        
        # If no pattern matches, send to AI for general conversation
        return self.handle_general_query(command)
    
    # System control handlers
    def handle_open_application(self, app_name):
        """Handle opening applications"""
        result = self.system_controller.open_application(app_name)
        return result
    
    def handle_close_application(self, app_name):
        """Handle closing applications"""
        result = self.system_controller.close_application(app_name)
        return result
    
    # File operation handlers
    def handle_open_file(self, file_path):
        """Handle opening files"""
        result = self.system_controller.open_file(file_path)
        return result
    
    def handle_open_folder(self, folder_path):
        """Handle opening folders"""
        result = self.system_controller.open_folder(folder_path)
        return result
    
    def handle_create_folder(self, folder_name):
        """Handle creating folders"""
        if not folder_name or folder_name.strip() == "":
            return "Please specify a folder name, sir. For example: 'create folder MyDocuments'"
        
        # Create folder in current directory or Desktop
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        folder_path = os.path.join(desktop_path, folder_name.strip())
        
        result = self.system_controller.create_folder(folder_path)
        return result
    
    def handle_delete_file(self, file_path):
        """Handle deleting files"""
        result = self.system_controller.delete_file(file_path)
        return result
    
    def handle_search_files(self, search_term):
        """Handle file searches"""
        results = self.system_controller.search_files(search_term)
        if results:
            return f"Found {len(results)} files matching '{search_term}', sir."
        else:
            return f"No files found matching '{search_term}', sir."
    
    # Media control handlers
    def handle_play_music(self, search_term=""):
        """Handle playing music"""
        if not search_term or search_term.strip() == "":
            # If no specific song, try to open music app or play any music
            result = self.system_controller.open_application("spotify")
            if "Could not find" in result:
                # Try other music apps
                music_apps = ["vlc", "windows media player", "groove music"]
                for app in music_apps:
                    result = self.system_controller.open_application(app)
                    if "Could not find" not in result:
                        return f"Opening {app} for music, sir."
                return "Opening default music application, sir."
            return result
        else:
            result = self.system_controller.find_and_play_music(search_term.strip())
            return result
    
    def handle_play_youtube(self, search_term):
        """Handle playing YouTube videos"""
        result = self.system_controller.play_youtube_video(search_term)
        return result
    
    def handle_search_youtube(self, search_term):
        """Handle YouTube searches"""
        result = self.system_controller.search_youtube(search_term)
        return result
    
    # Web handlers
    def handle_open_website(self, url):
        """Handle opening websites"""
        result = self.system_controller.open_website(url)
        return result
    
    # System information handlers
    def handle_system_info(self):
        """Handle system information requests"""
        info = self.system_controller.get_system_info()
        if info:
            response = f"System status: CPU at {info.get('cpu', 'unknown')}, "
            response += f"Memory at {info.get('memory', 'unknown')}, "
            response += f"Disk at {info.get('disk', 'unknown')}, sir."
            return response
        else:
            return "Unable to retrieve system information, sir."
    
    # Volume control handlers
    def handle_set_volume(self, level):
        """Handle setting volume to specific level"""
        try:
            # Clean the level string (remove % if present)
            level_str = str(level).replace('%', '').strip()
            volume_level = int(level_str)
            result = self.system_controller.adjust_volume(volume_level)
            return result
        except ValueError:
            return f"Invalid volume level '{level}', sir. Please specify a number between 0 and 100."
    
    def handle_increase_volume(self):
        """Handle increasing volume"""
        # This would need to get current volume first
        return "Increasing volume, sir."
    
    def handle_decrease_volume(self):
        """Handle decreasing volume"""
        # This would need to get current volume first
        return "Decreasing volume, sir."
    
    def handle_mute(self):
        """Handle muting audio"""
        result = self.system_controller.adjust_volume(0)
        return "Audio muted, sir."
    
    # Screenshot handler
    def handle_screenshot(self):
        """Handle taking screenshots"""
        result = self.system_controller.take_screenshot()
        return result
    
    # System power handlers
    def handle_shutdown(self):
        """Handle system shutdown"""
        result = self.system_controller.shutdown_system()
        return result
    
    def handle_restart(self):
        """Handle system restart"""
        result = self.system_controller.restart_system()
        return result
    
    def handle_lock_screen(self):
        """Handle screen lock"""
        result = self.system_controller.lock_screen()
        return result
    
    # Time and date handlers
    def handle_time(self):
        """Handle time requests"""
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}, sir."
    
    def handle_date(self):
        """Handle date requests"""
        current_date = datetime.now().strftime("%B %d, %Y")
        return f"Today is {current_date}, sir."
    
    # Conversation handlers
    def handle_greeting(self):
        """Handle greetings"""
        greetings = [
            "Hello sir, how may I assist you?",
            "Good to see you, sir. What can I do for you?",
            "At your service, sir.",
            "Hello sir, all systems ready.",
            "Greetings, sir. How may I be of assistance?"
        ]
        import random
        return random.choice(greetings)
    
    def handle_general_query(self, query):
        """Handle general queries using AI"""
        response = self.ai_assistant.ask_question(query)
        return response
    
    # JARVIS control handlers
    def handle_clear_history(self):
        """Handle clearing conversation history"""
        self.ai_assistant.clear_history()
        return "Conversation history cleared, sir."
    
    def handle_set_personality(self, mode):
        """Handle setting personality mode"""
        result = self.ai_assistant.set_personality_mode(mode)
        return result
    
    def handle_help(self):
        """Handle help requests"""
        help_text = """I can help you with:
        - Opening and closing applications
        - File and folder operations
        - Playing music and videos
        - Web browsing and YouTube
        - System control and information
        - Screenshots and volume control
        - General questions and conversation
        What would you like me to do, sir?"""
        return help_text
    
    def add_custom_command(self, pattern, handler):
        """Add a custom command pattern and handler"""
        self.command_patterns[pattern] = handler
        self.logger.info(f"Added custom command pattern: {pattern}")
    
    def remove_custom_command(self, pattern):
        """Remove a custom command pattern"""
        if pattern in self.command_patterns:
            del self.command_patterns[pattern]
            self.logger.info(f"Removed custom command pattern: {pattern}")
            return True
        return False
    
    def get_available_commands(self):
        """Get list of available command patterns"""
        return list(self.command_patterns.keys())
    
    def preprocess_command(self, command):
        """Preprocess command to handle common variations"""
        # Remove filler words
        filler_words = ['please', 'can you', 'could you', 'would you', 'jarvis']
        words = command.split()
        filtered_words = [word for word in words if word.lower() not in filler_words]
        
        return ' '.join(filtered_words)

# Test function
if __name__ == "__main__":
    # Mock objects for testing
    class MockSystemController:
        def open_application(self, app): return f"Opening {app}"
        def get_system_info(self): return {'cpu': '25%', 'memory': '60%', 'disk': '45%'}
    
    class MockTTS:
        def speak(self, text): print(f"TTS: {text}")
    
    processor = CommandProcessor(MockSystemController(), MockAI(), MockTTS())
    
    print("Testing command processor...")
    
    test_commands = [
        "open calculator",
        "play music coldplay",
        "what time is it",
        "system info",
        "hello jarvis"
    ]
    
    for cmd in test_commands:
        response = processor.process_command(cmd)
        print(f"Command: {cmd}")
        print(f"Response: {response}\n")