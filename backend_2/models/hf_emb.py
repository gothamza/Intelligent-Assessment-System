
# Set this before importing HuggingFaceEmbeddings or running your code
# os.environ["HF_HOME"] = r"C:\path\to\your\huggingface"

from langchain_huggingface import HuggingFaceEmbeddings

# hf_embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

hf_embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# class HFEmbeddings:
#     def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
#         self.embedder = HuggingFaceEmbeddings(model_name=model_name)

#     def embed_documents(self, texts):
#         # texts: List[str]
#         return self.embedder.embed_documents(texts)

#     def embed_query(self, text):
#         # text: str
#         return self.embedder.embed_query(text)