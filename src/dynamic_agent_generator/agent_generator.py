from smolagents import CodeAgent, HfApiModel, Tool, DuckDuckGoSearchTool
from .tools.tool_generator import generate_tool
from .tools.space_tool_generator import generate_space_tool
from .tools.search_tools import search_huggingface_spaces, validate_space, duckduckgo_search
from .tools.agent_structure_generator import generate_agent_structure
from .tools.dependency_tools import install_dependencies, check_dependencies
import json
import os
from typing import List, Dict, Optional

class AgentGenerator:
    def __init__(self, model_id="meta-llama/Llama-2-70b-chat-hf", hf_token=None, max_steps=10):
        self.model = HfApiModel(model_id=model_id)
        self.hf_token = hf_token
        self.agent = CodeAgent(
            tools=[
                generate_tool,
                generate_space_tool,
                search_huggingface_spaces,
                validate_space,
                generate_agent_structure,
                install_dependencies,
                check_dependencies,
                duckduckgo_search
            ],
            model=self.model,
            max_steps=max_steps,
            additional_authorized_imports=[
                "os", "black", "smolagents", "requests", "bs4",
                "subprocess", "sys", "pkg_resources", "json"
            ]
        )

    def _collect_generated_tools(self, agent_dir: str) -> List[Dict]:
        """Collect information about generated tools"""
        tools = []
        tools_dir = os.path.join(agent_dir, "src", "tools")
        
        if os.path.exists(tools_dir):
            for file in os.listdir(tools_dir):
                if file.endswith('.py') and file != '__init__.py':
                    tool_name = file[:-3]  # Remove .py extension
                    tools.append({
                        'name': tool_name,
                        'import_path': f'.tools.{tool_name}'
                    })
        
        return tools

    def generate_agent(self, requirements: str, output_dir: str, custom_max_steps: Optional[int] = None):
        """
        Generates a new CodeAgent based on requirements
        
        Args:
            requirements: Natural language description of agent requirements
            output_dir: Directory to save generated agent
            custom_max_steps: Optional override for max steps for this specific generation
        """
        try:
            # First, generate the agent structure and tools
            if custom_max_steps is not None:
                temp_agent = CodeAgent(
                    tools=self.agent.tools,
                    model=self.model,
                    max_steps=custom_max_steps,
                    additional_authorized_imports=self.agent._additional_authorized_imports
                )
                result = temp_agent.run(self._build_prompt(requirements, output_dir))
            else:
                result = self.agent.run(self._build_prompt(requirements, output_dir))

            # Parse the result
            result_data = json.loads(result)
            if result_data.get('status') == 'success':
                agent_dir = result_data.get('agent_dir')
                
                # Collect information about generated tools
                generated_tools = self._collect_generated_tools(agent_dir)
                
                # Update agent.py to include generated tools
                self._update_agent_imports(agent_dir, generated_tools)
                
                return json.dumps({
                    'status': 'success',
                    'message': 'Agent generated successfully with all tools',
                    'agent_dir': agent_dir,
                    'generated_tools': generated_tools
                })
            
            return result

        except Exception as e:
            return json.dumps({
                'status': 'error',
                'error': str(e)
            })

    def _update_agent_imports(self, agent_dir: str, tools: List[Dict]):
        """Update agent.py to include all generated tools"""
        agent_file = os.path.join(agent_dir, "src", "agent.py")
        
        if os.path.exists(agent_file):
            with open(agent_file, 'r') as f:
                content = f.read()
            
            # Add tool imports if not already present
            import_section = "from smolagents import CodeAgent, HfApiModel, DuckDuckGoSearchTool\n"
            for tool in tools:
                import_section += f"from {tool['import_path']} import {tool['name']}\n"
            
            # Update tools list in CodeAgent initialization
            tools_list = "[\n                self.search_tool,  # Add search tool first\n"
            for tool in tools:
                tools_list += f"                {tool['name']},\n"
            tools_list += "            ]"
            
            # Update the content
            content = content.replace(
                "from smolagents import CodeAgent, HfApiModel, DuckDuckGoSearchTool",
                import_section
            )
            content = content.replace(
                "tools=[self.search_tool]",
                f"tools={tools_list}"
            )
            
            with open(agent_file, 'w') as f:
                f.write(content)

    def _build_prompt(self, requirements: str, output_dir: str) -> str:
        """Helper method to build the generation prompt"""
        return f"""
        Create a new CodeAgent based on these requirements:
        {requirements}
        
        Follow these steps:
        1. First use duckduckgo_search to research and understand the requirements
        2. Analyze what tools will be needed based on the research
        3. For each required capability:
           a. Use search_huggingface_spaces to find relevant Spaces (returns JSON string)
           b. Parse the JSON response and validate found Spaces
           c. If a suitable Space is found, use generate_space_tool
           d. If no suitable Space exists, generate a custom tool
        4. Create the CodeAgent configuration file with:
           - All generated/found tools
           - DuckDuckGoSearchTool for web search capability
           - Appropriate system prompt
           - Required imports and dependencies
        5. Use generate_agent_structure to create the complete agent structure at: {output_dir}
           - This will create proper directory structure
           - Set up all necessary files
           - Include documentation and examples
           - Ensure all generated tools are properly imported and initialized
        
        When searching for Spaces:
        - Use specific search terms based on web research
        - Parse the JSON responses carefully
        - Validate that Spaces are still active and accessible
        - Prefer Spaces with:
          * High usage statistics
          * Recent updates
          * Clear documentation
          * Gradio interface (for AI/ML tasks)
        
        Make sure to handle:
        - Tool dependencies
        - System prompt customization for CodeAgent
        - Error handling for Space availability
        - Proper initialization of CodeAgent with all tools
        - Include DuckDuckGoSearchTool in generated agent for web search capability
        - Proper directory structure and file organization
        - Correct imports for all generated tools
        """ 