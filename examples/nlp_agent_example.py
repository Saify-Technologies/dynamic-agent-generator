from dynamic_agent_generator import AgentGenerator

def main():
    generator = AgentGenerator()
    
    requirements = """
    Create an NLP processing agent that can:
    - Perform text analysis
    - Handle language translation
    - Generate text summaries
    - Extract key information
    """
    
    output_dir = "./generated_agents/nlp_agent"
    result = generator.generate_agent(
        requirements=requirements,
        output_dir=output_dir
    )
    print(result)

if __name__ == "__main__":
    main() 