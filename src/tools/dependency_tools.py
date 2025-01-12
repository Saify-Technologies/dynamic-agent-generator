from smolagents import tool
import subprocess
import sys
import pkg_resources
import os
from typing import List, Dict

@tool
def install_dependencies(requirements: List[str], pip_command: str = None) -> Dict[str, str]:
    """
    Installs Python dependencies using pip
    
    Args:
        requirements: List of requirements to install
        pip_command: Custom pip command (optional)
    """
    pip_cmd = pip_command or [sys.executable, "-m", "pip"]
    results = {}
    
    for req in requirements:
        try:
            subprocess.check_call([*pip_cmd, "install", req], stdout=subprocess.PIPE)
            results[req] = "Successfully installed"
        except subprocess.CalledProcessError as e:
            results[req] = f"Failed to install: {str(e)}"
    
    return results

@tool
def check_dependencies(requirements: List[str]) -> Dict[str, bool]:
    """
    Checks if required packages are installed
    
    Args:
        requirements: List of requirements to check
    """
    installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    results = {}
    
    for req in requirements:
        pkg_name = req.split('==')[0].split('>=')[0].strip()
        results[req] = pkg_name.lower() in installed_packages
    
    return results 