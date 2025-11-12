"""
Research Module for Ollama Chatbot

This module provides comprehensive research capabilities including:
- Systematic sensitivity analysis
- Mathematical proofs and formal verification
- Data-based performance comparisons
- Interactive visualizations and dashboards
"""

__version__ = "1.0.0"
__author__ = "Research Team"

from .data_comparison import DataComparator
from .mathematical_proofs import MathematicalProofs
from .sensitivity_analysis import SensitivityAnalyzer
from .visualizations import ResearchVisualizer

__all__ = [
    "SensitivityAnalyzer",
    "MathematicalProofs",
    "DataComparator",
    "ResearchVisualizer",
]
