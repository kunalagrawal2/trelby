#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test LMNT API key directly
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_lmnt_api():
    """Test LMNT API directly"""
    api_key = os.getenv('LMNT_API_KEY')
    
    if not api_key:
        print("❌ LMNT_API_KEY not found in environment variables")
        return False
    
    print(f"API Key found: {api_key[:10]}...")
    
    # Test the voices endpoint first (this should work if the key is valid)
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        print("Testing voices endpoint...")
        response = requests.get("https://api.lmnt.com/voices", headers=headers)
        print(f"Voices endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            voices = response.json()
            print(f"✅ API key is valid! Found {len(voices)} voices")
            for voice in voices[:3]:  # Show first 3 voices
                print(f"  - {voice.get('id', 'Unknown')}: {voice.get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Voices endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing voices endpoint: {e}")
        return False
    
    # Test synthesis endpoint
    try:
        print("\nTesting synthesis endpoint...")
        data = {
            'text': 'Hello, this is a test.',
            'voice': 'burt',
            'speed': 1.0,
            'stability': 0.5
        }
        
        response = requests.post("https://api.lmnt.com/synthesize", 
                               headers=headers, json=data)
        print(f"Synthesis endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Synthesis successful! Audio data length: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Synthesis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing synthesis: {e}")
        return False

def main():
    """Main test function"""
    print("LMNT API Key Test")
    print("=" * 30)
    
    success = test_lmnt_api()
    
    if success:
        print("\n✅ API key is working correctly!")
        print("The issue might be in the TTS service implementation.")
    else:
        print("\n❌ API key test failed")
        print("Please check:")
        print("1. Your LMNT API key is correct")
        print("2. Your account has sufficient credits")
        print("3. The API key hasn't expired")
        print("4. You're not hitting rate limits")

if __name__ == "__main__":
    main() 