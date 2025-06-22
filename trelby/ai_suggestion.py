# -*- coding: utf-8 -*-

import wx
import tempfile
import os

from . import myimport
from . import screenplay

class AISuggestionManager:
    """
    Manages AI-generated suggestions, including generation, insertion,
    and handling of accept/reject actions.
    """

    def __init__(self, parent_frame, screenplay_ctrl):
        self.parent_frame = parent_frame
        self.screenplay_ctrl = screenplay_ctrl
        self.suggestion_active = False
        self.suggestion_start_line = -1
        self.suggestion_end_line = -1

    def insert_suggestion(self, suggestion_fountain_text):
        """
        Inserts a screenplay suggestion into the document.
        The suggestion is provided as a string in Fountain format.
        """
        if self.suggestion_active:
            # For now, only one suggestion at a time.
            # We could extend this to queue suggestions.
            wx.MessageBox("Another suggestion is already active.", "Info", wx.OK | wx.ICON_INFORMATION)
            return

        # Write the Fountain text to a temporary file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".fountain") as temp_f:
            temp_f.write(suggestion_fountain_text)
            temp_filepath = temp_f.name

        try:
            # Use Trelby's Fountain importer to parse the text
            # We need to pass mock objects for some arguments.
            # The dialog options are disabled by passing a dummy function.
            title_pages = [[]]
            
            # The importer shows a dialog. For now, we can't avoid it without
            # refactoring myimport.py. Let's assume default options are fine.
            # A better solution would be to refactor importFountain to allow
            # passing options directly.
            
            lines = myimport.importFountain(temp_filepath, self.parent_frame, title_pages)

            if not lines:
                wx.MessageBox("AI suggestion could not be parsed.", "Error", wx.OK | wx.ICON_ERROR)
                return

            # Insert the lines into the screenplay
            sp = self.screenplay_ctrl.sp
            cursor_line_idx = sp.cursorPos[0]
            
            self.suggestion_start_line = cursor_line_idx + 1
            
            for i, line in enumerate(lines):
                # Mark these lines as suggestions for custom styling/handling
                line.is_suggestion = True
                sp.lines.insert(cursor_line_idx + 1 + i, line)

            self.suggestion_end_line = self.suggestion_start_line + len(lines) - 1
            self.suggestion_active = True
            
            # Refresh the screenplay view
            self.screenplay_ctrl.updateText()
            self.screenplay_ctrl.setCursor((self.suggestion_end_line, 0))
            
            # Inform the user
            wx.MessageBox(f"An AI suggestion has been added from line {self.suggestion_start_line} to {self.suggestion_end_line}.\nRight-click on the suggestion to accept or reject it.", "AI Suggestion", wx.OK | wx.ICON_INFORMATION)

        finally:
            os.remove(temp_filepath)

    def accept_suggestion(self):
        """Accepts the current suggestion."""
        if not self.suggestion_active:
            return

        sp = self.screenplay_ctrl.sp
        for i in range(self.suggestion_start_line, self.suggestion_end_line + 1):
            if hasattr(sp.lines[i], 'is_suggestion'):
                del sp.lines[i].is_suggestion
        
        self.suggestion_active = False
        self.reset_suggestion_state()
        self.screenplay_ctrl.updateText()
        wx.MessageBox("Suggestion accepted.", "Info", wx.OK | wx.ICON_INFORMATION)


    def reject_suggestion(self):
        """Rejects the current suggestion."""
        if not self.suggestion_active:
            return

        sp = self.screenplay_ctrl.sp
        del sp.lines[self.suggestion_start_line : self.suggestion_end_line + 1]
        
        self.reset_suggestion_state()
        self.screenplay_ctrl.updateText()
        self.screenplay_ctrl.setCursor((self.suggestion_start_line, 0))
        wx.MessageBox("Suggestion rejected.", "Info", wx.OK | wx.ICON_INFORMATION)

    def reset_suggestion_state(self):
        self.suggestion_active = False
        self.suggestion_start_line = -1
        self.suggestion_end_line = -1 