from src.agent_generator import AgentGenerator
import os

def main():
    generator = AgentGenerator(hf_token=os.getenv("HF_TOKEN"))

    requirements = """
    Create a CodeAgent that can:
    1. System Automation:
       - File system operations
       - Process management
       - Scheduled tasks
       - System monitoring
    2. Network Operations:
       - Network scanning
       - Service monitoring
       - Email automation
       - FTP operations
    3. DevOps Tasks:
       - Docker container management
       - Log analysis
       - Configuration management
       - Deployment automation
    4. Security Features:
       - File integrity checking
       - Security scanning
       - Backup automation
       - Access control

    Note:
    - Include robust logging
    - Support different OS platforms
    - Handle permissions properly
    - Include security best practices
    """

    print("Generating Automation Agent...")
    result = generator.generate_agent(
        requirements=requirements,
        output_dir="generated_agents/automation_processor"
    )
    print(f"Generation Result:\n{result}")

if __name__ == "__main__":
    main() 