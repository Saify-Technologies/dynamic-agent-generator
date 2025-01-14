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

    def _analyze_requirements(self, requirements: str) -> str:
        """Get LLM suggestions for agent generation steps"""
        analysis_prompt = f"""
        Based on these requirements, suggest a detailed plan for generating a new AI agent:
        {requirements}

        Your response should be a JSON object with this structure:
        {{
            "analysis": {{
                "required_capabilities": [
                    "List of core capabilities needed"
                ],
                "suggested_tools": [
                    {{
                        "name": "tool_name",
                        "purpose": "what this tool will do",
                        "type": "custom/space",
                        "search_terms": ["terms to find relevant spaces"]
                    }}
                ],
                "architecture_decisions": [
                    "Key decisions about agent structure"
                ]
            }},
            "generation_steps": [
                {{
                    "step": 1,
                    "action": "specific_action",
                    "tool": "tool_to_use",
                    "details": "detailed instructions for this step"
                }}
            ],
            "additional_considerations": [
                "Important points to consider during generation"
            ]
        }}

        Make your response practical and specific to the requirements.
        Focus on steps that use our available tools:
        - generate_tool
        - generate_space_tool
        - search_huggingface_spaces
        - validate_space
        - generate_agent_structure
        - install_dependencies
        - check_dependencies
        - duckduckgo_search
        """

        try:
            result = self.agent.run(analysis_prompt)
            return json.loads(result)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": f"Failed to analyze requirements: {str(e)}"
            })

    def generate_agent(self, requirements: str, output_dir: str, custom_max_steps: Optional[int] = None):
        """
        Generates a new CodeAgent based on requirements
        
        Args:
            requirements: Natural language description of agent requirements
            output_dir: Directory to save generated agent
            custom_max_steps: Optional override for max steps for this specific generation
        """
        try:
            # First, analyze requirements and get generation steps
            analysis = self._analyze_requirements(requirements)
            if analysis.get("status") == "error":
                return json.dumps(analysis)

            # Use the analysis to build the generation prompt
            generation_prompt = self._build_prompt(requirements, output_dir, analysis)

            # Generate the agent
            if custom_max_steps is not None:
                temp_agent = CodeAgent(
                    tools=self.agent.tools,
                    model=self.model,
                    max_steps=custom_max_steps,
                    additional_authorized_imports=self.agent._additional_authorized_imports
                )
                result = temp_agent.run(generation_prompt)
            else:
                result = self.agent.run(generation_prompt)

            # Parse the result
            result_data = json.loads(result)
            if result_data.get('status') == 'success':
                agent_dir = result_data.get('agent_dir')
                generated_tools = self._collect_generated_tools(agent_dir)
                self._update_agent_imports(agent_dir, generated_tools)
                
                return json.dumps({
                    'status': 'success',
                    'message': 'Agent generated successfully with all tools',
                    'agent_dir': agent_dir,
                    'generated_tools': generated_tools,
                    'analysis': analysis
                })
            
            return result

        except Exception as e:
            return json.dumps({
                'status': 'error',
                'error': str(e)
            })

    def _build_prompt(self, requirements: str, output_dir: str, analysis: Dict) -> str:
        """Build generation prompt using LLM's analysis"""
        return f"""
        Follow these steps to generate a new AI agent:

        Requirements:
        {requirements}

        Generated Analysis:
        {json.dumps(analysis.get('analysis', {}), indent=2)}

        Steps to Execute:
        {json.dumps(analysis.get('generation_steps', []), indent=2)}

        Additional Considerations:
        {json.dumps(analysis.get('additional_considerations', []), indent=2)}

        Output Directory: {output_dir}

        Use these tools as needed:
        - generate_tool: Create custom tools
        - generate_space_tool: Create tools from Hugging Face Spaces
        - search_huggingface_spaces: Find relevant Spaces
        - validate_space: Verify Space accessibility
        - generate_agent_structure: Create agent directory structure
        - install_dependencies: Handle package dependencies
        - check_dependencies: Verify package installations
        - duckduckgo_search: Web research capability

        Execute each step in the generation_steps sequence, ensuring to:
        1. Follow the exact order of steps
        2. Use the specified tool for each step
        3. Follow the detailed instructions for each step
        4. Handle any errors appropriately
        5. Report progress after each step

        Return a JSON response with:
        {{
            "status": "success/error",
            "message": "Status message",
            "agent_dir": "Path to generated agent",
            "steps_completed": ["List of completed steps"],
            "generated_tools": ["List of generated tools"],
            "errors": ["Any errors encountered"]
        }}
        """

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