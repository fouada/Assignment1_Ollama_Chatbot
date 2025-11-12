"""
Flask REST API Wrapper
This is a wrapper that imports and runs the main Flask app from the src package.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import the Flask app
from ollama_chatbot.api.flask_app import app, logger

# Make everything available at module level
__all__ = ["app", "logger"]

# If run directly, start the Flask server
if __name__ == "__main__":
    import logging
    
    # Set logging level
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the Flask app
    logger.info("Starting Flask application...")
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )

