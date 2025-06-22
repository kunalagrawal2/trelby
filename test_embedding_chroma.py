#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for the embedding pipeline with ChromaDB integration.
This script demonstrates storing and retrieving embeddings using ChromaDB.
"""

import os
import sys
import openai
import chromadb
from dotenv import load_dotenv

class ChromaEmbeddingService:
    """
    Embedding service that integrates with ChromaDB for storage and retrieval.
    """
    def __init__(self, collection_name="screenplay_embeddings"):
        """
        Initializes the service with ChromaDB integration.
        
        Args:
            collection_name (str): Name of the ChromaDB collection to use
        """
        # Load API key from .env file
        self.api_key = self._get_api_key_from_env_file()
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = "text-embedding-3-large"
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client()
        self.collection_name = collection_name
        
        # Create or get collection
        try:
            self.collection = self.chroma_client.get_collection(name=collection_name)
            print(f"✓ Connected to existing collection: {collection_name}")
        except:
            self.collection = self.chroma_client.create_collection(name=collection_name)
            print(f"✓ Created new collection: {collection_name}")

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
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            embeddings = [embedding.embedding for embedding in response.data]
            return embeddings
        except openai.APIError as e:
            print(f"Error creating embeddings: An OpenAI API error occurred: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred during embedding creation: {e}")
            return []

    def store_embeddings(self, texts: list[str], metadata: list[dict] = None):
        """
        Create embeddings and store them in ChromaDB.
        
        Args:
            texts (list[str]): List of text documents to embed and store
            metadata (list[dict]): Optional metadata for each document
            
        Returns:
            list: List of document IDs that were stored
        """
        if not texts:
            return []
        
        # Create embeddings
        embeddings = self.create_embeddings(texts)
        if not embeddings:
            print("✗ Failed to create embeddings")
            return []
        
        # Prepare metadata
        if metadata is None:
            metadata = [{"source": "unknown"} for _ in texts]
        
        # Generate document IDs
        doc_ids = [f"doc_{i}_{hash(text[:50])}" for i, text in enumerate(texts)]
        
        try:
            # Store in ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadata,
                ids=doc_ids
            )
            print(f"✓ Stored {len(doc_ids)} documents in ChromaDB")
            return doc_ids
        except Exception as e:
            print(f"✗ Error storing in ChromaDB: {e}")
            return []

    def search_similar(self, query: str, n_results: int = 5):
        """
        Search for similar documents using a query.
        
        Args:
            query (str): The search query
            n_results (int): Number of results to return
            
        Returns:
            dict: Search results with documents, metadata, and distances
        """
        try:
            # Create embedding for the query
            query_embedding = self.create_embeddings([query])
            if not query_embedding:
                return None
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            return results
        except Exception as e:
            print(f"✗ Error searching: {e}")
            return None

    def get_collection_info(self):
        """Get information about the current collection."""
        try:
            count = self.collection.count()
            print(f"Collection '{self.collection_name}' contains {count} documents")
            return count
        except Exception as e:
            print(f"✗ Error getting collection info: {e}")
            return 0

def test_chroma_integration():
    """Test the ChromaDB integration."""
    print("=== Testing ChromaDB Integration ===")
    
    try:
        # Initialize the service
        print("Initializing ChromaDB embedding service...")
        service = ChromaEmbeddingService("test_screenplay_embeddings")
        print("✓ Service initialized successfully")
        
        # Test data
        test_texts = [
            "A person walks into a room and sits down.",
            "Someone enters the chamber and takes a seat.",
            "The weather is sunny and warm today.",
            "It's raining heavily outside.",
            "A character speaks their dialogue lines.",
            "Two people have a conversation about the weather.",
            "The protagonist faces a difficult decision.",
            "An action sequence unfolds with dramatic tension."
        ]
        
        test_metadata = [
            {"type": "action", "scene": "room", "character": "person"},
            {"type": "action", "scene": "chamber", "character": "someone"},
            {"type": "description", "scene": "outdoor", "weather": "sunny"},
            {"type": "description", "scene": "outdoor", "weather": "rainy"},
            {"type": "dialogue", "scene": "any", "character": "speaker"},
            {"type": "dialogue", "scene": "any", "topic": "weather"},
            {"type": "character", "scene": "any", "emotion": "conflicted"},
            {"type": "action", "scene": "any", "tension": "high"}
        ]
        
        # Store embeddings
        print(f"\nStoring {len(test_texts)} test documents...")
        doc_ids = service.store_embeddings(test_texts, test_metadata)
        
        if doc_ids:
            print(f"✓ Successfully stored {len(doc_ids)} documents")
            
            # Get collection info
            service.get_collection_info()
            
            # Test search functionality
            print("\n=== Testing Search Functionality ===")
            
            search_queries = [
                "person entering a room",
                "weather conditions",
                "dialogue between characters",
                "dramatic action"
            ]
            
            for query in search_queries:
                print(f"\nSearching for: '{query}'")
                results = service.search_similar(query, n_results=3)
                
                if results and results['documents']:
                    for i, (doc, metadata, distance) in enumerate(zip(
                        results['documents'][0], 
                        results['metadatas'][0], 
                        results['distances'][0]
                    )):
                        print(f"  {i+1}. Distance: {distance:.4f}")
                        print(f"     Text: {doc[:80]}...")
                        print(f"     Metadata: {metadata}")
                else:
                    print("  No results found")
            
            return True
        else:
            print("✗ Failed to store documents")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_file_processing(file_path):
    """Test processing a file and storing in ChromaDB."""
    print(f"\n=== Testing File Processing: {file_path} ===")
    
    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        return False
    
    try:
        # Read and chunk the file
        print(f"Reading file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        print(f"✓ File read successfully ({len(content)} characters)")
        
        # Simple chunking by paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Limit to avoid token limits
        if len(paragraphs) > 20:
            print(f"  - Limiting to first 20 paragraphs to avoid token limits")
            paragraphs = paragraphs[:20]
        
        print(f"✓ Found {len(paragraphs)} paragraphs to process")
        
        # Initialize service
        service = ChromaEmbeddingService("file_embeddings")
        
        # Create metadata
        metadata = [
            {
                "source": os.path.basename(file_path),
                "paragraph": i + 1,
                "length": len(para),
                "type": "paragraph"
            }
            for i, para in enumerate(paragraphs)
        ]
        
        # Store embeddings
        print(f"\nStoring {len(paragraphs)} paragraphs in ChromaDB...")
        doc_ids = service.store_embeddings(paragraphs, metadata)
        
        if doc_ids:
            print(f"✓ Successfully stored {len(doc_ids)} paragraphs")
            service.get_collection_info()
            
            # Test search on the stored content
            print("\n=== Testing Search on File Content ===")
            test_queries = [
                "main character",
                "important scene",
                "dialogue",
                "action sequence"
            ]
            
            for query in test_queries:
                print(f"\nSearching for: '{query}'")
                results = service.search_similar(query, n_results=2)
                
                if results and results['documents']:
                    for i, (doc, metadata, distance) in enumerate(zip(
                        results['documents'][0], 
                        results['metadatas'][0], 
                        results['distances'][0]
                    )):
                        print(f"  {i+1}. Distance: {distance:.4f}")
                        print(f"     Paragraph {metadata.get('paragraph', 'unknown')}: {doc[:100]}...")
                else:
                    print("  No results found")
            
            return True
        else:
            print("✗ Failed to store paragraphs")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def cleanup_test_collections():
    """Clean up test collections."""
    try:
        client = chromadb.Client()
        collections_to_delete = ["test_screenplay_embeddings", "file_embeddings"]
        
        for collection_name in collections_to_delete:
            try:
                client.delete_collection(name=collection_name)
                print(f"✓ Deleted test collection: {collection_name}")
            except:
                pass  # Collection might not exist
    except Exception as e:
        print(f"Warning: Could not clean up collections: {e}")

def main():
    """Run all tests."""
    print("ChromaDB Embedding Pipeline Test")
    print("=" * 50)
    
    # Test ChromaDB integration
    success1 = test_chroma_integration()
    
    # Test file processing
    file_path = "/Users/kunalagrawal/Downloads/2012.txt"
    success2 = test_file_processing(file_path)
    
    # Cleanup
    print("\n=== Cleanup ===")
    cleanup_test_collections()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✓ All tests completed successfully!")
    else:
        print("✗ Some tests failed")
    
    print("\nNotes:")
    print("- ChromaDB stores embeddings locally by default")
    print("- Collections are automatically created if they don't exist")
    print("- Search results include documents, metadata, and similarity scores")
    print("- The system can handle large files by chunking them")

if __name__ == "__main__":
    main() 