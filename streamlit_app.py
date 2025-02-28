import streamlit as st
import sys
import os

# Add the project root to the path so we can import from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main function from the existing app
from src.frontend.app import main

# Run the app
if __name__ == "__main__":
    main() 