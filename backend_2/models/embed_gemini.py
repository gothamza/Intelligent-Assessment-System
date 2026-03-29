import google.generativeai as genai

class GeminiEmbeddings:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = "models/embedding-001"  # or "gemini-embedding-exp-03-07"

    def embed_documents(self, texts):
        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="SEMANTIC_SIMILARITY"
            )
            embeddings.append(result["embedding"])
        return embeddings

    def embed_query(self, text):
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="SEMANTIC_SIMILARITY"
        )
        return result["embedding"]
