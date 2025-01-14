from smolagents import Tool
import os
import shutil
from typing import Dict, Optional, List
import json

class AgentStructureGenerator(Tool):
    """Tool for generating complete agent directory structure"""
    
    name = "generate_agent_structure"
    description = "Creates a complete agent directory structure with all necessary files and organization"
    inputs = {
        "agent_name": {
            "type": "string",
            "description": "Name of the agent"
        },
        "output_path": {
            "type": "string",
            "description": "Base output directory path"
        },
        "tools_config": {
            "type": "string",
            "description": "JSON string containing tool configurations"
        },
        "agent_config": {
            "type": "string",
            "description": "JSON string containing agent configuration"
        },
        "requirements": {
            "type": "string",
            "description": "Comma-separated list of Python package requirements",
            "nullable": True
        }
    }
    output_type = "string"

    def _create_directory_structure(self, base_path: str) -> Dict[str, str]:
        """Creates the full directory structure for the agent"""
        directories = {
            'root': base_path,
            'src': os.path.join(base_path, 'src'),
            'tools': os.path.join(base_path, 'src', 'tools'),
            'tests': os.path.join(base_path, 'tests'),
            'examples': os.path.join(base_path, 'examples'),
            'docs': os.path.join(base_path, 'docs')
        }
        
        for path in directories.values():
            os.makedirs(path, exist_ok=True)
            
        return directories

    def _generate_tool_template(self, tool_name: str, description: str) -> str:
        """Generate a tool class template"""
        return f'''
from smolagents import Tool
from typing import Optional
import json

class {tool_name}Tool(Tool):
    """{{description}}"""
    
    name = "{tool_name.lower()}"
    description = "{{description}}"
    inputs = {{
        "input": {{
            "type": "string",
            "description": "Input description"
        }},
        "optional_param": {{
            "type": "string",
            "description": "Optional parameter",
            "nullable": True
        }}
    }}
    output_type = "string"

    def forward(self, input: str, optional_param: Optional[str] = None) -> str:
        """Tool implementation"""
        results = {{"result": "value"}}
        return json.dumps(results)

# Create instance of the tool
{tool_name.lower()} = {tool_name}Tool()
'''

    def _create_agent_file(self, agent_name: str, config: Dict, tools: List[Dict], path: str):
        """Creates the main agent file"""
        agent_content = f'''
from smolagents import CodeAgent, HfApiModel, DuckDuckGoSearchTool
from .tools import *
from typing import Optional
import os
import json

class {agent_name}Agent:
    """Generated agent for {agent_name}"""
    
    def __init__(self, hf_token: Optional[str] = None, max_steps: int = 20):
        self.model = HfApiModel(
            model_id="{config.get('model_id', 'meta-llama/Llama-2-70b-chat-hf')}",
            token=hf_token or os.getenv("HF_TOKEN")
        )
        
        # Initialize DuckDuckGoSearchTool
        self.search_tool = DuckDuckGoSearchTool()
        
        self.agent = CodeAgent(
            tools=[
                self.search_tool,  # Add search tool first
                {", ".join(f"{t['name'].lower()}" for t in tools)}
            ],
            model=self.model,
            max_steps=max_steps,
            system_prompt="""{config.get('system_prompt', '')}""",
            additional_authorized_imports=[
                "os", "json", "typing", "smolagents", "requests"
            ] + {config.get('imports', [])}
        )
    
    def run(self, prompt: str, custom_max_steps: Optional[int] = None) -> str:
        """Run the agent with the given prompt"""
        try:
            if custom_max_steps is not None:
                temp_agent = CodeAgent(
                    tools=self.agent.tools,
                    model=self.model,
                    max_steps=custom_max_steps,
                    system_prompt=self.agent._system_prompt,
                    additional_authorized_imports=self.agent._additional_authorized_imports
                )
                result = temp_agent.run(prompt)
            else:
                result = self.agent.run(prompt)
            return json.dumps({{"status": "success", "result": result}})
        except Exception as e:
            return json.dumps({{"status": "error", "error": str(e)}})
'''
        
        # Write to both locations
        with open(os.path.join(path, 'src', 'agent.py'), 'w') as f:
            f.write(agent_content)
        with open(os.path.join(path, 'src', '__init__.py'), 'w') as f:
            f.write(f"from .agent import {agent_name}Agent")

    def _create_example(self, agent_name: str, path: str):
        """Creates example usage file"""
        example_content = f'''
from {agent_name.lower()}_agent import create_agent

def main():
    # Initialize the agent
    agent = create_agent(max_steps=30)
    
    # Example prompts
    prompts = [
        "Example task 1",
        "Example task 2"
    ]
    
    # Run examples
    for prompt in prompts:
        print(f"\\nPrompt: {prompt}")
        result = agent.run(prompt)
        print(f"Result: {result}")

if __name__ == "__main__":
    main()
'''
        with open(os.path.join(path, 'examples', 'basic_usage.py'), 'w') as f:
            f.write(example_content)

    def _create_documentation(self, agent_name: str, tools: List[Dict], path: str):
        """Creates documentation files"""
        readme_content = f'''
# {agent_name} Agent

Auto-generated CodeAgent with specific capabilities.

## Directory Structure
```
{agent_name}/
├── src/
│   ├── tools/
│   ├── agent.py
│   └── __init__.py
├── tests/
├── examples/
├── docs/
└── README.md
```

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
from {agent_name.lower()}_agent import create_agent

# Initialize with custom settings
agent = create_agent(
    hf_token="your_token_here",
    max_steps=30
)

# Run the agent
response = agent.run("your prompt here")
```

## Available Tools
{chr(10).join(f"- {t['name']}: {t.get('description', '')}" for t in tools)}

## Documentation
See the `docs/` directory for detailed documentation.
'''
        with open(os.path.join(path, 'README.md'), 'w') as f:
            f.write(readme_content)

    def forward(
        self,
        agent_name: str,
        output_path: str,
        tools_config: str,
        agent_config: str,
        requirements: Optional[str] = None
    ) -> str:
        """
        Creates complete agent structure
        """
        try:
            # Parse configurations
            tools = json.loads(tools_config)
            config = json.loads(agent_config)
            
            # Create full agent path
            agent_path = os.path.join(output_path, agent_name)
            
            # Create directory structure
            directories = self._create_directory_structure(agent_path)
            
            # Create tools
            for tool in tools:
                if 'file_path' in tool:
                    tool_content = self._generate_tool_template(
                        tool_name=tool['name'],
                        description=tool.get('description', 'Tool description')
                    )
                    tool_path = os.path.join(directories['tools'], f"{tool['name'].lower()}.py")
                    with open(tool_path, "w") as f:
                        f.write(tool_content)
            
            # Create __init__.py files
            with open(os.path.join(directories['tools'], '__init__.py'), 'w') as f:
                f.write(f"# Tools for {agent_name}\n")
                for tool in tools:
                    f.write(f"from .{tool['name'].lower()} import {tool['name'].lower()}\n")
            
            # Create main agent file
            self._create_agent_file(agent_name, config, tools, agent_path)
            
            # Create example
            self._create_example(agent_name, agent_path)
            
            # Create documentation
            self._create_documentation(agent_name, tools, agent_path)
            
            # Create requirements.txt
            base_requirements = [
                "smolagents>=1.2.2",
                "huggingface-hub>=0.19.0",
            ]
            if requirements:
                req_list = [r.strip() for r in requirements.split(",") if r.strip()]
                all_requirements = base_requirements + req_list
            else:
                all_requirements = base_requirements
                
            with open(os.path.join(agent_path, 'requirements.txt'), 'w') as f:
                f.write("\n".join(all_requirements))
            
            return json.dumps({
                "status": "success",
                "message": f"Agent structure created at {agent_path}",
                "agent_path": agent_path,
                "directories": directories
            })
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            })

# Create instance of the tool
generate_agent_structure = AgentStructureGenerator() 