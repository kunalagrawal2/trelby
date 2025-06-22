#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Detailed LMNT API test
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_detailed():
    """Test LMNT API with detailed debugging"""
    api_key = os.getenv('LMNT_API_KEY')
    
    print("=== Detailed LMNT API Test ===")
    print(f"API Key from .env: {api_key}")
    print(f"API Key length: {len(api_key) if api_key else 0}")
    print(f"API Key starts with 'ak_': {api_key.startswith('ak_') if api_key else False}")
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    # Test 1: Voices endpoint
    print("\n--- Test 1: Voices Endpoint ---")
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print(f"Headers: {headers}")
    
    try:
        response = requests.get("https://api.lmnt.com/voices", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            voices = response.json()
            print(f"✅ Voices endpoint successful! Found {len(voices)} voices")
            return True
        else:
            print(f"❌ Voices endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing voices endpoint: {e}")
        return False
    
    # Test 2: Synthesis endpoint
    print("\n--- Test 2: Synthesis Endpoint ---")
    data = {
        'text': 'Hello, this is a test.',
        'voice': 'brandon',
        'speed': 1.0,
        'stability': 0.5
    }
    
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post("https://api.lmnt.com/synthesize", 
                               headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"✅ Synthesis successful! Audio data length: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Synthesis failed with status {response.status_code}")
            print(f"Response Text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing synthesis: {e}")
        return False

def test_alternative_approaches():
    """Test alternative approaches to see if the API key works"""
    print("\n=== Alternative API Tests ===")
    
    api_key = os.getenv('LMNT_API_KEY')
    
    # Test with different header formats
    test_headers = [
        {'Authorization': f'Bearer {api_key}'},
        {'Authorization': f'bearer {api_key}'},
        {'Authorization': api_key},
        {'X-API-Key': api_key},
    ]
    
    for i, headers in enumerate(test_headers):
        print(f"\n--- Test {i+1}: {headers} ---")
        try:
            response = requests.get("https://api.lmnt.com/voices", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ This header format works!")
                return True
        except Exception as e:
            print(f"Error: {e}")
    
    return False

def main():
    """Main test function"""
    print("LMNT API Detailed Test")
    print("=" * 50)
    
    # Test 1: Detailed API test
    success1 = test_api_detailed()
    
    # Test 2: Alternative approaches
    success2 = test_alternative_approaches()
    
    print("\n" + "=" * 50)
    if success1 or success2:
        print("✅ API key is working!")
        print("The issue might be in the TTS service implementation.")
    else:
        print("❌ API key is not working")
        print("\nPossible issues:")
        print("1. API key is invalid or expired")
        print("2. Account has no credits")
        print("3. API key format is incorrect")
        print("4. Network connectivity issues")
        print("5. LMNT service is down")

if __name__ == "__main__":
    main() 