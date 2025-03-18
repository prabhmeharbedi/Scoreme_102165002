@echo off
echo Setting up PDF Table Extractor...

:: Create directories
if not exist samples mkdir samples

:: Check if sample PDFs exist
if not exist samples\test3.pdf (
    echo Sample PDFs not found. Please place test3.pdf and test6.pdf in the 'samples' directory.
    echo Current directory structure:
    dir
    exit /b 1
)

:: Set up Python virtual environment
echo Setting up Python virtual environment...
python -m venv venv
call venv\Scripts\activate

:: Install requirements
echo Installing dependencies...
pip install -r requirements.txt

:: Start the application
echo Starting Streamlit application...
streamlit run app.py
