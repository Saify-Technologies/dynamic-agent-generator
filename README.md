# Dynamic Agent Generator

A tool for dynamically generating specialized agents with proper structure and organization.

## Features

- Automated agent structure generation
- Intelligent tool discovery and integration
- Web research capabilities
- Proper Python package organization
- Comprehensive documentation generation
- Example code generation
- Test structure setup

## Directory Structure

```
project/
├── src/
│   └── dynamic_agent_generator/
│       ├── tools/
│       │   ├── agent_structure_generator.py  # Handles agent structure creation
│       │   ├── dependency_tools.py
│       │   ├── search_tools.py
│       │   ├── space_tool_generator.py
│       │   └── tool_generator.py
│       └── agent_generator.py
├── examples/
│   ├── automation_agent_example.py
│   ├── data_agent_example.py
│   ├── ml_agent_example.py
│   ├── nlp_agent_example.py
│   ├── web_agent_example.py
│   └── image_generation_agent_example.py
└── requirements.txt
```

## Installation

```bash
# Install in development mode
pip install -e .

# Or install from requirements
pip install -r requirements.txt
```

## Usage

```python
from dynamic_agent_generator import AgentGenerator

# Initialize the generator
generator = AgentGenerator()

# Generate an agent with proper structure
result = generator.generate_agent(
    requirements="Your agent requirements here",
    output_dir="./output/path",
    custom_max_steps=15  # Optional
)
```

### Generated Agent Structure

Each generated agent follows this structure:
```
output/path/
└── agent_name/
    ├── src/
    │   ├── tools/        # Agent-specific tools
    │   ├── agent.py      # Main agent implementation
    │   └── __init__.py   # Package initialization
    ├── tests/            # Test directory
    ├── examples/         # Usage examples
    ├── docs/             # Documentation
    ├── requirements.txt  # Dependencies
    └── README.md         # Agent documentation
```

## Example Agents

The package includes several example implementations:

### ML Agent
```python
# Generate an ML-focused agent
generator.generate_agent(
    requirements="ML processing requirements...",
    output_dir="./generated_agents/ml_agent",
    custom_max_steps=25
)
```

### NLP Agent
```python
# Generate an NLP processing agent
generator.generate_agent(
    requirements="NLP processing requirements...",
    output_dir="./generated_agents/nlp_agent"
)
```

### Web Automation Agent
```python
# Generate a web automation agent
generator.generate_agent(
    requirements="Web automation requirements...",
    output_dir="./generated_agents/web_agent"
)
```

See the `examples/` directory for more detailed implementations.

## Configuration

### Custom Steps
You can configure the number of steps for complex generations:
```python
generator.generate_agent(
    requirements="Complex requirements...",
    output_dir="./output",
    custom_max_steps=30  # More steps for complex tasks
)
```

### Output Structure
All generated files follow a consistent structure and include:
- Proper Python package organization
- Documentation
- Example code
- Test structure
- Dependency management

## Development

To contribute or modify:
1. Clone the repository
2. Install development dependencies
3. Run tests before submitting changes

## Requirements

See `requirements.txt` for full list of dependencies.
