from dynamic_agent_generator import AgentGenerator
import os

def main():
    generator = AgentGenerator(hf_token=os.getenv("HF_TOKEN"))

    requirements = """
    Create a CodeAgent specialized in image generation that can:
    1. Text-to-Image Generation:
       - Use Stable Diffusion models
       - Support DALL-E style models
       - Handle different art styles and prompts
       - Control image dimensions and quality
    
    2. Image Manipulation:
       - Image-to-Image transformation
       - Style transfer
       - Inpainting and outpainting
       - Face and object editing
    
    3. Advanced Controls:
       - Prompt engineering assistance
       - Negative prompts handling
       - Seed management for reproducibility
       - Batch processing capabilities
    
    4. Post-Processing:
       - Image enhancement
       - Resolution upscaling
       - Format conversion
       - Metadata management
    
    5. Organization:
       - Save generated images with metadata
       - Create image galleries
       - Export in various formats
       - Maintain generation history
    
    Required Spaces to search for and integrate:
    - Stable Diffusion spaces (search: "stable-diffusion-xl gradio")
    - Kandinsky spaces (search: "kandinsky gradio")
    - Midjourney-style spaces (search: "midjourney style gradio")
    - SD-Upscaler spaces (search: "stable diffusion upscaler")
    - Image enhancement spaces (search: "image enhancement gradio")
    
    Note:
    - Prioritize popular and well-maintained Spaces
    - Ensure Spaces have Gradio interfaces
    - Include proper error handling for API limits
    - Support both direct generation and fine-tuned control
    - Implement prompt templates and suggestions
    - Handle NSFW content filtering
    """

    print("Searching for and analyzing Hugging Face Spaces...")
    print("Generating Image Generation Agent...")
    
    result = generator.generate_agent(
        requirements=requirements,
        output_dir="generated_agents/image_generator"
    )
    
    # Example usage of the generated agent
    usage_example = """
    # Example usage of the generated image agent:
    from generated_agents.image_generator.agent import create_agent
    
    agent = create_agent(hf_token="your_token_here")
    
    # Generate an image
    result = agent.run('''
        Generate a photorealistic image of:
        - A sunset over mountains
        - With a lake in the foreground
        - In the style of Thomas Kinkade
        - Resolution: 1024x768
        - Save the result as "mountain_sunset.png"
    ''')
    
    # Apply style transfer
    result = agent.run('''
        Take image "mountain_sunset.png" and:
        - Apply an oil painting style
        - Enhance the colors
        - Upscale to 2048x1536
        - Save as "mountain_sunset_painted.png"
    ''')
    """
    
    print(f"Generation Result:\n{result}")
    print("\nExample Usage:")
    print(usage_example)

if __name__ == "__main__":
    main() 