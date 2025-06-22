# -*- coding: utf-8 -*-

import re
from trelby.line import Line
from trelby.screenplay import ACTION, LB_LAST, LB_FORCED, SCENE, CHARACTER, DIALOGUE, PAREN, TRANSITION, SHOT, ACTBREAK, NOTE

def fix_formatting(text):
    """
    Intelligently format text as screenplay by analyzing content and context.
    
    Args:
        text (str): Plain text to format
        
    Returns:
        list: List of Line objects with proper screenplay formatting
    """
    lines = []
    text_lines = text.strip().split('\n')
    
    # Analyze the entire text to understand context
    context = analyze_screenplay_context(text_lines)
    
    for i, line_text in enumerate(text_lines):
        line_text = line_text.strip()
        
        # Determine line break type
        if i == len(text_lines) - 1:
            lb = LB_LAST  # Last line
        else:
            lb = LB_FORCED  # Force line break for multi-line elements
        
        # Intelligently determine line type based on content and context
        line_type, formatted_text = determine_line_type(line_text, context, i, text_lines)
        
        # Create Line object with detected type
        line = Line(lb, line_type, formatted_text)
        lines.append(line)
    
    return lines

def analyze_screenplay_context(text_lines):
    """Analyze the entire text to understand screenplay context and patterns."""
    context = {
        'has_scene_headings': False,
        'has_characters': False,
        'has_dialogue': False,
        'character_names': set(),
        'dialogue_patterns': [],
        'scene_patterns': [],
        'line_types': [],  # Track detected types for context
        'conversation_flow': []  # Track character-dialogue patterns
    }
    
    for i, line in enumerate(text_lines):
        line = line.strip()
        if not line:
            continue
            
        # Detect scene headings
        if re.match(r'^(INT\.|EXT\.|INT/EXT\.|I/E\.)', line, re.IGNORECASE):
            context['has_scene_headings'] = True
            context['scene_patterns'].append(line.upper())
            context['line_types'].append(('scene', i))
        
        # Detect potential character names (all caps, reasonable length)
        elif (line.isupper() and 
              len(line) <= 50 and 
              not line.endswith('.') and
              not re.match(r'^(INT\.|EXT\.|INT/EXT\.|I/E\.|FADE|CUT|DISSOLVE|SMASH|MATCH)', line, re.IGNORECASE)):
            context['has_characters'] = True
            context['character_names'].add(line)
            context['line_types'].append(('character', i))
        
        # Detect dialogue patterns (quotes, conversational text)
        elif (('"' in line or "'" in line) or 
              re.search(r'\b(said|says|asks|replies|responds|shouts|whispers|mumbles)\b', line, re.IGNORECASE) or
              line.endswith('!') or line.endswith('?') or
              # Only match actual dialogue sentences, not character names or short phrases
              (re.match(r'^[A-Z][^A-Z]*[.!?]$', line) and len(line.split()) > 1 and not line.isupper())):
            context['has_dialogue'] = True
            context['dialogue_patterns'].append(line)
            context['line_types'].append(('dialogue', i))
        
        # Detect parentheticals
        elif line.startswith('(') and line.endswith(')'):
            context['line_types'].append(('paren', i))
        
        # Detect transitions
        elif re.match(r'^(FADE|CUT|DISSOLVE|SMASH|MATCH|JUMP|WIPE|IRIS|FREEZE|SUPER|TITLE|THE END)', line, re.IGNORECASE):
            context['line_types'].append(('transition', i))
        
        # Detect action (default)
        else:
            context['line_types'].append(('action', i))
    
    # Analyze conversation flow
    for i, (line_type, line_idx) in enumerate(context['line_types']):
        if line_type == 'character':
            # Look ahead for dialogue
            if i + 1 < len(context['line_types']):
                next_type, next_idx = context['line_types'][i + 1]
                if next_type in ['dialogue', 'paren']:
                    context['conversation_flow'].append((line_idx, next_idx))
    
    return context

def determine_line_type(line_text, context, line_index, all_lines):
    """Intelligently determine the line type based on content and context."""
    
    # Empty line
    if not line_text:
        return ACTION, line_text
    
    # Scene headings - look for location/time patterns
    if re.match(r'^(INT\.|EXT\.|INT/EXT\.|I/E\.)', line_text, re.IGNORECASE):
        return SCENE, line_text.upper()
    
    # Parentheticals - text in parentheses
    if line_text.startswith('(') and line_text.endswith(')'):
        return PAREN, line_text
    
    # Transitions - specific transition words
    if re.match(r'^(FADE|CUT|DISSOLVE|SMASH|MATCH|JUMP|WIPE|IRIS|FREEZE|SUPER|TITLE|THE END)', line_text, re.IGNORECASE):
        return TRANSITION, line_text.upper()
    
    # Shot descriptions - camera/angle terms
    if re.match(r'^(CLOSE|WIDE|MEDIUM|EXTREME|POV|ANGLE|CAMERA|OVER THE SHOULDER|OTS)', line_text, re.IGNORECASE):
        return SHOT, line_text.upper()
    
    # Act breaks
    if re.match(r'^(ACT \d+|END OF ACT \d+)', line_text, re.IGNORECASE):
        return ACTBREAK, line_text.upper()
    
    # Notes - marked with asterisks or brackets
    if (line_text.startswith('*') and line_text.endswith('*')) or line_text.startswith('[NOTE'):
        return NOTE, line_text
    
    # Character names - intelligent detection with context
    if is_character_name(line_text, context, line_index, all_lines):
        return CHARACTER, line_text
    
    # Dialogue - intelligent detection with context
    if is_dialogue(line_text, context, line_index, all_lines):
        return DIALOGUE, line_text
    
    # Default to action
    return ACTION, line_text

def is_character_name(line_text, context, line_index, all_lines):
    """Intelligently determine if a line is a character name with context awareness."""
    
    # Basic character name patterns
    if (line_text.isupper() and 
        len(line_text) <= 50 and 
        not line_text.endswith('.') and
        not re.match(r'^(INT\.|EXT\.|INT/EXT\.|I/E\.|FADE|CUT|DISSOLVE|SMASH|MATCH)', line_text, re.IGNORECASE)):
        
        # If we've seen this as a character before, it's likely a character
        if line_text in context['character_names']:
            return True
        
        # If it looks like a name (no special characters, reasonable length)
        if re.match(r'^[A-Z\s]+$', line_text) and len(line_text.split()) <= 3:
            # Check if the next line looks like dialogue
            if line_index + 1 < len(all_lines):
                next_line = all_lines[line_index + 1].strip()
                if is_dialogue(next_line, context, line_index + 1, all_lines):
                    return True
            
            # Check if we're in a conversation flow
            for char_idx, dialogue_idx in context['conversation_flow']:
                if line_index == char_idx:
                    return True
            
            # If it's a reasonable name and we have other characters, it's likely a character
            if context['has_characters']:
                return True
    
    return False

def is_dialogue(line_text, context, line_index, all_lines):
    """Intelligently determine if a line is dialogue with context awareness."""
    
    # If we have dialogue patterns, check against them
    if context['dialogue_patterns']:
        # Check if this line follows dialogue patterns
        if any(pattern.lower() in line_text.lower() for pattern in context['dialogue_patterns']):
            return True
    
    # Dialogue indicators
    if ('"' in line_text or "'" in line_text or
        re.search(r'\b(said|says|asks|replies|responds|shouts|whispers|mumbles)\b', line_text, re.IGNORECASE) or
        line_text.endswith('!') or line_text.endswith('?') or
        # Only match single sentences that start with capital and end with punctuation
        (re.match(r'^[A-Z][^A-Z]*[.!?]$', line_text) and len(line_text.split()) > 1)):
        return True
    
    # Check if this follows a character name
    if line_index > 0:
        prev_line = all_lines[line_index - 1].strip()
        if (prev_line.isupper() and 
            len(prev_line) <= 50 and 
            not prev_line.endswith('.') and
            re.match(r'^[A-Z\s]+$', prev_line) and 
            len(prev_line.split()) <= 3):
            return True
    
    # Check if we're in a conversation flow
    for char_idx, dialogue_idx in context['conversation_flow']:
        if line_index == dialogue_idx:
            return True
    
    # If we have characters and this follows a character line, it might be dialogue
    if context['has_characters'] and line_index > 0:
        # Check if previous line was a character name
        prev_line = all_lines[line_index - 1].strip()
        if is_character_name(prev_line, context, line_index - 1, all_lines):
            return True
    
    return False 