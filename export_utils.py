import os
import tempfile
from datetime import datetime
import streamlit as st
import weasyprint
from utils import highlight_differences

def create_export_html(pdf1_name, pdf2_name, diffs, summary):
    """
    Create HTML content for export with comparison results.
    
    Args:
        pdf1_name (str): The name of the first PDF
        pdf2_name (str): The name of the second PDF
        diffs (list): List of difference objects
        summary (dict): Summary of the comparison
        
    Returns:
        str: HTML content
    """
    # Sanitize content to prevent code display
    def sanitize_content(content):
        # Replace < and > to prevent any HTML/code rendering
        content = content.replace('<', '&lt;').replace('>', '&gt;')
        return content
    # Format current date and time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create HTML document
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Comparison Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
        .header h1 {{
            color: #FF4081;
            margin-bottom: 10px;
        }}
        .logo {{
            position: absolute;
            top: 20px;
            right: 20px;
            font-size: 16px;
            padding: 8px 16px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            background: linear-gradient(45deg, #FF4081, #553BFF);
        }}
        .logo::before {{
            content: "🧠";
            margin-right: 8px;
        }}
        .meta-info {{
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        .summary {{
            background-color: #f9f9f9;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }}
        .summary h2 {{
            color: #553BFF;
            text-align: center;
            margin-top: 0;
        }}
        .stats {{
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
        }}
        .stat-box {{
            flex: 1;
            min-width: 150px;
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        .color-additions {{
            color: #4CAF50;
        }}
        .color-deletions {{
            color: #F44336;
        }}
        .color-modifications {{
            color: #FFC107;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        .legend-item {{
            margin: 10px;
            display: flex;
            align-items: center;
        }}
        .color-box {{
            width: 20px;
            height: 20px;
            margin-right: 5px;
            border-radius: 4px;
        }}
        .bg-green {{
            background-color: #CCFFCC;
        }}
        .bg-red {{
            background-color: #FFCCCC;
        }}
        .bg-yellow {{
            background-color: #FFFFCC;
        }}
        .details {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 30px;
        }}
        .document {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background-color: #fcfcfc;
        }}
        .document h3 {{
            color: #0CA4A5;
            text-align: center;
            margin-top: 0;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }}
        .footer {{
            margin-top: 50px;
            text-align: center;
            font-size: 12px;
            color: #999;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
        @media print {{
            body {{
                padding: 0;
                font-size: 12px;
            }}
            .summary, .document {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="logo">Ideasouq Technologies</div>
    
    <div class="header">
        <h1>PDF Comparison Report</h1>
        <div class="meta-info">Generated on: {current_time}</div>
        <div class="meta-info">Files compared: {pdf1_name} vs {pdf2_name}</div>
    </div>
    
    <div class="summary">
        <h2>Summary of Changes</h2>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-label">Additions</div>
                <div class="stat-value color-additions">{summary['additions']['count']}</div>
                <div class="stat-label">{summary['additions']['words']} words</div>
            </div>
            
            <div class="stat-box">
                <div class="stat-label">Deletions</div>
                <div class="stat-value color-deletions">{summary['deletions']['count']}</div>
                <div class="stat-label">{summary['deletions']['words']} words</div>
            </div>
            
            <div class="stat-box">
                <div class="stat-label">Modifications</div>
                <div class="stat-value color-modifications">{summary['modifications']['count']}</div>
                <div class="stat-label">{summary['modifications']['words_new'] - summary['modifications']['words_old']} word difference</div>
            </div>
            
            <div class="stat-box">
                <div class="stat-label">Unchanged</div>
                <div class="stat-value">{summary['unchanged']['count']}</div>
                <div class="stat-label">sections</div>
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="color-box bg-green"></div>
                <span>Added Content</span>
            </div>
            <div class="legend-item">
                <div class="color-box bg-red"></div>
                <span>Removed Content</span>
            </div>
            <div class="legend-item">
                <div class="color-box bg-yellow"></div>
                <span>Modified Content</span>
            </div>
        </div>
    </div>
    
    <h2 style="text-align: center; color: #553BFF;">Detailed Differences</h2>
    
    <div class="details">
        <div class="document">
            <h3>First PDF</h3>
            {highlight_differences(diffs, 'old')}
        </div>
        
        <div class="document">
            <h3>Second PDF</h3>
            {highlight_differences(diffs, 'new')}
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by PDF Comparison Tool | Ideasouq Technologies</p>
    </div>
</body>
</html>
"""
    return html

def export_as_html(pdf1_name, pdf2_name, diffs, summary):
    """
    Generate and provide an HTML file for download
    
    Args:
        pdf1_name (str): The name of the first PDF
        pdf2_name (str): The name of the second PDF
        diffs (list): List of difference objects
        summary (dict): Summary of the comparison
        
    Returns:
        tuple: (html_string, filename)
    """
    html_content = create_export_html(pdf1_name, pdf2_name, diffs, summary)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comparison_report_{timestamp}.html"
    
    return html_content, filename

def export_as_pdf(pdf1_name, pdf2_name, diffs, summary):
    """
    Generate a PDF file for download
    
    Args:
        pdf1_name (str): The name of the first PDF
        pdf2_name (str): The name of the second PDF
        diffs (list): List of difference objects
        summary (dict): Summary of the comparison
        
    Returns:
        tuple: (pdf_bytes, filename)
    """
    html_content = create_export_html(pdf1_name, pdf2_name, diffs, summary)
    
    # Create a temporary file to store the HTML
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
        f.write(html_content.encode('utf-8'))
        temp_html_path = f.name
    
    try:
        # Convert HTML to PDF
        pdf_bytes = weasyprint.HTML(filename=temp_html_path).write_pdf()
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_report_{timestamp}.pdf"
        
        return pdf_bytes, filename
    finally:
        # Clean up temporary file
        if os.path.exists(temp_html_path):
            os.unlink(temp_html_path)