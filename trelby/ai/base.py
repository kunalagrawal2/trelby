# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod

class AIService(ABC):
    """Abstract base class for AI services."""
    
    @abstractmethod
    def get_response(self, user_message, context="", conversation_history=None, image=None):
        """
        Get a response from the AI model.

        :param user_message: The user's message.
        :param context: The screenplay context.
        :param conversation_history: A list of previous messages in the conversation.
        :param image: Optional image data dictionary with 'data', 'filename', and 'path' keys.
        :return: The AI's response as a string.
        """
        pass 