#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug test script for the embedding pipeline.
This script helps test the debug statements added to the AI service and embedding service.
"""

import os
import sys
from dotenv import load_dotenv

def test_embedding_service_debug():
    """Test the embedding service with debug statements."""
    print("=== Testing Embedding Service Debug ===")
    
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

def test_enhanced_ai_service_debug():
    """Test the enhanced AI service with debug statements."""
    print("\n=== Testing Enhanced AI Service Debug ===")
    
    try:
        from trelby.ai_service_enhanced import EnhancedAIService
        
        # Initialize the service
        print("Initializing enhanced AI service...")
        ai_service = EnhancedAIService()
        print("✓ Enhanced AI service initialized successfully")
        
        # Test collection info
        info = ai_service.get_collection_info()
        print(f"✓ ChromaDB collection: {info['collection_name']} ({info['document_count']} documents)")
        
        # Test with sample texts
        sample_texts = [
            "A character walks into a room.",
            "The protagonist speaks their mind.",
            "An action sequence unfolds."
        ]
        
        print(f"\nCreating embeddings for {len(sample_texts)} sample texts...")
        embeddings = ai_service.create_embeddings(sample_texts)
        
        if embeddings:
            print(f"✓ Successfully created {len(embeddings)} embeddings")
            print(f"  - Each embedding has {len(embeddings[0])} dimensions")
            
            # Test semantic search
            print("\nTesting semantic search...")
            search_results = ai_service.search_similar_scenes("character dialogue", n_results=2)
            
            if search_results and search_results.get('documents'):
                print(f"✓ Semantic search found {len(search_results['documents'][0])} results")
                for i, doc in enumerate(search_results['documents'][0]):
                    print(f"  Result {i+1}: {doc[:100]}...")
            else:
                print("✗ No semantic search results found")
        else:
            print("✗ Failed to create embeddings")
            
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        print("  Make sure you have both ANTHROPIC_API_KEY and OPENAI_API_KEY set")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("  Make sure you have the required dependencies installed")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

def test_api_keys():
    """Test API key configuration."""
    print("=== Testing API Key Configuration ===")
    
    # Load environment variables
    load_dotenv()
    
    # Check Anthropic API key
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key:
        print(f"✓ Anthropic API key found (length: {len(anthropic_key)} characters)")
        print(f"  - Key starts with: {anthropic_key[:10]}...")
    else:
        print("✗ Anthropic API key not found")
    
    # Check OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f"✓ OpenAI API key found (length: {len(openai_key)} characters)")
        print(f"  - Key starts with: {openai_key[:10]}...")
    else:
        print("✗ OpenAI API key not found")
    
    # Check .env file
    if os.path.exists('.env'):
        print("✓ .env file found")
        with open('.env', 'r') as f:
            lines = f.readlines()
            print(f"  - File has {len(lines)} lines")
    else:
        print("✗ .env file not found")

def main():
    """Run all debug tests."""
    print("Embedding Pipeline Debug Test Suite")
    print("=" * 50)
    
    # Test API key configuration
    test_api_keys()
    
    # Test embedding service
    test_embedding_service_debug()
    
    # Test enhanced AI service
    test_enhanced_ai_service_debug()
    
    print("\n" + "=" * 50)
    print("Debug test suite completed!")
    print("\nNotes:")
    print("- Check the debug output above for detailed information")
    print("- Look for any error messages or unexpected behavior")
    print("- The debug statements will help identify where issues occur")

if __name__ == "__main__":
    main() 