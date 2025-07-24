"""
Text-to-Speech Module for JARVIS
Handles voice synthesis with realistic voice options
"""

import pyttsx3
import logging
import threading
from queue import Queue
import os
import subprocess
import platform

class TextToSpeech:
    def __init__(self, voice_id=0, rate=180, volume=0.9):
        self.logger = logging.getLogger(__name__)
        self.speech_queue = Queue()
        self.speaking = False
        
        # Initialize TTS engine
        try:
            self.engine = pyttsx3.init()
            self.setup_voice(voice_id, rate, volume)
            
            # Start speech worker thread
            self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
            self.speech_thread.start()
            
            self.logger.info("Text-to-speech initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None
    
    def setup_voice(self, voice_id=0, rate=180, volume=0.9):
        """Setup voice parameters"""
        if not self.engine:
            return
            
        try:
            voices = self.engine.getProperty('voices')
            
            if voices and len(voices) > voice_id:
                self.engine.setProperty('voice', voices[voice_id].id)
                self.logger.info(f"Voice set to: {voices[voice_id].name}")
            
            # Set speech rate (words per minute)
            self.engine.setProperty('rate', rate)
            
            # Set volume (0.0 to 1.0)
            self.engine.setProperty('volume', volume)
            
            self.logger.info(f"Voice settings: rate={rate}, volume={volume}")
            
        except Exception as e:
            self.logger.error(f"Error setting up voice: {e}")
    
    def speak(self, text, priority=False):
        """
        Add text to speech queue
        
        Args:
            text: Text to speak
            priority: If True, speak immediately (skip queue)
        """
        if not text or not isinstance(text, str):
            return
        
        if priority:
            self.speak_immediately(text)
        else:
            self.speech_queue.put(text)
    
    def speak_immediately(self, text):
        """Speak text immediately, interrupting current speech"""
        if not self.engine:
            print(f"JARVIS: {text}")  # Fallback to console output
            return
        
        try:
            self.engine.stop()  # Stop current speech
            self.engine.say(text)
            self.engine.runAndWait()
            
        except Exception as e:
            self.logger.error(f"Error in immediate speech: {e}")
            print(f"JARVIS: {text}")  # Fallback
    
    def _speech_worker(self):
        """Background worker to process speech queue"""
        while True:
            try:
                text = self.speech_queue.get()
                if text is None:  # Shutdown signal
                    break
                
                self.speaking = True
                self.logger.info(f"Speaking: {text}")
                
                if self.engine:
                    self.engine.say(text)
                    self.engine.runAndWait()
                else:
                    print(f"JARVIS: {text}")  # Fallback
                
                self.speaking = False
                self.speech_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error in speech worker: {e}")
                self.speaking = False
    
    def is_speaking(self):
        """Check if currently speaking"""
        return self.speaking or not self.speech_queue.empty()
    
    def wait_until_done(self):
        """Wait until all queued speech is complete"""
        self.speech_queue.join()
    
    def clear_queue(self):
        """Clear all pending speech"""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except:
                break
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.engine:
            self.engine.stop()
        self.clear_queue()
    
    def get_available_voices(self):
        """Get list of available voices"""
        if not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            voice_list = []
            
            for i, voice in enumerate(voices):
                voice_info = {
                    'id': i,
                    'name': voice.name,
                    'language': getattr(voice, 'languages', ['Unknown'])[0] if hasattr(voice, 'languages') else 'Unknown',
                    'gender': getattr(voice, 'gender', 'Unknown')
                }
                voice_list.append(voice_info)
            
            return voice_list
            
        except Exception as e:
            self.logger.error(f"Error getting voices: {e}")
            return []
    
    def change_voice(self, voice_id):
        """Change the current voice"""
        try:
            voices = self.engine.getProperty('voices')
            if voices and 0 <= voice_id < len(voices):
                self.engine.setProperty('voice', voices[voice_id].id)
                self.logger.info(f"Voice changed to: {voices[voice_id].name}")
                return True
            else:
                self.logger.error(f"Invalid voice ID: {voice_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error changing voice: {e}")
            return False
    
    def set_rate(self, rate):
        """Set speech rate"""
        try:
            self.engine.setProperty('rate', rate)
            self.logger.info(f"Speech rate set to: {rate}")
        except Exception as e:
            self.logger.error(f"Error setting rate: {e}")
    
    def set_volume(self, volume):
        """Set speech volume (0.0 to 1.0)"""
        try:
            volume = max(0.0, min(1.0, volume))  # Clamp between 0 and 1
            self.engine.setProperty('volume', volume)
            self.logger.info(f"Volume set to: {volume}")
        except Exception as e:
            self.logger.error(f"Error setting volume: {e}")
    
    def save_to_file(self, text, filename):
        """Save speech to audio file"""
        try:
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            self.logger.info(f"Speech saved to: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving to file: {e}")
            return False
    
    def shutdown(self):
        """Shutdown TTS engine"""
        self.speech_queue.put(None)  # Signal worker to stop
        if self.engine:
            self.engine.stop()

# Test function
if __name__ == "__main__":
    tts = TextToSpeech()
    
    print("Available voices:")
    voices = tts.get_available_voices()
    for voice in voices:
        print(f"  {voice['id']}: {voice['name']} ({voice['language']})")
    
    print("\nTesting TTS...")
    tts.speak("Hello sir, JARVIS text to speech system is now online and ready for operation.")
    tts.wait_until_done()
    
    print("TTS test complete")