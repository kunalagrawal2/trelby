#!/usr/bin/env python3
"""
Simple test script for LMNT API using the official lmnt library
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_lmnt_api():
    """Test the LMNT API with the official library"""
    
    api_key = os.getenv('LMNT_API_KEY')
    if not api_key:
        print("❌ No LMNT_API_KEY found in .env file")
        return False
    
    print(f"🔑 Using API key: {api_key[:10]}...")
    
    try:
        from lmnt.api import Speech
        
        print("📡 Testing LMNT API connection...")
        
        async with Speech(api_key) as speech:
            # Test voice synthesis
            print("🎤 Synthesizing test audio...")
            synthesis = await speech.synthesize('Hello world from Trelby!', 'brandon')
            
            # Save the audio file
            with open('test_output.mp3', 'wb') as f:
                f.write(synthesis['audio'])
            
            print("✅ Success! Audio saved as 'test_output.mp3'")
            
            # Test getting voices
            print("🎭 Fetching available voices...")
            voices = await speech.voices()
            print(f"✅ Found {len(voices)} voices")
            
            # Show some voice examples
            for voice in voices[:5]:  # Show first 5 voices
                print(f"  - {voice['id']}: {voice.get('name', 'N/A')}")
            
            return True
            
    except ImportError:
        print("❌ lmnt library not installed. Install with: pip install lmnt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing LMNT API with official library...")
    success = asyncio.run(test_lmnt_api())
    
    if success:
        print("\n🎉 LMNT API test successful!")
        print("The TTS service should now work properly in Trelby.")
    else:
        print("\n💥 LMNT API test failed!")
        print("Please check your API key and try again.") 