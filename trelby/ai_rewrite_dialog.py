# -*- coding: utf-8 -*-

import wx
import threading
import re

class AIRewriteDialog(wx.Dialog):
    """Dialog for AI text rewriting with accept/reject functionality"""
    
    def __init__(self, parent, original_text, ctrl):
        wx.Dialog.__init__(self, parent, -1, "AI Rewrite", size=(600, 400))
        
        self.original_text = original_text
        self.ctrl = ctrl
        self.ai_suggestion = ""
        
        # Initialize AI service
        try:
            from trelby.ai_service import AIService
            self.ai_service = AIService()
            self.ai_available = True
        except Exception as e:
            self.ai_service = None
            self.ai_available = False
            print(f"AI Service not available: {e}")
        
        self.init_ui()
        self.generate_ai_suggestion()
    
    def init_ui(self):
        """Initialize the user interface"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Original text section
        original_label = wx.StaticText(self, -1, "Original Text:")
        self.original_text_ctrl = wx.TextCtrl(
            self, -1, self.original_text,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SUNKEN,
            size=(-1, 80)
        )
        
        # AI suggestion section
        suggestion_label = wx.StaticText(self, -1, "AI Suggestion:")
        self.suggestion_text_ctrl = wx.TextCtrl(
            self, -1, "Generating AI suggestion...",
            style=wx.TE_MULTILINE | wx.BORDER_SUNKEN,
            size=(-1, 120)
        )
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.accept_button = wx.Button(self, wx.ID_OK, "Accept")
        self.accept_button.Disable()  # Disable until AI suggestion is ready
        
        self.reject_button = wx.Button(self, wx.ID_CANCEL, "Reject")
        self.regenerate_button = wx.Button(self, -1, "Regenerate")
        self.regenerate_button.Disable()  # Disable until AI suggestion is ready
        
        button_sizer.Add(self.accept_button, 0, wx.RIGHT, 5)
        button_sizer.Add(self.reject_button, 0, wx.RIGHT, 5)
        button_sizer.Add(self.regenerate_button, 0)
        
        # Add to main sizer
        main_sizer.Add(original_label, 0, wx.ALL, 5)
        main_sizer.Add(self.original_text_ctrl, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(suggestion_label, 0, wx.ALL, 5)
        main_sizer.Add(self.suggestion_text_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        self.SetSizer(main_sizer)
        
        # Bind events
        self.regenerate_button.Bind(wx.EVT_BUTTON, self.OnRegenerate)
        self.accept_button.Bind(wx.EVT_BUTTON, self.OnAccept)
    
    def generate_ai_suggestion(self):
        """Generate AI suggestion in background thread"""
        if not self.ai_available:
            self.suggestion_text_ctrl.SetValue("AI service is not available. Please check your configuration.")
            return
        
        # Run AI call in background thread
        thread = threading.Thread(target=self.get_ai_rewrite, args=(self.original_text,))
        thread.daemon = True
        thread.start()
    
    def get_ai_rewrite(self, text):
        """Get AI rewrite suggestion in background thread"""
        try:
            # Create a specific prompt for screenplay rewriting
            prompt = f"""Please rewrite the following text to improve clarity, flow, and impact while maintaining the same meaning and tone. 

IMPORTANT: Return ONLY the rewritten screenplay content. Do not include:
- Explanations or commentary
- "Here's the rewritten version:" or similar phrases
- "Yes!" or other conversational responses
- Key points or summaries
- Any text that isn't part of the actual screenplay

Just return the pure screenplay text that should replace the original selection.

Original text to rewrite:
{text}"""
            
            # Get AI response
            response = self.ai_service.get_response(prompt)
            
            # Update UI in main thread
            wx.CallAfter(self.handle_ai_response, response)
        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            wx.CallAfter(self.handle_ai_response, error_msg)
    
    def handle_ai_response(self, response):
        """Handle AI response in main thread"""
        self.ai_suggestion = response
        self.suggestion_text_ctrl.SetValue(response)
        
        # Enable buttons
        self.accept_button.Enable()
        self.regenerate_button.Enable()
    
    def OnRegenerate(self, event):
        """Handle regenerate button click"""
        self.suggestion_text_ctrl.SetValue("Generating new AI suggestion...")
        self.accept_button.Disable()
        self.regenerate_button.Disable()
        self.generate_ai_suggestion()
    
    def OnAccept(self, event):
        """Handle accept button click"""
        if self.ai_suggestion:
            # Replace the selected text with AI suggestion
            self.replace_selected_text(self.ai_suggestion)
            self.EndModal(wx.ID_OK)
    
    def detect_screenplay_elements(self, text):
        """Detect screenplay elements in text and return formatted lines"""
        from trelby.screenplay import SCENE, ACTION, CHARACTER, DIALOGUE, PAREN, TRANSITION, SHOT, ACTBREAK, NOTE, LB_LAST, LB_FORCED
        from trelby.line import Line
        
        lines = []
        text_lines = text.strip().split('\n')
        
        for i, line_text in enumerate(text_lines):
            line_text = line_text.strip()
            if not line_text:
                continue
            
            # Determine line type based on content patterns
            line_type = ACTION  # Default to action
            
            # Scene headings (INT./EXT. or INT / EXT)
            if re.match(r'^(INT\.?|EXT\.?|INT\/EXT\.?|I\/E\.?)\s+', line_text, re.IGNORECASE):
                line_type = SCENE
                line_text = line_text.upper()
            
            # Character names (all caps, no period, not too long)
            elif (line_text.isupper() and 
                  len(line_text) <= 50 and 
                  not line_text.endswith('.') and
                  not re.match(r'^(INT\.?|EXT\.?|INT\/EXT\.?|I\/E\.?)\s+', line_text, re.IGNORECASE) and
                  not re.match(r'^(FADE|DISSOLVE|CUT|SMASH|JUMP|MATCH|WIPE|IRIS|FREEZE|SUPER|TITLE|THE END)', line_text, re.IGNORECASE)):
                line_type = CHARACTER
            
            # Parentheticals (enclosed in parentheses)
            elif line_text.startswith('(') and line_text.endswith(')'):
                line_type = PAREN
            
            # Transitions (specific transition words)
            elif re.match(r'^(FADE|DISSOLVE|CUT|SMASH|JUMP|MATCH|WIPE|IRIS|FREEZE|SUPER|TITLE|THE END)', line_text, re.IGNORECASE):
                line_type = TRANSITION
                line_text = line_text.upper()
            
            # Shot descriptions (CAMERA, ANGLE, CLOSE UP, etc.)
            elif re.match(r'^(CAMERA|ANGLE|CLOSE UP|CLOSEUP|WIDE|MEDIUM|LONG|EXTREME|POV|OVER THE SHOULDER|OTS)', line_text, re.IGNORECASE):
                line_type = SHOT
                line_text = line_text.upper()
            
            # Act breaks
            elif re.match(r'^(ACT\s+\d+|END\s+OF\s+ACT\s+\d+)', line_text, re.IGNORECASE):
                line_type = ACTBREAK
                line_text = line_text.upper()
            
            # Notes (if prefixed with NOTE: or similar)
            elif re.match(r'^(NOTE|COMMENT|TODO):', line_text, re.IGNORECASE):
                line_type = NOTE
            
            # Dialogue (if preceded by character name, this will be handled by the screenplay logic)
            # For now, we'll let the screenplay's automatic detection handle this
            
            # Determine line break type
            if i == len(text_lines) - 1:
                lb = LB_LAST  # Last line
            else:
                lb = LB_FORCED  # Force line break for multi-line elements
            
            # Create Line object
            line = Line(lb, line_type, line_text)
            lines.append(line)
        
        return lines
    
    def replace_selected_text(self, new_text):
        """Replace the selected text with new text, properly formatted"""
        try:
            # Get the current selection
            cd = self.ctrl.sp.getSelectedAsCD(False)
            if not cd:
                return
            
            # Use the existing cut functionality to delete selected text
            # This will also copy it to clipboard, but that's fine
            self.ctrl.OnCut(doDelete=True, copyToClip=False)
            
            # Detect and format screenplay elements
            formatted_lines = self.detect_screenplay_elements(new_text)
            
            if formatted_lines:
                # Use the paste functionality for proper formatting
                self.ctrl.sp.paste(formatted_lines)
            else:
                # Fallback to character-by-character insertion
                lines = new_text.split('\n')
                for i, line_text in enumerate(lines):
                    if i > 0:
                        # Add line break for subsequent lines
                        self.ctrl.sp.cmd("insertForcedLineBreak")
                    
                    # Insert the text character by character
                    for char in line_text:
                        self.ctrl.sp.cmd("addChar", char=char)
            
            # Update the screen
            self.ctrl.makeLineVisible(self.ctrl.sp.line)
            self.ctrl.updateScreen()
            
        except Exception as e:
            wx.MessageBox(
                f"Error replacing text: {str(e)}",
                "Error",
                wx.OK | wx.ICON_ERROR,
                self
            ) 