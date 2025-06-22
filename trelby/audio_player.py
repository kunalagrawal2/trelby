# -*- coding: utf-8 -*-

import io
import tempfile
import os
import threading
import time
from typing import Optional, Callable

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import pyaudio
    import wave
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False


class AudioPlayer:
    """Basic audio player for TTS output"""
    
    def __init__(self):
        self.current_audio = None
        self.is_playing = False
        self._should_stop = False
        
        # Initialize audio system
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
            print("✅ Audio system initialized with pygame")
        elif PYAUDIO_AVAILABLE:
            self.pyaudio_instance = pyaudio.PyAudio()
            print("✅ Audio system initialized with pyaudio")
        else:
            print("ℹ️  No audio library available. Audio playback will be simulated.")
    
    def play_audio_data(self, audio_data: bytes, callback: Optional[Callable] = None) -> bool:
        """Play audio data from bytes"""
        if not audio_data:
            return False
        
        # Check if this is simulation data
        if audio_data == b'dummy_audio_data_for_simulation':
            return self._simulate_playback(audio_data, callback)
        
        self.is_playing = True
        self._should_stop = False
        
        def playback_thread():
            try:
                if PYGAME_AVAILABLE:
                    self._play_with_pygame(audio_data)
                elif PYAUDIO_AVAILABLE:
                    self._play_with_pyaudio(audio_data)
                else:
                    # Simulate playback
                    self._simulate_playback(audio_data)
                
                if callback:
                    callback()
                    
            except Exception as e:
                print(f"Error during audio playback: {e}")
            finally:
                self.is_playing = False
        
        thread = threading.Thread(target=playback_thread)
        thread.daemon = True
        thread.start()
        
        return True
    
    def _detect_audio_format(self, audio_data: bytes) -> str:
        """Detect audio format from data"""
        # Check for common audio file signatures
        if audio_data.startswith(b'ID3') or audio_data.startswith(b'\xff\xfb'):
            return 'mp3'
        elif audio_data.startswith(b'RIFF'):
            return 'wav'
        elif audio_data.startswith(b'OggS'):
            return 'ogg'
        else:
            # Default to MP3 for LMNT API
            return 'mp3'
    
    def _play_with_pygame(self, audio_data: bytes):
        """Play audio using pygame"""
        try:
            # Detect format and set appropriate extension
            format_type = self._detect_audio_format(audio_data)
            extension = f'.{format_type}'
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Load and play the audio
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy() and not self._should_stop:
                time.sleep(0.1)
            
            # Clean up
            pygame.mixer.music.unload()
            os.unlink(temp_file_path)
            
        except Exception as e:
            print(f"Pygame playback error: {e}")
    
    def _play_with_pyaudio(self, audio_data: bytes):
        """Play audio using pyaudio (mainly for WAV files)"""
        try:
            format_type = self._detect_audio_format(audio_data)
            
            if format_type != 'wav':
                print(f"PyAudio only supports WAV files, got {format_type}. Falling back to simulation.")
                self._simulate_playback(audio_data)
                return
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Open and play the audio file
            with wave.open(temp_file_path, 'rb') as wf:
                stream = self.pyaudio_instance.open(
                    format=self.pyaudio_instance.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                data = wf.readframes(1024)
                while data and not self._should_stop:
                    stream.write(data)
                    data = wf.readframes(1024)
                
                stream.stop_stream()
                stream.close()
            
            # Clean up
            os.unlink(temp_file_path)
            
        except Exception as e:
            print(f"PyAudio playback error: {e}")
    
    def _simulate_playback(self, audio_data: bytes, callback: Optional[Callable] = None):
        """Simulate audio playback when no audio library is available"""
        self.is_playing = True
        self._should_stop = False
        
        def simulation_thread():
            try:
                # Estimate duration based on data size (rough approximation)
                if audio_data == b'dummy_audio_data_for_simulation':
                    estimated_duration = 2.0  # 2 seconds for simulation
                else:
                    estimated_duration = len(audio_data) / 16000  # Assuming 16kHz sample rate
                
                start_time = time.time()
                while time.time() - start_time < estimated_duration and not self._should_stop:
                    time.sleep(0.1)
                
                if callback:
                    callback()
                    
            except Exception as e:
                print(f"Simulation playback error: {e}")
            finally:
                self.is_playing = False
        
        thread = threading.Thread(target=simulation_thread)
        thread.daemon = True
        thread.start()
        
        return True
    
    def stop_playback(self):
        """Stop current audio playback"""
        self._should_stop = True
        
        if PYGAME_AVAILABLE:
            pygame.mixer.music.stop()
        
        self.is_playing = False
    
    def is_currently_playing(self) -> bool:
        """Check if audio is currently playing"""
        return self.is_playing
    
    def cleanup(self):
        """Clean up audio resources"""
        if PYAUDIO_AVAILABLE:
            self.pyaudio_instance.terminate()


# Global audio player instance
_audio_player = None

def get_audio_player() -> AudioPlayer:
    """Get the global audio player instance"""
    global _audio_player
    if _audio_player is None:
        _audio_player = AudioPlayer()
    return _audio_player

def cleanup_audio_player():
    """Clean up the global audio player"""
    global _audio_player
    if _audio_player:
        _audio_player.cleanup()
        _audio_player = None 