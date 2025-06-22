# -*- coding: utf-8 -*-

import re
from trelby.line import Line
from trelby.screenplay import ACTION, LB_LAST, LB_FORCED, SCENE, CHARACTER, DIALOGUE, PAREN, TRANSITION, SHOT, ACTBREAK, NOTE

def fix_formatting(text):
    """
    Convert plain text to properly formatted screenplay Line objects.
    
    Args:
        text (str): Plain text to format
        
    Returns:
        list: List of Line objects with proper screenplay formatting
    """
    lines = []
    text_lines = text.strip().split('\n')
    
    for i, line_text in enumerate(text_lines):
        line_text = line_text.strip()
        
        # Determine line break type
        if i == len(text_lines) - 1:
            lb = LB_LAST  # Last line
        else:
            lb = LB_FORCED  # Force line break for multi-line elements
        
        # Detect screenplay element type
        line_type = ACTION  # Default to action
        
        # Scene headings (INT., EXT., etc.)
        if re.match(r'^(INT\.|EXT\.|INT/EXT\.|I/E\.)', line_text, re.IGNORECASE):
            line_type = SCENE
            line_text = line_text.upper()
        
        # Character names (all caps, no period, reasonable length)
        elif (line_text.isupper() and 
              len(line_text) <= 50 and 
              not line_text.endswith('.') and
              not re.match(r'^(INT\.|EXT\.|INT/EXT\.|I/E\.|FADE|CUT|DISSOLVE|SMASH|MATCH)', line_text, re.IGNORECASE)):
            line_type = CHARACTER
        
        # Parentheticals
        elif line_text.startswith('(') and line_text.endswith(')'):
            line_type = PAREN
        
        # Transitions
        elif re.match(r'^(FADE|CUT|DISSOLVE|SMASH|MATCH)', line_text, re.IGNORECASE):
            line_type = TRANSITION
            line_text = line_text.upper()
        
        # Shot descriptions
        elif re.match(r'^(CLOSE|WIDE|MEDIUM|EXTREME|POV|ANGLE)', line_text, re.IGNORECASE):
            line_type = SHOT
            line_text = line_text.upper()
        
        # Act breaks
        elif re.match(r'^(ACT \d+|END OF ACT \d+)', line_text, re.IGNORECASE):
            line_type = ACTBREAK
            line_text = line_text.upper()
        
        # Notes
        elif line_text.startswith('*') and line_text.endswith('*'):
            line_type = NOTE
        
        # Create Line object with detected type
        line = Line(lb, line_type, line_text)
        lines.append(line)
    
    return lines 