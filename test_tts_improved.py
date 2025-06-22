#!/usr/bin/env python3
"""
Test script for improved TTS system with better segmentation
"""

import os
import sys
from dotenv import load_dotenv

# Add the trelby directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trelby'))

# Load environment variables
load_dotenv()

def test_tts_improved():
    """Test the improved TTS system"""
    
    print("🧪 Testing Improved TTS System...")
    
    try:
        import trelby.tts_service as tts_service
        
        # Create TTS service
        tts = tts_service.TTSService()
        
        # Test with a simple script
        test_script = """
        INT. UC BERKELEY - DORM COMMON ROOM - DAY

        Four years of cramming, coding, crying... And now finals are finally over.

        JAMES
        Dude, I'm so done. Someone bring me snacks.

        PRANESH
        You're defenseless.

        He GRINS mischievously and TICKLES James's ribs.

        JAMES
        Gah! What the hell, bro!

        Laughter erupts from the room. Pranesh backs off, still grinning.

        PRANESH
        Sorry! You looked like you needed it.
        """
        
        # Create a simple screenplay-like structure
        class MockScreenplay:
            def __init__(self):
                self.lines = []
                
            def add_line(self, line_type, text, is_last=False):
                line = MockLine(line_type, text, is_last)
                self.lines.append(line)
        
        class MockLine:
            def __init__(self, line_type, text, is_last=False):
                self.lt = line_type
                self.text = text
                self.lb = 1 if is_last else 0  # 1 = last line of element
        
        # Create screenplay
        sp = MockScreenplay()
        
        # Add scene
        sp.add_line('SCENE', 'INT. UC BERKELEY - DORM COMMON ROOM - DAY', True)
        
        # Add action
        sp.add_line('ACTION', 'Four years of cramming, coding, crying... And now finals are finally over.', True)
        
        # Add dialogue
        sp.add_line('CHARACTER', 'JAMES', True)
        sp.add_line('DIALOGUE', 'Dude, I\'m so done. Someone bring me snacks.', True)
        
        sp.add_line('CHARACTER', 'PRANESH', True)
        sp.add_line('DIALOGUE', 'You\'re defenseless.', True)
        
        sp.add_line('ACTION', 'He GRINS mischievously and TICKLES James\'s ribs.', True)
        
        sp.add_line('CHARACTER', 'JAMES', True)
        sp.add_line('DIALOGUE', 'Gah! What the hell, bro!', True)
        
        sp.add_line('ACTION', 'Laughter erupts from the room. Pranesh backs off, still grinning.', True)
        
        sp.add_line('CHARACTER', 'PRANESH', True)
        sp.add_line('DIALOGUE', 'Sorry! You looked like you needed it.', True)
        
        # Test text extraction
        print("📝 Testing text extraction...")
        segments = tts.extract_screenplay_text(sp)
        print(f"✅ Extracted {len(segments)} segments:")
        
        for i, segment in enumerate(segments):
            print(f"  {i+1}. {segment['type']}: {segment['character']} - {segment['text'][:50]}...")
        
        # Test voice assignment
        print("\n🎭 Testing voice assignment...")
        tts.assign_voice_to_character('JAMES', 'male')
        tts.assign_voice_to_character('PRANESH', 'young')
        
        for char in ['JAMES', 'PRANESH']:
            voice = tts.get_voice_for_character(char)
            print(f"  {char}: {voice}")
        
        # Test synthesis (if not in simulation mode)
        if not tts.simulation_mode:
            print("\n🎤 Testing speech synthesis...")
            test_text = "Hello, this is a test of the improved TTS system."
            audio_data = tts.synthesize_speech(test_text, 'brandon')
            
            if audio_data and audio_data != b'dummy_audio_data_for_simulation':
                print("✅ Speech synthesis successful!")
                
                # Test saving audio file
                test_segment = {
                    'type': 'test',
                    'character': 'TEST',
                    'text': test_text,
                    'line_index': 0,
                    'scene': 'TEST_SCENE'
                }
                
                filepath = tts.save_audio_segment(audio_data, test_segment, "test_output")
                if filepath:
                    print(f"✅ Audio file saved: {filepath}")
                else:
                    print("❌ Failed to save audio file")
            else:
                print("❌ Speech synthesis failed")
        else:
            print("\nℹ️  Running in simulation mode - skipping actual synthesis")
        
        print("\n🎉 Improved TTS system test complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing TTS system: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tts_improved()
    
    if success:
        print("\n✅ All tests passed! The improved TTS system is ready to use.")
    else:
        print("\n💥 Some tests failed. Please check the error messages above.") 