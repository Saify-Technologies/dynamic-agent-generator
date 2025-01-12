from src.agent_generator import AgentGenerator
import os

def main():
    generator = AgentGenerator(hf_token=os.getenv("HF_TOKEN"))

    requirements = """
    Create a CodeAgent that can:
    1. Read data from various sources:
       - CSV, JSON, Excel, Parquet files
       - SQL databases
       - REST APIs
       - Web scraping
    2. Perform data cleaning and transformation:
       - Handle missing values
       - Remove duplicates
       - Type conversion
       - Feature engineering
    3. Execute SQL queries on dataframes
    4. Generate visualizations:
       - Time series plots
       - Statistical charts
       - Interactive dashboards
    5. Export results in multiple formats
    6. Perform basic statistical analysis
    7. Handle large datasets efficiently
    8. Support data validation and quality checks

    Note:
    - Focus on data processing capabilities
    - Include error handling for file operations
    - Support parallel processing for large datasets
    - Include data validation tools
    """

    print("Generating Data Processing Agent...")
    result = generator.generate_agent(
        requirements=requirements,
        output_dir="generated_agents/data_processor"
    )
    print(f"Generation Result:\n{result}")

if __name__ == "__main__":
    main() 