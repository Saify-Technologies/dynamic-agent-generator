from dynamic_agent_generator import AgentGenerator

def main():
    generator = AgentGenerator()
    
    requirements = """
    Create a web automation agent that can:
    - Scrape web content
    - Process HTML/JSON data
    - Handle API interactions
    - Manage web sessions
    """
    
    output_dir = "./generated_agents/web_agent"
    result = generator.generate_agent(
        requirements=requirements,
        output_dir=output_dir
    )
    print(result)

if __name__ == "__main__":
    main() 