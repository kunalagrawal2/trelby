# AI Pane Appearance Adaptation

## Overview

The AI assistant pane now automatically adapts to your system's appearance settings (dark/light mode). This ensures that text is always readable regardless of your system theme preference.

## Features

### Automatic Detection
- **System Appearance Detection**: Automatically detects if your system is in dark or light mode
- **Cross-Platform Support**: Works on macOS, Windows, and Linux
- **Fallback Handling**: Gracefully handles cases where detection fails

### Color Adaptation
- **Dark Mode**: 
  - Dark backgrounds (45, 45, 45)
  - Light text (230, 230, 230)
  - Blue user messages (80, 120, 200)
  - Dark AI message backgrounds (60, 60, 60)

- **Light Mode**:
  - Light backgrounds (248, 248, 248)
  - Dark text (50, 50, 50)
  - Light blue user messages (200, 220, 255)
  - White AI message backgrounds (255, 255, 255)

### Real-time Updates
- **Dynamic Refresh**: Colors update automatically when you change system appearance
- **Event Handling**: Responds to system appearance change events
- **Smooth Transitions**: UI refreshes without interruption

## Implementation Details

### Files Modified
1. **`trelby/appearance_utils.py`** (new)
   - System appearance detection logic
   - Color scheme definitions
   - Cross-platform compatibility

2. **`trelby/ai_assistant.py`**
   - Updated to use appearance-aware colors
   - Added `refresh_appearance()` method
   - Integrated with color utility

3. **`trelby/trelbyframe.py`**
   - Added system appearance change event handler
   - Automatic refresh of AI panel colors

### Detection Methods
1. **wxPython 4.1+**: Uses `wx.SystemSettings.GetAppearance().IsDark()`
2. **macOS**: Analyzes window background color brightness
3. **Windows**: Checks system window background colors
4. **Linux**: Checks environment variables and system colors
5. **Fallback**: Defaults to light mode if detection fails

## Usage

The feature works automatically - no user configuration required:

1. **Start Trelby**: The AI pane will detect your system appearance
2. **Change System Theme**: Switch between dark/light mode in your system settings
3. **Automatic Update**: The AI pane colors will refresh automatically

## Testing

Run the test script to see the appearance detection in action:

```bash
python3 test_appearance.py
```

## Benefits

- **Accessibility**: Better readability in all lighting conditions
- **User Experience**: Consistent with system appearance preferences
- **Eye Comfort**: Reduces eye strain in dark environments
- **Modern UI**: Follows current design trends and user expectations

## Technical Notes

- **Modular Design**: Appearance detection is separated into a utility module
- **Simple Integration**: Easy to extend to other parts of the application
- **Performance**: Lightweight detection with minimal overhead
- **Compatibility**: Works with existing wxPython installations 