from smolagents import Tool, CodeAgent, HfApiModel
import os
import json
from typing import Optional, Dict, Any, Union
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
        # Model will be set when the tool is initialized by AgentGenerator

    def _validate_io_types(self, input_types: Dict, output_type: str) -> Dict[str, Any]:
        """Validate and normalize input/output types according to smolagents specifications"""
        valid_types = {
            # Basic types that behave as normal Python types
            "AgentText": "AgentText",  # Behaves as string
            "AgentImage": "AgentImage",  # Behaves as PIL.Image
            "AgentAudio": "AgentAudio",  # Audio type with samplerate
            
            # Python basic types
            "string": str,
            "int": int,
            "float": float,
            "bool": bool,
            "dict": dict,
            "list": list,
            "bytes": bytes,
            "NoneType": type(None)
        }

        # Validate output type
        if output_type not in valid_types:
            raise ValueError(f"Invalid output type: {output_type}. Must be one of {list(valid_types.keys())}")

        # Validate input types
        for param_name, param_spec in input_types.items():
            if "type" not in param_spec:
                raise ValueError(f"Input parameter {param_name} must specify a type")
            
            param_type = param_spec["type"]
            if param_type not in valid_types:
                raise ValueError(f"Invalid type for parameter {param_name}: {param_type}")
            
            # Add type validation code to the spec
            if param_type.startswith("Agent"):
                # For Agent types, we need to import from smolagents
                param_spec["validation"] = f"isinstance(value, smolagents.{param_type})"
            else:
                # For basic Python types
                param_spec["validation"] = f"isinstance(value, {valid_types[param_type].__name__})"
            
            # Add default value handling if specified
            if "default" in param_spec:
                if not isinstance(param_spec["default"], valid_types[param_type]):
                    raise ValueError(f"Default value for {param_name} must be of type {param_type}")

        return {
            "input_types": input_types,
            "output_type": output_type,
            "validation_code": self._generate_validation_code(input_types)
        }

    def _generate_validation_code(self, input_types: Dict) -> str:
        """Generate input validation code"""
        validation_code = []
        for param_name, param_spec in input_types.items():
            required = not param_spec.get("nullable", False)
            type_check = param_spec["validation"]
            
            if required:
                validation_code.append(f"""
            if "{param_name}" not in kwargs:
                raise ValueError("Required parameter {param_name} is missing")
            value = kwargs["{param_name}"]
            if value is not None and not {type_check}:
                raise TypeError("Parameter {param_name} must be of type {param_spec['type']}")
                """)
            else:
                validation_code.append(f"""
            if "{param_name}" in kwargs and kwargs["{param_name}"] is not None:
                value = kwargs["{param_name}"]
                if not {type_check}:
                    raise TypeError("Parameter {param_name} must be of type {param_spec['type']}")
                """)
        
        return "\n".join(validation_code)

    def _generate_tool_code(self, tool_name: str, description: str, inputs: Dict, output_type: str = "string", requirements: str = "") -> str:
        """Generate the tool class code with implementation based on requirements"""
        
        # Validate and normalize input/output types
        io_spec = self._validate_io_types(inputs, output_type)
        
        # Generate implementation code based on requirements
        implementation_code = self._generate_implementation(requirements, output_type)
        
        return f'''
from smolagents import Tool
from typing import Optional, Dict, Any, Union
import json

class {tool_name}Tool(Tool):
    """{description}"""
    
    name = "{tool_name.lower()}"
    description = "{description}"
    inputs = {json.dumps(io_spec["input_types"], indent=4)}
    output_type = "{output_type}"

    def setup(self):
        """Initialize any expensive operations"""
        {implementation_code.get('setup', '# No setup required\npass')}

    def forward(self, **kwargs) -> {output_type}:
        """
        Implement the tool's functionality
        
        Args:
            **kwargs: Input parameters as defined in inputs
        
        Returns:
            {output_type}: Results in the specified format
        
        Raises:
            ValueError: If required parameters are missing
            TypeError: If parameters are of wrong type
        """
        try:
            # Validate inputs
            {io_spec["validation_code"]}
            
            # Implementation
            {implementation_code.get('forward', '# Default implementation\nreturn json.dumps({"status": "success"})')}
            
        except Exception as e:
            return json.dumps({{"status": "error", "error": str(e)}})

    @classmethod
    def from_hub(cls, repo_id: str, token: Optional[str] = None, **kwargs):
        """Optional: Add Hub integration"""
        {implementation_code.get('from_hub', 'pass')}

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
            
            # Generate and format the tool code - Pass requirements here
            tool_code = self._generate_tool_code(
                tool_name=tool_name,
                description=requirements,
                inputs=input_types,
                output_type=output_type,
                requirements=requirements  # Add this line to pass requirements
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

    def _generate_implementation(self, requirements: str, output_type: str) -> Dict[str, str]:
        """Generate implementation code based on requirements"""
        implementation_prompt = f"""
        Generate implementation code for a tool with these requirements:
        {requirements}
        
        Output type: {output_type}
        
        The implementation should include:
        1. Any necessary setup code
        2. The main forward() implementation
        3. Optional from_hub() implementation if needed
        
        Return a JSON object with these sections:
        {{
            "setup": "setup code here",
            "forward": "forward implementation here",
            "from_hub": "hub integration code if needed"
        }}
        
        Guidelines:
        - Include proper error handling
        - Follow best practices for the output_type
        - Add relevant comments
        - Import required packages
        """
        
        try:
            # Use the agent to generate implementation using the model from AgentGenerator
            agent = CodeAgent(
                model=self.model,  # This will be the model passed from AgentGenerator
                max_steps=5,
                additional_authorized_imports=[
                    "os", "json", "requests", "typing",
                    "torch", "transformers", "PIL", "numpy"
                ]
            )
            result = agent.run(implementation_prompt)
            return json.loads(result)
            
        except Exception as e:
            print(f"Failed to generate implementation: {str(e)}")
            # Return default implementation if generation fails
            return {
                "setup": "pass",
                "forward": '# TODO: Implement based on requirements\nreturn json.dumps({"status": "not_implemented"})',
                "from_hub": "pass"
            }

# Create instance of the tool
generate_tool = ToolGenerator() 