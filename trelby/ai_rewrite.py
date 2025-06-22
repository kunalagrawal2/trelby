# -*- coding: utf-8 -*-

import wx
import threading
from trelby.screenplay_formatter import fix_formatting

class AIRewrite(wx.Dialog):
    """Dialog for AI text rewriting with accept/reject functionality"""
    
    def __init__(self, parent, ai_service, original_text):
        wx.Dialog.__init__(self, parent, -1, "AI Rewrite", size=(700, 500))
        
        self.original_text = original_text
        self.ai_service = ai_service
        self.ai_suggestion = ""
        
        self.init_ui()
        
        # Don't start AI rewrite automatically - wait for user instructions
        
    def init_ui(self):
        """Initialize the user interface"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Instructions label
        instructions_label = wx.StaticText(self, -1, "How would you like to rewrite this text? (optional)")
        instructions_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(instructions_label, 0, wx.ALL, 10)
        
        # Instructions text input
        self.instructions_text = wx.TextCtrl(
            self, -1, "", 
            style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER,
            size=(-1, 60)
        )
        self.instructions_text.SetHint("e.g., 'Make it more dramatic', 'Simplify the language', 'Add more detail', etc.")
        main_sizer.Add(self.instructions_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        # Original text section
        original_label = wx.StaticText(self, -1, "Original Text:")
        original_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(original_label, 0, wx.ALL, 10)
        
        self.original_text_ctrl = wx.TextCtrl(
            self, -1, self.original_text,
            style=wx.TE_MULTILINE | wx.TE_READONLY,
            size=(-1, 100)
        )
        main_sizer.Add(self.original_text_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        # AI suggestion section
        suggestion_label = wx.StaticText(self, -1, "AI Suggestion:")
        suggestion_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(suggestion_label, 0, wx.ALL, 10)
        
        self.suggestion_text_ctrl = wx.TextCtrl(
            self, -1, "Enter instructions above and click 'Generate Rewrite' to get an AI suggestion.",
            style=wx.TE_MULTILINE | wx.TE_READONLY,
            size=(-1, 120)
        )
        main_sizer.Add(self.suggestion_text_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.generate_button = wx.Button(self, -1, "Generate Rewrite")
        self.generate_button.Bind(wx.EVT_BUTTON, self.OnGenerate)
        button_sizer.Add(self.generate_button, 0, wx.ALL, 5)
        
        self.accept_button = wx.Button(self, wx.ID_OK, "Accept")
        self.accept_button.Disable()
        button_sizer.Add(self.accept_button, 0, wx.ALL, 5)
        
        self.reject_button = wx.Button(self, wx.ID_CANCEL, "Reject")
        button_sizer.Add(self.reject_button, 0, wx.ALL, 5)
        
        self.regenerate_button = wx.Button(self, -1, "Regenerate")
        self.regenerate_button.Disable()
        button_sizer.Add(self.regenerate_button, 0, wx.ALL, 5)
        
        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        self.SetSizer(main_sizer)
        
        # Bind events
        self.regenerate_button.Bind(wx.EVT_BUTTON, self.OnRegenerate)
        self.accept_button.Bind(wx.EVT_BUTTON, self.OnAccept)
        
        # Bind instructions text change to enable generate button
        self.instructions_text.Bind(wx.EVT_TEXT, self.OnInstructionsChanged)
    
    def OnInstructionsChanged(self, event):
        """Enable generate button when instructions are provided"""
        instructions = self.instructions_text.GetValue().strip()
        self.generate_button.Enable(bool(instructions))
        
        # Enable regenerate button if we have both instructions and a suggestion
        if instructions and self.ai_suggestion:
            self.regenerate_button.Enable()
        else:
            self.regenerate_button.Disable()
        
        event.Skip()
    
    def OnGenerate(self, event):
        """Generate AI rewrite based on instructions"""
        instructions = self.instructions_text.GetValue().strip()
        if not instructions:
            wx.MessageBox("Please enter instructions for the rewrite.", "No Instructions", wx.OK | wx.ICON_INFORMATION)
            return
        
        # Disable buttons during generation
        self.generate_button.Disable()
        self.generate_button.SetLabel("Generating...")
        self.accept_button.Disable()
        self.regenerate_button.Disable()
        
        # Update suggestion text
        self.suggestion_text_ctrl.SetValue("Generating AI suggestion...")
        
        # Start AI generation
        self.get_ai_rewrite()
    
    def OnRegenerate(self, event):
        """Regenerate AI suggestion with new instructions"""
        self.suggestion_text_ctrl.SetValue("Generating new suggestion...")
        self.accept_button.Disable()
        self.regenerate_button.Disable()
        self.get_ai_rewrite()
    
    def OnAccept(self, event):
        """Accept the AI suggestion and replace the text"""
        if self.ai_suggestion:
            self.replace_selected_text(self.ai_suggestion)
        event.Skip()
    
    def get_ai_rewrite(self):
        """Get AI rewrite suggestion in background thread"""
        def ai_thread():
            try:
                # Get user instructions
                instructions = self.instructions_text.GetValue().strip()
                
                # Create a more specific and reliable prompt for screenplay rewriting
                prompt = f"""You are an expert screenplay rewriter and formatter.
Rewrite the following text based on the user's instructions.
Then, format the result using Fountain markup.

Fountain formatting rules:
- Scene headings: Start with # (e.g., "# INT. ROOM - DAY")
- Character names: Start with @ (e.g., "@JOHN")
- Dialogue: Regular text after character name (no special markup)
- Parentheticals: In parentheses (e.g., "(whispering)")
- Transitions: Start with > (e.g., "> FADE OUT")
- Action: Regular text (no special markup)
- Notes: Between /* and */ (e.g., "/* This is a note */")

IMPORTANT FORMATTING GUIDELINES:
1. Scene headings should be in ALL CAPS: INT./EXT. LOCATION - TIME
2. Character names should be in ALL CAPS
3. Transitions should be in ALL CAPS
4. Dialogue should follow character names without any special markup
5. Parentheticals should be on their own line after character names
6. Action lines should be regular text with no markup
7. Maintain proper screenplay structure and flow

User instructions: "{instructions if instructions else 'Improve clarity, flow, and impact while maintaining proper screenplay formatting.'}"

Original text to rewrite:
{self.original_text}

Return ONLY the rewritten, Fountain-formatted screenplay content. No commentary or explanations."""
                
                # Get AI response
                response = self.ai_service.get_simple_response(prompt)
                
                # Update UI on main thread
                wx.CallAfter(self.update_suggestion, response)
                
            except Exception as e:
                error_msg = f"Error getting AI suggestion: {str(e)}"
                wx.CallAfter(self.update_suggestion, error_msg)
        
        # Start background thread
        thread = threading.Thread(target=ai_thread)
        thread.daemon = True
        thread.start()
    
    def update_suggestion(self, suggestion):
        """Update the suggestion text and enable buttons"""
        self.ai_suggestion = suggestion
        self.suggestion_text_ctrl.SetValue(suggestion)
        self.accept_button.Enable()
        
        # Re-enable generate button and reset its label
        self.generate_button.Enable()
        self.generate_button.SetLabel("Generate Rewrite")
        
        # Enable regenerate button if there are instructions
        if self.instructions_text.GetValue().strip():
            self.regenerate_button.Enable()
    
    def replace_selected_text(self, new_text):
        """Replace the selected text with new text"""
        try:
            # Get the current control from the parent frame
            current_ctrl = self.GetParent().panel.ctrl
            
            # Get the current selection
            cd = current_ctrl.sp.getSelectedAsCD(False)
            if not cd:
                return
            
            # Use the existing cut functionality to delete selected text
            current_ctrl.OnCut(doDelete=True, copyToClip=False)
            
            # Use intelligent formatting with AI service to create properly formatted lines
            lines = fix_formatting(new_text, self.ai_service)
            
            # Use Trelby's paste functionality to insert the formatted text
            if lines:
                current_ctrl.sp.paste(lines)
            
        except Exception as e:
            wx.MessageBox(
                f"Error replacing text: {str(e)}",
                "Error",
                wx.OK | wx.ICON_ERROR,
                self
            ) 