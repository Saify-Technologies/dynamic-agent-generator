from smolagents import Tool
import os
import json
from typing import Optional, Dict, Any
import black

class ToolGenerator(Tool):
    """Tool for generating custom tools based on requirements"""
    
    name = "generate_tool"
    description = """Generate a custom tool that follows smolagents.Tool specifications.
    Handles proper class structure, input/output types, and file organization."""
    
    inputs = {
        "requirements": {
            "type": "string",
            "description": "Natural language description of the tool's requirements"
        },
        "tool_name": {
            "type": "string",
            "description": "Name for the tool (will be converted to PascalCase)"
        },
        "output_dir": {
            "type": "string",
            "description": "Directory where the tool should be saved"
        },
        "input_types": {
            "type": "object",
            "description": "Dictionary of input parameter specifications",
            "nullable": True
        },
        "output_type": {
            "type": "string",
            "description": "Output type of the tool (e.g., 'string', 'AgentImage')",
            "nullable": True,
            "default": "string"
        }
    }
    output_type = "string"  # Returns JSON string with generation results

    def setup(self):
        """Initialize black formatter and ensure templates are ready"""
        self.mode = black.FileMode()
        # Could add more setup if needed

    def _generate_tool_code(self, tool_name: str, description: str, inputs: Dict, output_type: str = "string") -> str:
        """Generate the tool class code following smolagents.Tool specifications"""
        return f'''
from smolagents import Tool
from typing import Optional, Dict, Any
import json

class {tool_name}Tool(Tool):
    """{description}"""
    
    name = "{tool_name.lower()}"
    description = "{description}"
    inputs = {json.dumps(inputs, indent=4)}
    output_type = "{output_type}"

    def setup(self):
        """Initialize any expensive operations"""
        # Add initialization code here if needed
        pass

    def forward(self, **kwargs) -> {output_type}:
        """
        Implement the tool's functionality
        
        Args:
            **kwargs: Input parameters as defined in inputs
        
        Returns:
            {output_type}: Results in the specified format
        """
        try:
            # Tool implementation here
            results = {{"status": "success", "message": "Tool executed successfully"}}
            
            # Convert result based on output_type
            if self.output_type == "string":
                return json.dumps(results)
            elif self.output_type == "AgentImage":
                # Handle image output
                pass
            elif self.output_type == "AgentAudio":
                # Handle audio output
                pass
            else:
                return json.dumps(results)
            
        except Exception as e:
            return json.dumps({{"status": "error", "error": str(e)}})

    @classmethod
    def from_hub(cls, repo_id: str, token: Optional[str] = None, **kwargs):
        """Optional: Add Hub integration"""
        pass

# Create instance of the tool
{tool_name.lower()} = {tool_name}Tool()
'''

    def _format_code(self, code: str) -> str:
        """Format the code using black"""
        try:
            return black.format_str(code, mode=self.mode)
        except:
            return code

    def forward(
        self,
        requirements: str,
        tool_name: str,
        output_dir: str,
        input_types: Optional[Dict] = None,
        output_type: Optional[str] = "string"
    ) -> str:
        """
        Generate a custom tool based on requirements
        
        Args:
            requirements: Natural language description of the tool's requirements
            tool_name: Name for the tool
            output_dir: Directory where the tool should be saved
            input_types: Optional dictionary of input specifications
            output_type: Optional output type specification
        
        Returns:
            str: JSON string with generation results
        """
        try:
            # Ensure proper tool name format
            tool_name = "".join(x.capitalize() for x in tool_name.split("_"))
            
            # Get the agent name from the output path
            agent_name = os.path.basename(output_dir)
            
            # Build the complete path structure
            agent_dir = os.path.join(output_dir, agent_name)
            tools_dir = os.path.join(agent_dir, "src", "tools")
            os.makedirs(tools_dir, exist_ok=True)
            
            # Use provided input types or create default
            if not input_types:
                input_types = {
                    "input": {
                        "type": "string",
                        "description": "Primary input for the tool"
                    },
                    "options": {
                        "type": "object",
                        "description": "Optional configuration parameters",
                        "nullable": True
                    }
                }
            
            # Generate and format the tool code
            tool_code = self._generate_tool_code(
                tool_name=tool_name,
                description=requirements,
                inputs=input_types,
                output_type=output_type
            )
            formatted_code = self._format_code(tool_code)
            
            # Save the tool file in the correct location
            tool_file = os.path.join(tools_dir, f"{tool_name.lower()}.py")
            with open(tool_file, "w") as f:
                f.write(formatted_code)
            
            # Update __init__.py in the tools directory
            init_file = os.path.join(tools_dir, "__init__.py")
            init_content = f"from .{tool_name.lower()} import {tool_name.lower()}\n"
            
            mode = "a" if os.path.exists(init_file) else "w"
            with open(init_file, mode) as f:
                f.write(init_content)
            
            return json.dumps({
                "status": "success",
                "message": f"Tool {tool_name} generated successfully",
                "tool_path": tool_file,
                "tool_name": tool_name,
                "output_type": output_type,
                "agent_dir": agent_dir
            })
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            })

# Create instance of the tool
generate_tool = ToolGenerator() 