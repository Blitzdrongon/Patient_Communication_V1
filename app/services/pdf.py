
# import os
# import time
# from functools import lru_cache

# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_ollama import OllamaEmbeddings, OllamaLLM
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_community.vectorstores import FAISS


# TEMPLATE = """
# You are a helpful AI assistant analyzing a PDF.
# Use the extracted content to provide a short, clear answer.
# If some info is missing, answer as best as possible.

# Context:
# {context}

# Question: {question}
# Answer:
# """

# OLLAMA_MODEL_NAME = "llama3.2:3b"
# OLLAMA_LLM = OllamaLLM(model=OLLAMA_MODEL_NAME)
# OLLAMA_EMBED = OllamaEmbeddings(model="nomic-embed-text")


# class PDFRAGTemp:
#     def __init__(self, pdf_path: str):
#         if not pdf_path or not os.path.exists(pdf_path):
#             raise FileNotFoundError(f"❌ PDF not found: {pdf_path}")

#         print(f"📘 Loading PDF: {pdf_path}")
#         self.pdf_path = pdf_path
#         self.chunks = self._load_and_split_pdf()

#         start = time.time()
#         self.vectorstore = self._create_vectorstore()
#         end = time.time()

#         self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
#         self.prompt = ChatPromptTemplate.from_template(TEMPLATE)

#     def _load_and_split_pdf(self):
#         loader = PyPDFLoader(self.pdf_path)
#         docs = loader.load()

#         splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=150
#         )
#         return splitter.split_documents(docs)

#     @lru_cache(maxsize=10)
#     def _create_vectorstore(self):
#         return FAISS.from_documents(self.chunks, OLLAMA_EMBED)

#     def ask(self, query: str) -> str:
#         docs = self.retriever.invoke(query)
#         context = "\n\n".join(doc.page_content for doc in docs)

#         chain = self.prompt | OLLAMA_LLM
#         return chain.invoke({"context": context, "question": query})


import os
import time
import gc
from functools import lru_cache
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS

# Global Models
OLLAMA_MODEL_NAME = "llama3.2:3b"
OLLAMA_LLM = OllamaLLM(model=OLLAMA_MODEL_NAME)
OLLAMA_EMBED = OllamaEmbeddings(model="nomic-embed-text")

TEMPLATE = """
Context:
{context}

Question: {question}
Answer:
"""

# ---------------------------------------------------------
# ✅ CACHED FUNCTION (Outside the class)
# This handles the heavy lifting. Because it is decorated,
# Python remembers the result for the specific 'pdf_path'.
# ---------------------------------------------------------
@lru_cache(maxsize=1)  # Set to 1 to only keep the current PDF, or higher to keep a few
def get_cached_vectorstore(pdf_path: str):
    print(f"🔄 Computing Embeddings for: {pdf_path} (Not cached yet)")
    
    # 1. Load
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    # 2. Split
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    # 3. Embed (Heavy Operation)
    vectorstore = FAISS.from_documents(chunks, OLLAMA_EMBED)
    return vectorstore

class PDFRAGTemp:
    def __init__(self, pdf_path: str):
        if not pdf_path or not os.path.exists(pdf_path):
            raise FileNotFoundError(f"❌ PDF not found: {pdf_path}")

        self.pdf_path = pdf_path
        self.prompt = ChatPromptTemplate.from_template(TEMPLATE)

        # ✅ Call the cached function
        # If this PDF was loaded recently, it returns instantly from RAM.
        # If it's new, it computes it.
        start = time.time()
        self.vectorstore = get_cached_vectorstore(self.pdf_path)
        end = time.time()
        
        print(f"⚡ Vectorstore ready in {end - start:.4f}s")
        
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})

    def ask(self, query: str) -> str:
        docs = self.retriever.invoke(query)
        context = "\n\n".join(doc.page_content for doc in docs)
        chain = self.prompt | OLLAMA_LLM
        return chain.invoke({"context": context, "question": query})

    # ✅ METHOD TO CLEAR THE CACHE
    def clear_all_cache(self):
        #print("🧹 Wiping all cached vector stores from RAM...")
        
        # 1. Clear the specific function cache
        get_cached_vectorstore.cache_clear()
        
        # 2. Clear local references
        self.vectorstore = None
        self.retriever = None
        
        # 3. Force Garbage Collection
        gc.collect()
        #print("✨ RAM Cleared.")