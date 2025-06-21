# -*- coding: utf-8 -*-

from .ai import get_ai_service

class AIService:
    """AI service for Trelby"""
    
    def __init__(self, service_name="anthropic", model=None):
        self.service = get_ai_service(service_name, model)
    
    def get_response(self, user_message, context="", conversation_history=None, image=None):
        """Get a response from the configured AI service"""
        return self.service.get_response(user_message, context, conversation_history, image) 