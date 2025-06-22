# Text-to-Speech (TTS) Setup Guide

## Overview

Trelby now includes text-to-speech functionality powered by LMNT, allowing you to have your screenplays read aloud with different voices for different characters.

## Features

- **Table Read**: Read entire screenplays with character-specific voices
- **Voice Mapping**: Assign different voices to characters
- **Real-time Progress**: Track reading progress with visual feedback
- **Voice Settings**: Configure narrator, male, female, and character-specific voices
- **Audio Playback**: Actual audio output (with optional audio libraries)

## Setup

### 1. Get LMNT API Key

1. Visit [LMNT](https://lmnt.com/)
2. Create an account and get your API key
3. Add the key to your `.env` file:
   ```
   LMNT_API_KEY=your_actual_lmnt_api_key_here
   ```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Optional Audio Libraries

For actual audio playback, install one of these libraries:

```bash
# Option 1: Pygame (recommended for cross-platform)
pip install pygame

# Option 2: PyAudio (alternative)
pip install pyaudio
```

If no audio library is installed, the system will simulate playback (useful for testing).

## Usage

### Basic Table Read

1. Open Trelby and load a screenplay
2. Click the **Table Read (TTS)** button in the toolbar (📖 icon)
3. The Table Read dialog will open with three tabs:
   - **Reading**: Start/stop reading and view progress
   - **Voice Settings**: Configure default voices
   - **Character Mapping**: Assign specific voices to characters

### Voice Configuration

#### Default Voices
- **Narrator/Action**: Voice for scene descriptions and action lines
- **Male Characters**: Default voice for male characters
- **Female Characters**: Default voice for female characters
- **Young Characters**: Voice for young characters
- **Old Characters**: Voice for older characters

#### Character-Specific Voices
- Each character in your screenplay can be assigned a specific voice
- Available voices: burt, donna, harry, lisa
- Characters without specific assignments use the default voice for their type

### Reading Options

- **Reading Speed**: Adjust how fast the text is read (50-200%)
- **Pause Between Segments**: Control pauses between dialogue and action

## Testing

Run the test script to verify your setup:

```bash
python test_tts.py
```

This will check:
- LMNT API key configuration
- TTS service connectivity
- Audio player initialization
- Text processing functionality

## Troubleshooting

### API Key Issues
- Ensure `LMNT_API_KEY` is set in your `.env` file
- Check that the API key is valid and has sufficient credits
- Verify internet connectivity

### Audio Playback Issues
- Install pygame or pyaudio for actual audio output
- Check system audio settings
- On Linux, you may need additional audio libraries

### Performance Issues
- Large screenplays may take time to process
- Consider reading scenes individually for better performance
- Adjust reading speed if needed

## Technical Details

### Supported File Formats
- All Trelby screenplay formats (.trelby)
- Imported formats (Final Draft, Fountain, etc.)

### Text Processing
- Automatically cleans screenplay formatting
- Removes technical markers like (CONT'D), (MORE)
- Converts (V.O.) to "voice over", (O.S.) to "off screen"
- Handles parentheticals appropriately

### Audio Output
- LMNT provides high-quality neural voices
- Audio is streamed in real-time
- Supports different voice characteristics and speeds

## API Reference

### TTSService Class
```python
from trelby.tts_service import TTSService

# Create service
tts = TTSService()

# Synthesize speech
audio_data = tts.synthesize_speech("Hello world", "burt")

# Read screenplay
tts.read_screenplay(screenplay_object)
```

### AudioPlayer Class
```python
from trelby.audio_player import get_audio_player

# Get player instance
player = get_audio_player()

# Play audio data
player.play_audio_data(audio_bytes)
```

## Support

For issues with:
- **LMNT API**: Contact LMNT support
- **Trelby TTS**: Check the main Trelby documentation
- **Audio playback**: Verify system audio configuration 