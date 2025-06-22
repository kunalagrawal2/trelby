#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple test script for the embedding pipeline using a basic text file.
This script demonstrates the embedding service with a simple text file.
"""

import os
import sys
import openai
from dotenv import load_dotenv

class SimpleEmbeddingService:
    """
    Simple embedding service that doesn't depend on trelby modules.
    """
    def __init__(self):
        """
        Initializes the service by loading the environment variables
        and setting up the OpenAI client.
        """
        load_dotenv()
        # Only get from .env file, ignore environment variables
        self.api_key = self._get_api_key_from_env_file()
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = "text-embedding-3-large"

    def _get_api_key_from_env_file(self):
        """Read API key directly from .env file, ignoring environment variables."""
        try:
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('OPENAI_API_KEY='):
                        return line.split('=', 1)[1]
        except FileNotFoundError:
            return None
        return None

    def create_embeddings(self, texts: list[str]):
        """
        Generates embeddings for a list of text documents.

        Args:
            texts (list[str]): A list of strings to be embedded.

        Returns:
            list: A list of embedding vectors, or an empty list if an error occurs.
        """
        if not texts:
            return []

        try:
            # Note: OpenAI's API can handle a list of texts in a single call
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            # Extract the embedding data from the response object
            embeddings = [embedding.embedding for embedding in response.data]
            return embeddings
        except openai.APIError as e:
            print(f"Error creating embeddings: An OpenAI API error occurred: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred during embedding creation: {e}")
            return []

def check_api_key():
    """Check if the API key is valid by making a simple test call."""
    print("=== Checking API Key ===")
    
    try:
        # Read API key directly from .env file
        api_key = None
        try:
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('OPENAI_API_KEY='):
                        api_key = line.split('=', 1)[1]
                        break
        except FileNotFoundError:
            print("✗ .env file not found")
            return False
        
        if not api_key:
            print("✗ OPENAI_API_KEY not found in .env file")
            return False
        
        print(f"✓ API key found in .env file (length: {len(api_key)} characters)")
        print(f"  - Key starts with: {api_key[:10]}...")
        
        # Check if there's an environment variable that might interfere
        env_api_key = os.getenv("OPENAI_API_KEY")
        if env_api_key:
            print(f"⚠️  Warning: OPENAI_API_KEY environment variable is set (length: {len(env_api_key)})")
            print(f"   This might interfere with the .env file key")
            print(f"   Environment key starts with: {env_api_key[:10]}...")
        
        # Test the API key with a simple call
        print("Testing API key with OpenAI...")
        client = openai.OpenAI(api_key=api_key)
        
        # Try a simple embedding call
        response = client.embeddings.create(
            input=["test"],
            model="text-embedding-3-small"  # Use smaller model for testing
        )
        
        if response and response.data:
            print("✓ API key is valid and working!")
            print(f"  - Model used: {response.model}")
            print(f"  - Embedding dimensions: {len(response.data[0].embedding)}")
            return True
        else:
            print("✗ API call returned empty response")
            return False
            
    except openai.AuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
        print("  The API key is invalid or expired")
        return False
    except openai.APIError as e:
        print(f"✗ API error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_embedding_service():
    """Test the embedding service with sample text."""
    print("\n=== Testing Embedding Service ===")
    
    try:
        # Initialize the service
        print("Initializing embedding service...")
        embedding_service = SimpleEmbeddingService()
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

def test_with_file(file_path):
    """Test embedding with the specified text file."""
    print(f"\n=== Testing with File: {file_path} ===")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        return
    
    try:
        # Read the file
        print(f"Reading file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        print(f"✓ File read successfully")
        print(f"  - File size: {len(content)} characters")
        print(f"  - Lines: {len(content.split(chr(10)))}")
        
        # Simple chunking by paragraphs (separated by double newlines)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        print(f"✓ Found {len(paragraphs)} paragraphs")
        
        # Limit to first 10 paragraphs to avoid API limits
        if len(paragraphs) > 10:
            print(f"  - Limiting to first 10 paragraphs to avoid API limits")
            paragraphs = paragraphs[:10]
        
        # Test embedding the paragraphs
        embedding_service = SimpleEmbeddingService()
        
        print(f"\nCreating embeddings for {len(paragraphs)} paragraphs...")
        embeddings = embedding_service.create_embeddings(paragraphs)
        
        if embeddings:
            print(f"✓ Successfully created {len(embeddings)} embeddings")
            print(f"  - Each embedding has {len(embeddings[0])} dimensions")
            
            # Show some details about each paragraph
            print("\nParagraph details:")
            for i, (paragraph, embedding) in enumerate(zip(paragraphs, embeddings)):
                print(f"  Paragraph {i+1}:")
                print(f"    Length: {len(paragraph)} characters")
                print(f"    Embedding dimensions: {len(embedding)}")
                print(f"    Preview: {paragraph[:100]}...")
                print()
        else:
            print("✗ Failed to create embeddings")
            
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        print("  Make sure you have OPENAI_API_KEY set in your .env file")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_similarity():
    """Test similarity between embeddings."""
    print("\n=== Testing Similarity ===")
    
    try:
        embedding_service = SimpleEmbeddingService()
        
        # Test texts with different similarity levels
        texts = [
            "A person walks into a room.",
            "Someone enters the chamber.",
            "The weather is sunny today.",
            "It's raining outside."
        ]
        
        print("Creating embeddings for similarity test...")
        embeddings = embedding_service.create_embeddings(texts)
        
        if embeddings:
            print("✓ Created embeddings for similarity test")
            
            # Calculate cosine similarity between all pairs
            print("\nSimilarity matrix:")
            print("Text 1 vs Text 2:")
            
            for i in range(len(texts)):
                for j in range(i+1, len(texts)):
                    # Cosine similarity
                    dot_product = sum(a * b for a, b in zip(embeddings[i], embeddings[j]))
                    norm_i = sum(a * a for a in embeddings[i]) ** 0.5
                    norm_j = sum(b * b for b in embeddings[j]) ** 0.5
                    similarity = dot_product / (norm_i * norm_j)
                    
                    print(f"  {i+1} vs {j+1}: {similarity:.4f}")
                    print(f"    '{texts[i][:30]}...' vs '{texts[j][:30]}...'")
            
            print("\nExpected results:")
            print("- Texts 1 & 2 should be similar (both about entering a room)")
            print("- Texts 3 & 4 should be similar (both about weather)")
            print("- Other combinations should be less similar")
        else:
            print("✗ Failed to create embeddings for similarity test")
            
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")

def main():
    """Run all tests."""
    print("Simple Embedding Pipeline Test")
    print("=" * 40)
    
    # First check if API key works
    api_key_works = check_api_key()
    
    if not api_key_works:
        print("\n" + "=" * 40)
        print("API key check failed. Please fix the API key before running tests.")
        print("You can:")
        print("1. Check your .env file has the correct OPENAI_API_KEY")
        print("2. Verify the API key is valid at https://platform.openai.com/account/api-keys")
        print("3. Make sure you have sufficient credits in your OpenAI account")
        print("4. Unset any OPENAI_API_KEY environment variable: unset OPENAI_API_KEY")
        return
    
    # Test individual components
    test_embedding_service()
    
    # Test with the specified file
    file_path = "/Users/kunalagrawal/Downloads/2012.txt"
    test_with_file(file_path)
    
    # Test similarity
    test_similarity()
    
    print("\n" + "=" * 40)
    print("Test suite completed!")
    print("\nNotes:")
    print("- The embedding service requires OPENAI_API_KEY to be set")
    print("- This test uses a simple text file without trelby dependencies")
    print("- Similarity testing shows how embeddings can be compared")

if __name__ == "__main__":
    main() 