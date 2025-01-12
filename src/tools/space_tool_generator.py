from smolagents import Tool

@tool
def generate_space_tool(space_id: str, name: str, description: str) -> Tool:
    """
    Generates a tool from a Hugging Face Space
    
    Args:
        space_id: The Hugging Face Space ID (e.g. "username/space-name")
        name: Name for the tool
        description: Description of what the tool does
    """
    return Tool.from_space(
        space_id=space_id,
        name=name,
        description=description
    ) 