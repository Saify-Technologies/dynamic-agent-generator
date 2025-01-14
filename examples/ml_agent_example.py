from dynamic_agent_generator import AgentGenerator

def main():
    generator = AgentGenerator()
    
    requirements = """
    Create a machine learning agent that can:
    - Train and evaluate ML models
    - Handle data preprocessing
    - Perform model inference
    - Support common ML tasks
    """
    
    output_dir = "./generated_agents/ml_agent"
    result = generator.generate_agent(
        requirements=requirements,
        output_dir=output_dir,
        custom_max_steps=25  # ML tasks might need more steps
    )
    print(result)

if __name__ == "__main__":
    main() 