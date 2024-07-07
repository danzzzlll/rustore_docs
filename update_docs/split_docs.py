import os
from tqdm import tqdm
import pandas as pd
from typing import Optional, List, Tuple

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document as LangchainDocument
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, Runnable, RunnableSequence
from langchain import PromptTemplate

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

import re
from typing import List
import joblib

import json
import os

def split():
    
    def read_json_files_from_folder(folder_path):
        json_files_content = []

        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(folder_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        if data['text'] == "":
                            continue
                        json_files_content.append(data)
                except FileNotFoundError:
                    print(f"The file {file_path} does not exist.")
                except json.JSONDecodeError:
                    print(f"The file {file_path} is not a valid JSON file.")

        return json_files_content

    json_files_content = read_json_files_from_folder('./parser/processed_docs/')

    EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"

    def preprocess_text(text: str) -> str:
        separators = ["h1h1h1", "h2h2h2", "h3h3h3", "h4h4h4", "h5h5h5", "---End of row---", "tabletabletable", "paragraphparagraphparagraph"]
        pattern = '|'.join(map(re.escape, separators))

        text = re.sub(r'\x00', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(pattern, '\n', text)
        # text = re.sub(r'\n\n+', '', text)

        return text

    def split_documents(
        chunk_size: int,
        knowledge_base: List[LangchainDocument],
        tokenizer_name: Optional[str] = EMBEDDING_MODEL_NAME,
    ) -> List[LangchainDocument]:
        """
        Split documents into chunks of maximum size `chunk_size` tokens and return a list of documents.
        """
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer,
            chunk_size=chunk_size,
            chunk_overlap=int(chunk_size / 10),
            add_start_index=True,
            strip_whitespace=True,
            separators=["h1h1h1", "h2h2h2", "h3h3h3", "h4h4h4", "h5h5h5", "---End of row---", "tabletabletable", "paragraphparagraphparagraph",
                       '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.','9.','10.','11.','12.', '|'],
        )

        docs_processed = []
        for doc in knowledge_base:
            preprocessed_content = doc.page_content
            chunks = text_splitter.split_text(preprocessed_content)
            for chunk in chunks:
                chunk = preprocess_text(chunk)
                langchain_doc = LangchainDocument(
                    page_content=chunk,
                    metadata=doc.metadata
                )
                docs_processed.append(langchain_doc)

        unique_texts = {}
        docs_processed_unique = []
        for doc in docs_processed:
            if doc.page_content not in unique_texts:
                unique_texts[doc.page_content] = True
                docs_processed_unique.append(doc)

        return docs_processed_unique

    docs = [
        LangchainDocument(page_content=json_file['text'], metadata=json_file['meta']
                        )
        for json_file in json_files_content
    ]

    docs_processed = split_documents(
        512,
        docs,
        tokenizer_name=EMBEDDING_MODEL_NAME,
    )

    joblib.dump(docs_processed, './parser/processed_langchain_docs.pkl')