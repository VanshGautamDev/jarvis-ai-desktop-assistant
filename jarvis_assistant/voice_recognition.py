
"""
Voice Recognition Module for JARVIS
Handles speech-to-text conversion with wake word detection
"""

import speech_recognition as sr
import pyaudio
import logging
import time
from threading import Lock

class VoiceRecognizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.lock = Lock()
        
        # Adjust for ambient noise
        self.logger.info("Adjusting microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        # Recognition settings
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = None
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.8
        
        self.logger.info("Voice recognizer initialized")
    
    def listen(self, timeout=5, phrase_time_limit=None):
        """
        Listen for speech and convert to text
        
        Args:
            timeout: Maximum time to wait for speech
            phrase_time_limit: Maximum time for a single phrase
            
        Returns:
            str: Recognized text or None if no speech detected
        """
        with self.lock:
            try:
                with self.microphone as source:
                    # Listen for speech
                    self.logger.debug("Listening for speech...")
                    audio = self.recognizer.listen(
                        source, 
                        timeout=timeout, 
                        phrase_time_limit=phrase_time_limit
                    )
                
                # Convert speech to text
                self.logger.debug("Converting speech to text...")
                text = self.recognizer.recognize_google(audio)
                self.logger.info(f"Recognized: {text}")
                return text.lower()
                
            except sr.WaitTimeoutError:
                self.logger.debug("Listening timeout - no speech detected")
                return None
            except sr.UnknownValueError:
                self.logger.debug("Could not understand audio")
                return None
            except sr.RequestError as e:
                self.logger.error(f"Could not request results from speech recognition service: {e}")
                return None
            except Exception as e:
                self.logger.error(f"Error in voice recognition: {e}")
                return None
    
    def listen_continuously(self, callback, wake_word="hey jarvis"):
        """
        Continuously listen for wake word and commands
        
        Args:
            callback: Function to call when wake word is detected
            wake_word: Wake word to listen for
        """
        def listen_loop():
            while True:
                text = self.listen(timeout=1)
                if text and wake_word in text:
                    callback(text)
        
        import threading
        thread = threading.Thread(target=listen_loop, daemon=True)
        thread.start()
        return thread
    
    def test_microphone(self):
        """Test microphone functionality"""
        try:
            with self.microphone as source:
                self.logger.info("Testing microphone - say something...")
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio)
                self.logger.info(f"Microphone test successful. Heard: {text}")
                return True
        except Exception as e:
            self.logger.error(f"Microphone test failed: {e}")
            return False
    
    def set_energy_threshold(self, threshold):
        """Set energy threshold for speech detection"""
        self.recognizer.energy_threshold = threshold
        self.logger.info(f"Energy threshold set to {threshold}")
    
    def calibrate_microphone(self, duration=2):
        """Recalibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                self.logger.info(f"Calibrating microphone for {duration} seconds...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                self.logger.info("Microphone calibration complete")
                return True
        except Exception as e:
            self.logger.error(f"Microphone calibration failed: {e}")
            return False

# Test function
if __name__ == "__main__":
    recognizer = VoiceRecognizer()
    
    print("Testing voice recognition...")
    print("Say something (you have 10 seconds):")
    
    result = recognizer.listen(timeout=10)
    if result:
        print(f"You said: {result}")
    else:
        print("No speech detected or couldn't understand")