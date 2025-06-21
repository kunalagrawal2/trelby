# -*- coding: utf-8 -*-

import os
import anthropic
from dotenv import load_dotenv

class AIService:
    """Simple AI service for Claude integration"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get API key from environment
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        print(f"Debug: API key loaded: {api_key[:10]}...{api_key[-4:]}")
        
        # Initialize Claude client
        self.client = anthropic.Anthropic(api_key=api_key)
        print("Debug: Claude client initialized successfully")
    
    def get_response(self, user_message):
        """Get a response from Claude"""
        try:
            print(f"Debug: Attempting API call with model: claude-3-5-sonnet-20241022")
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )
            print("Debug: API call successful")
            return response.content[0].text
        except Exception as e:
            print(f"Debug: API call failed with error: {e}")
            return f"Error: {str(e)}" 