import chromadb
from typing import List, Dict, Optional

class EmbeddingStorage:
    """
    Handles storage and retrieval of embeddings using ChromaDB.
    """
    def __init__(self, collection_name: str = "embeddings", persist_directory: Optional[str] = None):
        """
        Initialize the ChromaDB client and collection.
        Args:
            collection_name (str): Name of the ChromaDB collection.
            persist_directory (str, optional): Directory to persist ChromaDB data. If None, uses in-memory.
        """
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(collection_name)

    def add_embeddings(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add embeddings and their associated documents/metadata to the collection.
        Args:
            embeddings (List[List[float]]): List of embedding vectors.
            documents (List[str]): List of original text documents.
            metadatas (List[Dict], optional): List of metadata dicts for each document.
            ids (List[str], optional): List of unique IDs for each document.
        """
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        if metadatas is None:
            metadatas = [{} for _ in documents]
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query_similar(
        self,
        query_embedding: List[float],
        n_results: int = 5
    ) -> Dict:
        """
        Query the collection for the most similar documents to the given embedding.
        Args:
            query_embedding (List[float]): The embedding vector to search with.
            n_results (int): Number of results to return.
        Returns:
            Dict: Results containing documents, metadatas, distances, and ids.
        """
        return self.collection.query(query_embeddings=[query_embedding], n_results=n_results)

    def count(self) -> int:
        """
        Return the number of documents in the collection.
        """
        return self.collection.count()

    def delete_all(self) -> None:
        """
        Delete all documents in the collection.
        """
        ids = self.collection.get()["ids"]
        if ids:
            self.collection.delete(ids=ids) 