# -*- coding: utf-8 -*-

from .anthropic import AnthropicService
from .groq import GroqService

def get_ai_service(service_name="anthropic", model=None):
    """
    Factory function to get an AI service instance.

    :param service_name: The name of the service to use (e.g., "anthropic", "groq").
    :param model: The model to use for the service.
    :return: An instance of the AI service.
    """
    if service_name == "anthropic":
        if model:
            return AnthropicService(model=model)
        return AnthropicService()
    elif service_name == "groq":
        if model:
            return GroqService(model=model)
        return GroqService()
    else:
        raise ValueError(f"Unknown AI service: {service_name}") 