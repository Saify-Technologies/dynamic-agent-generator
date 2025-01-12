from src.agent_generator import AgentGenerator
import os

def main():
    generator = AgentGenerator(hf_token=os.getenv("HF_TOKEN"))

    requirements = """
    Create a CodeAgent that can:
    1. Text Processing:
       - Sentiment analysis
       - Named Entity Recognition
       - Text classification
       - Topic modeling
    2. Language Tasks:
       - Translation between languages
       - Grammar correction
       - Text summarization
       - Question answering
    3. Document Processing:
       - PDF text extraction
       - Document classification
       - Key information extraction
       - Format conversion
    4. Advanced NLP:
       - Semantic search
       - Text generation
       - Chatbot capabilities
       - Intent recognition

    Note:
    - Use state-of-the-art NLP models
    - Support multiple languages
    - Handle large documents
    - Include text preprocessing tools
    """

    print("Generating NLP Agent...")
    result = generator.generate_agent(
        requirements=requirements,
        output_dir="generated_agents/nlp_processor"
    )
    print(f"Generation Result:\n{result}")

if __name__ == "__main__":
    main() 