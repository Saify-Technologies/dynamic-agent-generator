from smolagents import tool
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
import json

@tool(
    name="search_huggingface_spaces",
    description="Search for Hugging Face Spaces using DuckDuckGo",
    inputs={
        "query": {
            "type": "string",
            "description": "Search query for the type of Space needed"
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum number of results to return",
            "nullable": True,
            "default": 5
        }
    },
    output_type="string"
)
def search_huggingface_spaces(query: str, max_results: Optional[int] = 5) -> str:
    """
    Search for Hugging Face Spaces using DuckDuckGo
    
    Args:
        query: Search query for the type of Space needed
        max_results: Maximum number of results to return
    
    Returns:
        str: JSON string containing list of space information
    """
    search_url = f"https://duckduckgo.com/html/?q=site:huggingface.co/spaces {query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = []
    for result in soup.select('.result')[:max_results]:
        link = result.find('a', class_='result__a')
        if not link:
            continue
            
        url = link['href']
        # Extract space_id from URL
        space_match = re.search(r'spaces/([^/]+/[^/]+)', url)
        if not space_match:
            continue
            
        space_id = space_match.group(1)
        title = link.text.strip()
        description = result.find('a', class_='result__snippet')
        description = description.text.strip() if description else ""
        
        results.append({
            'space_id': space_id,
            'title': title,
            'description': description,
            'url': f"https://huggingface.co/spaces/{space_id}"
        })
    
    return json.dumps(results)

@tool(
    name="validate_space",
    description="Validate if a Hugging Face Space exists and is accessible",
    inputs={
        "space_id": {
            "type": "string",
            "description": "The Hugging Face Space ID to validate"
        }
    },
    output_type="string"
)
def validate_space(space_id: str) -> str:
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