# -*- coding: utf-8 -*-

import os
import re
import threading
import time
import asyncio
from typing import List, Dict, Optional, Callable
from dotenv import load_dotenv

import trelby.screenplay as screenplay
import trelby.audio_player as audio_player

# Load environment variables
load_dotenv()

class TTSService:
    """Text-to-Speech service using LMNT API"""
    
    def __init__(self):
        self.api_key = os.getenv('LMNT_API_KEY')
        self.speech_client = None
        self.current_audio = None
        self.is_playing = False
        self.stop_playback = False
        self.audio_player = audio_player.get_audio_player()
        self.simulation_mode = False  # Flag for fallback mode
        
        # System voices with descriptions - ONLY VALID LMNT VOICES
        self.system_voices = {
            'ansel': {
                'name': 'Ansel',
                'gender': 'neutral',
                'description': 'Young, engaging voice with subtle enthusiasm and natural emphasis. Perfect for persuasive content and polished advertising.',
                'category': 'marketer'
            },
            'autumn': {
                'name': 'Autumn',
                'gender': 'female',
                'description': 'Warm, friendly female voice with a professional yet approachable tone. Ideal for customer support and guidance.',
                'category': 'support agent'
            },
            'brandon': {
                'name': 'Brandon',
                'gender': 'male',
                'description': 'Clear, stable American broadcaster voice with engaging delivery. Great for news, announcements, and professional narration.',
                'category': 'broadcaster'
            },
            'cassian': {
                'name': 'Cassian',
                'gender': 'neutral',
                'description': 'Friendly, animated voice that\'s nurturing and engaging. Welcoming and enthusiastic, perfect for educational content and guiding students.',
                'category': 'tutor'
            },
            'elowen': {
                'name': 'Elowen',
                'gender': 'female',
                'description': 'Warm, velvety female voice with youthful charm. Captivating for storytelling and narrative content.',
                'category': 'storyteller'
            },
            'evander': {
                'name': 'Evander',
                'gender': 'male',
                'description': 'Weathered, husky voice with a calm, comforting presence. Perfect for customer support and reassuring conversations.',
                'category': 'support agent'
            },
            'huxley': {
                'name': 'Huxley',
                'gender': 'male',
                'description': 'Theatrical male voice with animated, expressive range. An intriguing and fun personality that\'s perfect for dynamic conversations and entertaining content.',
                'category': 'support agent'
            },
            'juniper': {
                'name': 'Juniper',
                'gender': 'female',
                'description': 'Commanding female voice with sophisticated, educated tones. Ideal for instruction and authoritative content.',
                'category': 'tutor'
            },
            'kennedy': {
                'name': 'Kennedy',
                'gender': 'female',
                'description': 'Young, emotive female voice that\'s conversational, inviting, and healing. Great for advertisements and friendly communication.',
                'category': 'marketer'
            },
            'leah': {
                'name': 'Leah',
                'gender': 'female',
                'description': 'Confident, expressive female voice with dynamic intonation patterns. Professional and engaging, perfect for customer support and content creation.',
                'category': 'support agent'
            },
            'lucas': {
                'name': 'Lucas',
                'gender': 'male',
                'description': 'Clear male voice with brisk, projected delivery. Speaks with the pace and clarity of professional broadcasting, prioritizing content over personality.',
                'category': 'broadcaster'
            },
            'morgan': {
                'name': 'Morgan',
                'gender': 'female',
                'description': 'Mature British female voice with depth and experience. Rich tones perfect for sophisticated content.',
                'category': 'content creator'
            },
            'natalie': {
                'name': 'Natalie',
                'gender': 'female',
                'description': 'Bright, youthful female voice with animated, friendly energy. Sounds like talking with a close friend.',
                'category': 'support agent'
            },
            'nyssa': {
                'name': 'Nyssa',
                'gender': 'female',
                'description': 'Warm female voice with animated Southern charm and spirited sass. Confident and motherly with distinctive personality, perfect for engaging conversations and personable support.',
                'category': 'support agent'
            }
        }
        
        # Default voice mapping for different character types - ONLY VALID VOICES
        self.voice_mapping = {
            'default': 'brandon',  # Default voice for action/narration
            'male': 'brandon',
            'female': 'autumn',
            'young': 'ansel',
            'old': 'brandon',
            'narrator': 'brandon',
            'marketer': 'ansel',
            'support': 'autumn',
            'broadcaster': 'brandon',
            'tutor': 'cassian',
            'storyteller': 'elowen',
            'content_creator': 'morgan',
            'educational': 'cassian',
            'authoritative': 'juniper',
            'theatrical': 'huxley',
            'british': 'morgan',
            'southern': 'nyssa',
            'youthful': 'natalie',
            'mature': 'evander',
            'energetic': 'kennedy',
            'professional': 'lucas',
            # Map any invalid voices to valid ones
            'burt': 'brandon',  # Map 'burt' to 'brandon'
            'any': 'brandon'    # Fallback for any unknown voice
        }
        
        # Character-specific voice assignments
        self.character_voices = {}
        
        if not self.api_key:
            print("Warning: LMNT_API_KEY not found. Running in simulation mode.")
            self.simulation_mode = True
        else:
            # Test the API key by trying to initialize the speech client
            try:
                from lmnt.api import Speech
                # We'll initialize the client when needed
                print("✅ LMNT API key found and ready")
            except ImportError:
                print("Warning: lmnt library not installed. Running in simulation mode.")
                self.simulation_mode = True
            except Exception as e:
                print(f"Warning: Could not initialize LMNT client. Running in simulation mode. Error: {e}")
                self.simulation_mode = True
    
    def get_available_voices(self) -> List[Dict]:
        """Get list of available voices from LMNT"""
        if self.simulation_mode:
            return []
        
        try:
            from lmnt.api import Speech
            
            async def get_voices():
                async with Speech(self.api_key) as speech:
                    voices = await speech.voices()
                    return voices
            
            # Run the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            voices = loop.run_until_complete(get_voices())
            loop.close()
            
            self.voices = {voice['id']: voice for voice in voices}
            return voices
            
        except Exception as e:
            print(f"Error fetching voices: {e}")
            return []
    
    def get_valid_voice(self, voice_id: str) -> str:
        """Get a valid voice ID, mapping invalid ones to valid alternatives"""
        # First check if it's a valid system voice
        if voice_id in self.system_voices:
            return voice_id
        
        # Check if it's in our mapping
        if voice_id in self.voice_mapping:
            return self.voice_mapping[voice_id]
        
        # Default fallback
        return 'brandon'
    
    def synthesize_speech(self, text: str, voice_id: str = 'brandon', 
                         speed: float = 1.0, stability: float = 0.5) -> Optional[bytes]:
        """Synthesize speech using LMNT API or simulation mode"""
        
        # Ensure we use a valid voice
        valid_voice = self.get_valid_voice(voice_id)
        if valid_voice != voice_id:
            print(f"⚠️  Voice '{voice_id}' not available, using '{valid_voice}' instead")
        
        # If in simulation mode, return dummy audio data
        if self.simulation_mode:
            print(f"[SIMULATION] Synthesizing: '{text[:50]}...' with voice '{valid_voice}'")
            # Return a small dummy audio data (just enough to trigger playback simulation)
            return b'dummy_audio_data_for_simulation'
        
        try:
            from lmnt.api import Speech
            
            async def synthesize():
                async with Speech(self.api_key) as speech:
                    synthesis = await speech.synthesize(text, valid_voice)
                    return synthesis['audio']
            
            # Run the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_data = loop.run_until_complete(synthesize())
            loop.close()
            
            return audio_data
            
        except Exception as e:
            print(f"Error synthesizing speech: {e}")
            # Fall back to simulation mode
            print("Falling back to simulation mode...")
            self.simulation_mode = True
            return self.synthesize_speech(text, valid_voice, speed, stability)
    
    def assign_voice_to_character(self, character_name: str, voice_type: str = 'default'):
        """Assign a voice type to a character"""
        # Use the valid voice mapping
        voice_id = self.voice_mapping.get(voice_type.lower(), 'brandon')
        self.character_voices[character_name.upper()] = voice_id
    
    def get_voice_for_character(self, character_name: str) -> str:
        """Get the assigned voice for a character"""
        # Use valid voice fallback instead of 'burt'
        return self.character_voices.get(character_name.upper(), 'brandon')
    
    def extract_screenplay_text(self, sp) -> List[Dict]:
        """Extract text from screenplay for TTS reading with better segmentation"""
        if not sp or not sp.lines:
            return []
        
        reading_segments = []
        current_character = None
        current_dialogue = []
        current_action = []
        current_scene = None
        
        for i, line in enumerate(sp.lines):
            if line.lt == screenplay.SCENE:
                # Scene heading - start new scene
                if line.text.strip():
                    current_scene = line.text.strip()
                    # Add scene as separate action segment
                    reading_segments.append({
                        'type': 'scene',
                        'character': 'NARRATOR',
                        'text': f"Scene: {current_scene}",
                        'line_index': i,
                        'scene': current_scene
                    })
                    
            elif line.lt == screenplay.ACTION:
                # Action line - group consecutive action lines
                if line.text.strip():
                    current_action.append(line.text.strip())
                    
            elif line.lt == screenplay.CHARACTER:
                # Character name - process any accumulated action first, then start new dialogue
                if current_action:
                    # Save accumulated action as a single segment
                    reading_segments.append({
                        'type': 'action',
                        'character': 'NARRATOR',
                        'text': ' '.join(current_action),
                        'line_index': i - len(current_action),
                        'scene': current_scene
                    })
                    current_action = []
                
                # Start new dialogue segment
                current_character = line.text.strip().upper()
                current_dialogue = []
                
            elif line.lt == screenplay.DIALOGUE:
                # Dialogue line - add to current dialogue
                if line.text.strip():
                    current_dialogue.append(line.text.strip())
                    
            elif line.lt == screenplay.PAREN:
                # Parenthetical - add to current dialogue with proper formatting
                if line.text.strip():
                    current_dialogue.append(f"({line.text.strip()})")
                    
            elif line.lt == screenplay.TRANSITION:
                # Transition - add as separate action segment
                if line.text.strip():
                    reading_segments.append({
                        'type': 'transition',
                        'character': 'NARRATOR',
                        'text': f"Transition: {line.text.strip()}",
                        'line_index': i,
                        'scene': current_scene
                    })
            
            # Process accumulated text when we hit the end of an element
            if line.lb == screenplay.LB_LAST:
                # Process accumulated action
                if current_action:
                    reading_segments.append({
                        'type': 'action',
                        'character': 'NARRATOR',
                        'text': ' '.join(current_action),
                        'line_index': i - len(current_action),
                        'scene': current_scene
                    })
                    current_action = []
                
                # Process accumulated dialogue
                if current_dialogue and current_character:
                    reading_segments.append({
                        'type': 'dialogue',
                        'character': current_character,
                        'text': ' '.join(current_dialogue),
                        'line_index': i - len(current_dialogue),
                        'scene': current_scene
                    })
                    current_dialogue = []
        
        # Process any remaining text
        if current_action:
            reading_segments.append({
                'type': 'action',
                'character': 'NARRATOR',
                'text': ' '.join(current_action),
                'line_index': len(sp.lines) - len(current_action),
                'scene': current_scene
            })
        
        if current_dialogue and current_character:
            reading_segments.append({
                'type': 'dialogue',
                'character': current_character,
                'text': ' '.join(current_dialogue),
                'line_index': len(sp.lines) - len(current_dialogue),
                'scene': current_scene
            })
        
        return reading_segments
    
    def save_audio_segment(self, audio_data: bytes, segment: Dict, output_dir: str = "tts_output") -> str:
        """Save an audio segment as a file"""
        if not audio_data or audio_data == b'dummy_audio_data_for_simulation':
            return None
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename based on segment info
        segment_type = segment['type']
        character = segment['character']
        scene = segment.get('scene', 'unknown')
        
        # Clean filename
        safe_scene = "".join(c for c in scene if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_scene = safe_scene.replace(' ', '_')[:30]  # Limit length
        
        # Create filename
        if segment_type == 'dialogue':
            filename = f"{safe_scene}_{character}_{segment['line_index']}.mp3"
        else:
            filename = f"{safe_scene}_{segment_type}_{segment['line_index']}.mp3"
        
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'wb') as f:
                f.write(audio_data)
            return filepath
        except Exception as e:
            print(f"Error saving audio file {filepath}: {e}")
            return None
    
    def read_screenplay(self, sp, progress_callback: Optional[Callable] = None, 
                       stop_callback: Optional[Callable] = None, 
                       save_audio_files: bool = False,
                       output_dir: str = "tts_output") -> bool:
        """Read the entire screenplay using TTS with improved segmentation"""
        if not sp:
            return False
        
        segments = self.extract_screenplay_text(sp)
        if not segments:
            print("No readable segments found in screenplay")
            return False
        
        print(f"🎬 Starting table read with {len(segments)} segments")
        
        self.is_playing = True
        self.stop_playback = False
        
        def playback_thread():
            try:
                for i, segment in enumerate(segments):
                    if self.stop_playback:
                        break
                    
                    # Update progress
                    if progress_callback:
                        progress = (i / len(segments)) * 100
                        progress_callback(progress, segment)
                    
                    # Determine voice for this segment
                    if segment['type'] == 'dialogue':
                        voice_id = self.get_voice_for_character(segment['character'])
                        print(f"🎭 {segment['character']} ({voice_id}): {segment['text'][:50]}...")
                    else:
                        voice_id = self.voice_mapping['narrator']
                        print(f"📖 Narrator ({voice_id}): {segment['text'][:50]}...")
                    
                    # Clean text for TTS
                    clean_text = self.clean_text_for_tts(segment['text'])
                    if not clean_text:
                        print(f"⚠️  Skipping empty segment: {segment['type']}")
                        continue
                    
                    # Synthesize speech
                    audio_data = self.synthesize_speech(clean_text, voice_id)
                    if audio_data:
                        # Save audio file if requested
                        if save_audio_files:
                            filepath = self.save_audio_segment(audio_data, segment, output_dir)
                            if filepath:
                                print(f"💾 Saved: {os.path.basename(filepath)}")
                        
                        # Play the audio using the audio player
                        print(f"🔊 Playing: {segment['character']} - {clean_text[:50]}...")
                        
                        # Play the audio and wait for completion
                        self.audio_player.play_audio_data(audio_data)
                        
                        # Wait for audio to finish playing
                        while self.audio_player.is_currently_playing() and not self.stop_playback:
                            time.sleep(0.1)
                    else:
                        print(f"❌ Failed to synthesize audio for segment {i}")
                    
                    # Small pause between segments
                    if not self.stop_playback:
                        time.sleep(0.5)
                
                print("✅ Table read complete!")
                self.is_playing = False
                
            except Exception as e:
                print(f"❌ Error during playback: {e}")
                self.is_playing = False
        
        # Start playback in a separate thread
        thread = threading.Thread(target=playback_thread)
        thread.daemon = True
        thread.start()
        
        return True
    
    def stop_reading(self):
        """Stop the current reading session"""
        self.stop_playback = True
        self.is_playing = False
        if hasattr(self, 'audio_player') and self.audio_player:
            self.audio_player.stop_playback()
    
    def clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS synthesis"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove screenplay formatting markers
        text = re.sub(r'\(CONT\'D\)', '', text)
        text = re.sub(r'\(MORE\)', '', text)
        text = re.sub(r'\(V\.O\.\)', 'voice over', text)
        text = re.sub(r'\(O\.S\.\)', 'off screen', text)
        
        # Clean up parentheticals
        text = re.sub(r'^\s*\(\s*', '(', text)
        text = re.sub(r'\s*\)\s*$', ')', text)
        
        # Remove empty parentheses
        text = re.sub(r'\(\s*\)', '', text)
        
        return text.strip()
    
    def get_reading_progress(self) -> float:
        """Get current reading progress (0-100)"""
        # This would need to be implemented based on actual playback progress
        return 0.0
    
    def is_currently_reading(self) -> bool:
        """Check if currently reading a screenplay"""
        return self.is_playing 