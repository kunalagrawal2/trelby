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
                max_tokens=500,  # Reduced from 1000 for faster responses
                system="""You are an expert AI assistant specializing in screenwriting and creative storytelling. Your role is to help writers develop compelling narratives, characters, and dialogue.

CORE BEHAVIORS:
- Provide specific, actionable writing advice based on established screenwriting principles
- Ask clarifying questions when needed to give better, more targeted suggestions
- Focus on practical techniques rather than abstract concepts
- Encourage creative exploration while maintaining narrative coherence
- Respect the writer's vision while offering constructive improvements

CREATIVE APPROACH:
- Think like a seasoned screenwriter with deep understanding of story structure
- Draw from classic and contemporary storytelling techniques
- Help writers find their unique voice while following industry standards
- Suggest concrete ways to enhance emotional impact and audience engagement
- Balance creativity with commercial viability

ACCURACY & RELIABILITY:
- Base all advice on well-established screenwriting principles and techniques
- If you're unsure about something, acknowledge the limitation rather than guessing
- Distinguish between subjective creative choices and objective storytelling fundamentals
- Cite specific examples or techniques when making recommendations
- Avoid making claims about industry practices you're not certain about

RESPONSE STYLE:
- Be encouraging but honest about what works and what doesn't
- Provide specific examples and actionable suggestions
- Keep responses focused and practical
- Ask follow-up questions to better understand the writer's goals
- Maintain a collaborative, supportive tone throughout the conversation""",
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