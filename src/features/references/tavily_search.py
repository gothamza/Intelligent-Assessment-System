"""
Tavily API integration for finding study references and resources.
"""
import os
from typing import List, Dict, Optional
from tavily import TavilyClient


class TavilyReferenceSearcher:
    """Search for study references using Tavily API"""
    
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.client = None
        if self.api_key:
            try:
                self.client = TavilyClient(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Tavily client: {e}")
    
    def is_available(self) -> bool:
        """Check if Tavily API is available"""
        return self.client is not None and self.api_key is not None
    
    def search_study_references(self, subjects: List[str], grade_level: str, language: str = "fr") -> Dict[str, List[Dict]]:
        """
        Search for study references for given subjects and grade level
        
        Args:
            subjects: List of subjects to search for
            grade_level: Grade level (e.g., "7ème année")
            language: Language for search results (default: "fr")
            
        Returns:
            Dictionary with subjects as keys and list of references as values
        """
        if not self.is_available():
            return {}
        
        references = {}
        
        for subject in subjects:
            try:
                # Create search query
                query = f"cours {subject} {grade_level} mathématiques exercices corrigés"
                
                # Search with Tavily
                search_results = self.client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=5,
                    include_answer=False,
                    include_raw_content=False,
                    include_images=False
                )
                
                # Process results
                subject_references = []
                for result in search_results.get("results", []):
                    reference = {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", ""),
                        "score": result.get("score", 0)
                    }
                    subject_references.append(reference)
                
                references[subject] = subject_references
                
            except Exception as e:
                print(f"Error searching for {subject}: {e}")
                references[subject] = []
        
        return references
    
    def search_general_math_resources(self, grade_level: str, language: str = "fr") -> List[Dict]:
        """
        Search for general math resources for a grade level
        
        Args:
            grade_level: Grade level (e.g., "7ème année")
            language: Language for search results (default: "fr")
            
        Returns:
            List of general math resources
        """
        if not self.is_available():
            return []
        
        try:
            # Create search query for general math resources
            query = f"ressources mathématiques {grade_level} cours exercices corrigés"
            
            # Search with Tavily
            search_results = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=8,
                include_answer=False,
                include_raw_content=False,
                include_images=False
            )
            
            # Process results
            resources = []
            for result in search_results.get("results", []):
                resource = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", ""),
                    "score": result.get("score", 0)
                }
                resources.append(resource)
            
            return resources
            
        except Exception as e:
            print(f"Error searching for general math resources: {e}")
            return []


def get_study_references(subjects: List[str], grade_level: str) -> Dict[str, any]:
    """
    Get study references for subjects and grade level
    
    Args:
        subjects: List of subjects
        grade_level: Grade level
        
    Returns:
        Dictionary with references and general resources
    """
    searcher = TavilyReferenceSearcher()
    
    if not searcher.is_available():
        return {
            "available": False,
            "message": "🔑 Tavily API non configurée. Pour activer la recherche de références, ajoutez TAVILY_API_KEY à vos variables d'environnement. Obtenez votre clé sur: https://tavily.com/",
            "subject_references": {},
            "general_resources": []
        }
    
    # Search for subject-specific references
    subject_references = searcher.search_study_references(subjects, grade_level)
    
    # Search for general math resources
    general_resources = searcher.search_general_math_resources(grade_level)
    
    return {
        "available": True,
        "subject_references": subject_references,
        "general_resources": general_resources
    }
