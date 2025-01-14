from dynamic_agent_generator import AgentGenerator

def main():
    generator = AgentGenerator()
    
    requirements = """
    Create an image generation agent that can:
    - Generate images from text
    - Edit and modify images
    - Handle different styles
    - Process image operations
    """
    
    output_dir = "./generated_agents/image_agent"
    result = generator.generate_agent(
        requirements=requirements,
        output_dir=output_dir,
        custom_max_steps=30  # Image generation might need more steps
    )
    print(result)

if __name__ == "__main__":
    main() 