# -*- coding: utf-8 -*-

import wx
import time
import threading
import hashlib
import base64
import os
from trelby.appearance_utils import get_ai_pane_colors
from trelby.ai_suggestion import AISuggestionManager
from trelby.embedding_service import EmbeddingService
from trelby.ai_service import AIService
import trelby.screenplay as screenplay

class AIAssistantPanel(wx.Panel):
    """AI Assistant Panel with automatic semantic search capabilities"""
    
    def __init__(self, parent, gd):
        wx.Panel.__init__(self, parent, -1)
        
        self.gd = gd
        self.ai_service = None
        self.embedding_service = None
        self.embedding_ai_service = None
        self.embeddings_initialized = False
        self.current_screenplay_hash = None
        self.processing_lock = threading.Lock()  # Keep lock for thread safety
        self.chat_history = []  # Add back the missing chat history
        self.chat_history = []
        self.current_image = None
        
        # Get appearance-aware colors
        self.colors = get_ai_pane_colors()
        
        # Available services and models with image support info
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
        
        # Models that support image input
        self.image_support = {
            "anthropic": [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ],
            "groq": []  # Groq models don't support images yet
        }
        
        # Initialize AI service
        try:
            from trelby.ai import get_ai_service
            self.ai_service = get_ai_service(service_name="anthropic", model="claude-3-5-sonnet-20241022")
            print("✓ AI service initialized successfully")
            self.current_service = "anthropic"
            self.ai_available = True  # Set to True when service is successfully initialized
        except Exception as e:
            print(f"✗ Failed to initialize AI service: {e}")
            self.ai_service = None
            self.ai_available = False
            self.current_service = None
        
        # Initialize embedding service
        try:
            self.embedding_service = EmbeddingService()
            print("✓ Embedding service initialized successfully")
        except Exception as e:
            print(f"✗ Failed to initialize embedding service: {e}")
            self.embedding_service = None
        
        # Initialize embedding AI service
        try:
            self.embedding_ai_service = AIService()
            print("✓ Embedding AI service initialized successfully")
        except Exception as e:
            print(f"✗ Failed to initialize embedding AI service: {e}")
            self.embedding_ai_service = None
        
        # Initialize UI
        self.init_ui()
        
        # No more constant monitoring - we'll update on-demand
    
    def init_ui(self):
        """Initialize the UI components"""
        # Get appearance-aware colors
        self.colors = get_ai_pane_colors()
        
        # Create the main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create status bar for embedding info
        self.status_bar = wx.StaticText(self, -1, "Initializing...")
        self.status_bar.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        main_sizer.Add(self.status_bar, 0, wx.EXPAND | wx.ALL, 2)
        
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
        
        # Create image input area
        image_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.image_button = wx.Button(self, -1, "📷 Add Image")
        self.image_button.SetBackgroundColour(self.colors['button_background'])
        self.image_button.SetForegroundColour(self.colors['button_text'])
        
        self.image_label = wx.StaticText(self, -1, "No image selected")
        self.image_label.SetForegroundColour(self.colors['text'])
        
        self.clear_image_button = wx.Button(self, -1, "❌ Clear")
        self.clear_image_button.SetBackgroundColour(self.colors['button_background'])
        self.clear_image_button.SetForegroundColour(self.colors['button_text'])
        self.clear_image_button.Disable()
        
        image_sizer.Add(self.image_button, 0, wx.RIGHT, 5)
        image_sizer.Add(self.image_label, 1, wx.EXPAND)
        image_sizer.Add(self.clear_image_button, 0)
        
        # Create image preview area
        self.image_preview = wx.StaticBitmap(self, -1, wx.NullBitmap, size=(200, 150))
        self.image_preview.SetBackgroundColour(self.colors['background'])
        self.image_preview.Hide()  # Initially hidden
        
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
        main_sizer.Add(image_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.image_preview, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        main_sizer.Add(self.chat_display, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
        
        # Bind events
        self.send_button.Bind(wx.EVT_BUTTON, self.OnSend)
        self.input_text.Bind(wx.EVT_TEXT_ENTER, self.OnSend)
        self.service_choice.Bind(wx.EVT_CHOICE, self.OnServiceChange)
        self.model_choice.Bind(wx.EVT_CHOICE, self.OnModelChange)
        self.image_button.Bind(wx.EVT_BUTTON, self.OnAddImage)
        self.clear_image_button.Bind(wx.EVT_BUTTON, self.OnClearImage)
        
        # Update image button state
        self.update_image_button_state()
        
        # Add welcome message
        if self.ai_service:
            welcome_msg = "Hello! I'm your AI writing assistant with automatic semantic search. I can help you with:\n\n• Character development and analysis\n• Plot suggestions and story structure\n• Dialogue improvements\n• Scene analysis and suggestions\n• Story themes and motifs\n\nI'll automatically analyze your screenplay and provide context-aware suggestions!"
        else:
            welcome_msg = "AI Assistant is not available. Please check your API key configuration in the .env file."
        
        self.add_message("AI Assistant", welcome_msg, is_user=False)
    
    def process_screenplay_embeddings(self, screenplay):
        """Process screenplay embeddings in background thread (legacy method)"""
        # This method is kept for compatibility but now uses synchronous processing
        print("Debug: Legacy process_screenplay_embeddings called, using sync method")
        return self.process_screenplay_embeddings_sync(screenplay)
    
    def update_status(self, message):
        """Update the status bar message"""
        wx.CallAfter(self.status_bar.SetLabel, message)
    
    def update_image_button_state(self):
        """Update image button state based on current model support"""
        selected_service = self.service_choice.GetString(self.service_choice.GetSelection())
        selected_model = self.model_choice.GetString(self.model_choice.GetSelection())
        
        supports_images = selected_model in self.image_support.get(selected_service, [])
        
        if supports_images:
            self.image_button.Enable()
            self.image_button.SetLabel("📷 Add Image")
        else:
            self.image_button.Disable()
            self.image_button.SetLabel("📷 Add Image (Not Supported)")
    
    def OnAddImage(self, event):
        """Handle image selection"""
        with wx.FileDialog(self, "Select an image", wildcard="Image files (*.png;*.jpg;*.jpeg;*.gif;*.bmp)|*.png;*.jpg;*.jpeg;*.gif;*.bmp",
                          style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            # Get the selected file path
            pathname = fileDialog.GetPath()
            
            try:
                # Read and encode the image
                with open(pathname, "rb") as image_file:
                    image_data = image_file.read()
                    self.current_image = {
                        'data': image_data,
                        'filename': os.path.basename(pathname),
                        'path': pathname
                    }
                
                # Load and display the image preview
                self.load_image_preview(pathname)
                
                # Update UI
                self.image_label.SetLabel(f"📷 {os.path.basename(pathname)}")
                self.clear_image_button.Enable()
                
                # Add system message about image
                self.add_message("AI Assistant", f"Image '{os.path.basename(pathname)}' loaded. You can now ask questions about it!", is_user=False)
                
            except Exception as e:
                wx.MessageBox(f"Error loading image: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    
    def load_image_preview(self, image_path):
        """Load and display image preview"""
        try:
            # Load the image
            image = wx.Image(image_path)
            
            # Resize image to fit preview area (max 200x150)
            max_width = 200
            max_height = 150
            
            img_width, img_height = image.GetSize()
            
            # Calculate scaling factor
            scale_x = max_width / img_width
            scale_y = max_height / img_height
            scale = min(scale_x, scale_y)
            
            # Resize image
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            image = image.Scale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)
            
            # Convert to bitmap and display
            bitmap = wx.Bitmap(image)
            self.image_preview.SetBitmap(bitmap)
            self.image_preview.Show()
            
            # Refresh layout
            self.Layout()
            
        except Exception as e:
            print(f"Error loading image preview: {e}")
            self.image_preview.Hide()
    
    def OnClearImage(self, event):
        """Handle image clearing"""
        self.current_image = None
        self.image_label.SetLabel("No image selected")
        self.clear_image_button.Disable()
        self.image_preview.Hide()
        self.Layout()
        self.add_message("AI Assistant", "Image cleared.", is_user=False)
    
    def OnServiceChange(self, event):
        """Handle service selection change"""
        selected_service = self.service_choice.GetString(self.service_choice.GetSelection())
        
        # Update model choices for the selected service
        models = self.available_services[selected_service]
        self.model_choice.Clear()
        for model in models:
            self.model_choice.Append(model)
        self.model_choice.SetSelection(0)
        
        # Update current service
        self.current_service = selected_service
        
        # Update image button state
        self.update_image_button_state()
        
        # Try to create new service with first model
        try:
            from trelby.ai import get_ai_service
            self.ai_service = get_ai_service(service_name=selected_service, model=models[0])
            self.ai_available = True  # Set to True when service is successfully created
            self.add_message("AI Assistant", f"Switched to {selected_service} with {models[0]}. How can I help you?", is_user=False)
        except Exception as e:
            self.ai_available = False  # Set to False if service creation fails
            self.add_message("AI Assistant", f"Error switching to {selected_service}: {str(e)}", is_user=False)
    
    def OnModelChange(self, event):
        """Handle model selection change"""
        selected_service = self.service_choice.GetString(self.service_choice.GetSelection())
        selected_model = self.model_choice.GetString(self.model_choice.GetSelection())
        
        # Update image button state
        self.update_image_button_state()
        
        try:
            # Create new AI service with selected model
            from trelby.ai import get_ai_service
            self.ai_service = get_ai_service(service_name=selected_service, model=selected_model)
            self.ai_available = True  # Set to True when service is successfully created
            
            # Add system message about model change
            self.add_message("AI Assistant", f"Switched to {selected_model}. How can I help you?", is_user=False)
        except Exception as e:
            self.ai_available = False  # Set to False if service creation fails
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
        
        # Update image button colors
        self.image_button.SetBackgroundColour(self.colors['button_background'])
        self.image_button.SetForegroundColour(self.colors['button_text'])
        self.image_button.Refresh()
        
        self.clear_image_button.SetBackgroundColour(self.colors['button_background'])
        self.clear_image_button.SetForegroundColour(self.colors['button_text'])
        self.clear_image_button.Refresh()
        
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
        
        # If it's an AI message and contains actionable content, show "Add to Script" button
        if not is_user and self.is_actionable_content(message):
            self.show_add_to_script_button(message)
    
    def is_actionable_content(self, message):
        """Check if the AI response contains content that could be added to the script"""
        # Disable automatic popup for now
        return False
        
        actionable_keywords = [
            'scene', 'character', 'dialogue', 'action', 'description', 'setting',
            'location', 'interior', 'exterior', 'day', 'night', 'morning', 'evening',
            'close up', 'wide shot', 'medium shot', 'fade', 'cut to', 'dissolve'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in actionable_keywords)
    
    def show_add_to_script_button(self, content):
        """Show a button to add AI content to the script"""
        # Extract just the actionable content from the AI response
        # Look for content that appears to be actual script content
        actionable_content = self.extract_actionable_content(content)
        
        if not actionable_content:
            wx.MessageBox("No actionable content found in the AI response.", "Info", wx.OK | wx.ICON_INFORMATION)
            return
        
        # Create a dialog with the content and options
        dialog = wx.Dialog(self, -1, "Add to Script", size=(500, 400))
        
        # Create sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add label
        label = wx.StaticText(dialog, -1, "AI Generated Content:")
        sizer.Add(label, 0, wx.ALL, 5)
        
        # Add content text area
        content_text = wx.TextCtrl(dialog, -1, actionable_content, 
                                  style=wx.TE_MULTILINE | wx.TE_READONLY,
                                  size=(-1, 200))
        sizer.Add(content_text, 1, wx.EXPAND | wx.ALL, 5)
        
        # Add insertion options
        options_label = wx.StaticText(dialog, -1, "Insert as:")
        sizer.Add(options_label, 0, wx.ALL, 5)
        
        # Radio buttons for insertion type
        self.insert_type = wx.RadioBox(dialog, -1, "", 
                                      choices=["Action Line", "Scene Heading", "Character Name", "Dialogue", "Parenthetical"],
                                      majorDimension=1, style=wx.RA_SPECIFY_COLS)
        sizer.Add(self.insert_type, 0, wx.EXPAND | wx.ALL, 5)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_button = wx.Button(dialog, wx.ID_OK, "Add to Script")
        cancel_button = wx.Button(dialog, wx.ID_CANCEL, "Cancel")
        
        button_sizer.Add(add_button, 0, wx.RIGHT, 5)
        button_sizer.Add(cancel_button, 0)
        
        sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        
        dialog.SetSizer(sizer)
        
        # Show dialog
        if dialog.ShowModal() == wx.ID_OK:
            self.insert_content_to_script(actionable_content, self.insert_type.GetSelection())
        
        dialog.Destroy()
    
    def extract_actionable_content(self, content):
        """Extract just the actionable script content from the AI response"""
        # Split content into lines
        lines = content.split('\n')
        actionable_lines = []
        
        # Look for lines that appear to be actual script content
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines that are clearly explanations or commentary
            if any(skip_word in line.lower() for skip_word in [
                'here\'s', 'here is', 'i suggest', 'you could', 'consider', 
                'try this', 'example', 'suggestion', 'note:', 'tip:', 'advice:',
                'ai assistant:', 'claude:', 'assistant:', 'user:', 'you:'
            ]):
                continue
                
            # Skip lines that are too long (likely explanations)
            if len(line) > 100:
                continue
                
            # Look for lines that look like script content
            if any(keyword in line.lower() for keyword in [
                'int.', 'ext.', 'scene', 'action', 'dialogue', 'character',
                '(', ')', 'fade', 'cut', 'dissolve', 'close up', 'wide shot'
            ]):
                actionable_lines.append(line)
            elif line.isupper() and len(line) > 3:  # Likely character names or scene headings
                actionable_lines.append(line)
            elif line.startswith('(') and line.endswith(')'):  # Parentheticals
                actionable_lines.append(line)
            elif len(line) < 80 and not line.startswith('Here') and not line.startswith('I '):  # Short action lines
                actionable_lines.append(line)
        
        # If we found actionable content, return it
        if actionable_lines:
            return '\n'.join(actionable_lines)
        
        # If no specific content found, return the first non-empty line that's not an explanation
        for line in lines:
            line = line.strip()
            if line and len(line) < 100 and not any(skip_word in line.lower() for skip_word in [
                'here\'s', 'here is', 'i suggest', 'you could', 'consider', 
                'try this', 'example', 'suggestion', 'note:', 'tip:', 'advice:'
            ]):
                return line
        
        return content  # Fallback to original content if nothing else works
    
    def insert_content_to_script(self, content, insert_type):
        """Insert AI-generated content into the screenplay"""
        sp = self.get_current_screenplay()
        if not sp:
            wx.MessageBox("No screenplay loaded. Please open a screenplay first.", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        try:
            # Determine the line type based on selection
            line_types = {
                0: screenplay.ACTION,      # Action Line
                1: screenplay.SCENE,       # Scene Heading
                2: screenplay.CHARACTER,   # Character Name
                3: screenplay.DIALOGUE,    # Dialogue
                4: screenplay.PAREN        # Parenthetical
            }
            
            target_type = line_types.get(insert_type, screenplay.ACTION)
            
            # Clean up the content for insertion
            cleaned_content = self.clean_content_for_insertion(content, target_type)
            
            # Split content into lines if it contains newlines
            content_lines = cleaned_content.split('\n')
            
            # Create Line objects for each line
            from trelby.line import Line
            new_lines = []
            
            for i, line_content in enumerate(content_lines):
                if line_content.strip():  # Only add non-empty lines
                    # Set line break type: LB_LAST for last line, LB_FORCED for others
                    lb_type = screenplay.LB_LAST if i == len(content_lines) - 1 else screenplay.LB_FORCED
                    new_line = Line(lb_type, target_type, line_content.strip())
                    new_lines.append(new_line)
            
            # If no valid lines, create one empty line
            if not new_lines:
                new_lines = [Line(screenplay.LB_LAST, target_type, "")]
            
            # Append all new lines to the end of the screenplay
            for new_line in new_lines:
                sp.lines.append(new_line)
            
            # Move cursor to the last new line
            sp.line = len(sp.lines) - 1
            sp.column = 0
            
            # Mark the screenplay as changed
            sp.markChanged()
            
            # Refresh the main editor
            if hasattr(self.gd, 'mainFrame') and self.gd.mainFrame:
                if hasattr(self.gd.mainFrame, 'panel') and self.gd.mainFrame.panel:
                    if hasattr(self.gd.mainFrame.panel, 'ctrl') and self.gd.mainFrame.panel.ctrl:
                        self.gd.mainFrame.panel.ctrl.Refresh()
            
            wx.MessageBox(f"Content added to script as {['Action Line', 'Scene Heading', 'Character Name', 'Dialogue', 'Parenthetical'][insert_type]}", 
                         "Success", wx.OK | wx.ICON_INFORMATION)
            
        except Exception as e:
            wx.MessageBox(f"Error inserting content: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    
    def clean_content_for_insertion(self, content, line_type):
        """Clean and format content for insertion into the screenplay"""
        # Remove common AI prefixes and formatting
        content = content.strip()
        
        # Remove quotes if present
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]
        
        # Remove AI assistant prefixes
        prefixes_to_remove = [
            "AI Assistant: ",
            "Here's a ",
            "Here is a ",
            "I suggest ",
            "You could write ",
            "Consider adding ",
            "Try this: ",
            "Here's an example: ",
            "Example: ",
            "Suggestion: "
        ]
        
        for prefix in prefixes_to_remove:
            if content.startswith(prefix):
                content = content[len(prefix):].strip()
        
        # Format based on line type
        if line_type == screenplay.SCENE:
            # Ensure scene headings are in proper format
            if not content.upper() == content:
                content = content.upper()
            if not content.startswith(('INT.', 'EXT.', 'INT/EXT.')):
                # Try to detect if it should be INT or EXT
                if any(word in content.lower() for word in ['inside', 'interior', 'room', 'house', 'building', 'office']):
                    content = f"INT. {content}"
                elif any(word in content.lower() for word in ['outside', 'exterior', 'street', 'park', 'forest', 'beach']):
                    content = f"EXT. {content}"
                else:
                    content = f"INT. {content}"  # Default to INT
        
        elif line_type == screenplay.CHARACTER:
            # Ensure character names are in proper format
            if not content.upper() == content:
                content = content.upper()
        
        elif line_type == screenplay.PAREN:
            # Ensure parentheticals are properly formatted
            if not content.startswith('(') and not content.endswith(')'):
                content = f"({content})"
        
        return content
    
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
        if self.ai_service:
            # Run AI call in background thread
            thread = threading.Thread(target=self.get_ai_response, args=(message,))
            thread.daemon = True
            thread.start()
        else:
            self.add_message("AI Assistant", "AI service is not available. Please check your configuration.", is_user=False)
            self.send_button.Enable()
            self.send_button.SetLabel("Send")
    
    def get_ai_response(self, user_message):
        """Get response from Claude in background thread with semantic search"""
        try:
            # Check if screenplay has changed and update embeddings if needed
            print("Debug: Checking if screenplay needs embedding update...")
            self.ensure_embeddings_up_to_date()
            
            # Get semantic context from embeddings if available
            semantic_context = ""
            if self.embedding_ai_service and self.embeddings_initialized:
                print("Debug: Getting semantic context from embeddings...")
                semantic_context = self.embedding_ai_service.get_semantic_context(user_message, n_results=3)
                print(f"Debug: Semantic context length: {len(semantic_context)} characters")
            
            # Get basic document context
            basic_context = self.get_basic_context()
            
            # Combine contexts
            if semantic_context:
                combined_context = f"{basic_context}\n\n{semantic_context}"
            else:
                combined_context = basic_context
            
            # Get conversation history
            conversation_history = self.chat_history.copy()
            
            # Debug logging
            print(f"Debug: Sending conversation with {len(conversation_history)} previous messages")
            if conversation_history:
                recent_messages = conversation_history[-6:]  # Last 6 messages
                print(f"Debug: Recent conversation:")
                for msg in recent_messages:
                    sender = "User" if msg['is_user'] else "AI"
                    preview = msg['message'][:50] + "..." if len(msg['message']) > 50 else msg['message']
                    print(f"  {sender}: {preview}")
            
            # Get AI response with combined context
            # Pass the current AI service to use the correct model
            response = self.embedding_ai_service.get_response(user_message, combined_context, conversation_history, self.ai_service)
            
            # Update UI in main thread
            wx.CallAfter(self.handle_ai_response, response)
        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            wx.CallAfter(self.handle_ai_response, error_msg)
    
    def handle_ai_response(self, response):
        """Handle AI response in main thread"""
        # Always show as regular message (insertion feature removed)
        self.add_message("AI Assistant", response, is_user=False)

        self.send_button.Enable()
        self.send_button.SetLabel("Send")
    
    def add_selected_text_to_chat(self):
        """Add selected text to the chat input field"""
        selected_text = self.get_selected_text()
        if selected_text:
            # Truncate for display if too long
            preview = selected_text[:100] + "..." if len(selected_text) > 100 else selected_text
            current_input = self.input_text.GetValue()
            
            if current_input:
                # If there's already text, add a separator
                new_input = current_input + "\n\nSelected text:\n" + preview
            else:
                new_input = "Selected text:\n" + preview
            
            self.input_text.SetValue(new_input)
            self.input_text.SetFocus()
            
            # Show a brief message in chat
            self.add_message("System", f"Added selected text to input ({len(selected_text)} characters)", is_user=False)
        else:
            # Show error message
            self.add_message("System", "No text selected. Please select some text first.", is_user=False)
    
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
            print(f"Error accessing screenplay: {e}")
            return None
    
    def get_screenplay_ctrl(self):
        """Get the screenplay control object"""
        try:
            # Access current screenplay control through the main frame
            if hasattr(self.gd, 'mainFrame') and self.gd.mainFrame:
                if hasattr(self.gd.mainFrame, 'panel') and self.gd.mainFrame.panel:
                    return self.gd.mainFrame.panel.ctrl
            return None
        except Exception as e:
            print(f"Error accessing screenplay control: {e}")
            return None
    
    def get_basic_context(self):
        """Get basic context from the current screenplay"""
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
                if line.lt == screenplay.SCENE and line.lb == screenplay.LB_LAST:
                    current_scene_text = line.text
                    break
            
            if current_scene_text:
                context_parts.append(f"\nCURRENT SCENE: {current_scene_text}")
        except:
            pass
        
        return "\n".join(context_parts)
    
    def get_screenplay_context(self, user_message):
        """Get context from the current screenplay based on user query (legacy method)"""
        sp = self.get_current_screenplay()
        if not sp:
            return "No screenplay loaded."
        
        # Check if user message contains selected text (added via menu)
        if "Selected text:" in user_message:
            # Extract the selected text from the message
            lines = user_message.split('\n')
            selected_text = ""
            in_selected_section = False
            
            for line in lines:
                if line.strip() == "Selected text:":
                    in_selected_section = True
                    continue
                elif in_selected_section and line.strip() == "":
                    break
                elif in_selected_section:
                    selected_text += line + "\n"
            
            if selected_text.strip():
                context_parts = []
                context_parts.append("SELECTED TEXT:")
                context_parts.append(selected_text.strip())
                context_parts.append("\n" + "="*50 + "\n")
                
                # Add basic script info for context
                context_parts.append("SCRIPT INFO:")
                context_parts.append(f"- Total lines: {len(sp.lines)}")
                context_parts.append(f"- Characters: {len(sp.getCharacterNames())}")
                context_parts.append(f"- Scenes: {len(sp.getSceneLocations())}")
                context_parts.append(f"- Current page: {sp.line2page(sp.line) if sp.line < len(sp.lines) else 'N/A'}")
                
                return "\n".join(context_parts)
        
        # Fall back to basic context
        return self.get_basic_context()
    
    def get_selected_text(self):
        """Get the currently selected text from the screenplay"""
        sp = self.get_current_screenplay()
        if not sp:
            return None
        
        # Get selected text as ClipData
        cd = sp.getSelectedAsCD(False)
        if not cd or not cd.lines:
            return None
        
        # Convert ClipData lines to text
        selected_lines = []
        for line in cd.lines:
            selected_lines.append(line.text)
        
        # Join lines with appropriate line breaks
        selected_text = "\n".join(selected_lines)
        
        # Only return if there's actually some text selected
        if selected_text.strip():
            return selected_text
        
        return None
    
    def clear_conversation_history(self):
        """Clear the conversation history"""
        self.chat_history = []
        self.chat_display.SetValue("")
        
        # Add welcome message back
        if self.ai_service:
            welcome_msg = "Conversation cleared. I'm ready to help you with your screenplay!"
        else:
            welcome_msg = "Conversation cleared. AI service is not available."
        
        self.add_message("AI Assistant", welcome_msg, is_user=False)
    
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
        
        # Embedding status
        if self.embeddings_initialized and self.embedding_ai_service:
            info = self.embedding_ai_service.get_collection_info()
            analysis += f"• Semantic search: {info['document_count']} scenes analyzed\n"
        else:
            analysis += "• Semantic search: Processing...\n"
        
        # Suggestions
        analysis += "\nSUGGESTIONS:\n"
        if len(characters) < 3:
            analysis += "• Consider adding more characters for richer interactions\n"
        if len(scenes) < 5:
            analysis += "• You might want to develop more scenes for a complete story\n"
        if element_counts.get(screenplay.ACTION, 0) < element_counts.get(screenplay.DIALOGUE, 0):
            analysis += "• Good balance between action and dialogue\n"
        else:
            analysis += "• Consider adding more dialogue to balance the action-heavy content\n"
        
        return analysis
    
    def get_screenplay_hash(self, screenplay):
        """Create a simple hash of the screenplay content to detect changes"""
        try:
            if not hasattr(screenplay, 'lines'):
                print("Debug: Screenplay has no lines attribute")
                return None
            
            # Use the first 1000 characters and total line count as a simple hash
            content = ""
            line_count = len(screenplay.lines)
            
            for i, line in enumerate(screenplay.lines):
                if i < 50:  # First 50 lines
                    content += line.text
                if len(content) > 1000:
                    break
            
            hash_input = content + str(line_count)
            hash_result = hash(hash_input)
            
            # Only log hash details when there's a significant change
            if not hasattr(self, '_last_hash_log') or self._last_hash_log != hash_result:
                print(f"Debug: Hash calculation - {line_count} lines, {len(content)} chars, hash: {hash_result}")
                self._last_hash_log = hash_result
            
            return hash_result
        except Exception as e:
            print(f"Debug: Error calculating screenplay hash: {e}")
            print(f"Debug: Exception type: {type(e)}")
            return None
    
    def ensure_embeddings_up_to_date(self):
        """Check if screenplay has changed and update embeddings if needed"""
        try:
            screenplay = self.get_current_screenplay()
            if not screenplay:
                print("Debug: No screenplay available for embedding update")
                return False
            
            # Calculate current hash
            current_hash = self.get_screenplay_hash(screenplay)
            if current_hash is None:
                print("Debug: Could not calculate screenplay hash")
                return False
            
            # Check if screenplay has changed
            if current_hash == self.current_screenplay_hash:
                print("Debug: Screenplay unchanged, embeddings are up to date")
                # Update embedding AI service hash to maintain cache consistency
                if self.embedding_ai_service:
                    self.embedding_ai_service.update_screenplay_hash(current_hash)
                return True
            
            print(f"Debug: Screenplay changed, updating embeddings")
            print(f"Debug: Old hash: {self.current_screenplay_hash}")
            print(f"Debug: New hash: {current_hash}")
            
            # Update embeddings
            success = self.process_screenplay_embeddings_sync(screenplay)
            if success:
                self.current_screenplay_hash = current_hash
                # Update embedding AI service hash to maintain cache consistency
                if self.embedding_ai_service:
                    self.embedding_ai_service.update_screenplay_hash(current_hash)
                return True
            else:
                print("Debug: Failed to update embeddings")
                return False
                
        except Exception as e:
            print(f"Debug: Error ensuring embeddings up to date: {e}")
            return False
    
    def process_screenplay_embeddings_sync(self, screenplay):
        """Process screenplay embeddings synchronously (for on-demand updates)"""
        try:
            print("Debug: Processing screenplay embeddings synchronously")
            print(f"Debug: Screenplay object type: {type(screenplay)}")
            print(f"Debug: Screenplay has 'lines' attribute: {hasattr(screenplay, 'lines')}")
            if hasattr(screenplay, 'lines'):
                print(f"Debug: Screenplay has {len(screenplay.lines)} lines")
            
            # Clear existing embeddings first
            if self.embedding_ai_service:
                print("Debug: Clearing existing embeddings...")
                self.embedding_ai_service.clear_embeddings()
                # Clear context cache for new screenplay (keep system prompt)
                self.embedding_ai_service.clear_context_cache()
            
            # Store new embeddings
            print("Debug: Storing new screenplay embeddings...")
            success = self.embedding_ai_service.store_screenplay_embeddings(screenplay)
            print(f"Debug: Embedding storage result: {success}")
            
            if success:
                # Get collection info
                print("Debug: Getting collection info...")
                info = self.embedding_ai_service.get_collection_info()
                print(f"Debug: Collection info: {info}")
                
                self.embeddings_initialized = True
                status_msg = f"✓ Semantic search ready ({info['document_count']} scenes analyzed)"
                print(f"Debug: Setting status: {status_msg}")
                self.update_status(status_msg)
                
                # Add a helpful message to the chat
                chat_msg = f"Screenplay updated! I can now help you with character development, plot analysis, scene structure, and finding patterns in your {info['document_count']} scenes."
                print(f"Debug: Adding chat message: {chat_msg}")
                self.add_message("System", chat_msg, is_user=False)
                return True
            else:
                print("Debug: Embedding storage failed, setting error status")
                self.update_status("⚠ Semantic search not available")
                self.embeddings_initialized = False
                return False
        except Exception as e:
            print(f"Debug: Exception in embedding processing: {e}")
            print(f"Debug: Exception type: {type(e)}")
            import traceback
            print(f"Debug: Traceback: {traceback.format_exc()}")
            self.update_status(f"Error processing screenplay: {e}")
            self.embeddings_initialized = False
            return False 