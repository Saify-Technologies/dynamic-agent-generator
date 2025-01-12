from src.agent_generator import AgentGenerator
import os

def main():
    generator = AgentGenerator(hf_token=os.getenv("HF_TOKEN"))

    requirements = """
    Create a CodeAgent that can:
    1. Generate images using Stable Diffusion
    2. Perform image classification
    3. Extract text from images (OCR)
    4. Process images (resize, crop, filter)
    5. Save and manage generated images
    6. Generate image descriptions
    7. Detect objects in images
    8. Perform face detection and recognition

    Note: 
    - Use only CodeAgent for implementation
    - Prefer using popular Spaces for ML tasks
    - Include error handling for API limits
    - Support batch processing
    """

    print("Generating ML Vision Agent...")
    result = generator.generate_agent(
        requirements=requirements,
        output_dir="generated_agents/vision_processor"
    )
    print(f"Generation Result:\n{result}")

if __name__ == "__main__":
    main() 