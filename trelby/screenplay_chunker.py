# -*- coding: utf-8 -*-

class ScreenplayChunker:
    """Handles chunking of screenplay content for embedding and retrieval."""

    def __init__(self, screenplay):
        """
        Initializes the chunker with a screenplay object.
        
        Args:
            screenplay: An instance of the Trelby screenplay object.
        """
        self.sp = screenplay

    def chunk_by_scene(self):
        """
        Chunks the screenplay into individual scenes. Each scene is a document
        that can be used for embedding.

        Returns:
            list: A list of dictionaries, where each dictionary represents a scene
                  with its content and metadata. Returns an empty list if there's
                  no screenplay to process.
        """
        if not self.sp:
            return []

        scene_chunks = []
        scene_locations = self.sp.getSceneLocations()

        for i, scene_name in enumerate(scene_locations):
            try:
                start_line, end_line = self.sp.getSceneIndexesFromName(scene_name)
                
                content = self._get_scene_content(start_line, end_line)
                characters = self._get_scene_characters(start_line, end_line)

                # Skip empty scenes that might exist in the data
                if not content.strip():
                    continue

                # Each chunk is a dictionary with a unique ID, text content, and metadata
                chunk = {
                    'id': f"scene_{i+1}_{start_line}-{end_line}",
                    'text': content,
                    'metadata': {
                        'scene_number': i + 1,
                        'scene_name': scene_name,
                        'start_line': start_line,
                        'end_line': end_line,
                        'characters': characters,
                        'word_count': len(content.split())
                    }
                }
                scene_chunks.append(chunk)

            except Exception as e:
                # Log errors for scenes that can't be processed, but don't crash
                print(f"Warning: Skipping scene '{scene_name}' due to an error: {e}")
                continue
                
        return scene_chunks

    def _get_scene_content(self, start_line, end_line):
        """
        Extracts the formatted text content from a given scene range,
        excluding transitions and parentheticals for cleaner embedding data.
        """
        content_lines = []
        for i in range(start_line, min(end_line + 1, len(self.sp.lines))):
            line = self.sp.lines[i]

            # Skip parenthetical and transition lines to keep the core content
            if line.lt in (self.sp.PAREN, self.sp.TRANSITION):
                continue

            # Prefixing with element type adds valuable context for the AI
            if line.lt == self.sp.SCENE:
                prefix = "Scene Heading:"
            elif line.lt == self.sp.CHARACTER:
                prefix = "Character:"
            elif line.lt == self.sp.DIALOGUE:
                prefix = "Dialogue:"
            elif line.lt == self.sp.ACTION:
                prefix = "Action:"
            else:
                prefix = ""  # For other elements like NOTE, SHOT, etc.

            content_lines.append(f"{prefix} {line.text}".strip())

        return "\n".join(content_lines)

    def _get_scene_characters(self, start_line, end_line):
        """Extracts a list of unique character names present in the scene."""
        characters = set()
        for i in range(start_line, min(end_line + 1, len(self.sp.lines))):
            line = self.sp.lines[i]
            if line.lt == self.sp.CHARACTER:
                characters.add(line.text.strip())
        return list(characters) 