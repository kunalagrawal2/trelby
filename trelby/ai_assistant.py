# -*- coding: utf-8 -*-

import wx
import time
import threading
import hashlib
from trelby.ai_service import AIService
from trelby.appearance_utils import get_ai_pane_colors
from trelby.ai_suggestion import AISuggestionManager

class AIAssistantPanel(wx.Panel):
    """AI Assistant Panel with automatic semantic search capabilities"""
    
    def __init__(self, parent, gd):
        wx.Panel.__init__(self, parent, -1)
        
        self.gd = gd
        self.ai_service = None
        self.embeddings_initialized = False
        self.current_screenplay_hash = None
        self.processing_lock = threading.Lock()  # Keep lock for thread safety
        self.chat_history = []  # Add back the missing chat history
        
        # Initialize AI service
        try:
            self.ai_service = AIService()
            print("✓ AI service initialized with embeddings")
        except Exception as e:
            print(f"✗ Failed to initialize AI service: {e}")
            self.ai_service = None
        
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
        main_sizer.Add(self.chat_display, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
        
        # Bind events
        self.send_button.Bind(wx.EVT_BUTTON, self.OnSend)
        self.input_text.Bind(wx.EVT_TEXT_ENTER, self.OnSend)
        
        # Add welcome message
        if self.ai_service:
            welcome_msg = "Hello! I'm your AI writing assistant powered by Claude with automatic semantic search. I can help you with:\n\n• Character development and analysis\n• Plot suggestions and story structure\n• Dialogue improvements\n• Scene analysis and suggestions\n• Story themes and motifs\n\nI'll automatically analyze your screenplay and provide context-aware suggestions!"
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
            
            # Get document context (simplified for AI service)
            context = self.get_basic_context()
            
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
            
            # Get AI response with semantic search context
            response = self.ai_service.get_response(user_message, context, conversation_history)
            
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
                if line.lt == sp.SCENE and line.lb == sp.LB_LAST:
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
        if self.embeddings_initialized:
            info = self.ai_service.get_collection_info()
            analysis += f"• Semantic search: {info['document_count']} scenes analyzed\n"
        else:
            analysis += "• Semantic search: Processing...\n"
        
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
                return True
            
            print(f"Debug: Screenplay changed, updating embeddings")
            print(f"Debug: Old hash: {self.current_screenplay_hash}")
            print(f"Debug: New hash: {current_hash}")
            
            # Update embeddings
            success = self.process_screenplay_embeddings_sync(screenplay)
            if success:
                self.current_screenplay_hash = current_hash
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
            if self.ai_service:
                print("Debug: Clearing existing embeddings...")
                self.ai_service.clear_embeddings()
                # Clear system prompt cache for new screenplay
                self.ai_service.clear_system_prompt_cache()
            
            # Store new embeddings
            print("Debug: Storing new screenplay embeddings...")
            success = self.ai_service.store_screenplay_embeddings(screenplay)
            print(f"Debug: Embedding storage result: {success}")
            
            if success:
                # Get collection info
                print("Debug: Getting collection info...")
                info = self.ai_service.get_collection_info()
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