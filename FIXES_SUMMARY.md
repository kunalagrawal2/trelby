# Debug Output Analysis and Fixes

## Issues Identified from Terminal Output

### 1. **Negative Similarity Scores** ❌ FIXED
**Problem**: Semantic search was returning negative similarity scores
```
Debug: Distances: ['1.295', '1.358', '1.374']
Debug: Added scene 1 with similarity -0.295
Debug: Added scene 2 with similarity -0.358
Debug: Added scene 3 with similarity -0.374
```

**Root Cause**: Incorrect conversion from ChromaDB cosine distance to similarity
- ChromaDB returns cosine distance (0-2 range)
- Old calculation: `similarity = 1 - distance` (gave negative values)
- New calculation: `similarity = 1 - (distance / 2)` (gives 0-1 range)

**Fix Applied**: Updated `get_semantic_context()` method in `ai_service_enhanced.py`

### 2. **Excessive Hash Calculation** ❌ FIXED
**Problem**: Hash function was being called every 2 seconds, creating spam
```
Debug: Calculating screenplay hash...
Debug: Screenplay has 5030 lines
Debug: Hash calculation complete
```

**Root Cause**: Monitoring thread was too aggressive and logging too frequently

**Fixes Applied**:
- Reduced monitoring frequency from 2 seconds to 5 seconds
- Added hash caching to prevent duplicate logging
- Reduced debug output frequency (60s for no changes, 30s for no screenplay)

### 3. **Empty Screenplay Processing** ❌ FIXED
**Problem**: System was trying to process empty screenplays
```
Debug: Screenplay has 1 lines
Debug: Content length: 0 characters
Debug: No text content found in screenplay
```

**Root Cause**: No validation for empty or insufficient content

**Fix Applied**: Added content validation in `store_screenplay_embeddings()`
- Check for minimum line count (>1)
- Check for minimum text content (>100 characters)
- Prevent processing of empty screenplays

## Test Results

### Similarity Calculation Fix
```
Old calculation (1 - distance):
  Scene 1: -0.295
  Scene 2: -0.358
  Scene 3: -0.374

New calculation (1 - distance/2):
  Scene 1: 0.353
  Scene 2: 0.321
  Scene 3: 0.313
```

✅ **Fixed**: All similarities are now positive and in the correct 0-1 range

## Expected Improvements

1. **Semantic Search**: Should now return meaningful, positive similarity scores
2. **Performance**: Reduced hash calculation spam and monitoring overhead
3. **Stability**: Won't try to process empty screenplays
4. **Debug Output**: Cleaner, more focused logging

## Next Steps

1. Test the application with the fixes
2. Verify semantic search returns relevant results
3. Monitor performance improvements
4. Check that empty screenplay handling works correctly 