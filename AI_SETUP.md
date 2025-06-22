# AI Assistant Setup Guide

## Quick Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create .env file:**
   ```bash
   echo "ANTHROPIC_API_KEY=your_actual_api_key_here" > .env
   echo "LMNT_API_KEY=your_lmnt_api_key_here" >> .env
   ```

3. **Get your API keys:**
   - **Claude API key**: Go to https://console.anthropic.com/
   - **LMNT API key**: Go to https://lmnt.com/ to get your API key for text-to-speech
   - Replace the placeholder values in the .env file

4. **Run Trelby:**
   ```bash
   python3 trelby.py
   ```

## Features

- **AI Assistant Panel**: Right side of the screen
- **Toggle**: View → AI Assistant to show/hide
- **Real-time Chat**: Ask questions about screenwriting
- **Background Processing**: UI stays responsive during AI calls
- **Text-to-Speech**: Table Read functionality with LMNT voices
- **Voice Mapping**: Assign different voices to characters

## Text-to-Speech Features

- **Table Read**: Tools → Table Read (TTS) button
- **Character Voices**: Assign different voices to characters
- **Voice Settings**: Configure narrator, male, female voices
- **Reading Progress**: Real-time progress tracking
- **Voice Preview**: Test voices before reading

## Demo Ready

The AI assistant and text-to-speech features are now ready for demos with real Claude responses and LMNT voices! 