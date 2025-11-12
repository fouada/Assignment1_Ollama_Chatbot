"""
Setup script for Ollama Chatbot

This file provides backward compatibility for tools that don't yet support pyproject.toml.
Modern Python packaging uses pyproject.toml as the primary configuration.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = (this_directory / "requirements.txt").read_text().strip().split("\n")

# Read dev requirements (may not exist in production Docker builds)
dev_requirements_file = this_directory / "requirements-dev.txt"
if dev_requirements_file.exists():
    dev_requirements = dev_requirements_file.read_text().strip().split("\n")
else:
    dev_requirements = []

setup(
    name="ollama-chatbot",
    version="1.0.0",
    author="Fouad Azouagh",
    author_email="your.email@example.com",
    description="Privacy-first local AI chatbot with dual interfaces (Streamlit UI + Flask API)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fouada/Assignment1_Ollama_Chatbot",
    project_urls={
        "Bug Tracker": "https://github.com/fouada/Assignment1_Ollama_Chatbot/issues",
        "Documentation": "https://github.com/fouada/Assignment1_Ollama_Chatbot/tree/main/docs",
        "Source Code": "https://github.com/fouada/Assignment1_Ollama_Chatbot",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.1",
            "pytest-asyncio>=0.21.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "ollama-chatbot-flask=ollama_chatbot.api.flask_app:main",
            "ollama-chatbot-streamlit=ollama_chatbot.ui.streamlit_app:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Typing :: Typed",
    ],
    keywords=[
        "ai", "chatbot", "ollama", "llm", "local-ai", "privacy",
        "streamlit", "flask", "rest-api", "machine-learning",
        "natural-language-processing", "plugin-system",
    ],
    license="MIT",
    zip_safe=False,
)

