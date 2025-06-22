#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify the similarity calculation fix.
"""

def test_similarity_calculation():
    """Test the similarity calculation fix."""
    print("Testing Similarity Calculation Fix")
    print("=" * 40)
    
    # Test cases based on the debug output we saw
    test_distances = [1.295, 1.358, 1.374]
    
    print("Original distances from ChromaDB:")
    for i, distance in enumerate(test_distances):
        print(f"  Distance {i+1}: {distance}")
    
    print("\nOld calculation (1 - distance):")
    for i, distance in enumerate(test_distances):
        old_similarity = 1 - distance
        print(f"  Scene {i+1}: {old_similarity:.3f}")
    
    print("\nNew calculation (1 - distance/2):")
    for i, distance in enumerate(test_distances):
        new_similarity = 1 - (distance / 2)
        print(f"  Scene {i+1}: {new_similarity:.3f}")
    
    print("\nExpected behavior:")
    print("- Similarity should be between 0 and 1")
    print("- Higher similarity means more relevant")
    print("- Lower distance should mean higher similarity")
    
    print("\nAnalysis:")
    for i, distance in enumerate(test_distances):
        old_sim = 1 - distance
        new_sim = 1 - (distance / 2)
        print(f"  Scene {i+1}: distance={distance:.3f}, old_sim={old_sim:.3f}, new_sim={new_sim:.3f}")
        if new_sim > 0:
            print(f"    ✓ New calculation gives positive similarity")
        else:
            print(f"    ✗ New calculation still negative")

if __name__ == "__main__":
    test_similarity_calculation() 