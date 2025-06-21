# -*- coding: utf-8 -*-

import wx
import time

class AIAssistantPanel(wx.Panel):
    """Basic AI Assistant Panel similar to Cursor's chat interface"""
    
    def __init__(self, parent, gd):
        wx.Panel.__init__(self, parent, -1)
        
        self.gd = gd
        self.chat_history = []
        
        # Create the main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create chat display area
        self.chat_display = wx.TextCtrl(
            self, -1, 
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.VSCROLL | wx.HSCROLL | wx.BORDER_SUNKEN
        )
        self.chat_display.SetBackgroundColour(wx.Colour(248, 248, 248))
        
        # Create input area
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.input_text = wx.TextCtrl(
            self, -1, 
            style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER,
            size=(-1, 60)
        )
        self.input_text.SetHint("Ask me anything about your screenplay...")
        
        self.send_button = wx.Button(self, -1, "Send")
        self.send_button.SetDefault()
        
        input_sizer.Add(self.input_text, 1, wx.EXPAND | wx.RIGHT, 5)
        input_sizer.Add(self.send_button, 0, wx.EXPAND)
        
        # Add to main sizer
        main_sizer.Add(self.chat_display, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
        
        # Bind events
        self.send_button.Bind(wx.EVT_BUTTON, self.OnSend)
        self.input_text.Bind(wx.EVT_TEXT_ENTER, self.OnSend)
        
        # Add welcome message
        self.add_message("AI Assistant", "Hello! I'm your AI writing assistant. I can help you with:\n\n• Character development\n• Plot suggestions\n• Dialogue improvements\n• Scene structure\n• Genre-specific advice\n\nWhat would you like to work on today?", is_user=False)
    
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
        
        # Simulate AI response (in a real implementation, this would call an AI service)
        self.simulate_ai_response(message)
    
    def simulate_ai_response(self, user_message):
        """Simulate AI response for demo purposes"""
        # This is a simple demo response system
        # In a real implementation, this would call an actual AI service
        
        response = "I understand you're asking about: " + user_message + "\n\n"
        response += "This is a demo response. In a real implementation, I would:\n"
        response += "• Analyze your screenplay context\n"
        response += "• Provide specific writing suggestions\n"
        response += "• Help with character development\n"
        response += "• Suggest plot improvements\n\n"
        response += "Would you like me to analyze your current screenplay?"
        
        # Simulate typing delay
        wx.CallAfter(self.delayed_response, response)
    
    def delayed_response(self, response):
        """Add response after a short delay to simulate AI processing"""
        self.add_message("AI Assistant", response, is_user=False)
    
    def get_screenplay_context(self):
        """Get context from the current screenplay"""
        # This would extract relevant context from the current screenplay
        # For now, return a placeholder
        return "Current screenplay context would be extracted here"
    
    def analyze_screenplay(self):
        """Analyze the current screenplay and provide insights"""
        # This would perform actual analysis
        # For now, return demo analysis
        analysis = "Screenplay Analysis:\n\n"
        analysis += "• Characters: 3 main characters detected\n"
        analysis += "• Scenes: 5 scenes identified\n"
        analysis += "• Dialogue: Good balance between action and dialogue\n"
        analysis += "• Structure: Standard three-act structure detected\n\n"
        analysis += "Suggestions:\n"
        analysis += "• Consider adding more character development in Act 2\n"
        analysis += "• The opening scene could be more engaging\n"
        analysis += "• Dialogue feels natural and flows well"
        
        return analysis 