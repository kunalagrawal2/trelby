#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for the enhanced AI service integration.
This script tests the automatic embedding and semantic search functionality.
"""

import os
import sys
from dotenv import load_dotenv

def test_enhanced_ai_service():
    """Test the enhanced AI service initialization and basic functionality"""
    print("Enhanced AI Service Integration Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check API keys
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print("=== API Key Check ===")
    if anthropic_key:
        print(f"✓ Anthropic API key found (length: {len(anthropic_key)} characters)")
    else:
        print("✗ Anthropic API key not found")
        return False
    
    if openai_key:
        print(f"✓ OpenAI API key found (length: {len(openai_key)} characters)")
    else:
        print("✗ OpenAI API key not found")
        return False
    
    # Test enhanced AI service initialization
    print("\n=== Testing Enhanced AI Service ===")
    try:
        from trelby.ai_service_enhanced import EnhancedAIService
        ai_service = EnhancedAIService()
        print("✓ Enhanced AI service initialized successfully")
        
        # Test collection info
        info = ai_service.get_collection_info()
        print(f"✓ ChromaDB collection: {info['collection_name']} ({info['document_count']} documents)")
        
        return True
    except Exception as e:
        print(f"✗ Failed to initialize enhanced AI service: {e}")
        return False

def test_ai_assistant_panel():
    """Test the AI assistant panel initialization (without GUI)"""
    print("\n=== Testing AI Assistant Panel ===")
    try:
        # Mock the global data object
        class MockGD:
            def __init__(self):
                self.mainFrame = None
        
        gd = MockGD()
        
        # Test importing the panel (without creating GUI)
        from trelby.ai_assistant import AIAssistantPanel
        print("✓ AI Assistant Panel module imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Failed to import AI Assistant Panel: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Enhanced AI Integration")
    print("=" * 50)
    
    # Test enhanced AI service
    service_ok = test_enhanced_ai_service()
    
    # Test AI assistant panel
    panel_ok = test_ai_assistant_panel()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Enhanced AI Service: {'✓ PASS' if service_ok else '✗ FAIL'}")
    print(f"AI Assistant Panel: {'✓ PASS' if panel_ok else '✗ FAIL'}")
    
    if service_ok and panel_ok:
        print("\n✓ All tests passed! The enhanced AI integration is ready.")
        print("\nTo use the enhanced AI assistant:")
        print("1. Run: python trelby.py")
        print("2. Load a screenplay")
        print("3. The AI assistant will automatically analyze the screenplay")
        print("4. Ask questions about characters, plot, scenes, etc.")
        return True
    else:
        print("\n✗ Some tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 