#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup script for TTS functionality
"""

import os
import sys

def check_env_file():
    """Check if .env file exists and has the required API keys"""
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("❌ .env file not found")
        print("Creating .env file...")
        
        # Create .env file with placeholders
        with open(env_file, 'w') as f:
            f.write("# Trelby Configuration\n")
            f.write("ANTHROPIC_API_KEY=your_anthropic_api_key_here\n")
            f.write("LMNT_API_KEY=your_lmnt_api_key_here\n")
        
        print("✅ Created .env file with placeholders")
        print("Please edit the .env file and add your actual API keys")
        return False
    
    # Check if LMNT_API_KEY is set
    with open(env_file, 'r') as f:
        content = f.read()
        if 'LMNT_API_KEY=your_lmnt_api_key_here' in content or 'LMNT_API_KEY=' not in content:
            print("❌ LMNT_API_KEY not configured in .env file")
            print("Please add your LMNT API key to the .env file:")
            print("LMNT_API_KEY=your_actual_lmnt_api_key_here")
            return False
    
    print("✅ .env file found and LMNT_API_KEY is configured")
    return True

def test_tts_connection():
    """Test the TTS connection"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('LMNT_API_KEY')
        if not api_key or api_key == 'your_lmnt_api_key_here':
            print("❌ LMNT_API_KEY not properly configured")
            return False
        
        # Test basic TTS functionality
        import trelby.tts_service as tts_service
        
        print("Testing TTS connection...")
        tts = tts_service.TTSService()
        
        # Test with a simple text
        test_text = "Hello, this is a test."
        audio_data = tts.synthesize_speech(test_text, 'burt')
        
        if audio_data:
            print(f"✅ TTS connection successful ({len(audio_data)} bytes received)")
            return True
        else:
            print("❌ TTS synthesis failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing TTS: {e}")
        return False

def main():
    """Main setup function"""
    print("TTS Setup and Configuration")
    print("=" * 40)
    
    # Check .env file
    env_ok = check_env_file()
    
    if not env_ok:
        print("\nTo get your LMNT API key:")
        print("1. Visit https://lmnt.com/")
        print("2. Create an account")
        print("3. Get your API key from the dashboard")
        print("4. Add it to the .env file")
        print("\nThen run this script again to test the connection.")
        return
    
    # Test TTS connection
    print("\nTesting TTS connection...")
    tts_ok = test_tts_connection()
    
    if tts_ok:
        print("\n✅ TTS setup complete!")
        print("\nYou can now use the Table Read feature in Trelby:")
        print("1. Open Trelby")
        print("2. Load a screenplay")
        print("3. Click the Table Read (TTS) button in the toolbar")
        print("4. Configure voices and start reading")
    else:
        print("\n❌ TTS setup failed")
        print("Please check your LMNT API key and try again")

if __name__ == "__main__":
    main() 