from src.agent_generator import AgentGenerator
import os

def main():
    # Initialize the generator with your Hugging Face token
    generator = AgentGenerator(hf_token=os.getenv("HF_TOKEN"))

    # Example 1: ML-focused agent using Spaces
    ml_requirements = """
    Create a CodeAgent that can:
    1. Generate images using Stable Diffusion
    2. Perform image classification
    3. Extract text from images (OCR)
    4. Save results to a file

    Note: 
    - Use only CodeAgent for implementation
    - Prefer using popular and well-maintained Spaces for ML tasks
    - Ensure all tools are compatible with CodeAgent's execution model
    """

    print("Generating ML Agent...")
    ml_agent = generator.generate_agent(
        requirements=ml_requirements,
        output_dir="generated_agents/ml_processor"
    )
    print(f"ML Agent Generation Result:\n{ml_agent}\n")

    # Example 2: Data processing agent
    data_requirements = """
    Create a CodeAgent that can:
    1. Read data from various file formats (CSV, JSON, Excel)
    2. Perform data cleaning and transformation
    3. Execute SQL queries on the data
    4. Generate visualization charts
    5. Export results in multiple formats

    Note:
    - Focus on data processing capabilities
    - Include error handling for file operations
    - Support large dataset processing
    """

    print("Generating Data Processing Agent...")
    data_agent = generator.generate_agent(
        requirements=data_requirements,
        output_dir="generated_agents/data_processor"
    )
    print(f"Data Agent Generation Result:\n{data_agent}\n")

    # Example 3: Web automation agent
    web_requirements = """
    Create a CodeAgent that can:
    1. Scrape web content from various websites
    2. Extract structured data from HTML
    3. Handle authentication and session management
    4. Process and clean extracted data
    5. Store results in a database

    Note:
    - Include robust error handling
    - Handle rate limiting and delays
    - Support proxy configuration
    """

    print("Generating Web Automation Agent...")
    web_agent = generator.generate_agent(
        requirements=web_requirements,
        output_dir="generated_agents/web_processor"
    )
    print(f"Web Agent Generation Result:\n{web_agent}\n")

if __name__ == "__main__":
    main() 