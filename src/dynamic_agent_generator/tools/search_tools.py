from smolagents import Tool
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
import re
import json

class HuggingFaceSpaceSearchTool(Tool):
    """Tool for searching Hugging Face Spaces"""
    
    name = "search_huggingface_spaces"
    description = "Search for Hugging Face Spaces using HF search and web research"
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
        "sort_by": {
            "type": "string",
            "description": "Sort method (trending, created, modified, likes)",
            "nullable": True,
            "default": "trending",
            "enum": ["trending", "created", "modified", "likes"]  # Valid HF sort options
        }
    }
    output_type = "string"

    def _get_search_terms(self, query: str) -> List[str]:
        """Get intelligent search terms using web research"""
        duckduckgo = DuckDuckGoSearchTool()
        search_terms = set()
        
        try:
            # Search for related technical terms and tools
            search_results = json.loads(duckduckgo.run(
                f"popular tools libraries frameworks for {query}"
            ))
            
            for result in search_results['results']:
                text = f"{result['title']} {result['snippet']}".lower()
                
                # Extract technical terms
                tech_terms = re.findall(r'\b[A-Za-z][A-Za-z0-9-]+(?:\s+[A-Za-z][A-Za-z0-9-]+){0,2}\b', text)
                search_terms.update(tech_terms)
                
                # Extract library/framework names
                lib_terms = re.findall(r'\b[A-Za-z][A-Za-z0-9-]*(?:\.[A-Za-z][A-Za-z0-9-]*)*\b', text)
                search_terms.update(lib_terms)
            
            # Clean up terms
            search_terms = {
                term.strip() for term in search_terms 
                if len(term.strip()) > 2 and not term.strip().lower() in {
                    'the', 'and', 'for', 'with', 'using', 'from', 'that', 'this'
                }
            }
            
            # Always include the original query terms
            search_terms.update(query.split())
            
            return list(search_terms)
            
        except Exception:
            return query.split()

    def _get_trending_context(self, query: str) -> Dict[str, Any]:
        """Get trending/popular names and terms related to the query"""
        duckduckgo = DuckDuckGoSearchTool()
        trending_info = {
            'popular_names': set(),
            'common_implementations': set(),
            'trending_terms': set()
        }
        
        try:
            # Search for trending/popular implementations
            search_results = json.loads(duckduckgo.run(
                f"most popular {query} models implementations trending github huggingface"
            ))
            
            for result in search_results['results']:
                text = f"{result['title']} {result['snippet']}".lower()
                
                # Look for popularity indicators
                popularity_patterns = [
                    r'popular (\w+(?:[- ]\w+)*)',
                    r'trending (\w+(?:[- ]\w+)*)',
                    r'widely used (\w+(?:[- ]\w+)*)',
                    r'(\w+(?:[- ]\w+)*) is popular',
                    r'(\w+(?:[- ]\w+)*) implementation'
                ]
                
                for pattern in popularity_patterns:
                    matches = re.findall(pattern, text)
                    trending_info['popular_names'].update(matches)
                
                # Look for specific implementation mentions
                if 'implementation' in text or 'based on' in text:
                    implementations = re.findall(r'(?:using|with|based on) (\w+(?:[- ]\w+)*)', text)
                    trending_info['common_implementations'].update(implementations)
                
                # Extract trending terms
                if any(word in text for word in ['trending', 'popular', 'latest', 'new']):
                    terms = re.findall(r'\b\w+(?:-\w+)*\b', text)
                    trending_info['trending_terms'].update(terms)
            
            # Clean up the sets
            for key in trending_info:
                trending_info[key] = {
                    term.strip() for term in trending_info[key]
                    if len(term.strip()) > 2 and not term.strip().lower() in {
                        'the', 'and', 'for', 'with', 'using', 'from', 'that', 'this'
                    }
                }
            
            return trending_info
            
        except Exception:
            return {
                'popular_names': set(),
                'common_implementations': set(),
                'trending_terms': set()
            }

    def forward(
        self, 
        query: str, 
        max_results: Optional[int] = 5,
        sort_by: Optional[str] = "trending"
    ) -> str:
        """
        Search for Hugging Face Spaces
        
        Args:
            query: Search query for the type of Space needed
            max_results: Maximum number of results to return
            sort_by: Sort method (trending, created, modified, likes)
        """
        # Validate sort_by parameter
        valid_sort_options = ["trending", "created", "modified", "likes"]
        if sort_by not in valid_sort_options:
            sort_by = "trending"  # Default to trending if invalid option provided
        
        # Get both search terms and trending context
        search_terms = self._get_search_terms(query)
        trending_context = self._get_trending_context(query)
        
        all_results = []
        found_spaces = set()
        
        # Build search variations including trending terms
        search_variations = [
            " ".join(terms) for terms in [
                search_terms,  # All terms
                trending_context['popular_names'],  # Popular model names
                trending_context['common_implementations'],  # Common implementations
                search_terms[:2],  # First two terms
                [query],  # Original query
                trending_context['trending_terms'],  # Trending terms
                [term for term in search_terms if len(term) > 3]  # Longer terms only
            ] if terms
        ]
        
        # Add combinations of popular names with task terms
        for popular_name in trending_context['popular_names']:
            for term in search_terms:
                search_variations.append(f"{popular_name} {term}")
        
        # Deduplicate and clean search variations
        search_variations = list(set(
            variation.strip() 
            for variation in search_variations 
            if variation.strip()
        ))
        
        for search_query in search_variations:
            try:
                # Use HF's space search URL with correct sort parameter
                search_url = f"https://huggingface.co/api/spaces?search={search_query}&sort={sort_by}&limit={max_results}"
                response = requests.get(search_url)
                
                if response.status_code == 200:
                    spaces = response.json()
                    
                    for space in spaces:
                        space_id = f"{space['owner']}/{space['id']}"
                        
                        if space_id in found_spaces:
                            continue
                            
                        # Calculate trending score
                        trending_score = 0
                        space_text = f"{space['title']} {space.get('description', '')}".lower()
                        
                        # Add points for matching trending terms
                        for term in trending_context['popular_names']:
                            if term.lower() in space_text:
                                trending_score += 3  # Higher weight for popular names
                        
                        for term in trending_context['common_implementations']:
                            if term.lower() in space_text:
                                trending_score += 2  # Medium weight for common implementations
                        
                        for term in trending_context['trending_terms']:
                            if term.lower() in space_text:
                                trending_score += 1  # Lower weight for general trending terms
                        
                        # Extract relevant information
                        space_info = {
                            'space_id': space_id,
                            'title': space['title'],
                            'description': space.get('description', ''),
                            'url': f"https://huggingface.co/spaces/{space_id}",
                            'likes': space.get('likes', 0),
                            'downloads': space.get('downloads', 0),
                            'last_modified': space.get('lastModified', ''),
                            'sdk': space.get('sdk', ''),
                            'verified': space.get('verified', False),
                            'matched_terms': [
                                term for term in search_terms 
                                if term.lower() in space_text
                            ],
                            'trending_score': trending_score,
                            'matches_popular_name': any(
                                name.lower() in space_text 
                                for name in trending_context['popular_names']
                            )
                        }
                        
                        all_results.append(space_info)
                        found_spaces.add(space_id)
                        
                        if len(all_results) >= max_results:
                            break
                            
            except Exception as e:
                continue
                
            if len(all_results) >= max_results:
                break
        
        # Sort results by a combination of factors
        all_results.sort(
            key=lambda x: (
                x['trending_score'],  # First by trending score
                len(x['matched_terms']),  # Then by term matches
                x['likes'],  # Then by likes
                x['matches_popular_name']  # Finally by popular name matches
            ), 
            reverse=True
        )
        
        return json.dumps({
            'status': 'success',
            'query': query,
            'search_terms': search_terms,
            'trending_context': {
                'popular_names': list(trending_context['popular_names']),
                'common_implementations': list(trending_context['common_implementations']),
                'trending_terms': list(trending_context['trending_terms'])
            },
            'results': all_results[:max_results]
        })

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