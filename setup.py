from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dynamic-agent-generator",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A system for dynamically generating specialized CodeAgents using Hugging Face Spaces",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dynamic-agent-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "generate-agent=dynamic_agent_generator.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "dynamic_agent_generator": ["examples/*", "templates/*"],
    },
) 