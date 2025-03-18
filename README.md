# PDF Table Extractor - Scoreme - 102165002

A Streamlit web application that extracts tables from PDFs and outputs them as Excel files.

## Features

- Upload your own PDFs or use pre-loaded sample files
- Automatic detection of different table types
- Specialized extraction for bank statements
- Download results as Excel files
- Preview extracted tables within the app

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Local Development

1. Clone this repository:
   ```
   git clone <repository-url>
   cd pdf-table-extractor
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Make sure sample PDFs are in the correct directory:
   ```
   mkdir -p samples
   # Place test3.pdf and test6.pdf in the samples directory
   ```

5. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

### Docker Deployment

1. Build the Docker image:
   ```
   docker build -t pdf-table-extractor .
   ```

2. Run the container:
   ```
   docker run -p 8501:8501 pdf-table-extractor
   ```

3. Access the application at `http://localhost:8501`

## Deployment to Cloud

### Streamlit Cloud

1. Push this repository to GitHub
2. Log in to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy by connecting to your GitHub repository

### Heroku

1. Make sure you have the Heroku CLI installed
2. Log in to Heroku:
   ```
   heroku login
   ```
3. Create a new Heroku app:
   ```
   heroku create your-app-name
   ```
4. Deploy to Heroku:
   ```
   git push heroku main
   ```

## How It Works

The application uses the following techniques to extract tables from PDFs:

1. Text extraction using PyPDF2
2. Table detection algorithms based on text patterns and layout
3. Multiple specialized extractors for different table types:
   - Bank statement extractor
   - Code-based table extractor
   - General table extractor
   - Vertical table extractor (for key-value pairs)
   - Line-based extractor (fallback method)
4. Conversion of extracted data to Excel format

## Project Structure

- `app.py`: Main Streamlit application
- `requirements.txt`: Python dependencies
- `Dockerfile`: Docker configuration for containerization
- `samples/`: Directory containing sample PDF files
  - `test3.pdf`: Bank statement sample
  - `test6.pdf`: Complex tables sample

## License

This project is licensed under the MIT License - see the LICENSE file for details.
