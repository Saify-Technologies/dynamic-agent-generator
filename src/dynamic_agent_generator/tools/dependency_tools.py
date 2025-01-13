from smolagents import Tool
import subprocess
import sys
import pkg_resources
import os
from typing import List, Dict, Optional
import json

class DependencyInstallerTool(Tool):
    """Tool for installing Python dependencies"""
    
    name = "install_dependencies"
    description = "Installs Python dependencies using pip"
    inputs = {
        "requirements": {
            "type": "string",
            "description": "Comma-separated list of requirements to install"
        },
        "pip_command": {
            "type": "string",
            "description": "Custom pip command (optional)",
            "nullable": True
        }
    }
    output_type = "string"

    def forward(self, requirements: str, pip_command: Optional[str] = None) -> str:
        """
        Install Python dependencies
        
        Args:
            requirements: Comma-separated list of requirements to install
            pip_command: Custom pip command (optional)
        
        Returns:
            str: JSON string with installation results
        """
        pip_cmd = pip_command or [sys.executable, "-m", "pip"]
        results = {}
        
        # Split requirements string into list
        req_list = [r.strip() for r in requirements.split(",") if r.strip()]
        
        for req in req_list:
            try:
                subprocess.check_call([*pip_cmd, "install", req], stdout=subprocess.PIPE)
                results[req] = "Successfully installed"
            except subprocess.CalledProcessError as e:
                results[req] = f"Failed to install: {str(e)}"
        
        return json.dumps(results)

class DependencyCheckerTool(Tool):
    """Tool for checking installed Python dependencies"""
    
    name = "check_dependencies"
    description = "Checks if required packages are installed"
    inputs = {
        "requirements": {
            "type": "string",
            "description": "Comma-separated list of requirements to check"
        }
    }
    output_type = "string"

    def forward(self, requirements: str) -> str:
        """
        Check if required packages are installed
        
        Args:
            requirements: Comma-separated list of requirements to check
        
        Returns:
            str: JSON string with check results
        """
        installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        results = {}
        
        # Split requirements string into list
        req_list = [r.strip() for r in requirements.split(",") if r.strip()]
        
        for req in req_list:
            pkg_name = req.split('==')[0].split('>=')[0].strip()
            results[req] = pkg_name.lower() in installed_packages
        
        return json.dumps(results)

# Create instances of the tools
install_dependencies = DependencyInstallerTool()
check_dependencies = DependencyCheckerTool() 