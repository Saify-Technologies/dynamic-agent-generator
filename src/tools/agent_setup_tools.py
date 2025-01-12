from smolagents import tool
import os
import shutil
from typing import List, Dict
import json
from .dependency_tools import install_dependencies, check_dependencies

@tool
def setup_agent_directory(
    agent_name: str,
    base_dir: str,
    tools: List[Dict],
    agent_config: Dict,
    requirements: List[str] = None
) -> str:
    """
    Sets up a new directory for a generated agent with all necessary files and structure
    
    Args:
        agent_name: Name of the agent
        base_dir: Base directory where to create the agent folder
        tools: List of tool configurations with their file paths
        agent_config: Configuration for the CodeAgent
        requirements: List of Python package requirements
    """
    # Create main agent directory
    agent_dir = os.path.join(base_dir, agent_name)
    os.makedirs(agent_dir, exist_ok=True)
    
    # Create subdirectories
    tools_dir = os.path.join(agent_dir, "tools")
    os.makedirs(tools_dir, exist_ok=True)
    
    # Copy tools to the tools directory
    for tool in tools:
        if 'file_path' in tool:
            tool_name = os.path.basename(tool['file_path'])
            shutil.copy2(tool['file_path'], os.path.join(tools_dir, tool_name))
    
    # Create main agent file
    agent_file_content = f'''
from smolagents import CodeAgent, HfApiModel
from tools import *
import os

def create_agent(hf_token=None):
    model = HfApiModel(
        model_id="{agent_config.get('model_id', 'meta-llama/Llama-2-70b-chat-hf')}",
        token=hf_token or os.getenv("HF_TOKEN")
    )
    
    agent = CodeAgent(
        tools=[{", ".join(t['name'] for t in tools)}],
        model=model,
        system_prompt="""{agent_config.get('system_prompt', '')}""",
        additional_authorized_imports={agent_config.get('imports', [])}
    )
    
    return agent

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
from typing import List
import subprocess

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
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Install dependencies
    install_requirements()
    
    # Import and run agent
    from agent import create_agent
    
    agent = create_agent()
    
    # If command line argument provided, use it as the prompt
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        result = agent.run(prompt)
        print(result)
    else:
        print("Usage: python run.py 'your prompt here'")
'''
    
    with open(os.path.join(agent_dir, "run.py"), "w") as f:
        f.write(run_script_content)
    
    # Create base requirements.txt with essential packages
    base_requirements = [
        "smolagents>=1.0.0",
        "huggingface-hub>=0.19.0",
    ]
    
    # Combine with additional requirements
    all_requirements = base_requirements + (requirements or [])
    
    with open(os.path.join(agent_dir, "requirements.txt"), "w") as f:
        f.write("\n".join(all_requirements))
    
    # Make run.py executable
    os.chmod(os.path.join(agent_dir, "run.py"), 0o755)
    
    # Create README.md
    readme_content = f'''
# {agent_name}

Auto-generated CodeAgent with specific capabilities.

## Setup

bash
pip install -r requirements.txt
python
from agent import create_agent
Initialize the agent
agent = create_agent(hf_token="your_token_here")
Use the agent
response = agent.run("your prompt here")


## Available Tools

{chr(10).join(f"- {t['name']}: {t.get('description', '')}" for t in tools)}

## Configuration

The agent is configured with:
- Model: {agent_config.get('model_id', 'default')}
- Custom system prompt
- Specific tool set for its purpose
'''
    
    with open(os.path.join(agent_dir, "README.md"), "w") as f:
        f.write(readme_content)
    
    # Save agent configuration
    with open(os.path.join(agent_dir, "agent_config.json"), "w") as f:
        json.dump(agent_config, f, indent=2)
    
    return f"Agent setup completed at {agent_dir}"