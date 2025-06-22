#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug TTS service to find the issue
"""

import os
import sys
from dotenv import load_dotenv

# Add the trelby directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trelby'))

# Load environment variables
load_dotenv()

def debug_api_key():
    """Debug API key reading"""
    print("=== API Key Debug ===")
    
    # Method 1: Direct os.getenv
    api_key1 = os.getenv('LMNT_API_KEY')
    print(f"Method 1 (os.getenv): {api_key1[:10] if api_key1 else 'None'}...")
    
    # Method 2: Read from .env file directly
    try:
        with open('.env', 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('LMNT_API_KEY='):
                    api_key2 = line.split('=', 1)[1].strip()
                    print(f"Method 2 (direct file read): {api_key2[:10]}...")
                    break
    except Exception as e:
        print(f"Error reading .env file: {e}")
    
    # Method 3: Check if there are any hidden characters
    if api_key1:
        print(f"API key length: {len(api_key1)}")
        print(f"API key bytes: {api_key1.encode()}")
        print(f"API key starts with 'ak_': {api_key1.startswith('ak_')}")

def test_tts_service_directly():
    """Test TTS service directly"""
    print("\n=== TTS Service Test ===")
    
    try:
        import trelby.tts_service as tts_service
        
        # Create TTS service
        print("Creating TTS service...")
        tts = tts_service.TTSService()
        print("✅ TTS service created")
        
        # Test synthesis
        print("Testing synthesis...")
        test_text = "Hello, this is a test."
        audio_data = tts.synthesize_speech(test_text, 'burt')
        
        if audio_data:
            print(f"✅ Synthesis successful: {len(audio_data)} bytes")
        else:
            print("❌ Synthesis failed")
            
    except Exception as e:
        print(f"❌ Error in TTS service: {e}")
        import traceback
        traceback.print_exc()

def test_requests_directly():
    """Test requests directly with the same headers"""
    print("\n=== Direct Requests Test ===")
    
    import requests
    
    api_key = os.getenv('LMNT_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print(f"Using headers: {headers}")
    
    try:
        # Test voices endpoint
        print("Testing voices endpoint...")
        response = requests.get("https://api.lmnt.com/voices", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Voices endpoint works")
        else:
            print("❌ Voices endpoint failed")
            
    except Exception as e:
        print(f"❌ Error in requests: {e}")

def main():
    """Main debug function"""
    print("TTS Debug Session")
    print("=" * 50)
    
    debug_api_key()
    test_requests_directly()
    test_tts_service_directly()

if __name__ == "__main__":
    main() 