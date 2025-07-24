
"""
AI Integration Module for JARVIS
Handles integration with AI services like Claude and OpenAI GPT
"""

import requests
import json
import logging
import os
from datetime import datetime
import anthropic
import openai

class AIAssistant:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # API keys (set these as environment variables)
        self.claude_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize clients
        self.claude_client = None
        self.openai_client = None
        
        if self.claude_api_key:
            try:
                self.claude_client = anthropic.Anthropic(api_key=self.claude_api_key)
                self.logger.info("Claude client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Claude client: {e}")
        
        if self.openai_api_key:
            try:
                openai.api_key = self.openai_api_key
                self.openai_client = openai
                self.logger.info("OpenAI client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Conversation history
        self.conversation_history = []
        self.max_history_length = 10
        
        # JARVIS personality prompt
        self.jarvis_personality = """
        You are JARVIS, an advanced AI assistant like from Iron Man. You should:
        - Be intelligent, helpful, and efficient
        - Speak in a sophisticated but friendly manner
        - Address the user as "sir" or "boss" occasionally
        - Be concise but informative
        - Show personality while being professional
        - Act like you're part of an advanced technological system
        """
    
    def ask_claude(self, question, context=None):
        """Ask Claude AI a question"""
        if not self.claude_client:
            return "Claude AI is not available. Please set ANTHROPIC_API_KEY environment variable."
        
        try:
            # Prepare the prompt
            full_prompt = f"{self.jarvis_personality}\n\nUser: {question}"
            
            if context:
                full_prompt = f"{self.jarvis_personality}\n\nContext: {context}\n\nUser: {question}"
            
            # Add conversation history
            if self.conversation_history:
                history_text = "\n".join([f"User: {h['user']}\nJARVIS: {h['assistant']}" for h in self.conversation_history[-3:]])
                full_prompt = f"{self.jarvis_personality}\n\nRecent conversation:\n{history_text}\n\nUser: {question}"
            
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            answer = response.content[0].text
            
            # Add to conversation history
            self.add_to_history(question, answer)
            
            self.logger.info(f"Claude response generated for: {question[:50]}...")
            return answer
            
        except Exception as e:
            self.logger.error(f"Error with Claude AI: {e}")
            return "I'm having trouble connecting to my AI systems right now, sir."
    
    def ask_openai(self, question, context=None):
        """Ask OpenAI GPT a question"""
        if not self.openai_client:
            return "OpenAI is not available. Please set OPENAI_API_KEY environment variable."
        
        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": self.jarvis_personality}
            ]
            
            # Add conversation history
            for hist in self.conversation_history[-3:]:
                messages.append({"role": "user", "content": hist['user']})
                messages.append({"role": "assistant", "content": hist['assistant']})
            
            # Add context if provided
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            
            # Add current question
            messages.append({"role": "user", "content": question})
            
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            # Add to conversation history
            self.add_to_history(question, answer)
            
            self.logger.info(f"OpenAI response generated for: {question[:50]}...")
            return answer
            
        except Exception as e:
            self.logger.error(f"Error with OpenAI: {e}")
            return "I'm experiencing difficulties with my neural networks, sir."
    
    def ask_question(self, question, context=None, preferred_ai="claude"):
        """Ask a question using preferred AI service"""
        question = question.strip()
        
        if not question:
            return "I didn't catch that, sir. Could you repeat your question?"
        
        # Try preferred AI first
        if preferred_ai == "claude" and self.claude_client:
            return self.ask_claude(question, context)
        elif preferred_ai == "openai" and self.openai_client:
            return self.ask_openai(question, context)
        
        # Fallback to available AI
        if self.claude_client:
            return self.ask_claude(question, context)
        elif self.openai_client:
            return self.ask_openai(question, context)
        
        # If no AI available, provide basic responses
        return self.provide_basic_response(question)
    
    def provide_basic_response(self, question):
        """Provide basic responses when AI services are unavailable"""
        question_lower = question.lower()
        
        # Basic greeting responses
        if any(word in question_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return "Hello sir. How may I assist you today?"
        
        # Time-related queries
        if any(word in question_lower for word in ['time', 'date', 'day']):
            current_time = datetime.now().strftime("%I:%M %p on %B %d, %Y")
            return f"The current time is {current_time}, sir."
        
        # Weather (basic response)
        if 'weather' in question_lower:
            return "I would need to access weather services to provide that information, sir."
        
        # How are you
        if any(phrase in question_lower for phrase in ['how are you', 'how do you feel']):
            return "All systems are operating at optimal capacity, sir."
        
        # Default response
        return "I apologize, sir, but I need access to my AI systems to answer that question properly."
    
    def add_to_history(self, user_input, assistant_response):
        """Add interaction to conversation history"""
        self.conversation_history.append({
            'user': user_input,
            'assistant': assistant_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.logger.info("Conversation history cleared")
    
    def get_conversation_summary(self):
        """Get a summary of recent conversation"""
        if not self.conversation_history:
            return "No recent conversation history."
        
        summary_parts = []
        for interaction in self.conversation_history[-5:]:
            summary_parts.append(f"Q: {interaction['user'][:50]}...")
            summary_parts.append(f"A: {interaction['assistant'][:50]}...")
        
        return "\n".join(summary_parts)
    
    def analyze_command_intent(self, command):
        """Analyze command to determine intent"""
        command_lower = command.lower()
        
        # System control intents
        if any(word in command_lower for word in ['open', 'launch', 'start', 'run']):
            return {'type': 'system_control', 'action': 'open', 'confidence': 0.8}
        
        if any(word in command_lower for word in ['close', 'quit', 'exit', 'shutdown']):
            return {'type': 'system_control', 'action': 'close', 'confidence': 0.8}
        
        # Media control intents
        if any(word in command_lower for word in ['play', 'music', 'song', 'video']):
            return {'type': 'media_control', 'action': 'play', 'confidence': 0.8}
        
        # Information requests
        if any(word in command_lower for word in ['what', 'who', 'where', 'when', 'why', 'how']):
            return {'type': 'information_request', 'action': 'answer', 'confidence': 0.7}
        
        # Default to information request
        return {'type': 'information_request', 'action': 'answer', 'confidence': 0.5}
    
    def generate_contextual_response(self, command, system_result=None):
        """Generate a contextual response based on command and system result"""
        if system_result:
            context = f"The system executed a command with result: {system_result}"
            return self.ask_question(f"Provide a brief acknowledgment for: {command}", context)
        else:
            return self.ask_question(command)
    
    def set_personality_mode(self, mode):
        """Set different personality modes for JARVIS"""
        modes = {
            'professional': """You are JARVIS, a professional AI assistant. Be formal, efficient, and direct.""",
            'friendly': """You are JARVIS, a friendly AI assistant. Be warm, conversational, and helpful.""",
            'technical': """You are JARVIS, a technical AI assistant. Provide detailed, technical explanations.""",
            'iron_man': """You are JARVIS from Iron Man. Be sophisticated, slightly witty, and address the user as 'sir' or 'Mr. Stark'."""
        }
        
        if mode in modes:
            self.jarvis_personality = modes[mode]
            self.logger.info(f"Personality mode set to: {mode}")
            return f"Personality mode updated to {mode}, sir."
        else:
            return "Invalid personality mode. Available modes: professional, friendly, technical, iron_man."

# Test function
if __name__ == "__main__":
    ai = AIAssistant()
    
    print("Testing AI integration...")
    
    # Test basic response
    response = ai.ask_question("Hello, how are you?")
    print(f"Response: {response}")
    
    # Test command analysis
    intent = ai.analyze_command_intent("open calculator")
    print(f"Intent analysis: {intent}")
    
    # Test conversation history
    print(f"Conversation summary: {ai.get_conversation_summary()}")