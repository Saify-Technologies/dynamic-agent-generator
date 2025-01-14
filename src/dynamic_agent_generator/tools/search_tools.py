from smolagents import Tool
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
import json

class HuggingFaceSpaceSearchTool(Tool):
    """Tool for searching Hugging Face Spaces"""
    
    name = "search_huggingface_spaces"
    description = "Search for Hugging Face Spaces with intelligent query expansion"
    inputs = {
        "query": {
            "type": "string",
            "description": "Search query for the type of Space needed"
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum number of results to return",
            "nullable": True,
            "default": 5
        },
        "require_gradio": {
            "type": "boolean",
            "description": "Whether to require Gradio interface",
            "nullable": True,
            "default": False
        }
    }
    output_type = "string"

    def _expand_search_terms(self, query: str) -> List[str]:
        """Expand search terms using web search"""
        duckduckgo = DuckDuckGoSearchTool()
        try:
            # Search for related technical terms
            search_results = json.loads(duckduckgo.run(f"technical terms for {query} AI ML tools"))
            
            if search_results['status'] != 'success':
                return [query]
                
            # Extract keywords from search results
            keywords = set()
            for result in search_results['results']:
                # Extract words that might be technical terms
                text = f"{result['title']} {result['snippet']}"
                # Find technical terms using common patterns
                technical_terms = re.findall(r'\b[A-Za-z]+(?:\s*[A-Za-z]+)*(?:\d*\.?\d+)?\b', text)
                keywords.update(term.lower() for term in technical_terms if len(term) > 2)
            
            # Remove common words
            common_words = {'the', 'and', 'or', 'but', 'for', 'with', 'in', 'on', 'at', 'to', 'of'}
            keywords = keywords - common_words
            
            return list(keywords)
        except Exception:
            return [query]

    def _is_ai_task(self, query: str, keywords: List[str]) -> bool:
        """Check if the query is related to AI/ML tasks using expanded context"""
        # Base AI/ML indicators
        base_indicators = {
            'model', 'inference', 'prediction', 'generation', 'classification',
            'detection', 'recognition', 'ai', 'ml', 'deep learning', 'machine learning'
        }
        
        # Check if any of the expanded keywords match known AI tasks
        combined_terms = set(keywords) | {query.lower()}
        return bool(combined_terms & base_indicators)

    def forward(self, query: str, max_results: Optional[int] = 5, require_gradio: Optional[bool] = None) -> str:
        """
        Search for Hugging Face Spaces with intelligent query expansion
        
        Args:
            query: Search query for the type of Space needed
            max_results: Maximum number of results to return
            require_gradio: Whether to require Gradio interface. If None, auto-detect based on task.
        
        Returns:
            str: JSON string containing list of space information
        """
        # Expand search terms
        expanded_terms = self._expand_search_terms(query)
        
        # Auto-detect if Gradio should be required
        if require_gradio is None:
            require_gradio = self._is_ai_task(query, expanded_terms)
        
        # Build search queries
        search_queries = []
        base_query = query.strip()
        
        # Add the original query
        search_queries.append(base_query)
        
        # Add expanded terms combinations
        for term in expanded_terms:
            if term != base_query:
                search_queries.append(f"{base_query} {term}")
        
        if require_gradio:
            search_queries.extend([f"{q} gradio" for q in search_queries])
        
        # Search with all queries
        all_results = []
        found_spaces = set()  # Track unique spaces
        
        for search_query in search_queries:
            search_url = f"https://duckduckgo.com/html/?q=site:huggingface.co/spaces {search_query}"
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(search_url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for result in soup.select('.result'):
                    if len(all_results) >= max_results:
                        break
                        
                    link = result.find('a', class_='result__a')
                    if not link:
                        continue
                    
                    url = link['href']
                    space_match = re.search(r'spaces/([^/]+/[^/]+)', url)
                    if not space_match:
                        continue
                    
                    space_id = space_match.group(1)
                    
                    # Skip if we've already found this space
                    if space_id in found_spaces:
                        continue
                    
                    # Validate if needed
                    if require_gradio:
                        validation = self._validate_space(space_id)
                        if not validation.get('is_gradio', False):
                            continue
                    
                    title = link.text.strip()
                    description = result.find('a', class_='result__snippet')
                    description = description.text.strip() if description else ""
                    
                    space_info = {
                        'space_id': space_id,
                        'title': title,
                        'description': description,
                        'url': f"https://huggingface.co/spaces/{space_id}",
                        'requires_gradio': require_gradio,
                        'matched_terms': [term for term in expanded_terms if term.lower() in f"{title} {description}".lower()]
                    }
                    
                    all_results.append(space_info)
                    found_spaces.add(space_id)
                    
            except Exception as e:
                continue
        
        # Sort results by relevance (number of matched terms)
        all_results.sort(key=lambda x: len(x['matched_terms']), reverse=True)
        
        return json.dumps({
            'status': 'success',
            'query': query,
            'expanded_terms': expanded_terms,
            'results': all_results[:max_results]
        })

    def _validate_space(self, space_id: str) -> Dict:
        """Internal validation of a space"""
        url = f"https://huggingface.co/spaces/{space_id}"
        try:
            response = requests.get(url)
            return {
                'exists': response.status_code == 200,
                'is_gradio': 'gradio' in response.text.lower() if response.status_code == 200 else False,
                'is_accessible': response.status_code == 200
            }
        except Exception:
            return {
                'exists': False,
                'is_gradio': False,
                'is_accessible': False
            }

class SpaceValidatorTool(Tool):
    """Tool for validating Hugging Face Spaces"""
    
    name = "validate_space"
    description = "Validate if a Hugging Face Space exists and is accessible"
    inputs = {
        "space_id": {
            "type": "string",
            "description": "The Hugging Face Space ID to validate"
        }
    }
    output_type = "string"

    def forward(self, space_id: str) -> str:
        """
        Validate if a Hugging Face Space exists and is accessible
        
        Args:
            space_id: The Hugging Face Space ID to validate
        
        Returns:
            str: JSON string with validation results
        """
        url = f"https://huggingface.co/spaces/{space_id}"
        response = requests.get(url)
        
        results = {
            'exists': response.status_code == 200,
            'is_gradio': 'gradio' in response.text.lower() if response.status_code == 200 else False,
            'is_accessible': response.status_code == 200
        }
        
        return json.dumps(results)

class DuckDuckGoSearchTool(Tool):
    """Tool for performing web searches using DuckDuckGo"""
    
    name = "duckduckgo_search"
    description = "Search the web using DuckDuckGo and return relevant results"
    inputs = {
        "query": {
            "type": "string",
            "description": "Search query"
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum number of results to return",
            "nullable": True,
            "default": 5
        }
    }
    output_type = "string"

    def forward(self, query: str, max_results: Optional[int] = 5) -> str:
        """
        Perform a web search using DuckDuckGo
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
        
        Returns:
            str: JSON string containing search results
        """
        search_url = f"https://duckduckgo.com/html/?q={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.select('.result')[:max_results]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem:
                    result_info = {
                        'title': title_elem.text.strip(),
                        'url': title_elem['href'],
                        'snippet': snippet_elem.text.strip() if snippet_elem else ""
                    }
                    results.append(result_info)
            
            return json.dumps({
                'status': 'success',
                'results': results
            })
            
        except Exception as e:
            return json.dumps({
                'status': 'error',
                'error': str(e)
            })

# Create instances of the tools
duckduckgo_search = DuckDuckGoSearchTool()
search_huggingface_spaces = HuggingFaceSpaceSearchTool()
validate_space = SpaceValidatorTool() 