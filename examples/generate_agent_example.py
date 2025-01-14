from dynamic_agent_generator import AgentGenerator

def main():
    # Initialize the generator
    generator = AgentGenerator()
    
    # Example requirements
    requirements = """
    Create an agent that can perform image generation tasks.
    It should be able to:
    - Generate images from text descriptions
    - Modify existing images
    - Handle different art styles
    """
    
    # Generate the agent with proper structure
    output_dir = "./generated_agents"
    result = generator.generate_agent(
        requirements=requirements,
        output_dir=output_dir,
        custom_max_steps=20  # Optional: Set higher steps for complex generation
    )
    print(result)

if __name__ == "__main__":
    main() 