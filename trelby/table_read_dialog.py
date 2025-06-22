# -*- coding: utf-8 -*-

import wx
import wx.adv
import threading
import time
from typing import Dict, List, Optional

import trelby.tts_service as tts_service
import trelby.screenplay as screenplay


class TableReadDialog(wx.Dialog):
    """Enhanced Table Read Dialog with TTS functionality"""
    
    def __init__(self, parent, screenplay):
        wx.Dialog.__init__(self, parent, -1, "Table Read - Text to Speech", 
                          size=(800, 600), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self.screenplay = screenplay
        self.tts_service = None
        self.current_segment = 0
        self.segments = []
        self.is_reading = False
        
        try:
            self.tts_service = tts_service.TTSService()
            
            # Check if we're in simulation mode
            if hasattr(self.tts_service, 'simulation_mode') and self.tts_service.simulation_mode:
                wx.MessageBox(
                    "TTS is running in simulation mode.\n\n"
                    "This means:\n"
                    "• No actual audio will be played\n"
                    "• Text will be displayed as it would be read\n"
                    "• You can test the interface and voice assignments\n\n"
                    "To enable real TTS:\n"
                    "1. Get a valid LMNT API key from https://lmnt.com/\n"
                    "2. Add it to your .env file\n"
                    "3. Restart Trelby",
                    "Simulation Mode", 
                    wx.OK | wx.ICON_INFORMATION, 
                    self
                )
            
        except Exception as e:
            error_msg = str(e)
            if "LMNT_API_KEY" in error_msg:
                wx.MessageBox(
                    "LMNT API Key not found!\n\n"
                    "To use the Table Read feature:\n"
                    "1. Get your API key from https://lmnt.com/\n"
                    "2. Add it to your .env file:\n"
                    "   LMNT_API_KEY=your_actual_api_key_here\n"
                    "3. Restart Trelby\n\n"
                    "The interface will work in simulation mode for testing.",
                    "Configuration Error", 
                    wx.OK | wx.ICON_ERROR, 
                    self
                )
            else:
                wx.MessageBox(
                    f"TTS Service Error: {error_msg}\n\n"
                    "Please check your configuration and try again.",
                    "Configuration Error", 
                    wx.OK | wx.ICON_ERROR, 
                    self
                )
            self.Destroy()
            return
        
        self.create_ui()
        self.load_screenplay_data()
    
    def create_ui(self):
        """Create the dialog UI"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(self, -1, "Table Read - Text to Speech")
        title.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(title, 0, wx.ALL | wx.CENTER, 10)
        
        # Create notebook for different sections
        self.notebook = wx.Notebook(self, -1)
        
        # Reading tab
        self.create_reading_tab()
        
        # Voice settings tab
        self.create_voice_settings_tab()
        
        # Character mapping tab
        self.create_character_mapping_tab()
        
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 10)
        
        # Control buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.start_btn = wx.Button(self, -1, "Start Table Read")
        self.start_btn.Bind(wx.EVT_BUTTON, self.on_start_reading)
        button_sizer.Add(self.start_btn, 1, wx.RIGHT, 5)
        
        self.stop_btn = wx.Button(self, -1, "Stop")
        self.stop_btn.Bind(wx.EVT_BUTTON, self.on_stop_reading)
        self.stop_btn.Enable(False)
        button_sizer.Add(self.stop_btn, 1, wx.LEFT | wx.RIGHT, 5)
        
        self.close_btn = wx.Button(self, -1, "Close")
        self.close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        button_sizer.Add(self.close_btn, 1, wx.LEFT, 5)
        
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 10)
        
        self.SetSizer(main_sizer)
        
        # Bind close event
        self.Bind(wx.EVT_CLOSE, self.on_close)
    
    def create_reading_tab(self):
        """Create the main reading tab"""
        panel = wx.Panel(self.notebook, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Progress section
        progress_group = wx.StaticBox(panel, -1, "Reading Progress")
        progress_sizer = wx.StaticBoxSizer(progress_group, wx.VERTICAL)
        
        self.progress_bar = wx.Gauge(panel, -1, 100, size=(300, 25))
        progress_sizer.Add(self.progress_bar, 0, wx.EXPAND | wx.ALL, 5)
        
        self.progress_text = wx.StaticText(panel, -1, "Ready to start table read")
        progress_sizer.Add(self.progress_text, 0, wx.ALL, 5)
        
        sizer.Add(progress_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Current segment display
        segment_group = wx.StaticBox(panel, -1, "Current Segment")
        segment_sizer = wx.StaticBoxSizer(segment_group, wx.VERTICAL)
        
        self.segment_text = wx.TextCtrl(panel, -1, "", style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 100))
        segment_sizer.Add(self.segment_text, 1, wx.EXPAND | wx.ALL, 5)
        
        sizer.Add(segment_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        # Reading options
        options_group = wx.StaticBox(panel, -1, "Reading Options")
        options_sizer = wx.StaticBoxSizer(options_group, wx.VERTICAL)
        
        options_grid = wx.FlexGridSizer(3, 2, 5, 5)
        
        options_grid.Add(wx.StaticText(panel, -1, "Reading Speed:"))
        self.speed_slider = wx.Slider(panel, -1, 100, 50, 200, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        options_grid.Add(self.speed_slider, 1, wx.EXPAND)
        
        options_grid.Add(wx.StaticText(panel, -1, "Pause between segments:"))
        self.pause_slider = wx.Slider(panel, -1, 5, 0, 20, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        options_grid.Add(self.pause_slider, 1, wx.EXPAND)
        
        options_grid.Add(wx.StaticText(panel, -1, "Save audio files:"))
        self.save_audio_cb = wx.CheckBox(panel, -1, "Save individual MP3 files")
        self.save_audio_cb.SetValue(False)
        options_grid.Add(self.save_audio_cb, 1, wx.EXPAND)
        
        options_sizer.Add(options_grid, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(options_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(sizer)
        self.notebook.AddPage(panel, "Reading")
    
    def create_voice_settings_tab(self):
        """Create the voice settings tab"""
        panel = wx.Panel(self.notebook, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Voice selection
        voice_group = wx.StaticBox(panel, -1, "Voice Settings")
        voice_sizer = wx.StaticBoxSizer(voice_group, wx.VERTICAL)
        
        # Default voices with descriptions
        default_voices = [
            ("Narrator/Action", "narrator", "Clear, professional narration for scene descriptions and action"),
            ("Male Characters", "male", "Strong, clear voice for male characters"),
            ("Female Characters", "female", "Warm, approachable voice for female characters"),
            ("Young Characters", "young", "Energetic, engaging voice for young characters"),
            ("Old Characters", "old", "Mature, experienced voice for older characters"),
            ("Marketing/Enthusiastic", "marketer", "Persuasive, enthusiastic voice for dynamic content"),
            ("Support/Friendly", "support", "Warm, helpful voice for supportive characters"),
            ("Broadcaster/News", "broadcaster", "Clear, authoritative voice for announcements"),
            ("Educational/Tutor", "tutor", "Friendly, nurturing voice for educational content"),
            ("Storyteller", "storyteller", "Warm, captivating voice for narrative content"),
            ("Content Creator", "content_creator", "Sophisticated voice for professional content"),
            ("Authoritative", "authoritative", "Commanding voice for instruction and authority"),
            ("Theatrical", "theatrical", "Expressive, animated voice for dynamic conversations"),
            ("British", "british", "Mature British voice with depth and experience"),
            ("Southern", "southern", "Warm Southern voice with charm and personality"),
            ("Youthful", "youthful", "Bright, animated voice with friendly energy"),
            ("Mature", "mature", "Weathered, comforting voice with calm presence"),
            ("Energetic", "energetic", "Young, emotive voice for engaging communication"),
            ("Professional", "professional", "Clear, projected voice for professional delivery")
        ]
        
        # Available system voices - all 14 voices
        system_voices = ["ansel", "autumn", "brandon", "cassian", "elowen", "evander", "huxley", "juniper", "kennedy", "leah", "lucas", "morgan", "natalie", "nyssa"]
        
        for label, voice_type, description in default_voices:
            row_sizer = wx.BoxSizer(wx.HORIZONTAL)
            
            # Label and description
            label_sizer = wx.BoxSizer(wx.VERTICAL)
            label_text = wx.StaticText(panel, -1, f"{label}:")
            label_text.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            label_sizer.Add(label_text, 0, wx.BOTTOM, 2)
            
            desc_text = wx.StaticText(panel, -1, description)
            desc_text.SetForegroundColour(wx.Colour(100, 100, 100))
            label_sizer.Add(desc_text, 0)
            
            row_sizer.Add(label_sizer, 1, wx.EXPAND | wx.RIGHT, 10)
            
            # Voice choice
            voice_choice = wx.Choice(panel, -1, choices=system_voices)
            voice_choice.SetSelection(0)  # Default to first voice
            setattr(self, f"{voice_type}_voice_choice", voice_choice)
            
            row_sizer.Add(voice_choice, 0)
            voice_sizer.Add(row_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        sizer.Add(voice_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Voice preview
        preview_group = wx.StaticBox(panel, -1, "Voice Preview")
        preview_sizer = wx.StaticBoxSizer(preview_group, wx.VERTICAL)
        
        preview_sizer.Add(wx.StaticText(panel, -1, "Test text:"), 0, wx.ALL, 5)
        
        self.preview_text = wx.TextCtrl(panel, -1, "Hello, this is a test of the text-to-speech system.", 
                                       style=wx.TE_MULTILINE, size=(-1, 60))
        preview_sizer.Add(self.preview_text, 1, wx.EXPAND | wx.ALL, 5)
        
        preview_btn = wx.Button(panel, -1, "Preview Voice")
        preview_btn.Bind(wx.EVT_BUTTON, self.on_preview_voice)
        preview_sizer.Add(preview_btn, 0, wx.ALL, 5)
        
        sizer.Add(preview_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(sizer)
        self.notebook.AddPage(panel, "Voice Settings")
    
    def create_character_mapping_tab(self):
        """Create the character voice mapping tab"""
        panel = wx.Panel(self.notebook, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Character list
        char_group = wx.StaticBox(panel, -1, "Character Voice Assignments")
        char_sizer = wx.StaticBoxSizer(char_group, wx.VERTICAL)
        
        # Get characters from screenplay
        if self.screenplay:
            characters = list(self.screenplay.getCharacterNames().keys())
            characters.sort()
            
            if characters:
                # Available voices with descriptions
                voice_options = [
                    ("ansel", "Ansel - Young, engaging, enthusiastic"),
                    ("autumn", "Autumn - Warm, friendly, professional"),
                    ("brandon", "Brandon - Clear, stable, broadcaster"),
                    ("cassian", "Cassian - Friendly, animated, nurturing"),
                    ("elowen", "Elowen - Warm, velvety, storyteller"),
                    ("evander", "Evander - Weathered, husky, comforting"),
                    ("huxley", "Huxley - Theatrical, expressive, fun"),
                    ("juniper", "Juniper - Commanding, sophisticated, authoritative"),
                    ("kennedy", "Kennedy - Young, emotive, conversational"),
                    ("leah", "Leah - Confident, expressive, professional"),
                    ("lucas", "Lucas - Clear, brisk, professional"),
                    ("morgan", "Morgan - Mature British, sophisticated"),
                    ("natalie", "Natalie - Bright, youthful, friendly"),
                    ("nyssa", "Nyssa - Warm Southern, spirited, motherly")
                ]
                
                for char in characters:
                    row_sizer = wx.BoxSizer(wx.HORIZONTAL)
                    
                    # Character name
                    char_label = wx.StaticText(panel, -1, f"{char}:")
                    char_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                    row_sizer.Add(char_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
                    
                    # Voice choice with descriptions
                    voice_choice = wx.Choice(panel, -1, choices=[desc for _, desc in voice_options])
                    voice_choice.SetSelection(0)  # Default to first voice
                    setattr(self, f"char_{char}_voice", voice_choice)
                    
                    row_sizer.Add(voice_choice, 1, wx.EXPAND)
                    char_sizer.Add(row_sizer, 0, wx.EXPAND | wx.ALL, 5)
            else:
                char_sizer.Add(wx.StaticText(panel, -1, "No characters found in screenplay"), 0, wx.ALL, 10)
        else:
            char_sizer.Add(wx.StaticText(panel, -1, "No screenplay loaded"), 0, wx.ALL, 10)
        
        sizer.Add(char_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(sizer)
        self.notebook.AddPage(panel, "Character Mapping")
    
    def load_screenplay_data(self):
        """Load screenplay data for TTS"""
        if not self.screenplay or not self.tts_service:
            return
        
        self.segments = self.tts_service.extract_screenplay_text(self.screenplay)
        
        # Update progress text
        if self.segments:
            mode_text = " (Simulation Mode)" if hasattr(self.tts_service, 'simulation_mode') and self.tts_service.simulation_mode else ""
            self.progress_text.SetLabel(f"Ready to read {len(self.segments)} segments{mode_text}")
        else:
            self.progress_text.SetLabel("No readable content found in screenplay")
    
    def on_start_reading(self, event):
        """Start the table read"""
        if not self.tts_service or not self.segments:
            wx.MessageBox("No TTS service available or no content to read", 
                         "Error", wx.OK | wx.ICON_ERROR, self)
            return
        
        # Get voice settings
        self.update_voice_settings()
        
        # Start reading
        self.is_reading = True
        self.start_btn.Enable(False)
        self.stop_btn.Enable(True)
        self.progress_text.SetLabel("Reading in progress...")
        
        # Start reading in background thread
        thread = threading.Thread(target=self.reading_thread)
        thread.daemon = True
        thread.start()
    
    def reading_thread(self):
        """Background thread for reading"""
        try:
            # Get reading options
            save_audio = self.save_audio_cb.GetValue()
            output_dir = "tts_output"
            
            # Use the improved TTS service reading method
            success = self.tts_service.read_screenplay(
                self.screenplay,
                progress_callback=self.update_progress_callback,
                stop_callback=self.stop_reading_callback,
                save_audio_files=save_audio,
                output_dir=output_dir
            )
            
            if not success:
                wx.CallAfter(wx.MessageBox, 
                            "Failed to start table read. Please check your script and try again.",
                            "Error", wx.OK | wx.ICON_ERROR, self)
            
            # The reading_complete will be called by the TTS service
            wx.CallAfter(self.reading_complete)
            
        except Exception as e:
            print(f"Error during reading: {e}")
            wx.CallAfter(self.reading_complete)
    
    def update_progress_callback(self, progress, segment):
        """Callback for progress updates from TTS service"""
        wx.CallAfter(self.update_progress, int(progress), segment)
    
    def stop_reading_callback(self):
        """Callback for stop reading from TTS service"""
        wx.CallAfter(self.on_stop_reading, None)
    
    def update_progress(self, progress_percent, segment):
        """Update progress display"""
        self.progress_bar.SetValue(progress_percent)
        
        # Update segment display
        if segment:
            display_text = f"Character: {segment['character']}\nType: {segment['type']}\nText: {segment['text'][:200]}..."
            if len(segment['text']) > 200:
                display_text += "..."
            self.segment_text.SetValue(display_text)
    
    def reading_complete(self):
        """Called when reading is complete"""
        self.is_reading = False
        self.start_btn.Enable(True)
        self.stop_btn.Enable(False)
        self.progress_text.SetLabel("Reading complete")
        self.progress_bar.SetValue(100)
    
    def on_stop_reading(self, event):
        """Stop the current reading"""
        self.is_reading = False
        if self.tts_service:
            self.tts_service.stop_reading()
        
        self.start_btn.Enable(True)
        self.stop_btn.Enable(False)
        self.progress_text.SetLabel("Reading stopped")
    
    def update_voice_settings(self):
        """Update voice settings from UI"""
        if not self.tts_service:
            return
        
        # Update default voice mappings
        voice_mappings = {
            'narrator': getattr(self, 'narrator_voice_choice', None),
            'male': getattr(self, 'male_voice_choice', None),
            'female': getattr(self, 'female_voice_choice', None),
            'young': getattr(self, 'young_voice_choice', None),
            'old': getattr(self, 'old_voice_choice', None),
            'marketer': getattr(self, 'marketer_voice_choice', None),
            'support': getattr(self, 'support_voice_choice', None),
            'broadcaster': getattr(self, 'broadcaster_voice_choice', None)
        }
        
        for voice_type, choice in voice_mappings.items():
            if choice and choice.GetSelection() >= 0:
                voices = ["ansel", "autumn", "brandon", "cassian", "elowen", "evander", "huxley", "juniper", "kennedy", "leah", "lucas", "morgan", "natalie", "nyssa"]
                selected_voice = voices[choice.GetSelection()]
                self.tts_service.voice_mapping[voice_type] = selected_voice
        
        # Update character-specific voices
        if self.screenplay:
            characters = list(self.screenplay.getCharacterNames().keys())
            voice_ids = ["ansel", "autumn", "brandon", "cassian", "elowen", "evander", "huxley", "juniper", "kennedy", "leah", "lucas", "morgan", "natalie", "nyssa"]
            
            for char in characters:
                choice = getattr(self, f"char_{char}_voice", None)
                if choice and choice.GetSelection() >= 0:
                    selected_voice = voice_ids[choice.GetSelection()]
                    self.tts_service.assign_voice_to_character(char, selected_voice)
    
    def on_preview_voice(self, event):
        """Preview the selected voice"""
        if not self.tts_service:
            return
        
        text = self.preview_text.GetValue()
        if not text:
            return
        
        # Get selected voice (use narrator voice for preview)
        voice_id = self.tts_service.voice_mapping.get('narrator', 'brandon')
        
        # Synthesize speech
        audio_data = self.tts_service.synthesize_speech(text, voice_id)
        if audio_data:
            # For now, just show a message (actual audio playback would need additional implementation)
            wx.MessageBox(f"Voice preview generated for: {text[:50]}...", 
                         "Preview", wx.OK | wx.ICON_INFORMATION, self)
        else:
            wx.MessageBox("Failed to generate voice preview", 
                         "Error", wx.OK | wx.ICON_ERROR, self)
    
    def on_close(self, event):
        """Close the dialog"""
        if self.is_reading:
            self.on_stop_reading(None)
        
        self.Destroy() 