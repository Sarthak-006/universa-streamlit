#!/usr/bin/env python
"""
Demo script for the UNIVERSA app using mock data.
This will run the app with mock API data for demonstration purposes.
"""

import os
import sys
import streamlit.web.cli as stcli

def main():
    # Set environment variables for demo mode
    os.environ["USE_MOCK_API"] = "true"
    
    # Use streamlit to run the app
    sys.argv = ["streamlit", "run", "streamlit_app.py", "--server.port=8501"]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main() 