from smolagents import tool
import os
import black

@tool
def generate_tool(name: str, description: str, inputs: dict, output_type: str, implementation: str) -> str:
    """
    Generates a new tool file compatible with CodeAgent
    
    Args:
        name: Name of the tool
        description: Description of what the tool does
        inputs: Dictionary of input parameters and their types/descriptions
        output_type: Return type of the tool
        implementation: Python code for the tool
    """
    template = f'''
from smolagents import tool

@tool
def {name}({", ".join(inputs.keys())}) -> {output_type}:
    """{description}
    
    Args:
        {chr(10).join(f"{k}: {v['description']}" for k,v in inputs.items())}
    Returns:
        {output_type}: Description of the return value
    """
    {implementation}
    '''
    
    # Format code with black
    formatted_code = black.format_str(template, mode=black.FileMode())
    
    # Create tools directory if it doesn't exist
    os.makedirs("generated_tools", exist_ok=True)
    
    # Save tool file
    tool_path = f"generated_tools/{name}.py"
    with open(tool_path, "w") as f:
        f.write(formatted_code)
        
    return f"Tool generated at {tool_path}" 