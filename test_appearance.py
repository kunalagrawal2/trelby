#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to demonstrate the appearance-aware AI pane colors.
This script shows how the colors adapt to system dark/light mode.
"""

import sys
import os

# Add the trelby directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trelby'))

try:
    from trelby.appearance_utils import is_dark_mode, get_ai_pane_colors
    
    print("=== AI Pane Appearance Detection Test ===")
    print()
    
    # Test dark mode detection
    dark_mode = is_dark_mode()
    print(f"System Dark Mode Detected: {dark_mode}")
    print()
    
    # Get colors for the current appearance
    colors = get_ai_pane_colors()
    print("AI Pane Colors:")
    for key, color in colors.items():
        print(f"  {key}: RGB({color.Red()}, {color.Green()}, {color.Blue()})")
    print()
    
    # Show what the colors would look like in different modes
    print("=== Color Preview ===")
    if dark_mode:
        print("Current mode: DARK")
        print("Text will be light colored for better visibility")
        print("Background will be dark to reduce eye strain")
    else:
        print("Current mode: LIGHT") 
        print("Text will be dark colored for traditional appearance")
        print("Background will be light for familiar interface")
    
    print()
    print("The AI assistant pane will automatically adapt to your system settings!")
    print("If you change your system appearance (dark/light mode),")
    print("the AI pane will refresh its colors automatically.")
    
except ImportError as e:
    print(f"Import error: {e}")
    print("This test requires wxPython to be installed.")
    print("The appearance detection will work when running the full Trelby application.")
except Exception as e:
    print(f"Error: {e}") 