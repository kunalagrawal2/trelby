# AI Assistant Setup Guide

## Quick Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create .env file:**
   ```bash
   echo "ANTHROPIC_API_KEY=your_actual_api_key_here" > .env
   ```

3. **Get your Claude API key:**
   - Go to https://console.anthropic.com/
   - Create an account and get your API key
   - Replace `your_actual_api_key_here` in the .env file

4. **Run Trelby:**
   ```bash
   python3 trelby.py
   ```

## Features

- **AI Assistant Panel**: Right side of the screen
- **Toggle**: View → AI Assistant to show/hide
- **Real-time Chat**: Ask questions about screenwriting
- **Background Processing**: UI stays responsive during AI calls

## Demo Ready

The AI assistant is now ready for demos with real Claude responses! 