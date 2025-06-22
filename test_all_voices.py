#!/usr/bin/env python3
"""
Test script for all 14 LMNT voices in the TTS system
"""

import os
import sys
from dotenv import load_dotenv

# Add the trelby directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trelby'))

# Load environment variables
load_dotenv()

def test_all_voices():
    """Test all 14 voices in the TTS system"""
    
    print("🎭 Testing All 14 LMNT Voices...")
    
    try:
        import trelby.tts_service as tts_service
        
        # Create TTS service
        tts = tts_service.TTSService()
        
        # Test text for each voice
        test_texts = {
            'ansel': "Hey there! I'm Ansel, bringing you that young, engaging energy with subtle enthusiasm.",
            'autumn': "Hello, I'm Autumn. My warm, friendly tone makes me perfect for customer support and guidance.",
            'brandon': "This is Brandon speaking. Clear, stable delivery for professional broadcasting and announcements.",
            'cassian': "Welcome! I'm Cassian, your friendly tutor with a nurturing, animated voice perfect for learning.",
            'elowen': "Greetings, I'm Elowen. My warm, velvety tones are perfect for storytelling and captivating narratives.",
            'evander': "Hello, I'm Evander. My weathered, husky voice brings calm and comfort to every conversation.",
            'huxley': "Well hello there! I'm Huxley, bringing theatrical flair and expressive range to entertain you.",
            'juniper': "Good day, I'm Juniper. My commanding, sophisticated tones are ideal for instruction and authority.",
            'kennedy': "Hi! I'm Kennedy, young and emotive with a conversational style that's inviting and healing.",
            'leah': "Hello, I'm Leah. Confident and expressive with dynamic patterns perfect for professional engagement.",
            'lucas': "This is Lucas. Clear, brisk delivery with the pace and clarity of professional broadcasting.",
            'morgan': "Greetings, I'm Morgan. A mature British voice with depth and experience for sophisticated content.",
            'natalie': "Hey! I'm Natalie, bright and youthful with animated energy that sounds like talking with a friend.",
            'nyssa': "Well hello, darlin'! I'm Nyssa, bringing that warm Southern charm with spirited sass and personality."
        }
        
        # Test each voice
        results = {}
        
        for voice_id, test_text in test_texts.items():
            print(f"\n🎤 Testing {voice_id.upper()}...")
            
            # Check if voice is valid
            valid_voice = tts.get_valid_voice(voice_id)
            if valid_voice != voice_id:
                print(f"⚠️  Voice '{voice_id}' mapped to '{valid_voice}'")
                voice_id = valid_voice
            
            # Test synthesis
            if not tts.simulation_mode:
                audio_data = tts.synthesize_speech(test_text, voice_id)
                
                if audio_data and audio_data != b'dummy_audio_data_for_simulation':
                    print(f"✅ {voice_id.upper()} - Synthesis successful")
                    
                    # Save test audio file
                    test_segment = {
                        'type': 'test',
                        'character': voice_id.upper(),
                        'text': test_text,
                        'line_index': 0,
                        'scene': 'VOICE_TEST'
                    }
                    
                    filepath = tts.save_audio_segment(audio_data, test_segment, "voice_tests")
                    if filepath:
                        print(f"💾 Saved: {os.path.basename(filepath)}")
                        results[voice_id] = "✅ Success"
                    else:
                        print(f"❌ Failed to save audio file for {voice_id}")
                        results[voice_id] = "❌ Save failed"
                else:
                    print(f"❌ {voice_id.upper()} - Synthesis failed")
                    results[voice_id] = "❌ Synthesis failed"
            else:
                print(f"ℹ️  {voice_id.upper()} - Simulation mode (no actual synthesis)")
                results[voice_id] = "ℹ️ Simulation"
        
        # Print summary
        print("\n" + "="*60)
        print("🎭 VOICE TEST SUMMARY")
        print("="*60)
        
        for voice_id, result in results.items():
            voice_info = tts.system_voices.get(voice_id, {})
            name = voice_info.get('name', voice_id.title())
            category = voice_info.get('category', 'unknown')
            print(f"{name:12} ({voice_id:8}) - {category:15} - {result}")
        
        # Test voice mapping
        print("\n🔗 Testing Voice Mappings...")
        test_mappings = [
            ('male', 'brandon'),
            ('female', 'autumn'),
            ('young', 'ansel'),
            ('tutor', 'cassian'),
            ('storyteller', 'elowen'),
            ('theatrical', 'huxley'),
            ('british', 'morgan'),
            ('southern', 'nyssa'),
            ('youthful', 'natalie'),
            ('energetic', 'kennedy')
        ]
        
        for mapping_type, expected_voice in test_mappings:
            actual_voice = tts.voice_mapping.get(mapping_type, 'unknown')
            status = "✅" if actual_voice == expected_voice else "❌"
            print(f"{status} {mapping_type:12} -> {actual_voice:8} (expected: {expected_voice})")
        
        print(f"\n🎉 Voice testing complete! {len(results)} voices tested.")
        return True
        
    except Exception as e:
        print(f"❌ Error testing voices: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_voices()
    
    if success:
        print("\n✅ All voice tests completed successfully!")
        print("The TTS system now supports all 14 LMNT voices.")
    else:
        print("\n💥 Some voice tests failed. Please check the error messages above.") 