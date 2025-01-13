# Dynamic Agent Generator

A system for dynamically generating specialized CodeAgents using Hugging Face Spaces and smolagents. This tool allows you to create custom AI agents based on natural language requirements.

## 🌟 Features

- Dynamic tool generation based on requirements
- Automatic Hugging Face Space integration
- Custom system prompt generation
- Dependency management
- Automated agent setup and configuration
- Support for multiple specialized domains

## 📋 Prerequisites

- Python 3.8+
- Hugging Face account and API token
- Git
- pip or conda

## 🚀 Installation

You can install the package directly from GitHub:
```bash
pip install git+https://github.com/Saify-Technologies/dynamic-agent-generator.git
```

Or clone and install in development mode:
```bash
git clone https://github.com/Saify-Technologies/dynamic-agent-generator.git
cd dynamic-agent-generator
pip install -e .
```

## Command Line Usage

After installation, you can use the command-line tool:
```bash
# Generate an agent from requirements file
generate-agent -r requirements.txt -o output_directory

# Or directly from requirements string
generate-agent -r "Create an agent that can generate images..." -o output_directory
```

4. Set up your Hugging Face token:
```bash
# On Unix/macOS
export HF_TOKEN="your_token_here"

# On Windows (CMD)
set HF_TOKEN=your_token_here

# On Windows (PowerShell)
$env:HF_TOKEN="your_token_here"
```

## 💻 Usage

### Basic Usage

```python
from dynamic_agent_generator import AgentGenerator

generator = AgentGenerator(hf_token="your_hf_token")
result = generator.generate_agent(
    requirements="Your requirements in natural language",
    output_dir="path/to/output"
)
```

### Running Example Agents

The repository includes several example agent generators:

1. Image Generation Agent:
```bash
python examples/image_generation_agent_example.py
```

2. ML Vision Agent:
```bash
python examples/ml_agent_example.py
```

3. Data Processing Agent:
```bash
python examples/data_agent_example.py
```

4. Web Automation Agent:
```bash
python examples/web_agent_example.py
```

5. NLP Agent:
```bash
python examples/nlp_agent_example.py
```

6. System Automation Agent:
```bash
python examples/automation_agent_example.py
```

### Using Generated Agents

Each generated agent includes its own setup and can be run independently:

```bash
cd generated_agents/your_agent_name
python run.py "your prompt here"
```

## 📁 Project Structure

```
dynamic-agent-generator/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── agent_generator.py
│   └── tools/
│       ├── __init__.py
│       ├── tool_generator.py
│       ├── space_tool_generator.py
│       ├── search_tools.py
│       ├── dependency_tools.py
│       └── agent_setup_tools.py
├── examples/
│   ├── image_generation_agent_example.py
│   ├── ml_agent_example.py
│   ├── data_agent_example.py
│   ├── web_agent_example.py
│   ├── nlp_agent_example.py
│   └── automation_agent_example.py
└── generated_agents/
    └── [Generated agents will be created here]
```

## 🛠️ Generated Agent Structure

Each generated agent follows this structure:
```
generated_agents/agent_name/
├── README.md
├── requirements.txt
├── agent.py
├── run.py
├── agent_config.json
└── tools/
    ├── __init__.py
    └── [Generated tools...]
```

## 🔧 Configuration

### Environment Variables

- `HF_TOKEN`: Your Hugging Face API token
- `PYTHONPATH`: Should include the project root directory

### Agent Configuration

Each generated agent can be configured through its `agent_config.json`:
```json
{
    "model_id": "meta-llama/Llama-2-70b-chat-hf",
    "system_prompt": "Custom prompt for the agent",
    "imports": ["list", "of", "allowed", "imports"]
}
```

## 🚨 Common Issues & Solutions

1. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - Check individual agent requirements

2. **Hugging Face Token Issues**
   - Ensure token is set in environment
   - Verify token has necessary permissions

3. **Space Access Issues**
   - Check Space availability
   - Verify API rate limits
   - Ensure Space supports Gradio client

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License. This means you can use, share, and adapt the material for non-commercial purposes, provided you give appropriate credit. For more details, see the LICENSE file.

## 🙏 Acknowledgments

- Hugging Face for Spaces and models
- smolagents library
- All contributors and maintainers
- Saify Technologies for their support and innovation. Visit [Saify Technologies](https://saifytech.com) for more information.
- Saifs AI, our cutting-edge AI product. Learn more at [Saifs AI](https://saifs.ai).

## 📧 Contact

- Create an issue for bug reports
- Submit a PR for contributions
- Contact maintainers for other queries
