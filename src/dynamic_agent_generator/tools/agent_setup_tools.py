from smolagents import Tool
import os
import shutil
from typing import Dict, Optional
import json
import argparse

class AgentSetupTool(Tool):
    """Tool for setting up a new agent directory"""
    
    name = "setup_agent_directory"
    description = "Sets up a new directory for a generated agent with all necessary files and structure"
    inputs = {
        "agent_name": {
            "type": "string",
            "description": "Name of the agent"
        },
        "base_dir": {
            "type": "string",
            "description": "Base directory where to create the agent folder"
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

    def _generate_tool_template(self, tool_name: str, description: str) -> str:
        """Generate a tool class template that follows smolagents standards"""
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
        """
        Tool implementation
        
        Args:
            input: Input description
            optional_param: Optional parameter description
        
        Returns:
            str: JSON string containing results
        """
        # Implementation here
        results = {{"result": "value"}}
        return json.dumps(results)

# Create instance of the tool
{tool_name.lower()} = {tool_name}Tool()
'''

    def forward(
        self,
        agent_name: str,
        base_dir: str,
        tools_config: str,
        agent_config: str,
        requirements: Optional[str] = None
    ) -> str:
        """
        Sets up a new agent directory
        
        Args:
            agent_name: Name of the agent
            base_dir: Base directory where to create the agent folder
            tools_config: JSON string containing tool configurations
            agent_config: JSON string containing agent configuration
            requirements: Comma-separated list of Python package requirements
        
        Returns:
            str: Success message with directory path
        """
        # Parse JSON configs
        tools = json.loads(tools_config)
        config = json.loads(agent_config)
        
        # Create main agent directory
        agent_dir = os.path.join(base_dir, agent_name)
        os.makedirs(agent_dir, exist_ok=True)
        
        # Create subdirectories
        tools_dir = os.path.join(agent_dir, "tools")
        os.makedirs(tools_dir, exist_ok=True)
        
        # Create tools with proper Tool class implementation
        for tool in tools:
            if 'file_path' in tool:
                tool_content = self._generate_tool_template(
                    tool_name=tool['name'],
                    description=tool.get('description', 'Tool description')
                )
                tool_path = os.path.join(tools_dir, f"{tool['name'].lower()}.py")
                with open(tool_path, "w") as f:
                    f.write(tool_content)
        
        # Create main agent file
        agent_file_content = f'''
from smolagents import CodeAgent, HfApiModel, DuckDuckGoSearchTool
from tools import *
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
        """
        Run the agent with the given prompt
        
        Args:
            prompt: Input prompt for the agent
            custom_max_steps: Optional override for max steps for this specific run
        
        Returns:
            str: Agent's response
        """
        try:
            if custom_max_steps is not None:
                # Create temporary agent with custom steps
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

def create_agent(hf_token: Optional[str] = None, max_steps: int = 20) -> {agent_name}Agent:
    """
    Create an instance of the agent
    
    Args:
        hf_token: Optional Hugging Face token
        max_steps: Maximum number of steps for the agent (default: 20)
    """
    return {agent_name}Agent(hf_token=hf_token, max_steps=max_steps)

if __name__ == "__main__":
    agent = create_agent()
    # Add any default behavior here
'''
        
        with open(os.path.join(agent_dir, "agent.py"), "w") as f:
            f.write(agent_file_content)
        
        # Create __init__.py files
        with open(os.path.join(agent_dir, "__init__.py"), "w") as f:
            f.write("")
        with open(os.path.join(tools_dir, "__init__.py"), "w") as f:
            f.write(f"# Auto-generated tools for {agent_name}\n")
            for tool in tools:
                f.write(f"from .{tool['name']} import {tool['name']}\n")
        
        # Create run.py for easy execution
        run_script_content = '''
import os
import sys
import subprocess
import argparse

def install_requirements():
    """Install required packages if not already installed"""
    if os.path.exists("requirements.txt"):
        with open("requirements.txt") as f:
            requirements = f.read().splitlines()
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the agent with custom configuration")
    parser.add_argument("prompt", nargs="?", help="Input prompt for the agent")
    parser.add_argument("--max-steps", type=int, default=20, help="Maximum number of steps (default: 20)")
    args = parser.parse_args()

    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Install dependencies
    install_requirements()
    
    # Import and run agent
    from agent import create_agent
    
    agent = create_agent(max_steps=args.max_steps)
    
    if args.prompt:
        result = agent.run(args.prompt)
        print(result)
    else:
        print("Usage: python run.py 'your prompt here' [--max-steps N]")
'''
        
        with open(os.path.join(agent_dir, "run.py"), "w") as f:
            f.write(run_script_content)
        
        # Add smolagents type validation to requirements
        base_requirements = [
            "smolagents>=1.2.2",
            "huggingface-hub>=0.19.0",
        ]
        
        if requirements:
            req_list = [r.strip() for r in requirements.split(",") if r.strip()]
            all_requirements = base_requirements + req_list
        else:
            all_requirements = base_requirements

        with open(os.path.join(agent_dir, "requirements.txt"), "w") as f:
            f.write("\n".join(all_requirements))
        
        # Create README.md
        readme_content = f'''
# {agent_name}

Auto-generated CodeAgent with specific capabilities.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```python
from agent import create_agent

# Initialize the agent with custom max_steps
agent = create_agent(hf_token="your_token_here", max_steps=30)

# Use the agent
response = agent.run("your prompt here")

# Or run with custom max_steps for a specific task
response = agent.run("your prompt here", custom_max_steps=50)
```

### Command Line Usage

```bash
# Run with default max_steps (20)
python run.py "your prompt here"

# Run with custom max_steps
python run.py "your prompt here" --max-steps 30
```

## Available Tools

{chr(10).join(f"- {t['name']}: {t.get('description', '')}" for t in tools)}

## Configuration

The agent is configured with:
- Model: {config.get('model_id', 'default')}
- Default max steps: 20 (configurable)
- Custom system prompt
- Specific tool set for its purpose
'''
        
        with open(os.path.join(agent_dir, "README.md"), "w") as f:
            f.write(readme_content)
        
        # Save agent configuration
        with open(os.path.join(agent_dir, "agent_config.json"), "w") as f:
            json.dump(config, f, indent=2)
        
        return json.dumps({
            "status": "success",
            "message": f"Agent setup completed at {agent_dir}",
            "agent_dir": agent_dir
        })

# Create instance of the tool
setup_agent_directory = AgentSetupTool()