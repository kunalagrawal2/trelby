# -*- coding: utf-8 -*-

import os
import re
import hashlib
import anthropic
import openai
import chromadb
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
import trelby.screenplay as screenplay_module
from trelby.ai import get_ai_service

class AIService:
    """
    AI service that uses embeddings and ChromaDB for semantic search
    to provide better context-aware responses.
    """
    
    def __init__(self, collection_name: str = "screenplay_embeddings"):
        """
        Initialize AI service with Claude and OpenAI embeddings.
        
        Args:
            collection_name: Name of ChromaDB collection for embeddings
        """
        print("Debug: Initializing AIService...")
        
        # Load environment variables
        self._load_env_variables()
        
        # Initialize Claude client
        self._init_claude_client()
        
        # Initialize OpenAI client for embeddings
        self._init_openai_client()
        
        # Initialize ChromaDB
        self._init_chromadb(collection_name)
        
        # Cache for system prompts and embeddings
        self.cached_system_prompt = None
        self.cached_semantic_context = None
        self.cached_document_context = None
        
        # Query embedding cache to avoid recreating embeddings for every search
        self.query_embedding_cache = {}
        self.last_screenplay_hash = None
        
        print("Debug: AIService initialization complete")
    
    def _load_env_variables(self):
        """Load environment variables from .env file"""
        print("Debug: Environment variables loaded")
        load_dotenv()
    
    def _init_claude_client(self):
        """Initialize Claude client with API key from .env"""
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            
            print(f"Debug: Anthropic API key found (length: {len(api_key)} chars)")
            self.claude_client = anthropic.Anthropic(api_key=api_key)
            print("Debug: Claude client initialized successfully")
        except Exception as e:
            print(f"Debug: Failed to initialize Claude client: {e}")
            raise
    
    def _init_openai_client(self):
        """Initialize OpenAI client with API key from .env"""
        try:
            # Try to get API key from .env file first
            api_key = self._get_openai_key_from_env_file()
            if not api_key:
                # Fallback to environment variable
                api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in .env file or environment variables")
            
            print(f"Debug: OpenAI API key found (length: {len(api_key)} chars)")
            self.openai_client = openai.OpenAI(api_key=api_key)
            self.embedding_model = "text-embedding-3-large"
            print(f"Debug: OpenAI client initialized with model: {self.embedding_model}")
        except Exception as e:
            print(f"Debug: Failed to initialize OpenAI client: {e}")
            raise
    
    def _get_openai_key_from_env_file(self):
        """Read OpenAI API key directly from .env file, ignoring environment variables."""
        try:
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('OPENAI_API_KEY='):
                        key = line.split('=', 1)[1]
                        print(f"Debug: Read OpenAI API key from .env file (length: {len(key)} chars)")
                        return key
            print("Debug: OPENAI_API_KEY not found in .env file")
            return None
        except FileNotFoundError:
            print("Debug: .env file not found")
            return None
        except Exception as e:
            print(f"Debug: Error reading .env file: {e}")
            return None
    
    def chunk_screenplay_scenes(self, screenplay) -> List[Dict]:
        """
        Chunk the screenplay into scenes with metadata.
        
        Args:
            screenplay: Trelby screenplay object
            
        Returns:
            List of dictionaries with 'text', 'metadata', and 'id' keys
        """
        print("Debug: Starting screenplay chunking...")
        
        if not screenplay:
            print("Debug: No screenplay provided")
            return []
        
        if not hasattr(screenplay, 'lines'):
            print("Debug: Screenplay has no 'lines' attribute")
            return []
        
        print(f"Debug: Processing screenplay with {len(screenplay.lines)} lines")
        
        # Import the constants from screenplay module
        import trelby.screenplay as screenplay_module
        
        # Check if screenplay has the required constants
        if not hasattr(screenplay_module, 'SCENE'):
            print("Debug: screenplay_module missing SCENE constant")
            return []
        
        print(f"Debug: Screenplay constants available - SCENE: {screenplay_module.SCENE}")
        
        chunks = []
        current_scene_text = []
        current_scene_metadata = {}
        scene_number = 0
        
        for i, line in enumerate(screenplay.lines):
            # Check if this is a scene heading
            if hasattr(line, 'lt') and hasattr(line, 'lb'):
                if line.lt == screenplay_module.SCENE and line.lb == screenplay_module.LB_LAST:
                    # Save previous scene if it exists
                    if current_scene_text:
                        scene_text = "\n".join(current_scene_text)
                        if scene_text.strip():
                            chunk_id = f"scene_{scene_number}_{hash(scene_text[:50])}"
                            chunks.append({
                                'text': scene_text,
                                'metadata': current_scene_metadata,
                                'id': chunk_id
                            })
                            print(f"Debug: Created chunk {scene_number} with {len(scene_text)} chars")
                    
                    # Start new scene
                    scene_number += 1
                    current_scene_text = [line.text]
                    current_scene_metadata = {
                        'type': 'scene',
                        'scene_number': scene_number,
                        'scene_heading': line.text,
                        'line_number': i,
                        'element_type': 'scene_heading'
                    }
                    print(f"Debug: Found scene {scene_number}: {line.text}")
                else:
                    # Add line to current scene
                    current_scene_text.append(line.text)
                    
                    # Update metadata based on line type
                    if hasattr(line, 'lt'):
                        if line.lt == screenplay_module.CHARACTER:
                            current_scene_metadata['has_character'] = True
                        elif line.lt == screenplay_module.DIALOGUE:
                            current_scene_metadata['has_dialogue'] = True
                        elif line.lt == screenplay_module.ACTION:
                            current_scene_metadata['has_action'] = True
            else:
                print(f"Debug: Line {i} missing required attributes (lt, lb)")
        
        # Add the last scene
        if current_scene_text:
            scene_text = "\n".join(current_scene_text)
            if scene_text.strip():
                chunk_id = f"scene_{scene_number}_{hash(scene_text[:50])}"
                chunks.append({
                    'text': scene_text,
                    'metadata': current_scene_metadata,
                    'id': chunk_id
                })
                print(f"Debug: Created final chunk {scene_number} with {len(scene_text)} chars")
        
        print(f"Debug: Created {len(chunks)} chunks from screenplay")
        return chunks
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        print(f"Debug: Creating embeddings for {len(texts)} texts")
        
        if not texts:
            print("Debug: No texts provided for embedding")
            return []
        
        try:
            print(f"Debug: Calling OpenAI embeddings API with model: {self.embedding_model}")
            response = self.openai_client.embeddings.create(
                input=texts,
                model=self.embedding_model
            )
            embeddings = [embedding.embedding for embedding in response.data]
            print(f"Debug: Successfully created {len(embeddings)} embeddings")
            if embeddings:
                print(f"Debug: Each embedding has {len(embeddings[0])} dimensions")
            return embeddings
        except Exception as e:
            print(f"Debug: Error creating embeddings: {e}")
            return []
    
    def store_screenplay_embeddings(self, screenplay) -> bool:
        """
        Process screenplay, create embeddings, and store in ChromaDB.
        
        Args:
            screenplay: Trelby screenplay object
            
        Returns:
            True if successful, False otherwise
        """
        print("Debug: Starting screenplay embedding storage...")
        
        try:
            # Check if screenplay has meaningful content
            if not screenplay or not hasattr(screenplay, 'lines') or len(screenplay.lines) <= 1:
                print("Debug: Screenplay is empty or has insufficient content")
                return False
            
            # Check if screenplay has actual text content
            total_text = ""
            for line in screenplay.lines:
                if hasattr(line, 'text') and line.text.strip():
                    total_text += line.text + " "
            
            if len(total_text.strip()) < 100:  # Require at least 100 characters
                print(f"Debug: Screenplay has insufficient text content ({len(total_text)} chars)")
                return False
            
            # Chunk the screenplay
            print("Debug: Chunking screenplay...")
            chunks = self.chunk_screenplay_scenes(screenplay)
            if not chunks:
                # Fallback: create a single chunk with the entire screenplay
                print("Debug: No scenes found, creating fallback chunk")
                chunks = self.create_fallback_chunk(screenplay)
                if not chunks:
                    print("Debug: Failed to create fallback chunk")
                    return False
            
            print(f"Debug: Created {len(chunks)} chunks")
            
            # Extract texts and metadata
            texts = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            ids = [chunk['id'] for chunk in chunks]
            
            print(f"Debug: Extracted {len(texts)} texts, {len(metadatas)} metadata, {len(ids)} ids")
            
            # Create embeddings
            print("Debug: Creating embeddings...")
            embeddings = self.create_embeddings(texts)
            if not embeddings:
                print("Debug: Failed to create embeddings")
                return False
            
            print(f"Debug: Created {len(embeddings)} embeddings")
            
            # Store in ChromaDB
            print("Debug: Storing embeddings in ChromaDB...")
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Debug: Successfully stored {len(chunks)} scene embeddings in ChromaDB")
            return True
            
        except Exception as e:
            print(f"Debug: Error storing screenplay embeddings: {e}")
            return False
    
    def create_fallback_chunk(self, screenplay) -> List[Dict]:
        """
        Create a fallback chunk when no scenes are found.
        
        Args:
            screenplay: Trelby screenplay object
            
        Returns:
            List with a single chunk containing the entire screenplay
        """
        print("Debug: Creating fallback chunk...")
        
        try:
            # Get all text from the screenplay
            all_text = []
            for line in screenplay.lines:
                all_text.append(line.text)
            
            screenplay_text = "\n".join(all_text)
            
            if not screenplay_text.strip():
                print("Debug: No text content found in screenplay")
                return []
            
            print(f"Debug: Fallback chunk has {len(screenplay_text)} characters")
            
            # Create a single chunk
            chunk = {
                'text': screenplay_text,
                'metadata': {
                    'type': 'fallback',
                    'scene_number': 1,
                    'scene_heading': 'Entire Screenplay',
                    'line_number': 0,
                    'element_type': 'fallback',
                    'total_lines': len(screenplay.lines)
                },
                'id': f"fallback_{hash(screenplay_text[:100])}"
            }
            
            print("Debug: Created fallback chunk successfully")
            return [chunk]
            
        except Exception as e:
            print(f"Debug: Error creating fallback chunk: {e}")
            return []
    
    def search_similar_scenes(self, query: str, n_results: int = 5) -> Optional[Dict]:
        """
        Search for scenes similar to the query.
        
        Args:
            query: Search query string
            n_results: Number of results to return
            
        Returns:
            Search results dictionary or None if error
        """
        print(f"Debug: Searching for scenes similar to: '{query[:50]}...'")
        print(f"Debug: Requesting {n_results} results")
        
        try:
            # Check if query embedding is cached
            query_hash = hash(query)
            if query_hash in self.query_embedding_cache:
                print("Debug: Query embedding found in cache")
                query_embeddings = self.query_embedding_cache[query_hash]
            else:
                print("Debug: Query embedding not found in cache, creating new embedding")
                query_embeddings = self.create_embeddings([query])
                if query_embeddings:
                    # Cache the embedding for future use
                    self.query_embedding_cache[query_hash] = query_embeddings
                    print("Debug: Query embedding cached for future use")
            
            if not query_embeddings:
                print("Debug: Failed to create query embedding")
                return None
            
            print("Debug: Query embedding ready for search")
            
            # Search in ChromaDB
            print("Debug: Searching ChromaDB...")
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results
            )
            
            print(f"Debug: ChromaDB search returned results")
            if results and 'documents' in results:
                print(f"Debug: Found {len(results['documents'][0])} documents")
                if results['distances']:
                    print(f"Debug: Distances: {[f'{d:.3f}' for d in results['distances'][0]]}")
            
            return results
        except Exception as e:
            print(f"Debug: Error searching similar scenes: {e}")
            return None
    
    def get_semantic_context(self, user_message: str, n_results: int = 2) -> str:
        """
        Get semantic context from similar scenes for the user's query.
        
        Args:
            user_message: User's query
            n_results: Number of similar scenes to include
            
        Returns:
            Context string with relevant scenes
        """
        print(f"Debug: Getting semantic context for: '{user_message[:50]}...'")
        
        search_results = self.search_similar_scenes(user_message, n_results)
        if not search_results or not search_results.get('documents'):
            print("Debug: No search results found for semantic context")
            return ""
        
        print(f"Debug: Found {len(search_results['documents'][0])} search results")
        
        context_parts = ["SEMANTIC SEARCH RESULTS:"]
        
        for i, (doc, metadata, distance) in enumerate(zip(
            search_results['documents'][0],
            search_results['metadatas'][0],
            search_results['distances'][0]
        )):
            scene_info = f"Scene {metadata.get('scene_number', 'Unknown')}"
            if metadata.get('scene_heading'):
                scene_info += f": {metadata['scene_heading']}"
            
            # Fix: Convert distance to similarity correctly
            # ChromaDB returns cosine distance (0-2), where 0 is most similar
            # Convert to similarity score (0-1) where 1 is most similar
            similarity = 1 - (distance / 2)
            
            context_parts.append(f"\n--- {scene_info} (similarity: {similarity:.2f}) ---")
            context_parts.append(doc[:500] + "..." if len(doc) > 500 else doc)
            
            print(f"Debug: Added scene {i+1} with similarity {similarity:.3f} (distance: {distance:.3f})")
        
        context = "\n".join(context_parts)
        print(f"Debug: Semantic context length: {len(context)} characters")
        return context
    
    def get_simple_response(self, user_message: str, ai_service=None) -> str:
        """
        Get AI response without semantic search or complex context.
        Used for formatting and other simple tasks.
        
        Args:
            user_message: User's message
            ai_service: Optional AI service instance to use instead of internal Claude client
            
        Returns:
            AI response string
        """
        try:
            print(f"Debug: Getting simple AI response for: '{user_message[:50]}...'")
            
            # If an external AI service is provided, use it directly
            if ai_service:
                print("Debug: Using external AI service for simple response")
                return ai_service.get_response(user_message, "", None)
            
            # Simple system prompt for formatting tasks
            system_prompt = """You are an expert AI assistant for screenwriting tasks. 
Provide clear, direct responses without unnecessary context or explanations.
For formatting tasks, return only the formatted content as requested."""
            
            print("Debug: Calling Claude API with simple prompt...")
            
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,  # Higher limit for formatting
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            response_text = response.content[0].text
            print(f"Debug: Simple API call successful, response length: {len(response_text)} characters")
            return response_text
        except Exception as e:
            print(f"Debug: Simple API call failed with error: {e}")
            return f"Error: {str(e)}"
    
    def get_response(self, user_message: str, context: str = "", conversation_history: List[Dict] = None, ai_service=None) -> str:
        """
        Get AI response with enhanced semantic search context.
        
        Args:
            user_message: User's message
            context: Additional context (e.g., current scene info)
            conversation_history: Previous conversation messages
            ai_service: Optional AI service instance to use instead of internal Claude client
            
        Returns:
            AI response string
        """
        try:
            print(f"Debug: Getting AI response for: '{user_message[:50]}...'")
            print(f"Debug: Context provided: {len(context)} characters")
            print(f"Debug: Conversation history: {len(conversation_history) if conversation_history else 0} messages")
            
            # If an external AI service is provided, use it directly
            if ai_service:
                print("Debug: Using external AI service for response")
                # Combine context with user message for the external service
                if context and context.strip():
                    enhanced_message = f"{user_message}\n\nCONTEXT:\n{context}"
                else:
                    enhanced_message = user_message
                
                return ai_service.get_response(enhanced_message, "", conversation_history)
            
            # Get semantic context from similar scenes
            print("Debug: Getting semantic context...")
            semantic_context = self.get_semantic_context(user_message)
            print(f"Debug: Semantic context length: {len(semantic_context)} characters")
            
            # Check if we need to send a new system prompt or context update
            # Only trigger context update if document context changed, not semantic context
            # (semantic context changes with each query, which is expected)
            context_changed = (
                self.cached_document_context != context
            )
            
            # Build messages array with conversation history
            messages = []
            
            # Only send system prompt if it's the first time or if we don't have one cached
            if self.cached_system_prompt is None:
                print("Debug: Sending initial system prompt")
                system_prompt = """You are an expert AI assistant specializing in screenwriting and creative storytelling. Your role is to help writers develop compelling narratives, characters, and dialogue.

CORE BEHAVIORS:
- Provide specific, actionable writing advice based on established screenwriting principles
- Ask clarifying questions when needed to give better, more targeted suggestions
- Focus on practical techniques rather than abstract concepts
- Encourage creative exploration while maintaining narrative coherence
- Respect the writer's vision while offering constructive improvements

CREATIVE APPROACH:
- Think like a seasoned screenwriter with deep understanding of story structure
- Draw from classic and contemporary storytelling techniques
- Help writers find their unique voice while following industry standards
- Suggest concrete ways to enhance emotional impact and audience engagement
- Balance creativity with commercial viability

ACCURACY & RELIABILITY:
- Base all advice on well-established screenwriting principles and techniques
- If you're unsure about something, acknowledge the limitation rather than guessing
- Distinguish between subjective creative choices and objective storytelling fundamentals
- Cite specific examples or techniques when making recommendations
- Avoid making claims about industry practices you're not certain about

RESPONSE STYLE:
- Be encouraging but honest about what works and what doesn't
- Provide specific examples and actionable suggestions
- Keep responses focused and practical
- Ask follow-up questions to better understand the writer's goals
- Maintain a collaborative, supportive tone throughout the conversation

SEMANTIC SEARCH CONTEXT:
- When provided with semantic search results, use them to give more relevant advice
- Reference specific scenes, characters, or elements from the search results
- Connect your suggestions to existing content in the screenplay
- Use the similarity scores to understand how relevant each scene is to the query
- Provide context-aware suggestions that build on what's already written

DOCUMENT CONTEXT:
- When provided with screenplay context, use it to give more specific, relevant advice
- Reference specific characters, scenes, or elements from the script when appropriate
- Provide context-aware suggestions that build on what's already written
- If the context shows a complete script, offer comprehensive analysis and suggestions
- If the context shows a partial script, focus on development and expansion ideas

CONVERSATION MEMORY:
- Remember previous messages in the conversation and build upon them
- Reference earlier points made by the user or yourself when relevant
- Maintain continuity in your advice and suggestions
- Don't repeat information already discussed unless specifically asked"""
                
                self.cached_system_prompt = system_prompt
                print(f"Debug: Cached system prompt (length: {len(system_prompt)} characters)")
            else:
                print("Debug: Using cached system prompt")
            
            # Add conversation history if provided
            if conversation_history:
                print(f"Debug: Including {len(conversation_history)} previous messages in conversation")
                for i, msg in enumerate(conversation_history):
                    if msg['message'].strip():  # Only add non-empty messages
                        role = "user" if msg['is_user'] else "assistant"
                        messages.append({
                            "role": role,
                            "content": msg['message']
                        })
                        print(f"Debug: Added message {i+1}: {role} ({len(msg['message'])} chars)")
            
            # Send context update as a user message if context changed
            if context_changed:
                print("Debug: Document context changed, sending context update")
                context_update = []
                
                if context and context.strip():
                    context_update.append(f"UPDATED SCREENPLAY CONTEXT:\n{context}")
                    print("Debug: Added document context to update")
                
                if context_update:
                    context_message = "\n\n".join(context_update)
                    messages.append({
                        "role": "user",
                        "content": f"Please update your context with the following information:\n\n{context_message}"
                    })
                    print(f"Debug: Added context update message ({len(context_message)} chars)")
                
                # Update cached document context
                self.cached_document_context = context
            else:
                print("Debug: Document context unchanged, no update needed")
            
            # Always include semantic context in the system prompt or as part of the conversation
            # since it changes with each query (this is expected behavior)
            if semantic_context:
                # Include semantic context in the current user message
                enhanced_user_message = f"{user_message}\n\nSEMANTIC SEARCH RESULTS:\n{semantic_context}"
                messages.append({
                    "role": "user",
                    "content": enhanced_user_message
                })
                print(f"Debug: Added current user message with semantic context ({len(enhanced_user_message)} chars)")
            else:
                # Add current user message without semantic context
                messages.append({
                    "role": "user",
                    "content": user_message
                })
                print(f"Debug: Added current user message ({len(user_message)} chars)")
            
            print(f"Debug: Total messages: {len(messages)}")
            print("Debug: Calling Claude API...")
            
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                system=self.cached_system_prompt,
                messages=messages
            )
            
            response_text = response.content[0].text
            print(f"Debug: Claude API call successful, response length: {len(response_text)} characters")
            return response_text
        except Exception as e:
            print(f"Debug: Enhanced API call failed with error: {e}")
            return f"Error: {str(e)}"
    
    def get_collection_info(self) -> Dict:
        """Get information about the ChromaDB collection."""
        try:
            count = self.collection.count()
            print(f"Debug: Collection '{self.collection_name}' has {count} documents")
            return {
                'collection_name': self.collection_name,
                'document_count': count,
                'status': 'active'
            }
        except Exception as e:
            print(f"Debug: Error getting collection info: {e}")
            return {
                'collection_name': self.collection_name,
                'document_count': 0,
                'status': f'error: {e}'
            }
    
    def clear_embeddings(self) -> bool:
        """Clear all embeddings from the collection."""
        try:
            print("Debug: Clearing all embeddings from collection...")
            ids = self.collection.get()["ids"]
            if ids:
                self.collection.delete(ids=ids)
                print(f"Debug: Cleared {len(ids)} embeddings from collection")
            else:
                print("Debug: No embeddings to clear")
            return True
        except Exception as e:
            print(f"Debug: Error clearing embeddings: {e}")
            return False
    
    def clear_system_prompt_cache(self):
        """Clear cached system prompt and contexts"""
        print("Debug: Clearing system prompt cache")
        self.cached_system_prompt = None
        self.cached_semantic_context = None
        self.cached_document_context = None
        self.query_embedding_cache = {}
        self.last_screenplay_hash = None
    
    def clear_context_cache(self):
        """Clear only context caches, keep system prompt"""
        print("Debug: Clearing context caches only")
        self.cached_semantic_context = None
        self.cached_document_context = None
    
    def clear_query_cache(self):
        """Clear the query embedding cache"""
        print("Debug: Clearing query embedding cache")
        self.query_embedding_cache = {}
    
    def update_screenplay_hash(self, screenplay_hash):
        """Update the screenplay hash and clear caches if it changed"""
        if screenplay_hash != self.last_screenplay_hash:
            print("Debug: Screenplay hash changed, clearing context caches")
            self.clear_context_cache()  # Only clear context, not system prompt
            self.last_screenplay_hash = screenplay_hash
        else:
            print("Debug: Screenplay hash unchanged, keeping caches")
    
    def _init_chromadb(self, collection_name: str):
        """Initialize ChromaDB with the specified collection"""
        self.collection_name = collection_name
        print(f"Debug: Initializing ChromaDB with collection: {collection_name}")
        
        try:
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
            print(f"Debug: Created new ChromaDB collection: {collection_name}")
        except Exception as e:
            print(f"Debug: Error initializing ChromaDB: {e}")
            raise 