# -*- coding: utf-8 -*-

import wx
import platform

def is_dark_mode():
    """
    Detect if the system is in dark mode.
    Returns True for dark mode, False for light mode.
    """
    try:
        # Try to detect system appearance using wxPython
        if hasattr(wx, 'SystemSettings') and hasattr(wx.SystemSettings, 'GetAppearance'):
            # wxPython 4.1+ has GetAppearance method
            appearance = wx.SystemSettings.GetAppearance()
            if hasattr(appearance, 'IsDark'):
                return appearance.IsDark()
        
        # Fallback: Check system colors on different platforms
        system = platform.system()
        
        if system == "Darwin":  # macOS
            # On macOS, we can check if the system is using dark mode
            # by looking at the appearance of system colors
            try:
                # Check if the system is using dark mode by examining
                # the color of the window background
                test_window = wx.Frame(None, -1, "Test")
                bg_color = test_window.GetBackgroundColour()
                test_window.Destroy()
                
                # If background is dark, assume dark mode
                # This is a heuristic - dark mode typically has darker backgrounds
                brightness = (bg_color.Red() + bg_color.Green() + bg_color.Blue()) / 3
                return brightness < 128
            except:
                pass
        
        elif system == "Windows":
            # On Windows, check if the system is using dark mode
            try:
                # Check the color of the window background
                test_window = wx.Frame(None, -1, "Test")
                bg_color = test_window.GetBackgroundColour()
                test_window.Destroy()
                
                # Windows dark mode typically has darker backgrounds
                brightness = (bg_color.Red() + bg_color.Green() + bg_color.Blue()) / 3
                return brightness < 128
            except:
                pass
        
        elif system == "Linux":
            # On Linux, check environment variables or system colors
            try:
                import os
                # Check for common dark mode environment variables
                if os.environ.get('GTK_THEME', '').lower().find('dark') != -1:
                    return True
                if os.environ.get('QT_STYLE_OVERRIDE', '').lower().find('dark') != -1:
                    return True
                
                # Fallback to checking system colors
                test_window = wx.Frame(None, -1, "Test")
                bg_color = test_window.GetBackgroundColour()
                test_window.Destroy()
                
                brightness = (bg_color.Red() + bg_color.Green() + bg_color.Blue()) / 3
                return brightness < 128
            except:
                pass
    
    except Exception:
        pass
    
    # Default to light mode if detection fails
    return False

def get_ai_pane_colors():
    """
    Get appropriate colors for the AI assistant pane based on system appearance.
    Returns a dictionary with color keys.
    """
    is_dark = is_dark_mode()
    
    if is_dark:
        return {
            'background': wx.Colour(45, 45, 45),      # Dark gray background
            'text': wx.Colour(230, 230, 230),         # Light gray text
            'input_background': wx.Colour(60, 60, 60), # Slightly lighter input background
            'input_text': wx.Colour(230, 230, 230),   # Light text for input
            'button_background': wx.Colour(70, 70, 70), # Button background
            'button_text': wx.Colour(230, 230, 230),  # Button text
            'border': wx.Colour(80, 80, 80),          # Border color
            'user_message_bg': wx.Colour(80, 120, 200), # User message background (blue)
            'ai_message_bg': wx.Colour(60, 60, 60),   # AI message background
        }
    else:
        return {
            'background': wx.Colour(248, 248, 248),   # Light gray background (original)
            'text': wx.Colour(50, 50, 50),            # Dark text
            'input_background': wx.Colour(255, 255, 255), # White input background
            'input_text': wx.Colour(50, 50, 50),      # Dark text for input
            'button_background': wx.Colour(240, 240, 240), # Button background
            'button_text': wx.Colour(50, 50, 50),     # Button text
            'border': wx.Colour(200, 200, 200),       # Border color
            'user_message_bg': wx.Colour(200, 220, 255), # User message background (light blue)
            'ai_message_bg': wx.Colour(255, 255, 255), # AI message background (white)
        } 