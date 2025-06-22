# -*- coding: utf-8 -*-

import re
import json
from trelby.line import Line
from trelby.screenplay import ACTION, LB_LAST, LB_FORCED, SCENE, CHARACTER, DIALOGUE, PAREN, TRANSITION, SHOT, ACTBREAK, NOTE

def fix_formatting(text, ai_service=None):
    """
    Intelligently format text as screenplay using AI-powered formatting.
    
    Args:
        text (str): Plain text to format
        ai_service: Optional AI service for intelligent formatting
        
    Returns:
        list: List of Line objects with proper screenplay formatting
    """
    # If AI service is available, use it for intelligent formatting
    if ai_service:
        try:
            formatted_text = use_ai_formatting(text, ai_service)
        except Exception as e:
            print(f"AI formatting failed, falling back to basic formatting: {e}")
            formatted_text = text
    else:
        formatted_text = text
    
    # Convert to Line objects
    lines = convert_to_lines(formatted_text)
    
    return lines

def use_ai_formatting(text, ai_service):
    """
    Use Claude to intelligently format the screenplay text.
    Converts to Fountain format as an intermediary step.
    """
    prompt = f"""You are an expert screenplay formatter. Convert the following text into proper Fountain screenplay format.

Fountain is a plain text markup language for screenplays. Here are the key formatting rules:

- Scene headings: Start with # (e.g., "# INT. ROOM - DAY")
- Character names: Start with @ (e.g., "@JOHN")
- Dialogue: Regular text after character name (no special markup)
- Parentheticals: In parentheses (e.g., "(whispering)")
- Transitions: Start with > (e.g., "> FADE OUT")
- Action: Regular text (no special markup)
- Notes: Between /* and */ (e.g., "/* This is a note */")

IMPORTANT GUIDELINES:
1. Scene headings should be in ALL CAPS and follow the pattern: INT./EXT. LOCATION - TIME
2. Character names should be in ALL CAPS
3. Transitions should be in ALL CAPS
4. Dialogue should follow character names without any special markup
5. Parentheticals should be on their own line after character names
6. Action lines should be regular text with no markup
7. Use proper screenplay structure and flow

Analyze the content intelligently and apply the appropriate Fountain formatting. Consider context, content, and screenplay conventions.

Input text:
{text}

Return ONLY the Fountain-formatted text, no explanations or commentary."""

    try:
        # Use simple response method to avoid semantic search and complex context
        response = ai_service.get_simple_response(prompt)
        return response.strip()
    except Exception as e:
        print(f"AI formatting error: {e}")
        return text

def convert_to_lines(fountain_text):
    """
    Convert Fountain-formatted text to Trelby Line objects using an improved stateful parser
    to correctly identify elements like dialogue.
    """
    lines = []
    fountain_lines = fountain_text.strip().split('\n')
    
    # Enhanced state tracking
    last_line_type = None
    in_dialogue_block = False
    dialogue_character = None

    for i, line_text in enumerate(fountain_lines):
        line_text = line_text.strip()
        current_line_type = None
        formatted_text = line_text

        # Determine line break type
        lb = LB_FORCED
        if i == len(fountain_lines) - 1:
            lb = LB_LAST
        
        # Enhanced line type detection with better context awareness
        if not line_text:
            current_line_type = ACTION
            formatted_text = ""
            # Reset dialogue context on blank lines
            in_dialogue_block = False
            dialogue_character = None
        elif line_text.startswith('# '):
            current_line_type = SCENE
            formatted_text = line_text[2:].upper()
            # Reset dialogue context on scene headings
            in_dialogue_block = False
            dialogue_character = None
        elif line_text.startswith('@'):
            current_line_type = CHARACTER
            # Strip the @ symbol and any leading space, ensure uppercase
            formatted_text = line_text.lstrip('@ ').upper()
            # Set dialogue context
            in_dialogue_block = True
            dialogue_character = formatted_text
        elif line_text.startswith('> '):
            current_line_type = TRANSITION
            formatted_text = line_text[2:].upper()
            # Reset dialogue context on transitions
            in_dialogue_block = False
            dialogue_character = None
        elif line_text.startswith('/* ') and line_text.endswith(' */'):
            current_line_type = NOTE
            formatted_text = line_text[3:-3]
            # Notes don't affect dialogue context
        elif line_text.startswith('(') and line_text.endswith(')'):
            current_line_type = PAREN
            formatted_text = line_text
            # Parentheticals maintain dialogue context
        else:
            # Enhanced stateful logic with better dialogue detection
            if in_dialogue_block and dialogue_character:
                # If we're in a dialogue block and this isn't a special markup line,
                # it's likely dialogue
                current_line_type = DIALOGUE
            elif last_line_type in (CHARACTER, PAREN, DIALOGUE):
                # Fallback: if the last line was character, parenthetical, or dialogue,
                # this line is likely dialogue
                current_line_type = DIALOGUE
                in_dialogue_block = True
            else:
                current_line_type = ACTION
                # Reset dialogue context for action lines
                in_dialogue_block = False
                dialogue_character = None
        
        # Validate and clean up the formatted text
        formatted_text = clean_formatted_text(formatted_text, current_line_type)
        
        # Create Line object and add it to our list
        line_obj = Line(lb, current_line_type, formatted_text)
        lines.append(line_obj)

        # Update the state for the next line
        if not line_text:
            last_line_type = None  # Blank lines reset the context
        else:
            last_line_type = current_line_type
            
    return lines

def clean_formatted_text(text, line_type):
    """
    Clean and validate formatted text based on line type.
    """
    if not text:
        return ""
    
    # Remove any trailing whitespace
    text = text.rstrip()
    
    # Apply type-specific cleaning
    if line_type == SCENE:
        # Ensure scene headings are properly formatted
        if not text.endswith(('DAY', 'NIGHT', 'MORNING', 'EVENING', 'AFTERNOON', 'LATER', 'CONTINUOUS')):
            # If it doesn't end with a time indicator, try to add one
            if 'INT.' in text or 'EXT.' in text:
                text += ' - DAY'
    elif line_type == CHARACTER:
        # Ensure character names are uppercase and clean
        text = text.upper().strip()
        # Remove any extra spaces
        text = ' '.join(text.split())
    elif line_type == TRANSITION:
        # Ensure transitions are uppercase
        text = text.upper().strip()
    elif line_type == DIALOGUE:
        # Dialogue should be clean but preserve case
        text = text.strip()
    elif line_type == ACTION:
        # Action should be clean but preserve case
        text = text.strip()
    elif line_type == PAREN:
        # Parentheticals should be in parentheses
        if not text.startswith('('):
            text = '(' + text
        if not text.endswith(')'):
            text = text + ')'
    
    return text

def fountain_to_trelby_line(fountain_line):
    """
    DEPRECATED: This stateless function is no longer used.
    The new stateful parser is in `convert_to_lines`.
    """
    # This function is kept to avoid breaking other parts of the app
    # if they were somehow still calling it, but it should be removed
    # in a future refactor.
    if not fountain_line:
        return ACTION, fountain_line
    if fountain_line.startswith('# '):
        return SCENE, fountain_line[2:].upper()
    if fountain_line.startswith('@ '):
        return CHARACTER, fountain_line[2:].upper()
    if fountain_line.startswith('> '):
        return TRANSITION, fountain_line[2:].upper()
    if fountain_line.startswith('/* ') and fountain_line.endswith(' */'):
        return NOTE, fountain_line[3:-3]
    if fountain_line.startswith('(') and fountain_line.endswith(')'):
        return PAREN, fountain_line
    return ACTION, fountain_line 