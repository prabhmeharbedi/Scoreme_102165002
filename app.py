import streamlit as st
import io
import re
import os
import pandas as pd
import numpy as np
import tempfile
from datetime import datetime
from pdf_processor import PDFTableExtractor

# Add this at the top of your app.py file, replacing the current CSS

# Add this at the top of your app.py file, replacing the current CSS

st.set_page_config(
    page_title="PDF Table Extractor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Global styling */
    .main {
        background-color: #1e1e2e;
        color: #cdd6f4;
        padding: 0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Container styling */
    .block-container {
        padding: 3rem 3rem 3rem 3rem;
        max-width: 100%;
    }
    
    /* Title styling */
    .title-container {
        background: linear-gradient(90deg, #313244, #181825);
        color: white;
        padding: 3rem 2rem;
        border-radius: 12px;
        margin-bottom: 2.5rem;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        border: 1px solid #45475a;
        overflow: hidden;
        position: relative;
    }
    
    .title-container::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at 50% 50%, rgba(166, 227, 161, 0.1), transparent 50%);
        z-index: 0;
    }
    
    .title-container h1 {
        color: #cba6f7;
        font-size: 3.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
        position: relative;
        z-index: 1;
    }
    
    .title-container p {
        color: #bac2de;
        font-size: 1.25rem;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    /* File uploader styling */
    .file-uploader {
        padding: 2.5rem;
        background-color: #313244;
        border-radius: 12px;
        margin-bottom: 2.5rem;
        border: 1px solid #45475a;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .file-uploader:hover {
        border-color: #cba6f7;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }
    
    .file-uploader h2, .file-uploader h3 {
        color: #cdd6f4;
        font-weight: 600;
    }
    
    /* Results container styling */
    .results-container {
        padding: 2.5rem;
        background-color: #313244;
        border-radius: 12px;
        margin-top: 2.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid #45475a;
    }
    
    .results-container h2 {
        color: #cdd6f4;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    
    /* Instructions area styling */
    .instructions {
        background-color: #1e1e2e;
        padding: 1.75rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border-left: 4px solid #a6e3a1;
        box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.1);
    }
    
    .instructions p {
        color: #bac2de;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    
    .instructions strong {
        color: #f5c2e7;
        font-weight: 600;
    }
    
    .instructions ul {
        margin-left: 1.5rem;
        color: #bac2de;
    }
    
    .instructions li {
        margin-bottom: 0.5rem;
    }
    
    /* File uploader component styling */
    [data-testid="stFileUploader"] {
        width: 100%;
    }
    
    [data-testid="stFileUploader"] > div > div {
        background-color: #181825;
        border: 2px dashed #45475a;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"] > div > div:hover {
        border-color: #cba6f7;
        background-color: #1e1e2e;
    }
    
    [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {
        color: #bac2de;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #cba6f7, #f5c2e7);
        color: #11111b;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        width: 100%;
        height: auto;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        background: linear-gradient(90deg, #f5c2e7, #cba6f7);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(90deg, #a6e3a1, #94e2d5);
        color: #11111b;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        background: linear-gradient(90deg, #94e2d5, #a6e3a1);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #181825;
        padding-top: 2rem;
        border-right: 1px solid #313244;
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 2rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    
    [data-testid="stSidebar"] h1 {
        color: #cdd6f4;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    
    [data-testid="stSidebar"] .stRadio > div {
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        color: #bac2de;
    }
    
    [data-testid="stRadio"] > div {
        background-color: #181825;
        border-radius: 8px;
        padding: 0.75rem;
    }
    
    [data-testid="stRadio"] > div:hover {
        background-color: #1e1e2e;
    }
    
    /* Footer styling */
    footer {
        margin-top: 4rem;
        padding-top: 1.5rem;
        border-top: 1px solid #45475a;
        text-align: center;
        color: #6c7086;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1e1e2e;
        border-radius: 8px;
        font-weight: 600;
        color: #cdd6f4;
        padding: 1rem;
        border: 1px solid #45475a;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #313244;
    }
    
    .streamlit-expanderContent {
        background-color: #181825;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
        border: 1px solid #45475a;
        border-top: none;
    }
    
    /* Table display styling */
    [data-testid="stDataFrame"] {
        width: 100%;
    }
    
    [data-testid="stDataFrame"] > div {
        background-color: #181825;
        border-radius: 8px;
        border: 1px solid #45475a;
        overflow: hidden;
    }
    
    [data-testid="stDataFrame"] th {
        background-color: #313244;
        color: #cdd6f4;
        border-bottom: 1px solid #45475a;
        text-align: left;
        padding: 0.75rem 1rem;
    }
    
    [data-testid="stDataFrame"] td {
        border-bottom: 1px solid #313244;
        color: #bac2de;
        padding: 0.75rem 1rem;
    }
    
    [data-testid="stDataFrame"] tr:hover td {
        background-color: #1e1e2e;
    }
    
    /* Headers styling */
    h1, h2, h3, h4, h5, h6 {
        color: #cdd6f4;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    h1 {
        font-size: 2.5rem;
        letter-spacing: -0.025em;
    }
    
    h2 {
        font-size: 2rem;
        letter-spacing: -0.025em;
    }
    
    h3 {
        font-size: 1.5rem;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: #181825;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 0.5rem 0 0.5rem;
        border: 1px solid #45475a;
        border-bottom: none;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: auto;
        white-space: pre-wrap;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        background-color: #313244;
        color: #bac2de;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #cba6f7;
        color: #11111b;
    }
    
    /* Text input styling */
    input[type="text"] {
        background-color: #1e1e2e;
        border: 1px solid #45475a;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #cdd6f4;
    }
    
    /* Progress bar styling */
    [role="progressbar"] > div > div {
        background-color: #cba6f7 !important;
    }
    
    /* Notification styling */
    .stAlert {
        background-color: #313244;
        color: #cdd6f4;
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #f38ba8;
        margin-bottom: 1.5rem;
    }
    
    /* Icon styling */
    .stIcon > svg {
        fill: #cba6f7;
    }
</style>
""", unsafe_allow_html=True)

def is_date(text):
    """Check if text is a date in common formats."""
    date_patterns = [
        r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',  # dd/mm/yyyy or dd-mm-yyyy
        r'\d{1,2}[-/][A-Za-z]{3}[-/]\d{2,4}',  # dd/mmm/yyyy
        r'\d{1,2}[-/][A-Za-z]{3,9}[-/]\d{2,4}',  # dd/month/yyyy
    ]
    
    return any(re.match(pattern, text) for pattern in date_patterns)

def extract_bank_statement_tables(text_content):
    """
    Extract tables from bank statement format PDFs.
    This function is specialized for the format in the first PDF.
    """
    # Split by pages or sections
    sections = re.split(r'Page No: \d+|Statement of account', text_content)
    
    transactions = []
    current_date = None
    
    # Regular expression to match transaction lines with date, description, and amount
    transaction_pattern = r'(\d{2}[-/]\w{3}[-/]\d{4}|\d{2}[-/]\d{2}[-/]\d{4})\s+(.*?)\s+([\d,.]+\.\d{2})\s+(.*?Dr|.*?Cr)'
    simple_transaction_pattern = r'(\d{2}[-/]\w{3}[-/]\d{4}|\d{2}[-/]\d{2}[-/]\d{4})\s+([A-Z].*?)\s+([\d,.]+\.\d{2})'
    
    for section in sections:
        lines = section.strip().split('\n')
        for line in lines:
            # Skip empty lines and headers
            if not line.strip() or "BANK NAME" in line or "BRANCH NAME" in line:
                continue
                
            # Try to extract transaction using patterns
            match = re.search(transaction_pattern, line)
            if not match:
                match = re.search(simple_transaction_pattern, line)
                
            if match:
                date_str = match.group(1)
                description = match.group(2).strip()
                amount = match.group(3).strip().replace(',', '')
                
                # Try to determine if it's debit or credit
                is_debit = "Dr" in line or "TO " in description
                
                transactions.append({
                    "Date": date_str,
                    "Description": description,
                    "Amount": float(amount),
                    "Type": "Debit" if is_debit else "Credit"
                })
    
    # If transactions were found, convert to DataFrame
    if transactions:
        df = pd.DataFrame(transactions)
        return {"Bank Statement": df}
    
    # Fallback to general table extraction
    return extract_general_tables(text_content)

def extract_code_based_tables(text_content):
    """
    Extract tables with code-based structure like those in the test6.pdf
    where each line might start with a code or reference.
    """
    # Split text into lines
    lines = text_content.split('\n')
    
    # Remove empty lines
    lines = [line.strip() for line in lines if line.strip()]
    
    # Look for patterns like "$2 $ $2 $ )0*-*" or similar
    pattern = r'\$\d+\s+\$\s+\$\d+\s+\$\s+[A-Za-z0-9\*\-]+\s+'
    
    # Group lines by potential tables
    current_table = []
    all_tables = []
    in_table = False
    
    for line in lines:
        # Check if this line could be a new table row
        if re.match(pattern, line):
            if not in_table:
                in_table = True
                current_table = [line]
            else:
                current_table.append(line)
        elif in_table and line and not line.startswith("---"):
            # Continue adding to current table if we're not seeing a separator
            current_table.append(line)
        else:
            # End of table
            if in_table and current_table:
                all_tables.append(current_table)
                current_table = []
                in_table = False
    
    # Don't forget the last table
    if in_table and current_table:
        all_tables.append(current_table)
    
    # Process tables
    processed_tables = {}
    for i, table_lines in enumerate(all_tables):
        if len(table_lines) < 3:  # Skip too small tables
            continue
        
        # Create dataframe from the table
        try:
            # Extract columns by splitting on consistent whitespace
            table_data = []
            for line in table_lines:
                # Split by multiple spaces
                cols = re.split(r'\s{2,}', line)
                table_data.append(cols)
            
            # Find the max columns
            max_cols = max(len(row) for row in table_data)
            
            # Normalize data
            normalized_data = [row + [''] * (max_cols - len(row)) for row in table_data]
            
            # Create dataframe
            df = pd.DataFrame(normalized_data)
            
            # Use first row as header if it seems appropriate
            if all(isinstance(cell, str) and not cell.isdigit() for cell in normalized_data[0]):
                df.columns = df.iloc[0]
                df = df.iloc[1:]
            
            # Add to processed tables
            processed_tables[f"Code_Table_{i+1}"] = df
        except Exception as e:
            st.error(f"Error processing table {i+1}: {str(e)}")
    
    return processed_tables

def extract_vertical_tables(text_content):
    """
    Extract tables where content is organized vertically with key-value pairs.
    Common in bank statements and other financial documents.
    """
    # Split text into lines
    lines = text_content.split('\n')
    
    # Remove empty lines
    lines = [line.strip() for line in lines if line.strip()]
    
    # Look for patterns like "Key : Value" or "Key: Value"
    info_data = []
    
    for line in lines:
        # Try to extract key-value pairs
        match = re.search(r'([A-Za-z0-9\s\./]+)\s*[:]\s*(.+)', line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            info_data.append({"Field": key, "Value": value})
    
    if info_data:
        df = pd.DataFrame(info_data)
        return {"Account_Information": df}
    
    return {}

def extract_general_tables(text_content):
    """
    Extract tables from general PDF content by identifying tabular structures.
    This is a more generic approach for PDFs with various table formats.
    """
    tables = {}
    table_count = 0
    
    # Split text into lines
    lines = text_content.split('\n')
    
    # Remove empty lines
    lines = [line.strip() for line in lines if line.strip()]
    
    # Variables to track table detection
    in_table = False
    current_table = []
    column_widths = []
    current_table_name = None
    
    for i, line in enumerate(lines):
        # Check if this line might be a header
        if (re.search(r'^\s*[A-Za-z\s]+\s*$', line) and 
            i + 1 < len(lines) and 
            re.search(r'\d', lines[i + 1])):
            # This could be a table header followed by data
            if in_table:
                # Save previous table
                if current_table:
                    table_df = pd.DataFrame(current_table)
                    table_name = current_table_name or f"Table_{table_count}"
                    tables[table_name] = table_df
                    table_count += 1
                    current_table = []
            
            in_table = True
            current_table_name = line.strip()
            continue
        
        # If we detect a line with multiple numeric values or specific patterns
        # indicating tabular data
        if in_table or re.search(r'(\d+\s+){2,}', line) or re.search(r'(\$[\d,.]+\s+){2,}', line):
            if not in_table:
                in_table = True
            
            # Try to split the line into columns
            # First by whitespace
            columns = line.split()
            
            # Check if we can identify a better delimiter
            if len(columns) <= 2 and ("|" in line or "," in line or "\t" in line):
                if "|" in line:
                    columns = [col.strip() for col in line.split("|") if col.strip()]
                elif "," in line:
                    columns = [col.strip() for col in line.split(",")]
                elif "\t" in line:
                    columns = [col.strip() for col in line.split("\t")]
            
            # Add to current table
            if columns:
                current_table.append(columns)
        else:
            # Check if we're ending a table
            if in_table and not re.search(r'(\d+\s+){2,}', line):
                if current_table:
                    try:
                        # Try to create a DataFrame
                        # Normalize columns to handle different lengths
                        max_cols = max(len(row) for row in current_table)
                        normalized_table = [row + [''] * (max_cols - len(row)) for row in current_table]
                        
                        # Use first row as header if it seems like a header
                        if all(isinstance(cell, str) and not cell.isdigit() for cell in normalized_table[0]):
                            headers = normalized_table[0]
                            data = normalized_table[1:]
                            table_df = pd.DataFrame(data, columns=headers)
                        else:
                            table_df = pd.DataFrame(normalized_table)
                        
                        table_name = current_table_name or f"Table_{table_count}"
                        tables[table_name] = table_df
                        table_count += 1
                    except Exception as e:
                        st.error(f"Error creating table: {e}")
                
                in_table = False
                current_table = []
                current_table_name = None
    
    # Don't forget the last table
    if in_table and current_table:
        try:
            max_cols = max(len(row) for row in current_table)
            normalized_table = [row + [''] * (max_cols - len(row)) for row in current_table]
            
            if all(isinstance(cell, str) and not cell.isdigit() for cell in normalized_table[0]):
                headers = normalized_table[0]
                data = normalized_table[1:]
                table_df = pd.DataFrame(data, columns=headers)
            else:
                table_df = pd.DataFrame(normalized_table)
            
            table_name = current_table_name or f"Table_{table_count}"
            tables[table_name] = table_df
        except Exception as e:
            st.error(f"Error creating last table: {e}")
    
    # If no tables found with the structured approach, try a simpler line-based approach
    if not tables:
        tables = extract_line_based_tables(text_content)
    
    return tables

def extract_line_based_tables(text_content):
    """
    Fallback method to extract tables based on line patterns.
    """
    tables = {}
    table_count = 0
    
    # Split by potential table boundaries
    sections = re.split(r'-{5,}|={5,}|\*{5,}', text_content)
    
    for section in sections:
        lines = section.strip().split('\n')
        if len(lines) <= 3:  # Too small to be a table
            continue
        
        # Check if this section has consistent patterns that might indicate a table
        data_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line has numeric content
            if re.search(r'\d', line):
                # Split on consistent delimiters or whitespace patterns
                if '|' in line:
                    columns = [col.strip() for col in line.split('|') if col.strip()]
                elif re.search(r'\s{2,}', line):
                    columns = re.split(r'\s{2,}', line)
                else:
                    columns = line.split()
                
                data_lines.append(columns)
        
        if data_lines and len(data_lines) >= 3:  # Need at least a few rows to consider it a table
            # Normalize column count
            max_cols = max(len(row) for row in data_lines)
            normalized_data = [row + [''] * (max_cols - len(row)) for row in data_lines]
            
            # Create DataFrame
            table_df = pd.DataFrame(normalized_data)
            tables[f"Table_{table_count}"] = table_df
            table_count += 1
    
    return tables

def extract_tables_from_pdf(file):
    """
    Extract tables from a PDF file using our enhanced PDF processor.
    
    Args:
        file: A file-like object containing the PDF.
    
    Returns:
        dict: Dictionary with table names as keys and pandas DataFrames as values.
    """
    try:
        # Create a PDF processor instance with the file object
        processor = PDFTableExtractor(file_object=file)
        
        # Extract layout elements and text
        processor.extract_layout_elements()
        processor.extract_text()
        
        # Extract tables with the enhanced processing
        tables = processor.extract_tables()
        
        return tables
    except Exception as e:
        st.error(f"Error extracting tables: {str(e)}")
        return {}

def save_to_excel(tables):
    """
    Save extracted tables to an Excel file.
    
    Args:
        tables: Dictionary with table names as keys and pandas DataFrames as values.
    
    Returns:
        bytes: Excel file as bytes.
    """
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        for sheet_name, df in tables.items():
            # Clean the sheet name (Excel has a 31 character limit and doesn't allow certain characters)
            valid_sheet_name = re.sub(r'[\\/*?:[\]]', '', sheet_name)
            valid_sheet_name = valid_sheet_name[:31]
            
            df.to_excel(writer, sheet_name=valid_sheet_name, index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets[valid_sheet_name]
            for i, col in enumerate(df.columns):
                # Set column width based on max length in column
                max_len = max(df[col].astype(str).map(len).max(), len(str(col))) + 2
                worksheet.set_column(i, i, max_len)
    
    buffer.seek(0)
    return buffer.getvalue()

# Main app
def main():
    # App title
    st.markdown('<div class="title-container"><h1>📊 PDF Table Extractor</h1><p>Extract tables from PDFs with precision and download as Excel</p></div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose an option:", ["Upload Your PDF", "Use Sample PDFs"])
    
    if app_mode == "Upload Your PDF":
        st.markdown('<div class="file-uploader">', unsafe_allow_html=True)
        st.subheader("📄 Upload Your PDF File")
        
        # Instructions
        st.markdown("""
        <div class="instructions">
        <p><strong>How it works:</strong> Upload a PDF file containing tables. Our intelligent algorithm will detect and extract all tables automatically.</p>
        <p><strong>Supported formats:</strong></p>
        <ul>
            <li>Standard tables with borders</li>
            <li>Tables without visible borders</li>
            <li>Irregularly structured tables</li>
            <li>Financial documents and bank statements</li>
            <li>Multi-column layouts</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Drop your PDF here or click to browse", type="pdf")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file is not None:
            with st.spinner("Extracting tables..."):
                # Extract tables
                tables = extract_tables_from_pdf(uploaded_file)
                
                # Count total tables
                total_tables = len(tables)
                
                if total_tables > 0:
                    st.markdown(f'<div class="results-container">', unsafe_allow_html=True)
                    st.markdown(f"<h2>🎉 Successfully Extracted {total_tables} Tables</h2>", unsafe_allow_html=True)
                    
                    # Add a summary of the extraction
                    st.markdown("""
                    <div class="instructions">
                    <p><strong>Extraction complete!</strong> The tables have been successfully identified and processed. You can preview them below or download the complete Excel file.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Convert to Excel
                    excel_data = save_to_excel(tables)
                    
                    # Add download button with better styling
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.download_button(
                            label="📥 Download Excel File",
                            data=excel_data,
                            file_name=f"extracted_tables_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                        )
                    
                    # Display preview of tables
                    st.subheader("Table Previews")
                    for table_name, df in tables.items():
                        with st.expander(f"📋 {table_name}"):
                            st.dataframe(df.head(10), use_container_width=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="results-container">', unsafe_allow_html=True)
                    st.error("No tables found in the uploaded PDF. Please try a different file or check if your PDF contains tabular data.")
                    st.markdown("""
                    <div class="instructions">
                    <p><strong>Troubleshooting tips:</strong></p>
                    <ul>
                        <li>Ensure your PDF contains structured data in a tabular format</li>
                        <li>Check if the PDF has text content (not scanned images)</li>
                        <li>Try our sample PDFs to test the extractor functionality</li>
                    </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
    
    else:  # Use Sample PDFs
        st.markdown('<div class="file-uploader">', unsafe_allow_html=True)
        st.subheader("📚 Sample PDFs")
        
        # Information about sample files
        st.markdown("""
        <div class="instructions">
        <p><strong>Try our demo files:</strong> Select one of the sample PDFs to test the extraction capabilities:</p>
        <ul>
            <li><strong>Bank Statement</strong> - Contains transaction data with complex formatting</li>
            <li><strong>Complex Tables</strong> - Features multiple tables with various styles and structures</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample file selection
        sample_choice = st.radio(
            "Select a sample PDF to process:",
            ["Bank Statement (test3.pdf)", "Complex Tables (test6.pdf)"]
        )
        
        # Map selection to filenames
        sample_file_map = {
            "Bank Statement (test3.pdf)": "test3.pdf",
            "Complex Tables (test6.pdf)": "test6.pdf"
        }
        
        selected_file = sample_file_map[sample_choice]
        
        # Make the button stand out
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            extract_button = st.button("Extract Tables from Sample", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if extract_button:
            with st.spinner(f"Extracting tables from {selected_file}..."):
                # Process the selected sample file
                file_path = os.path.join("samples", selected_file)
                
                try:
                    with open(file_path, "rb") as file:
                        tables = extract_tables_from_pdf(file)
                    
                    # Count total tables
                    total_tables = len(tables)
                    
                    if total_tables > 0:
                        st.markdown(f'<div class="results-container">', unsafe_allow_html=True)
                        st.markdown(f"<h2>🎉 Successfully Extracted {total_tables} Tables</h2>", unsafe_allow_html=True)
                        
                        # Add a summary of the extraction
                        st.markdown("""
                        <div class="instructions">
                        <p><strong>Extraction complete!</strong> The tables have been successfully identified and processed from the sample file. You can preview them below or download as Excel.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Convert to Excel
                        excel_data = save_to_excel(tables)
                        
                        # Add download button
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.download_button(
                                label="📥 Download Excel File",
                                data=excel_data,
                                file_name=f"sample_{selected_file.split('.')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True,
                            )
                        
                        # Display preview of tables
                        st.subheader("Table Previews")
                        for table_name, df in tables.items():
                            with st.expander(f"📋 {table_name}"):
                                st.dataframe(df.head(10), use_container_width=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="results-container">', unsafe_allow_html=True)
                        st.error("No tables found in the sample PDF.")
                        st.markdown('</div>', unsafe_allow_html=True)
                except FileNotFoundError:
                    st.markdown('<div class="results-container">', unsafe_allow_html=True)
                    st.error(f"Sample file {selected_file} not found. Please make sure the file exists in the 'samples' directory.")
                    st.markdown("""
                    <div class="instructions">
                    <p><strong>Setup required:</strong> To use the sample files, please:</p>
                    <ol>
                        <li>Create a directory named 'samples' in the same location as the app.py file</li>
                        <li>Place the test3.pdf and test6.pdf files in this directory</li>
                        <li>Restart the application</li>
                    </ol>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown('<div class="results-container">', unsafe_allow_html=True)
                    st.error(f"Error processing sample file: {str(e)}")
                    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <footer>
        <p>PDF Table Extractor | Developed for Hackathon Assignment</p>
        <p>This tool intelligently extracts tables from PDFs and converts them to Excel format</p>
    </footer>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()