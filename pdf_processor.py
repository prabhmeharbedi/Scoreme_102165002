import re
import pandas as pd
import io
import os
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox, LTTextLine, LTLine, LTRect, LTFigure, LTChar
from pdfminer.utils import Rect
from collections import defaultdict

class PDFTableExtractor:
    """
    Utility class for extracting tables from PDFs using pdfminer.six for more precise extraction
    """
    def __init__(self, file_path=None, file_object=None):
        """
        Initialize with either a file path or a file object
        """
        self.file_path = file_path
        self.file_object = file_object
        self.pdf_text = ""
        self.layout_elements = []
        self.text_boxes = []
        self.lines = []
        self.rects = []
        
    def extract_text(self):
        """
        Extract text from PDF using PyPDF2
        """
        try:
            if self.file_path:
                with open(self.file_path, 'rb') as file:
                    reader = PdfReader(file)
                    for page in reader.pages:
                        self.pdf_text += page.extract_text() + "\n\n"
            elif self.file_object:
                # Save current position
                position = self.file_object.tell()
                # Reset to beginning
                self.file_object.seek(0)
                
                reader = PdfReader(self.file_object)
                for page in reader.pages:
                    self.pdf_text += page.extract_text() + "\n\n"
                
                # Reset file position to what it was
                self.file_object.seek(position)
            else:
                raise ValueError("No file path or file object provided")
                
            return self.pdf_text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_layout_elements(self):
        """
        Extract layout elements (textboxes, lines, rectangles) using pdfminer.six
        """
        try:
            # Clear previous data
            self.layout_elements = []
            self.text_boxes = []
            self.lines = []
            self.rects = []
            
            # Use the appropriate source
            if self.file_path:
                pages = extract_pages(self.file_path)
            elif self.file_object:
                # Save current position
                position = self.file_object.tell()
                # Reset to beginning
                self.file_object.seek(0)
                
                pages = extract_pages(io.BytesIO(self.file_object.read()))
                
                # Reset file position to what it was
                self.file_object.seek(position)
            else:
                raise ValueError("No file path or file object provided")
            
            # Process each page
            for page_num, page in enumerate(pages):
                page_elements = []
                page_text_boxes = []
                page_lines = []
                page_rects = []
                
                # Extract all elements
                for element in page:
                    page_elements.append(element)
                    
                    # Categorize elements
                    if isinstance(element, LTTextBox):
                        page_text_boxes.append(element)
                    elif isinstance(element, LTLine):
                        page_lines.append(element)
                    elif isinstance(element, LTRect):
                        page_rects.append(element)
                
                # Store elements for this page
                self.layout_elements.append(page_elements)
                self.text_boxes.append(page_text_boxes)
                self.lines.append(page_lines)
                self.rects.append(page_rects)
                
            return self.layout_elements
        except Exception as e:
            raise Exception(f"Error extracting layout elements: {str(e)}")
    
    def detect_table_type(self):
        """
        Detect the type of tables in the PDF
        """
        if not self.pdf_text:
            self.extract_text()
            
        if "BANK NAME" in self.pdf_text or "Statement of account" in self.pdf_text:
            return "bank_statement"
        elif re.search(r'\$\d+\s+\$\s+\$\d+\s+\$', self.pdf_text):
            return "code_based"
        else:
            return "general"
    
    def extract_tables(self):
        """
        Extract tables from PDF based on detected type, with enhanced layout analysis
        """
        if not self.pdf_text:
            self.extract_text()
            
        # Extract layout elements if not done already
        if not self.layout_elements:
            self.extract_layout_elements()
            
        table_type = self.detect_table_type()
        
        # Try layout-based extraction first
        layout_tables = self.extract_tables_from_layout()
        
        # If layout extraction found tables, return those
        if layout_tables:
            return layout_tables
        
        # Otherwise, fall back to text-based methods
        if table_type == "bank_statement":
            tables = self.extract_bank_statement_tables()
            account_info = self.extract_vertical_tables()
            tables.update(account_info)
            return tables
        elif table_type == "code_based":
            return self.extract_code_based_tables()
        else:
            general_tables = self.extract_general_tables()
            if not general_tables:
                general_tables = self.extract_line_based_tables()
            return general_tables
    
    def extract_tables_from_layout(self):
        """
        Extract tables by analyzing the layout elements (text boxes and lines)
        """
        tables = {}
        table_count = 0
        
        # Process each page
        for page_num, (text_boxes, lines, rects) in enumerate(zip(self.text_boxes, self.lines, self.rects)):
            # Skip pages without enough elements
            if len(text_boxes) < 3:
                continue
                
            # First, detect tables based on rectangles (bordered tables)
            bordered_tables = self.detect_bordered_tables(text_boxes, rects, page_num)
            tables.update(bordered_tables)
            table_count += len(bordered_tables)
            
            # Next, detect tables based on aligned text boxes (borderless tables)
            if not bordered_tables:
                borderless_tables = self.detect_borderless_tables(text_boxes, page_num)
                tables.update(borderless_tables)
                table_count += len(borderless_tables)
        
        return tables
    
    def detect_bordered_tables(self, text_boxes, rects, page_num):
        """
        Detect tables that have borders (rectangles) around them
        """
        tables = {}
        
        # Skip if no rectangles
        if not rects:
            return tables
            
        # Find potential table rectangles (larger rectangles that might contain tables)
        potential_table_rects = [rect for rect in rects if rect.height > 50 and rect.width > 100]
        
        for i, table_rect in enumerate(potential_table_rects):
            # Find all text boxes within this rectangle
            contained_text_boxes = []
            for box in text_boxes:
                if (box.x0 >= table_rect.x0 and box.x1 <= table_rect.x1 and
                    box.y0 >= table_rect.y0 and box.y1 <= table_rect.y1):
                    contained_text_boxes.append(box)
            
            # Skip if not enough text boxes
            if len(contained_text_boxes) < 3:
                continue
                
            # Sort text boxes from top to bottom
            contained_text_boxes.sort(key=lambda box: -box.y1)  # Negative because PDF coordinates are bottom-up
            
            # Convert to rows and columns
            table_data = self.convert_text_boxes_to_table(contained_text_boxes)
            
            if table_data:
                table_name = f"Bordered_Table_Page{page_num+1}_{i+1}"
                tables[table_name] = pd.DataFrame(table_data)
        
        return tables
    
    def detect_borderless_tables(self, text_boxes, page_num):
        """
        Detect tables without borders by analyzing alignment of text boxes
        """
        tables = {}
        
        # Skip if not enough text boxes
        if len(text_boxes) < 5:
            return tables
            
        # Sort text boxes from top to bottom
        text_boxes.sort(key=lambda box: -box.y1)  # Negative because PDF coordinates are bottom-up
        
        # Group text boxes by similar y-positions (potential rows)
        row_groups = self.group_by_position(text_boxes, 'y', threshold=10)
        
        # Filter groups: keep only those with multiple text boxes (potential table rows)
        potential_rows = [group for group in row_groups if len(group) >= 2]
        
        # Skip if not enough potential rows
        if len(potential_rows) < 3:
            return tables
            
        # For each group of potential rows, try to detect a table
        i = 0
        while i < len(potential_rows) - 2:  # Need at least 3 rows
            # Check if this and the next few rows have similar number of text boxes
            row_lens = [len(potential_rows[i+j]) for j in range(3)]  # Check 3 consecutive rows
            
            # If the rows have similar number of elements, they might form a table
            if max(row_lens) - min(row_lens) <= 1 and min(row_lens) >= 2:
                # Find how many consecutive rows match this pattern
                j = 3
                while i + j < len(potential_rows):
                    if abs(len(potential_rows[i+j]) - len(potential_rows[i])) <= 1:
                        j += 1
                    else:
                        break
                
                # Extract this table (rows i through i+j-1)
                table_rows = potential_rows[i:i+j]
                
                # Convert to a structured table
                table_data = []
                for row in table_rows:
                    # Sort cells from left to right
                    row.sort(key=lambda box: box.x0)
                    # Extract text from each cell
                    table_data.append([box.get_text().strip() for box in row])
                
                # Normalize the table (make sure all rows have the same number of columns)
                max_cols = max(len(row) for row in table_data)
                table_data = [row + [''] * (max_cols - len(row)) for row in table_data]
                
                # Create a DataFrame
                table_name = f"Borderless_Table_Page{page_num+1}_{len(tables)+1}"
                tables[table_name] = pd.DataFrame(table_data)
                
                # Move past this table
                i += j
            else:
                i += 1
        
        return tables
    
    def group_by_position(self, elements, axis, threshold=10):
        """
        Group elements that have similar positions along an axis
        
        Args:
            elements: List of layout elements
            axis: 'x' for horizontal or 'y' for vertical grouping
            threshold: Maximum difference in position to be considered the same group
            
        Returns:
            List of groups, where each group is a list of elements
        """
        if not elements:
            return []
            
        # Sort elements by the chosen axis
        if axis == 'x':
            sorted_elements = sorted(elements, key=lambda e: e.x0)
        else:  # axis == 'y'
            sorted_elements = sorted(elements, key=lambda e: -e.y0)  # Negative for top-to-bottom sorting
        
        groups = []
        current_group = [sorted_elements[0]]
        current_pos = getattr(sorted_elements[0], f"{axis}0")
        
        for element in sorted_elements[1:]:
            element_pos = getattr(element, f"{axis}0")
            
            if abs(element_pos - current_pos) <= threshold:
                # Element belongs to the current group
                current_group.append(element)
            else:
                # Start a new group
                groups.append(current_group)
                current_group = [element]
                current_pos = element_pos
        
        # Don't forget the last group
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def convert_text_boxes_to_table(self, text_boxes):
        """
        Convert a list of text boxes to a structured table
        """
        if not text_boxes:
            return []
            
        # Group text boxes by similar y-positions (rows)
        row_groups = self.group_by_position(text_boxes, 'y')
        
        # Convert each row group to a list of text values
        table_data = []
        for row in row_groups:
            # Sort cells from left to right
            row.sort(key=lambda box: box.x0)
            # Extract text from each cell
            table_data.append([box.get_text().strip() for box in row])
        
        # Normalize the table (make sure all rows have the same number of columns)
        if table_data:
            max_cols = max(len(row) for row in table_data)
            table_data = [row + [''] * (max_cols - len(row)) for row in table_data]
        
        return table_data
    
    def extract_bank_statement_tables(self):
        """
        Extract tables from bank statements
        """
        # Split by pages or sections
        sections = re.split(r'Page No: \d+|Statement of account', self.pdf_text)
        
        transactions = []
        
        # Regular expression to match transaction lines
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
        return self.extract_general_tables()
    
    def extract_vertical_tables(self):
        """
        Extract vertical tables (key-value pairs)
        """
        # Split text into lines
        lines = self.pdf_text.split('\n')
        
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
    
    def extract_code_based_tables(self):
        """
        Extract tables with code-based structure
        """
        # Split text into lines
        lines = self.pdf_text.split('\n')
        
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
                print(f"Error processing table {i+1}: {str(e)}")
        
        return processed_tables
    
    def extract_general_tables(self):
        """
        Extract general tables based on text structure
        """
        tables = {}
        table_count = 0
        
        # Split text into lines
        lines = self.pdf_text.split('\n')
        
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
                            print(f"Error creating table: {e}")
                    
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
                print(f"Error creating last table: {e}")
        
        return tables
    
    def extract_line_based_tables(self):
        """
        Fallback method for table extraction
        """
        tables = {}
        table_count = 0
        
        # Split by potential table boundaries
        sections = re.split(r'-{5,}|={5,}|\*{5,}', self.pdf_text)
        
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