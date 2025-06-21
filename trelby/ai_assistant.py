# -*- coding: utf-8 -*-

import wx
import time
import threading
from trelby.appearance_utils import get_ai_pane_colors

class AIAssistantPanel(wx.Panel):
    """Basic AI Assistant Panel similar to Cursor's chat interface"""
    
    def __init__(self, parent, gd):
        wx.Panel.__init__(self, parent, -1)
        
        self.gd = gd
        self.chat_history = []
        
        # Get appearance-aware colors
        self.colors = get_ai_pane_colors()
        
        # Available services and models
        self.available_services = {
            "anthropic": [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ],
            "groq": [
                "llama3-8b-8192",
                "llama3-70b-8192",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
                "llama2-70b-4096"
            ]
        }
        
        # Initialize AI service
        try:
            from trelby.ai_service import AIService
            self.ai_service = AIService(service_name="anthropic", model="claude-3-5-sonnet-20241022")
            self.ai_available = True
            self.current_service = "anthropic"
        except Exception as e:
            self.ai_service = None
            self.ai_available = False
            self.current_service = None
        
        # Create the main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create service and model selection area
        selection_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        service_label = wx.StaticText(self, -1, "Service:")
        service_label.SetForegroundColour(self.colors['text'])
        
        self.service_choice = wx.Choice(self, -1, choices=list(self.available_services.keys()))
        self.service_choice.SetSelection(0)  # Default to first service
        self.service_choice.SetBackgroundColour(self.colors['input_background'])
        self.service_choice.SetForegroundColour(self.colors['input_text'])
        
        model_label = wx.StaticText(self, -1, "Model:")
        model_label.SetForegroundColour(self.colors['text'])
        
        self.model_choice = wx.Choice(self, -1, choices=self.available_services["anthropic"])
        self.model_choice.SetSelection(0)  # Default to first model
        self.model_choice.SetBackgroundColour(self.colors['input_background'])
        self.model_choice.SetForegroundColour(self.colors['input_text'])
        
        selection_sizer.Add(service_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        selection_sizer.Add(self.service_choice, 1, wx.EXPAND | wx.RIGHT, 10)
        selection_sizer.Add(model_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        selection_sizer.Add(self.model_choice, 1, wx.EXPAND)
        
        # Create chat display area
        self.chat_display = wx.TextCtrl(
            self, -1, 
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.VSCROLL | wx.BORDER_SUNKEN
        )
        self.chat_display.SetBackgroundColour(self.colors['background'])
        self.chat_display.SetForegroundColour(self.colors['text'])
        
        # Create input area
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.input_text = wx.TextCtrl(
            self, -1, 
            style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER,
            size=(-1, 60)
        )
        self.input_text.SetHint("Ask me anything about your screenplay...")
        self.input_text.SetBackgroundColour(self.colors['input_background'])
        self.input_text.SetForegroundColour(self.colors['input_text'])
        
        self.send_button = wx.Button(self, -1, "Send")
        self.send_button.SetDefault()
        self.send_button.SetBackgroundColour(self.colors['button_background'])
        self.send_button.SetForegroundColour(self.colors['button_text'])
        
        input_sizer.Add(self.input_text, 1, wx.EXPAND | wx.RIGHT, 5)
        input_sizer.Add(self.send_button, 0, wx.EXPAND)
        
        # Add to main sizer
        main_sizer.Add(selection_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.chat_display, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
        
        # Bind events
        self.send_button.Bind(wx.EVT_BUTTON, self.OnSend)
        self.input_text.Bind(wx.EVT_TEXT_ENTER, self.OnSend)
        self.service_choice.Bind(wx.EVT_CHOICE, self.OnServiceChange)
        self.model_choice.Bind(wx.EVT_CHOICE, self.OnModelChange)
        
        # Add welcome message
        if self.ai_available:
            welcome_msg = "Hello! I'm your AI writing assistant. I can help you with:\n\n• Character development\n• Plot suggestions\n• Dialogue improvements\n• Scene structure\n• Genre-specific advice\n\nI have access to your current screenplay and can provide context-aware feedback. What would you like to work on today?"
        else:
            welcome_msg = "AI Assistant is not available. Please check your API key configuration in the .env file."
        
        self.add_message("AI Assistant", welcome_msg, is_user=False)
    
    def OnServiceChange(self, event):
        """Handle service selection change"""
        if not self.ai_available:
            return
            
        selected_service = self.service_choice.GetString(self.service_choice.GetSelection())
        
        # Update model choices for the selected service
        models = self.available_services[selected_service]
        self.model_choice.Clear()
        for model in models:
            self.model_choice.Append(model)
        self.model_choice.SetSelection(0)
        
        # Update current service
        self.current_service = selected_service
        
        # Try to create new service with first model
        try:
            from trelby.ai_service import AIService
            self.ai_service = AIService(service_name=selected_service, model=models[0])
            self.add_message("AI Assistant", f"Switched to {selected_service} with {models[0]}. How can I help you?", is_user=False)
        except Exception as e:
            self.add_message("AI Assistant", f"Error switching to {selected_service}: {str(e)}", is_user=False)
    
    def OnModelChange(self, event):
        """Handle model selection change"""
        if not self.ai_available:
            return
            
        selected_service = self.service_choice.GetString(self.service_choice.GetSelection())
        selected_model = self.model_choice.GetString(self.model_choice.GetSelection())
        
        try:
            # Create new AI service with selected model
            from trelby.ai_service import AIService
            self.ai_service = AIService(service_name=selected_service, model=selected_model)
            
            # Add system message about model change
            self.add_message("AI Assistant", f"Switched to {selected_model}. How can I help you?", is_user=False)
        except Exception as e:
            self.add_message("AI Assistant", f"Error switching to {selected_model}: {str(e)}", is_user=False)
    
    def refresh_appearance(self):
        """Refresh colors when system appearance changes"""
        self.colors = get_ai_pane_colors()
        
        # Update all UI elements with new colors
        self.chat_display.SetBackgroundColour(self.colors['background'])
        self.chat_display.SetForegroundColour(self.colors['text'])
        self.chat_display.Refresh()
        
        self.input_text.SetBackgroundColour(self.colors['input_background'])
        self.input_text.SetForegroundColour(self.colors['input_text'])
        self.input_text.Refresh()
        
        self.send_button.SetBackgroundColour(self.colors['button_background'])
        self.send_button.SetForegroundColour(self.colors['button_text'])
        self.send_button.Refresh()
        
        # Update choice colors
        self.service_choice.SetBackgroundColour(self.colors['input_background'])
        self.service_choice.SetForegroundColour(self.colors['input_text'])
        self.service_choice.Refresh()
        
        self.model_choice.SetBackgroundColour(self.colors['input_background'])
        self.model_choice.SetForegroundColour(self.colors['input_text'])
        self.model_choice.Refresh()
        
        # Refresh the panel itself
        self.Refresh()
    
    def add_message(self, sender, message, is_user=True):
        """Add a message to the chat display"""
        # Format the message
        if is_user:
            formatted_message = f"You: {message}\n\n"
        else:
            formatted_message = f"{sender}: {message}\n\n"
        
        # Add to display
        current_text = self.chat_display.GetValue()
        self.chat_display.SetValue(current_text + formatted_message)
        
        # Scroll to bottom
        self.chat_display.ShowPosition(len(self.chat_display.GetValue()))
        
        # Store in history
        self.chat_history.append({
            'sender': sender,
            'message': message,
            'is_user': is_user,
            'timestamp': time.time()
        })
    
    def OnSend(self, event):
        """Handle send button click or Enter key"""
        message = self.input_text.GetValue().strip()
        if not message:
            return
        
        # Add user message
        self.add_message("You", message, is_user=True)
        
        # Clear input
        self.input_text.SetValue("")
        
        # Disable send button while processing
        self.send_button.Disable()
        self.send_button.SetLabel("Thinking...")
        
        # Get AI response
        if self.ai_available:
            # Run AI call in background thread
            thread = threading.Thread(target=self.get_ai_response, args=(message,))
            thread.daemon = True
            thread.start()
        else:
            self.add_message("AI Assistant", "AI service is not available. Please check your configuration.", is_user=False)
            self.send_button.Enable()
            self.send_button.SetLabel("Send")
    
    def get_ai_response(self, user_message):
        """Get response from Claude in background thread"""
        try:
            # Get document context
            context = self.get_screenplay_context(user_message)
            
            # Get conversation history (all previous messages)
            # Note: The current user message hasn't been added to chat_history yet
            conversation_history = self.chat_history.copy()
            
            # Get AI response with context and conversation history
            response = self.ai_service.get_response(user_message, context, conversation_history)
            
            # Update UI in main thread
            wx.CallAfter(self.handle_ai_response, response)
        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            wx.CallAfter(self.handle_ai_response, error_msg)
    
    def handle_ai_response(self, response):
        """Handle AI response in main thread"""
        self.add_message("AI Assistant", response, is_user=False)
        self.send_button.Enable()
        self.send_button.SetLabel("Send")
    
    def get_current_screenplay(self):
        """Get the current screenplay object"""
        try:
            # Access current screenplay through the main frame
            if hasattr(self.gd, 'mainFrame') and self.gd.mainFrame:
                if hasattr(self.gd.mainFrame, 'panel') and self.gd.mainFrame.panel:
                    if hasattr(self.gd.mainFrame.panel, 'ctrl') and self.gd.mainFrame.panel.ctrl:
                        return self.gd.mainFrame.panel.ctrl.sp
            return None
        except Exception as e:
            return None
    
    def get_screenplay_context(self, user_message):
        """Get context from the current screenplay based on user query"""
        sp = self.get_current_screenplay()
        if not sp:
            return "No screenplay loaded."
        
        context_parts = []
        
        # Basic script info
        context_parts.append(f"SCRIPT INFO:")
        context_parts.append(f"- Total lines: {len(sp.lines)}")
        context_parts.append(f"- Characters: {len(sp.getCharacterNames())}")
        context_parts.append(f"- Scenes: {len(sp.getSceneLocations())}")
        context_parts.append(f"- Current page: {sp.line2page(sp.line) if sp.line < len(sp.lines) else 'N/A'}")
        
        # Character list
        characters = list(sp.getCharacterNames().keys())
        if characters:
            context_parts.append(f"\nCHARACTERS:")
            context_parts.append(", ".join(characters[:10]))  # Limit to first 10
            if len(characters) > 10:
                context_parts.append(f"... and {len(characters) - 10} more")
        
        # Current scene context
        try:
            current_scene_start, current_scene_end = sp.getSceneIndexesFromLine(sp.line)
            current_scene_text = ""
            for i in range(current_scene_start, min(current_scene_end + 1, len(sp.lines))):
                line = sp.lines[i]
                if line.lt == sp.SCENE and line.lb == sp.LB_LAST:
                    current_scene_text = line.text
                    break
            
            if current_scene_text:
                context_parts.append(f"\nCURRENT SCENE: {current_scene_text}")
        except:
            pass
        
        # Add full script if user requests it or asks for analysis
        analysis_keywords = ['analyze', 'full script', 'entire script', 'whole script', 'complete script']
        if any(keyword in user_message.lower() for keyword in analysis_keywords):
            try:
                # Get script text (limit to reasonable size)
                script_text = sp.generateText(False)
                if len(script_text) > 8000:  # Limit context size
                    script_text = script_text[:8000] + "\n\n[Script truncated for length]"
                context_parts.append(f"\nFULL SCRIPT:\n{script_text}")
            except Exception as e:
                context_parts.append(f"\n[Error getting full script: {e}]")
        
        return "\n".join(context_parts)
    
    def analyze_screenplay(self):
        """Analyze the current screenplay and provide insights"""
        sp = self.get_current_screenplay()
        if not sp:
            return "No screenplay loaded for analysis."
        
        analysis = "SCREENPLAY ANALYSIS:\n\n"
        
        # Basic stats
        total_lines = len(sp.lines)
        characters = list(sp.getCharacterNames().keys())
        scenes = sp.getSceneLocations()
        
        analysis += f"• Total lines: {total_lines}\n"
        analysis += f"• Characters: {len(characters)} ({', '.join(characters[:5])}{'...' if len(characters) > 5 else ''})\n"
        analysis += f"• Scenes: {len(scenes)}\n"
        
        # Element breakdown
        element_counts = {}
        for line in sp.lines:
            element_type = line.lt
            element_counts[element_type] = element_counts.get(element_type, 0) + 1
        
        analysis += f"• Action lines: {element_counts.get(sp.ACTION, 0)}\n"
        analysis += f"• Dialogue lines: {element_counts.get(sp.DIALOGUE, 0)}\n"
        analysis += f"• Scene headings: {element_counts.get(sp.SCENE, 0)}\n"
        
        # Suggestions
        analysis += "\nSUGGESTIONS:\n"
        if len(characters) < 3:
            analysis += "• Consider adding more characters for richer interactions\n"
        if len(scenes) < 5:
            analysis += "• You might want to develop more scenes for a complete story\n"
        if element_counts.get(sp.ACTION, 0) < element_counts.get(sp.DIALOGUE, 0):
            analysis += "• Good balance between action and dialogue\n"
        else:
            analysis += "• Consider adding more dialogue to balance the action-heavy content\n"
        
        return analysis 