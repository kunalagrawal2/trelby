#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple test script for TTS functionality (no wx dependency)
"""

import os
import sys
from dotenv import load_dotenv

# Add the trelby directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trelby'))

# Load environment variables
load_dotenv()

def test_tts_service():
    """Test the TTS service without wx dependencies"""
    try:
        import trelby.tts_service as tts_service
        
        print("Testing TTS Service...")
        
        # Check if API key is available
        api_key = os.getenv('LMNT_API_KEY')
        if not api_key:
            print("❌ LMNT_API_KEY not found in environment variables")
            print("Please add your LMNT API key to the .env file")
            return False
        
        print("✅ LMNT_API_KEY found")
        
        # Create TTS service
        tts = tts_service.TTSService()
        print("✅ TTS Service created successfully")
        
        # Test voice synthesis
        test_text = "Hello, this is a test of the text-to-speech system."
        print(f"Testing synthesis with text: '{test_text}'")
        
        audio_data = tts.synthesize_speech(test_text, 'burt')
        if audio_data:
            print(f"✅ Speech synthesis successful ({len(audio_data)} bytes)")
            
            # Test text cleaning
            test_screenplay_text = "JOHN (CONT'D)\nThis is some dialogue with (parenthetical) text."
            cleaned = tts.clean_text_for_tts(test_screenplay_text)
            print(f"✅ Text cleaning test: '{cleaned}'")
            
            return True
        else:
            print("❌ Speech synthesis failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing TTS service: {e}")
        return False

def test_audio_player():
    """Test the audio player without wx dependencies"""
    try:
        import trelby.audio_player as audio_player
        
        print("\nTesting Audio Player...")
        
        player = audio_player.get_audio_player()
        print("✅ Audio player created")
        
        # Check if any audio library is available
        if audio_player.PYGAME_AVAILABLE:
            print("✅ Pygame available for audio playback")
        elif audio_player.PYAUDIO_AVAILABLE:
            print("✅ PyAudio available for audio playback")
        else:
            print("⚠️  No audio library available - playback will be simulated")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing audio player: {e}")
        return False

def test_screenplay_parsing():
    """Test screenplay text extraction"""
    try:
        print("\nTesting Screenplay Parsing...")
        
        # Create a simple mock screenplay structure
        class MockLine:
            def __init__(self, lt, lb, text):
                self.lt = lt
                self.lb = lb
                self.text = text
        
        class MockScreenplay:
            def __init__(self):
                self.lines = [
                    MockLine(1, 5, "INT. ROOM - DAY"),  # SCENE
                    MockLine(2, 5, "John enters the room."),  # ACTION
                    MockLine(3, 5, "JOHN"),  # CHARACTER
                    MockLine(4, 5, "Hello, how are you?"),  # DIALOGUE
                    MockLine(5, 5, "(nervously)"),  # PAREN
                    MockLine(4, 5, "I'm doing well."),  # DIALOGUE
                ]
        
        import trelby.tts_service as tts_service
        tts = tts_service.TTSService()
        
        mock_sp = MockScreenplay()
        segments = tts.extract_screenplay_text(mock_sp)
        
        print(f"✅ Extracted {len(segments)} segments from mock screenplay")
        for i, segment in enumerate(segments):
            print(f"   Segment {i+1}: {segment['character']} - {segment['text'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing screenplay parsing: {e}")
        return False

def main():
    """Main test function"""
    print("TTS Functionality Test (Simple)")
    print("=" * 50)
    
    # Test TTS service
    tts_ok = test_tts_service()
    
    # Test audio player
    audio_ok = test_audio_player()
    
    # Test screenplay parsing
    parsing_ok = test_screenplay_parsing()
    
    print("\n" + "=" * 50)
    if tts_ok and audio_ok and parsing_ok:
        print("✅ All tests passed! TTS functionality is ready.")
        print("\nTo use the table read feature:")
        print("1. Open Trelby")
        print("2. Load a screenplay")
        print("3. Click the Table Read (TTS) button in the toolbar")
        print("4. Configure voices and start reading")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("- Make sure LMNT_API_KEY is set in your .env file")
        print("- Install optional audio libraries: pip install pygame pyaudio")
        print("- Check your internet connection for API calls")

if __name__ == "__main__":
    main() 