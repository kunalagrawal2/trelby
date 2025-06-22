# Enhanced AI Assistant Integration

## Overview

The AI assistant has been enhanced with automatic semantic search capabilities using embeddings and ChromaDB. This replaces the basic text approach with a more intelligent, context-aware system.

## Key Features

### 1. Automatic Screenplay Analysis
- **Automatic Processing**: When a screenplay is loaded, the AI assistant automatically analyzes it in the background
- **Scene Chunking**: Breaks down the screenplay into individual scenes for better context understanding
- **Embedding Generation**: Creates semantic embeddings for each scene using OpenAI's text-embedding-3-large model
- **ChromaDB Storage**: Stores embeddings in a vector database for fast semantic search

### 2. Semantic Search Integration
- **Context-Aware Responses**: The AI uses semantic search to find relevant scenes when answering questions
- **Similarity Matching**: Can find scenes similar to user queries about characters, plot points, themes, etc.
- **Enhanced Context**: Provides the AI with relevant scenes from the screenplay for more accurate responses

### 3. Seamless User Experience
- **No Manual Setup**: Everything happens automatically in the background
- **Real-time Updates**: Monitors for screenplay changes and updates embeddings accordingly
- **Status Indicators**: Shows processing status in the AI assistant panel
- **Fallback Handling**: Works even with screenplays that don't have proper scene structure

## Technical Implementation

### Files Modified/Created

1. **`trelby/ai_service_enhanced.py`** - New enhanced AI service with embedding capabilities
2. **`trelby/ai_assistant.py`** - Updated AI assistant panel with automatic processing
3. **`trelby/embedding_service.py`** - OpenAI embedding service (existing)
4. **`trelby/embedding_storage.py`** - ChromaDB storage service (existing)

### Key Components

#### EnhancedAIService
- Handles both Claude API calls and OpenAI embeddings
- Manages ChromaDB collection for semantic search
- Provides scene chunking and metadata extraction
- Includes fallback mechanisms for robustness

#### AIAssistantPanel
- Automatically monitors screenplay changes
- Processes embeddings in background threads
- Provides status updates to users
- Integrates semantic search into AI responses

## Usage

### For Users
1. **Load a Screenplay**: Open any screenplay in Trelby
2. **Automatic Processing**: The AI assistant will automatically analyze the screenplay
3. **Ask Questions**: Ask about characters, plot, scenes, themes, etc.
4. **Get Context-Aware Responses**: The AI will use semantic search to provide relevant answers

### Example Questions
- "Tell me about the main character's development"
- "What are the key plot points in the story?"
- "How does the protagonist change throughout the script?"
- "Find scenes that deal with the theme of redemption"
- "What's the relationship between Character A and Character B?"

## Benefits

### Over Basic Text Approach
- **Semantic Understanding**: Can find relevant content even with different wording
- **Context Awareness**: Understands relationships between scenes and characters
- **Better Responses**: More accurate and relevant answers based on actual screenplay content
- **Scalability**: Works efficiently with large screenplays

### Technical Advantages
- **Modular Design**: Clean separation of concerns
- **Robust Error Handling**: Graceful fallbacks and error recovery
- **Background Processing**: Doesn't block the UI
- **Memory Efficient**: Uses vector database for fast retrieval

## Requirements

- **OpenAI API Key**: For creating embeddings (text-embedding-3-large)
- **Anthropic API Key**: For Claude AI responses
- **ChromaDB**: For vector storage (included in requirements)
- **Python Dependencies**: openai, anthropic, chromadb, dotenv

## Status

✅ **Integration Complete**: All components are integrated and tested
✅ **Automatic Processing**: Screenplay analysis happens automatically
✅ **Semantic Search**: Context-aware responses using embeddings
✅ **Error Handling**: Robust fallback mechanisms in place
✅ **User Experience**: Seamless, no manual intervention required

The enhanced AI assistant is now ready for use with automatic semantic search capabilities! 