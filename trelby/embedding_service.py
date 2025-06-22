# -*- coding: utf-8 -*-
import os
import openai
from dotenv import load_dotenv

class EmbeddingService:
    """
    Handles the creation of text embeddings using OpenAI's API.
    """
    def __init__(self):
        """
        Initializes the service by loading the environment variables
        and setting up the OpenAI client.
        """
        print("Debug: Initializing EmbeddingService...")
        
        load_dotenv()
        print("Debug: Environment variables loaded")
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("Debug: OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY not found in .env file or environment variables.")
        
        print(f"Debug: OpenAI API key found (length: {len(self.api_key)} characters)")
        print(f"Debug: API key starts with: {self.api_key[:10]}...")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = "text-embedding-3-large"
        print(f"Debug: OpenAI client initialized with model: {self.model}")
        print("Debug: EmbeddingService initialization complete")

    def create_embeddings(self, texts: list[str]):
        """
        Generates embeddings for a list of text documents.

        Args:
            texts (list[str]): A list of strings to be embedded.

        Returns:
            list: A list of embedding vectors, or an empty list if an error occurs.
        """
        print(f"Debug: Creating embeddings for {len(texts)} texts")
        
        if not texts:
            print("Debug: No texts provided for embedding")
            return []

        # Log some details about the texts
        for i, text in enumerate(texts):
            print(f"Debug: Text {i+1}: {len(text)} characters")
            if len(text) > 100:
                print(f"Debug: Text {i+1} preview: {text[:100]}...")
            else:
                print(f"Debug: Text {i+1}: {text}")

        try:
            print(f"Debug: Calling OpenAI embeddings API with model: {self.model}")
            print(f"Debug: API key being used: {self.api_key[:10]}...{self.api_key[-4:]}")
            
            # Note: OpenAI's API can handle a list of texts in a single call
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            
            print("Debug: OpenAI API call successful")
            print(f"Debug: Response object type: {type(response)}")
            print(f"Debug: Response has 'data' attribute: {hasattr(response, 'data')}")
            
            # Extract the embedding data from the response object
            embeddings = [embedding.embedding for embedding in response.data]
            
            print(f"Debug: Successfully created {len(embeddings)} embeddings")
            if embeddings:
                print(f"Debug: Each embedding has {len(embeddings[0])} dimensions")
                print(f"Debug: First embedding sample values: {embeddings[0][:5]}...")
            
            return embeddings
        except openai.APIError as e:
            print(f"Debug: OpenAI API error occurred: {e}")
            print(f"Debug: Error type: {type(e)}")
            print(f"Debug: Error details: {str(e)}")
            return []
        except Exception as e:
            print(f"Debug: Unexpected error during embedding creation: {e}")
            print(f"Debug: Error type: {type(e)}")
            print(f"Debug: Error details: {str(e)}")
            return [] 