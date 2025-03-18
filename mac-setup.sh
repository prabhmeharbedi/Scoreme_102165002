#!/bin/bash

# Create directories
mkdir -p samples

# Check if the sample PDFs exist
if [ ! -f "samples/test3.pdf" ] || [ ! -f "samples/test6.pdf" ]; then
    echo "Sample PDFs not found. Please place test3.pdf and test6.pdf in the 'samples' directory."
    echo "Current directory structure:"
    ls -la
    exit 1
fi

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
python -m venv venv
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the application
echo "Starting Streamlit application..."
streamlit run app.py
