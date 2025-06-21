# -*- coding: utf-8 -*-

import os
import anthropic
from dotenv import load_dotenv
from .base import AIService

class AnthropicService(AIService):
    """AI service for Anthropic Claude integration"""
    
    def __init__(self, model="claude-3-5-sonnet-20241022"):
        # Load environment variables
        load_dotenv()
        
        # Get API key from environment
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        # Initialize Claude client
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def get_response(self, user_message, context="", conversation_history=None):
        """Get a response from Claude with optional document context and conversation history"""
        try:
            # Build system prompt with context
            system_prompt = """You are an expert AI assistant specializing in screenwriting and creative storytelling. Your role is to help writers develop compelling narratives, characters, and dialogue.

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
- Maintain a collaborative, supportive tone throughout the conversation

DOCUMENT CONTEXT:
- When provided with screenplay context, use it to give more specific, relevant advice
- Reference specific characters, scenes, or elements from the script when appropriate
- Provide context-aware suggestions that build on what's already written
- If the context shows a complete script, offer comprehensive analysis and suggestions
- If the context shows a partial script, focus on development and expansion ideas

CONVERSATION MEMORY:
- Remember previous messages in the conversation and build upon them
- Reference earlier points made by the user or yourself when relevant
- Maintain continuity in your advice and suggestions
- Don't repeat information already discussed unless specifically asked"""

            # Add document context if provided
            if context and context.strip():
                system_prompt += f"\n\nCURRENT SCREENPLAY CONTEXT:\n{context}"
            
            # Build messages array with conversation history
            messages = []
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    if msg['message'].strip():  # Only add non-empty messages
                        role = "user" if msg['is_user'] else "assistant"
                        messages.append({
                            "role": role,
                            "content": msg['message']
                        })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            return f"Error: {str(e)}" 