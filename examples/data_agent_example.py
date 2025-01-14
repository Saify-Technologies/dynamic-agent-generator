from dynamic_agent_generator import AgentGenerator

def main():
    generator = AgentGenerator()
    
    requirements = """
    Create a data processing agent that can:
    - Handle various data formats
    - Clean and transform data
    - Perform data analysis
    - Generate visualizations
    """
    
    output_dir = "./generated_agents/data_agent"
    result = generator.generate_agent(
        requirements=requirements,
        output_dir=output_dir
    )
    print(result)

if __name__ == "__main__":
    main() 