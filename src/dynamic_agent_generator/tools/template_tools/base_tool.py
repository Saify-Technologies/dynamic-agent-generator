from smolagents import Tool

class BaseToolTemplate(Tool):
    """Base template for generating new tools"""
    
    def __init__(self, name: str, description: str, input_types: dict, output_type: str):
        self.name = name
        self.description = description
        self.inputs = input_types
        self.output_type = output_type
        super().__init__()

    def forward(self, *args, **kwargs):
        raise NotImplementedError("Tool functionality needs to be implemented") 