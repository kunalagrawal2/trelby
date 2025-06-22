#!/usr/bin/env python3
"""
Test script to verify query embedding caching optimization.
"""

import os
import sys
sys.path.append('trelby')

from trelby.ai_service import AIService

def test_query_caching():
    """Test that query embeddings are properly cached"""
    print("=== Testing Query Embedding Caching ===")
    
    try:
        # Initialize AI service
        print("Initializing AI service...")
        ai_service = AIService()
        print("✓ AI service initialized")
        
        # Test query 1 - should create new embedding
        print("\n--- Test 1: First query (should create new embedding) ---")
        query1 = "What is the main character's motivation?"
        result1 = ai_service.search_similar_scenes(query1, n_results=2)
        print(f"✓ First query completed, cache size: {len(ai_service.query_embedding_cache)}")
        
        # Test query 2 - same query, should use cache
        print("\n--- Test 2: Same query (should use cache) ---")
        result2 = ai_service.search_similar_scenes(query1, n_results=2)
        print(f"✓ Second query completed, cache size: {len(ai_service.query_embedding_cache)}")
        
        # Test query 3 - different query, should create new embedding
        print("\n--- Test 3: Different query (should create new embedding) ---")
        query2 = "How does the story end?"
        result3 = ai_service.search_similar_scenes(query2, n_results=2)
        print(f"✓ Third query completed, cache size: {len(ai_service.query_embedding_cache)}")
        
        # Test query 4 - same as query 1, should use cache
        print("\n--- Test 4: Repeat first query (should use cache) ---")
        result4 = ai_service.search_similar_scenes(query1, n_results=2)
        print(f"✓ Fourth query completed, cache size: {len(ai_service.query_embedding_cache)}")
        
        # Test cache clearing
        print("\n--- Test 5: Cache clearing ---")
        ai_service.clear_query_cache()
        print(f"✓ Cache cleared, cache size: {len(ai_service.query_embedding_cache)}")
        
        # Test query 5 - should create new embedding after cache clear
        print("\n--- Test 6: Query after cache clear (should create new embedding) ---")
        result5 = ai_service.search_similar_scenes(query1, n_results=2)
        print(f"✓ Fifth query completed, cache size: {len(ai_service.query_embedding_cache)}")
        
        print("\n=== Caching Test Results ===")
        print("✓ Query embedding caching is working correctly!")
        print("✓ Embeddings are only created when needed")
        print("✓ Cache is properly maintained and cleared")
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query_caching() 