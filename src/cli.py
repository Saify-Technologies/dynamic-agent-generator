import argparse
import os
from .agent_generator import AgentGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate specialized AI agents")
    parser.add_argument(
        "--requirements", "-r",
        type=str,
        required=True,
        help="Path to requirements file or requirements string"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="generated_agents",
        help="Output directory for generated agent"
    )
    parser.add_argument(
        "--model-id",
        type=str,
        default="meta-llama/Llama-2-70b-chat-hf",
        help="Hugging Face model ID to use"
    )
    parser.add_argument(
        "--hf-token",
        type=str,
        default=os.getenv("HF_TOKEN"),
        help="Hugging Face API token"
    )
    
    args = parser.parse_args()
    
    # Read requirements from file if it exists
    if os.path.exists(args.requirements):
        with open(args.requirements, "r") as f:
            requirements = f.read()
    else:
        requirements = args.requirements
    
    generator = AgentGenerator(
        model_id=args.model_id,
        hf_token=args.hf_token
    )
    
    result = generator.generate_agent(
        requirements=requirements,
        output_dir=args.output_dir
    )
    
    print(result)

if __name__ == "__main__":
    main() 