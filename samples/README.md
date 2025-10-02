# Sample Usage Examples

This directory contains example documents and their processed outputs to demonstrate the capabilities of the Intelligent Document Processing System.

## Sample Documents

### 1. Technical Document (T1.jpeg)
- Input: [T1.jpeg](images/T1.jpeg)
- Outputs:
  - [JSON Data](output/T1.json)
  - [Summary Report](output/T1_summary.png)
  - [CSV Report](output/T1.csv)
  - [Full Report](output/T1.docx)

### Processing Results

The system successfully extracted:
- Document metadata
- Technical specifications
- Measurements and values
- Tabular data

## Running the Examples

To process these samples yourself:

```bash
# Process a single image
python main.py samples/images/T1.jpeg --output-dir samples/output

# Process all images in the samples directory
python main.py samples/images --output-dir samples/output
```

## Generated Reports

The system generates multiple report formats:
1. JSON: Structured data extraction
2. CSV: Tabular format for data analysis
3. DOCX: Formatted document with extracted information
4. PNG: Visualizations of detected regions and data

## Adding New Samples

To add your own samples:
1. Add your input document to `samples/images/`
2. Run the processing pipeline
3. Check the outputs in `samples/output/`