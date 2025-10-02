import re
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

class DataExtractor:
    """A class to extract structured data from OCR text."""
    
    def __init__(self):
        """Initialize the DataExtractor with common regex patterns."""
        self.logger = self._setup_logger()
        
        # Common regex patterns
        self.patterns = {
            'date': r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
            'email': r'[\w\.-]+@[\w\.-]+\.\w+',
            'phone': r'\+?\d{1,3}[-.]?\d{3}[-.]?\d{4}',
            'amount': r'\$?\d+(?:,\d{3})*(?:\.\d{2})?',
            'measurement': r'\d+(?:\.\d+)?\s*(?:mm|cm|m|kg|g|ml|l)',
            'document_id': r'(?i)(?:id|doc|document)\s*#?\s*[\w-]+',
        }
    
    def _setup_logger(self):
        """Set up logging configuration."""
        logger = logging.getLogger('DataExtractor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def find_pattern(self, text: str, pattern: str) -> List[str]:
        """
        Find all occurrences of a pattern in text.
        
        Args:
            text (str): Text to search in
            pattern (str): Regex pattern to search for
            
        Returns:
            List[str]: List of matched strings
        """
        try:
            matches = re.findall(pattern, text)
            return matches
        except Exception as e:
            self.logger.error(f"Error matching pattern '{pattern}': {str(e)}")
            return []
    
    def extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        return self.find_pattern(text, self.patterns['date'])
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        return self.find_pattern(text, self.patterns['email'])
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        return self.find_pattern(text, self.patterns['phone'])
    
    def extract_amounts(self, text: str) -> List[str]:
        """Extract monetary amounts from text."""
        return self.find_pattern(text, self.patterns['amount'])
    
    def extract_measurements(self, text: str) -> List[str]:
        """Extract measurements from text."""
        return self.find_pattern(text, self.patterns['measurement'])
    
    def extract_document_ids(self, text: str) -> List[str]:
        """Extract document IDs from text."""
        return self.find_pattern(text, self.patterns['document_id'])
    
    def extract_tables(self, text: str) -> List[List[str]]:
        """
        Extract tabular data from text.
        This is a simple implementation that looks for consistent delimiters.
        
        Args:
            text (str): Text containing tabular data
            
        Returns:
            List[List[str]]: Extracted table as list of rows
        """
        try:
            table = []
            lines = text.split('\n')
            
            for line in lines:
                # Try different delimiters
                for delimiter in ['\t', '  ', '|', ',']:
                    if delimiter in line:
                        # Split and clean row data
                        row = [cell.strip() for cell in line.split(delimiter)
                              if cell.strip()]
                        if len(row) > 1:  # Only consider rows with multiple cells
                            table.append(row)
                            break
            
            return table
        except Exception as e:
            self.logger.error(f"Error extracting table data: {str(e)}")
            return []
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Process text and extract all available data.
        
        Args:
            text (str): Text to process
            
        Returns:
            Dict[str, Any]: Dictionary containing all extracted data
        """
        try:
            self.logger.info("Starting data extraction")
            
            result = {
                'dates': self.extract_dates(text),
                'emails': self.extract_emails(text),
                'phone_numbers': self.extract_phone_numbers(text),
                'amounts': self.extract_amounts(text),
                'measurements': self.extract_measurements(text),
                'document_ids': self.extract_document_ids(text),
                'tables': self.extract_tables(text),
                'raw_text': text,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("Data extraction completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing text: {str(e)}")
            raise