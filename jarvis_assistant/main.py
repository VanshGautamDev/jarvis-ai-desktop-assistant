
"""
JARVIS - AI Desktop Assistant
Main module that coordinates all components
"""

import threading
import time
import logging
from datetime import datetime
import sys
import os

# Import custom modules
from voice_recognition import VoiceRecognizer
from text_to_speech import TextToSpeech
from system_controller import SystemController
from ai_integration import AIAssistant
from gui_interface import JarvisGUI
from command_processor import CommandProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class JarvisAssistant:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.wake_word = "hey jarvis"
        self.listening_for_wake_word = True
        
        # Initialize components
        self.logger.info("Initializing JARVIS components...")
        try:
            self.voice_recognizer = VoiceRecognizer()
            self.tts = TextToSpeech()
            self.system_controller = SystemController()
            self.ai_assistant = AIAssistant()
            self.command_processor = CommandProcessor(
                self.system_controller, 
                self.ai_assistant, 
                self.tts
            )
            self.gui = JarvisGUI()
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            sys.exit(1)
    
    def start(self):
        """Start JARVIS assistant"""
        self.running = True
        self.logger.info("JARVIS is starting up...")
        
        # Welcome message
        welcome_msg = "JARVIS is online and ready for commands, sir."
        self.tts.speak(welcome_msg)
        
        # Start GUI in separate thread
        gui_thread = threading.Thread(target=self.gui.run, daemon=True)
        gui_thread.start()
        
        # Main listening loop
        self.main_loop()
    
    def main_loop(self):
        """Main listening and processing loop"""
        while self.running:
            try:
                if self.listening_for_wake_word:
                    # Listen for wake word
                    audio_text = self.voice_recognizer.listen()
                    
                    if audio_text and self.wake_word in audio_text.lower():
                        self.logger.info("Wake word detected")
                        self.tts.speak("Yes sir?")
                        self.listening_for_wake_word = False
                        self.gui.update_status("Listening for command...")
                        
                else:
                    # Listen for actual command
                    command = self.voice_recognizer.listen(timeout=10)
                    
                    if command:
                        self.logger.info(f"Command received: {command}")
                        self.gui.add_command(command)
                        
                        # Process command
                        response = self.command_processor.process_command(command)
                        
                        if response:
                            self.tts.speak(response)
                            self.gui.add_response(response)
                    
                    # Return to wake word listening
                    self.listening_for_wake_word = True
                    self.gui.update_status("Listening for wake word...")
                    
            except KeyboardInterrupt:
                self.logger.info("Shutdown requested")
                self.shutdown()
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(1)
    
    def shutdown(self):
        """Shutdown JARVIS gracefully"""
        self.running = False
        self.tts.speak("JARVIS is shutting down. Goodbye sir.")
        self.logger.info("JARVIS shutdown complete")

def main():
    """Main entry point"""
    jarvis = JarvisAssistant()
    
    try:
        jarvis.start()
    except KeyboardInterrupt:
        jarvis.shutdown()

if __name__ == "__main__":
    main()