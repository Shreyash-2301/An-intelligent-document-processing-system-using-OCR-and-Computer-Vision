import argparse
import logging
from pathlib import Path
from datetime import datetime

from src.ocr.processor import DocumentProcessor
from src.vision.contour_detector import ContourDetector
from src.ocr.data_extractor import DataExtractor
from src.ocr.report_generator import ReportGenerator

def setup_logger():
    """Set up logging configuration."""
    logger = logging.getLogger('DocumentProcessingPipeline')
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create file handler
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatters
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add formatters to handlers
        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)
        
        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger

def process_document(input_path: str, output_dir: str, ocr_engine: str = 'tesseract'):
    """
    Process a single document through the complete pipeline.
    
    Args:
        input_path (str): Path to input document
        output_dir (str): Directory for output files
        ocr_engine (str): OCR engine to use ('tesseract' or 'easyocr')
    """
    logger = setup_logger()
    logger.info(f"Starting document processing pipeline for: {input_path}")
    
    try:
        # Initialize components
        doc_processor = DocumentProcessor(ocr_engine=ocr_engine)
        contour_detector = ContourDetector()
        data_extractor = DataExtractor()
        report_generator = ReportGenerator(output_dir)
        
        # Process image and detect regions
        regions = contour_detector.process_image(input_path)
        
        # Extract text from each region and combine
        all_text = []
        # First, process the entire image
        text = doc_processor.process(input_path)
        if text:
            all_text.append(text)
        
        # If no regions found, process the entire image
        if not all_text:
            text = doc_processor.process(input_path)
            all_text.append(text)
        
        # Extract structured data
        combined_text = '\n'.join(all_text)
        extracted_data = data_extractor.process_text(combined_text)
        
        # Generate reports
        base_filename = Path(input_path).stem
        reports = report_generator.generate_reports(extracted_data, base_filename)
        
        logger.info("Document processing completed successfully")
        logger.info("Generated reports:")
        for report_type, report_path in reports.items():
            logger.info(f"- {report_type}: {report_path}")
        
        return reports
        
    except Exception as e:
        logger.error(f"Error in document processing pipeline: {str(e)}")
        raise

def main():
    """Main entry point for the document processing pipeline."""
    parser = argparse.ArgumentParser(
        description='Intelligent Document Processing Pipeline'
    )
    parser.add_argument(
        'input_path',
        help='Path to input document or directory of documents'
    )
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Directory for output files'
    )
    parser.add_argument(
        '--ocr-engine',
        choices=['tesseract', 'easyocr'],
        default='tesseract',
        help='OCR engine to use'
    )
    
    args = parser.parse_args()
    
    # Convert to Path objects
    input_path = Path(args.input_path)
    output_dir = Path(args.output_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process single file or directory
    if input_path.is_file():
        process_document(str(input_path), str(output_dir), args.ocr_engine)
    elif input_path.is_dir():
        # Process all supported files in directory
        supported_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.pdf'}
        for file_path in input_path.glob('*'):
            if file_path.suffix.lower() in supported_extensions:
                process_document(str(file_path), str(output_dir), args.ocr_engine)
    else:
        raise FileNotFoundError(f"Input path not found: {input_path}")

if __name__ == '__main__':
    main()