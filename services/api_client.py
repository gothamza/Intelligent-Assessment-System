import requests
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    """Client for communicating with the FastAPI backend"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        if not self.base_url.startswith("http"):
            self.base_url = f"http://{self.base_url}"
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to backend"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def chat(
        self,
        message: str,
        context: Dict[str, Any],
        chat_history: Optional[List[Dict]] = None,
        use_rag: bool = True
    ) -> Dict[str, Any]:
        """Send chat message to backend"""
        return self._make_request(
            "POST",
            "/api/tutor/chat",
            json={
                "message": message,
                "context": context,
                "chat_history": chat_history or [],
                "use_rag": use_rag
            }
        )
    
    def generate_question(self, context: Dict[str, Any]) -> str:
        """Generate a math question"""
        response = self._make_request(
            "POST",
            "/api/tutor/generate-question",
            json={"context": context}
        )
        return response["question"]
    
    def generate_hint(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a hint for a question"""
        response = self._make_request(
            "POST",
            "/api/tutor/generate-hint",
            json={"question": question, "context": context or {}}
        )
        return response["hint"]
    
    def generate_exercise(self, context: Dict[str, Any]) -> str:
        """Generate an exercise with solution"""
        response = self._make_request(
            "POST",
            "/api/tutor/generate-exercise",
            json={"context": context}
        )
        return response["exercise"]
    
    def generate_course(self, context: Dict[str, Any]) -> str:
        """Generate a complete course"""
        response = self._make_request(
            "POST",
            "/api/tutor/generate-course",
            json={"context": context}
        )
        return response["course"]
    
    def classify_answer(self, question: str, answer: str) -> Dict[str, Any]:
        """Classify answer quality"""
        return self._make_request(
            "POST",
            "/api/tutor/classify-answer",
            json={"question": question, "answer": answer}
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        return self._make_request("GET", "/api/stats/stats")
    
    def reset_stats(self) -> Dict[str, Any]:
        """Reset statistics"""
        return self._make_request("POST", "/api/stats/reset")
    
    def update_stats(self, classification: str) -> Dict[str, Any]:
        """Update statistics"""
        return self._make_request(
            "POST",
            "/api/stats/update",
            params={"classification": classification}
        )
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return self._make_request("GET", "/health")
    
    def list_documents(self) -> Dict[str, Any]:
        """List all uploaded documents"""
        return self._make_request("GET", "/api/documents/list")
    
    def upload_document(self, file, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Upload a document
        
        Args:
            file: Can be a file path (str), file-like object, or Streamlit UploadedFile
            metadata: Optional metadata dict
        """
        # Handle file path string
        if isinstance(file, str):
            with open(file, 'rb') as f:
                file_content = f.read()
                file_tuple = (os.path.basename(file), file_content, 'application/octet-stream')
                files = {"file": file_tuple}
                data = metadata or {}
                url = f"{self.base_url}/api/documents/upload"
                response = requests.post(url, files=files, data=data, timeout=300)
                response.raise_for_status()
                return response.json()
        # Handle Streamlit UploadedFile (has getvalue method)
        elif hasattr(file, 'getvalue'):
            # Streamlit UploadedFile - use getvalue() which is the recommended method
            file_tuple = (file.name, file.getvalue(), file.type if hasattr(file, 'type') else 'application/octet-stream')
            files = {"file": file_tuple}
            data = metadata or {}
            url = f"{self.base_url}/api/documents/upload"
            response = requests.post(url, files=files, data=data, timeout=300)  # 5 min timeout
            response.raise_for_status()
            return response.json()
        # Handle file-like object with read method
        elif hasattr(file, 'read'):
            # Regular file-like object
            file.seek(0)  # Reset to beginning
            file_content = file.read()
            file_name = getattr(file, 'name', 'uploaded_file')
            file_type = getattr(file, 'type', 'application/octet-stream')
            file_tuple = (file_name, file_content, file_type)
            files = {"file": file_tuple}
            data = metadata or {}
            url = f"{self.base_url}/api/documents/upload"
            response = requests.post(url, files=files, data=data, timeout=300)
            response.raise_for_status()
            return response.json()
        else:
            raise ValueError("file must be a path string, Streamlit UploadedFile, or file-like object")
    
    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete a document"""
        return self._make_request("DELETE", f"/api/documents/{doc_id}")
    
    def search_documents(self, query: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search documents"""
        return self._make_request(
            "POST",
            "/api/documents/search",
            json={"query": query, "filters": filters or {}}
        )

