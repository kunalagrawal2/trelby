#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple test script for the embedding pipeline.
This script demonstrates the embedding service and screenplay chunking functionality.
"""

import sys
import os
import json

# Add the trelby directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trelby'))

def test_embedding_service():
    """Test the embedding service with sample text."""
    print("=== Testing Embedding Service ===")
    
    try:
        from trelby.embedding_service import EmbeddingService
        
        # Initialize the service
        print("Initializing embedding service...")
        embedding_service = EmbeddingService()
        print("✓ Embedding service initialized successfully")
        
        # Test with sample texts
        sample_texts = [
            "This is a sample scene heading.",
            "CHARACTER: This is some dialogue.",
            "This is an action line describing what happens."
        ]
        
        print(f"\nCreating embeddings for {len(sample_texts)} sample texts...")
        embeddings = embedding_service.create_embeddings(sample_texts)
        
        if embeddings:
            print(f"✓ Successfully created {len(embeddings)} embeddings")
            print(f"  - Each embedding has {len(embeddings[0])} dimensions")
            print(f"  - Model used: {embedding_service.model}")
        else:
            print("✗ Failed to create embeddings")
            
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        print("  Make sure you have OPENAI_API_KEY set in your .env file")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("  Make sure you have the required dependencies installed")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

def test_screenplay_chunker():
    """Test the screenplay chunker with a mock screenplay."""
    print("\n=== Testing Screenplay Chunker ===")
    
    try:
        from trelby.screenplay_chunker import ScreenplayChunker
        
        # Create a mock screenplay object for testing
        class MockScreenplay:
            def __init__(self):
                self.SCENE = 0
                self.CHARACTER = 1
                self.DIALOGUE = 2
                self.ACTION = 3
                self.PAREN = 4
                self.TRANSITION = 5
                
                # Mock lines representing a simple scene
                self.lines = [
                    MockLine(self.SCENE, "INT. ROOM - DAY"),
                    MockLine(self.ACTION, "A person sits at a desk."),
                    MockLine(self.CHARACTER, "PERSON"),
                    MockLine(self.DIALOGUE, "Hello, world!"),
                    MockLine(self.ACTION, "They smile.")
                ]
            
            def getSceneLocations(self):
                return ["INT. ROOM - DAY"]
            
            def getSceneIndexesFromName(self, scene_name):
                return (0, 4)  # Start and end line indices
        
        class MockLine:
            def __init__(self, lt, text):
                self.lt = lt
                self.text = text
        
        # Test the chunker
        print("Creating mock screenplay...")
        mock_screenplay = MockScreenplay()
        
        print("Initializing screenplay chunker...")
        chunker = ScreenplayChunker(mock_screenplay)
        
        print("Chunking screenplay by scenes...")
        chunks = chunker.chunk_by_scene()
        
        if chunks:
            print(f"✓ Successfully created {len(chunks)} scene chunks")
            for i, chunk in enumerate(chunks):
                print(f"\n  Scene {i+1}:")
                print(f"    ID: {chunk['id']}")
                print(f"    Name: {chunk['metadata']['scene_name']}")
                print(f"    Characters: {chunk['metadata']['characters']}")
                print(f"    Word count: {chunk['metadata']['word_count']}")
                print(f"    Content preview: {chunk['text'][:100]}...")
        else:
            print("✗ No chunks were created")
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

def test_full_pipeline():
    """Test the complete embedding pipeline."""
    print("\n=== Testing Full Pipeline ===")
    
    try:
        from trelby.embedding_service import EmbeddingService
        from trelby.screenplay_chunker import ScreenplayChunker
        
        # Create mock screenplay (reusing from above)
        class MockScreenplay:
            def __init__(self):
                self.SCENE = 0
                self.CHARACTER = 1
                self.DIALOGUE = 2
                self.ACTION = 3
                self.PAREN = 4
                self.TRANSITION = 5
                
                self.lines = [
                    MockLine(self.SCENE, "INT. ROOM - DAY"),
                    MockLine(self.ACTION, "A person sits at a desk."),
                    MockLine(self.CHARACTER, "PERSON"),
                    MockLine(self.DIALOGUE, "Hello, world!"),
                    MockLine(self.ACTION, "They smile.")
                ]
            
            def getSceneLocations(self):
                return ["INT. ROOM - DAY"]
            
            def getSceneIndexesFromName(self, scene_name):
                return (0, 4)
        
        class MockLine:
            def __init__(self, lt, text):
                self.lt = lt
                self.text = text
        
        print("Step 1: Creating mock screenplay...")
        mock_screenplay = MockScreenplay()
        
        print("Step 2: Chunking screenplay...")
        chunker = ScreenplayChunker(mock_screenplay)
        chunks = chunker.chunk_by_scene()
        
        if not chunks:
            print("✗ No chunks created, skipping embedding step")
            return
        
        print("Step 3: Extracting text content for embedding...")
        texts_to_embed = [chunk['text'] for chunk in chunks]
        
        print("Step 4: Creating embeddings...")
        try:
            embedding_service = EmbeddingService()
            embeddings = embedding_service.create_embeddings(texts_to_embed)
            
            if embeddings:
                print(f"✓ Pipeline completed successfully!")
                print(f"  - Created {len(chunks)} scene chunks")
                print(f"  - Generated {len(embeddings)} embeddings")
                print(f"  - Each embedding has {len(embeddings[0])} dimensions")
                
                # Show how the data could be stored/used
                print("\n  Pipeline output structure:")
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    print(f"    Scene {i+1}:")
                    print(f"      ID: {chunk['id']}")
                    print(f"      Text length: {len(chunk['text'])} chars")
                    print(f"      Embedding dimensions: {len(embedding)}")
            else:
                print("✗ Failed to create embeddings")
                
        except ValueError as e:
            print(f"✗ Embedding service error: {e}")
            print("  (This is expected if OPENAI_API_KEY is not configured)")
            
    except Exception as e:
        print(f"✗ Pipeline error: {e}")

def main():
    """Run all tests."""
    print("Embedding Pipeline Test Suite")
    print("=" * 40)
    
    # Test individual components
    test_embedding_service()
    test_screenplay_chunker()
    test_full_pipeline()
    
    print("\n" + "=" * 40)
    print("Test suite completed!")
    print("\nNotes:")
    print("- The embedding service requires OPENAI_API_KEY to be set")
    print("- The chunker works with any screenplay object")
    print("- The full pipeline demonstrates the complete workflow")

if __name__ == "__main__":
    main() 