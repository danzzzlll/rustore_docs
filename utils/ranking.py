# !pip install ragatouille -q

from sentence_transformers import SentenceTransformer
from voyager import Index, Space

import joblib
from typing import List, Dict
from rank_bm25 import BM25Okapi
import pandas as pd

class MyExistingRetrievalPipeline:
    index: Index
    embedder: SentenceTransformer
    bm25: BM25Okapi

    def __init__(self, embedder_name: str = "embaas/sentence-transformers-multilingual-e5-large"):
        self.embedder = SentenceTransformer(embedder_name)
        self.collection_map = {}
        self.index = Index(
            Space.Cosine,
            num_dimensions=self.embedder.get_sentence_embedding_dimension(),
        )
        self.bm25 = None
        self.doc_texts = []

    def index_documents(self, df: pd.DataFrame, batch_size: int = 32) -> None: # if we want to batching again
        self.df = df  
        self.doc_texts = df['Full_Content'].tolist()
        self.bm25 = BM25Okapi(self.doc_texts)

        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            documents = batch['Full_Content'].tolist()
            embeddings = self.embedder.encode(documents, show_progress_bar=True)
            for j, embedding in enumerate(embeddings):
                doc_id = batch.iloc[j]['Meta']
                self.collection_map[self.index.add_item(embedding)] = {
                    'doc_id': doc_id,
                    'content': documents[j]
                }
                
    def save_index(self, index_file_path: str, map_file_path: str, doc_texts_path: str):
        """Saves the index to a file and the collection map using joblib."""
        self.index.save(index_file_path)  # Utilize the index's own save method
        joblib.dump(self.collection_map, map_file_path)  # Save the collection map separately
        joblib.dump(self.doc_texts, doc_texts_path) # for bm25 model

    def load_index(self, index_file_path: str, map_file_path: str, doc_texts_path: str):
        """Loads the index from a file and the collection map using joblib."""
        index = Index.load(index_file_path) # Utilize the index's own load method
        self.index = index  
        self.collection_map = joblib.load(map_file_path)  # Load the collection map separately
        self.doc_texts = joblib.load(doc_texts_path)
        self.bm25 = BM25Okapi(self.doc_texts)

    def query(self, query: str, k: int = 10) -> List[Dict[str, str]]:
        query_embedding = self.embedder.encode(query)
        dense_results = self.index.query(query_embedding, k=k)[0]
        dense_docs = [{'index':idx, 'doc_id': self.collection_map[idx]['doc_id'], 'content': self.collection_map[idx]['content']} for idx in dense_results]

        bm25_scores = self.bm25.get_scores(query)
        sorted_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)
        bm25_docs = [{'index':idx, 'doc_id': self.collection_map[idx]['doc_id'], 'content': self.collection_map[idx]['content']} for idx in sorted_indices[:k]]

        combined_docs = dense_docs #+ bm25_docs
        combined_docs = list(set([tuple(doc.items()) for doc in combined_docs]))
        combined_docs = [dict(doc) for doc in combined_docs]
        new_k = 2 * k
        
        return combined_docs[:new_k]
