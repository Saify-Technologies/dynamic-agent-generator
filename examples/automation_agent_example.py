from dynamic_agent_generator import AgentGenerator

def main():
    generator = AgentGenerator()
    
    requirements = """
    Create an automation agent that can:
    - Handle system tasks
    - Automate file operations
    - Schedule tasks
    """
    
    output_dir = "./automation_agents"
    result = generator.generate_agent(requirements, output_dir)
    print(result)

if __name__ == "__main__":
    main() 