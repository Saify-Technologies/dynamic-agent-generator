from src.agent_generator import AgentGenerator
import os

def main():
    generator = AgentGenerator(hf_token=os.getenv("HF_TOKEN"))

    requirements = """
    Create a CodeAgent that can:
    1. Web Scraping and Automation:
       - Handle dynamic JavaScript content
       - Support login and authentication
       - Handle CAPTCHA and anti-bot measures
       - Extract structured data
    2. API Integration:
       - REST API interaction
       - GraphQL queries
       - OAuth authentication
       - Rate limiting handling
    3. Data Processing:
       - Clean and normalize web data
       - Extract specific patterns
       - Handle multiple data formats
    4. Storage:
       - Save to databases
       - Export to various formats
       - Maintain data integrity
    5. Advanced Features:
       - Proxy support
       - Browser fingerprint randomization
       - Concurrent requests
       - Session management

    Note:
    - Include robust error handling
    - Implement rate limiting and delays
    - Support proxy configuration
    - Handle various authentication methods
    """

    print("Generating Web Automation Agent...")
    result = generator.generate_agent(
        requirements=requirements,
        output_dir="generated_agents/web_processor"
    )
    print(f"Generation Result:\n{result}")

if __name__ == "__main__":
    main() 