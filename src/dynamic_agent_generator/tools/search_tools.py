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

    def _get_task_keywords(self, query: str) -> List[str]:
        """Get task-related keywords without model names"""
        # First, search for general task information
        duckduckgo = DuckDuckGoSearchTool()
        try:
            # Search for task-related terms rather than specific models
            search_results = json.loads(duckduckgo.run(f"what is {query} task application use cases"))
            
            # Categories of terms to extract
            categories = {
                'tasks': set(),  # e.g., "translation", "generation", "detection"
                'domains': set(),  # e.g., "image", "text", "audio"
                'applications': set(),  # e.g., "web app", "api", "interface"
                'features': set()  # e.g., "real-time", "batch processing"
            }
            
            for result in search_results['results']:
                text = f"{result['title']} {result['snippet']}".lower()
                
                # Extract task-related terms
                if "task" in text or "application" in text or "use case" in text:
                    # Find noun phrases that describe tasks
                    task_terms = re.findall(r'\b\w+(?:\s+\w+){0,2}\b(?=\s+(?:task|application|processing|detection|generation|analysis))', text)
                    categories['tasks'].update(task_terms)
                
                # Extract domain-specific terms
                domain_indicators = ['image', 'text', 'audio', 'video', 'speech', 'data']
                for indicator in domain_indicators:
                    if indicator in text:
                        domain_terms = re.findall(f'{indicator}\\s*\\w+', text)
                        categories['domains'].update(domain_terms)
                
                # Extract application types
                if "application" in text or "interface" in text:
                    app_terms = re.findall(r'\b\w+(?:\s+\w+)?\s+(?:application|interface|app|api)\b', text)
                    categories['applications'].update(app_terms)
                
                # Extract feature-related terms
                feature_terms = re.findall(r'\b(?:real-time|online|batch|interactive|automated)\s+\w+\b', text)
                categories['features'].update(feature_terms)
            
            # Combine all relevant terms
            all_terms = set()
            for terms in categories.values():
                all_terms.update(terms)
            
            # Remove common words and very short terms
            common_words = {'the', 'and', 'or', 'but', 'for', 'with', 'in', 'on', 'at', 'to', 'of'}
            filtered_terms = {term for term in all_terms if len(term) > 2 and term not in common_words}
            
            return list(filtered_terms)
            
        except Exception:
            # Fallback to basic task extraction
            return [term.strip() for term in query.split() if len(term.strip()) > 2]

    def forward(self, query: str, max_results: Optional[int] = 5, require_gradio: Optional[bool] = None) -> str:
        """
        Search for Hugging Face Spaces with task-focused approach
        
        Args:
            query: Search query for the type of Space needed
            max_results: Maximum number of results to return
            require_gradio: Whether to require Gradio interface
        """
        # Get task-related keywords
        task_keywords = self._get_task_keywords(query)
        
        # Build search variations
        search_variations = []
        
        # Add task-focused searches
        for keyword in task_keywords:
            # Search for functionality rather than specific models
            search_variations.extend([
                f"{keyword} demo",
                f"{keyword} application",
                f"{keyword} interface",
                f"interactive {keyword}"
            ])
        
        # Add domain-specific searches
        if any(domain in query.lower() for domain in ['image', 'text', 'audio', 'video']):
            for domain in ['image', 'text', 'audio', 'video']:
                if domain in query.lower():
                    search_variations.extend([
                        f"{domain} {kw}" for kw in task_keywords
                    ])
        
        # Add the original query as fallback
        search_variations.append(query)
        
        # If Gradio is required, add Gradio-specific searches
        if require_gradio:
            gradio_variations = [f"{q} gradio" for q in search_variations]
            search_variations.extend(gradio_variations)
        
        # Deduplicate search variations
        search_variations = list(set(search_variations))
        
        # Search and collect results
        all_results = []
        found_spaces = set()
        
        for search_query in search_variations:
            search_url = f"https://duckduckgo.com/html/?q=site:huggingface.co/spaces {search_query}"
            
            try:
                response = requests.get(
                    search_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
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
                    if space_id in found_spaces:
                        continue
                    
                    # Validate space if needed
                    if require_gradio:
                        validation = self._validate_space(space_id)
                        if not validation.get('is_gradio', False):
                            continue
                    
                    title = link.text.strip()
                    description = result.find('a', class_='result__snippet')
                    description = description.text.strip() if description else ""
                    
                    # Calculate relevance score based on matched keywords
                    matched_keywords = [
                        kw for kw in task_keywords 
                        if kw.lower() in f"{title} {description}".lower()
                    ]
                    
                    space_info = {
                        'space_id': space_id,
                        'title': title,
                        'description': description,
                        'url': f"https://huggingface.co/spaces/{space_id}",
                        'matched_keywords': matched_keywords,
                        'relevance_score': len(matched_keywords)
                    }
                    
                    all_results.append(space_info)
                    found_spaces.add(space_id)
                    
            except Exception as e:
                continue
        
        # Sort results by relevance score
        all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return json.dumps({
            'status': 'success',
            'query': query,
            'task_keywords': task_keywords,
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