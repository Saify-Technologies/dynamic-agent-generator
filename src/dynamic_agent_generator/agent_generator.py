from smolagents import CodeAgent, HfApiModel, Tool
from .tools.tool_generator import generate_tool
from .tools.space_tool_generator import generate_space_tool
from .tools.search_tools import search_huggingface_spaces, validate_space
from .tools.agent_setup_tools import setup_agent_directory
from .tools.dependency_tools import install_dependencies, check_dependencies
import json

class AgentGenerator:
    def __init__(self, model_id="meta-llama/Llama-2-70b-chat-hf", hf_token=None):
        self.model = HfApiModel(model_id=model_id)
        self.hf_token = hf_token
        self.agent = CodeAgent(
            tools=[
                generate_tool,
                generate_space_tool,
                search_huggingface_spaces,
                validate_space,
                setup_agent_directory,
                install_dependencies,
                check_dependencies
            ],
            model=self.model,
            additional_authorized_imports=[
                "os", "black", "smolagents", "requests", "bs4",
                "subprocess", "sys", "pkg_resources", "json"
            ]
        )
        
    def generate_agent(self, requirements: str, output_dir: str):
        """
        Generates a new CodeAgent based on requirements
        
        Args:
            requirements: Natural language description of agent requirements
            output_dir: Directory to save generated agent
        """
        prompt = f"""
        Create a new CodeAgent based on these requirements:
        {requirements}
        
        Follow these steps:
        1. First analyze what tools will be needed
        2. For each required capability:
           a. Use search_huggingface_spaces to find relevant Spaces (returns JSON string)
           b. Parse the JSON response and validate found Spaces
           c. If a suitable Space is found, use generate_space_tool
           d. If no suitable Space exists, generate a custom tool
        3. Create the CodeAgent configuration file with:
           - All generated/found tools
           - Appropriate system prompt
           - Required imports and dependencies
        4. Return the full setup instructions
        
        When searching for Spaces:
        - Use specific search terms (e.g., "stable diffusion image generation gradio")
        - Parse the JSON responses carefully
        - Validate that Spaces are still active and accessible
        - Prefer Spaces with:
          * High usage statistics
          * Recent updates
          * Clear documentation
          * Gradio interface
        
        Make sure to handle:
        - Tool dependencies
        - System prompt customization for CodeAgent
        - Error handling for Space availability
        - Proper initialization of CodeAgent with all tools
        """
        
        return self.agent.run(prompt) 