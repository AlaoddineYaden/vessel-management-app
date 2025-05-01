import json
import csv
from io import StringIO, BytesIO
from abc import ABC, abstractmethod
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.utils import timezone

class Exporter(ABC):
    """Base class for report exporters"""
    
    @abstractmethod
    def export(self, data):
        """Export the report data in the specified format"""
        pass

class BaseExporter:
    def export(self, data):
        raise NotImplementedError("Subclasses must implement export()")

class JSONExporter(BaseExporter):
    """Export report data as JSON"""
    
    def export(self, data):
        return json.dumps(data, ensure_ascii=False, indent=2)

class CSVExporter(BaseExporter):
    """Export report data as CSV with enhanced formatting"""
    
    def _format_header(self, text):
        """Format header text by capitalizing words and replacing underscores"""
        return text.replace('_', ' ').title()

    def _format_value(self, value):
        """Format values for better readability"""
        if isinstance(value, bool):
            return 'Yes' if value else 'No'
        elif value is None:
            return 'N/A'
        elif isinstance(value, (int, float)):
            return f"{value:,}"
        elif isinstance(value, dict):
            # Convert dictionary to a readable string
            return '; '.join(f"{k}: {v}" for k, v in value.items())
        elif isinstance(value, list):
            # Convert list to a readable string
            return '; '.join(str(item) for item in value)
        return str(value)

    def flatten_dict(self, d, parent_key='', sep=' > '):
        """Flatten a nested dictionary with improved key formatting"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, self._format_header(new_key), sep=sep).items())
            else:
                items.append((self._format_header(new_key), self._format_value(v)))
        return dict(items)

    def export(self, data):
        output = StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        
        # Add report metadata
        writer.writerow(['Report Generated On', timezone.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])  # Empty row for spacing
        
        # Handle different data types
        if isinstance(data, list):
            if len(data) > 0 and isinstance(data[0], dict):
                # Handle list of dictionaries
                flat_data = [self.flatten_dict(item) for item in data]
                
                # Get all unique headers
                headers = []
                for item in flat_data:
                    for key in item.keys():
                        if key not in headers:
                            headers.append(key)
                
                # Write headers
                writer.writerow(headers)
                
                # Write data rows
                for item in flat_data:
                    row = [item.get(header, 'N/A') for header in headers]
                    writer.writerow(row)
            else:
                # Handle simple list
                writer.writerow(['Item', 'Value'])
                for i, item in enumerate(data, 1):
                    writer.writerow([f"Item {i}", self._format_value(item)])
        elif isinstance(data, dict):
            # Handle dictionary
            flat_data = self.flatten_dict(data)
            writer.writerow(['Field', 'Value'])
            for key, value in flat_data.items():
                writer.writerow([key, value])
        else:
            # Handle single value
            writer.writerow(['Value'])
            writer.writerow([self._format_value(data)])
        
        return output.getvalue()

class PDFExporter(BaseExporter):
    """Export report data as PDF with enhanced formatting"""
    
    def _format_header(self, text):
        """Format header text by capitalizing words and replacing underscores"""
        return text.replace('_', ' ').title()

    def _format_value(self, value):
        """Format values for better readability"""
        if isinstance(value, bool):
            return 'Yes' if value else 'No'
        elif value is None:
            return 'N/A'
        elif isinstance(value, (int, float)):
            return f"{value:,}"
        return str(value)

    def export(self, data):
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        styles = getSampleStyleSheet()
        elements = []

        # Add title and timestamp
        title_style = styles['Heading1']
        title_style.alignment = 1  # Center alignment
        title = Paragraph("Vessel Management Report", title_style)
        elements.append(title)
        
        # Add timestamp
        date_style = styles['Normal']
        date_style.alignment = 1
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        date_text = Paragraph(f"Generated on: {timestamp}", date_style)
        elements.append(date_text)
        elements.append(Spacer(1, 20))

        # Convert data to table format
        if isinstance(data, list):
            if len(data) > 0 and isinstance(data[0], dict):
                # Get headers from first dictionary and format them
                headers = [self._format_header(h) for h in data[0].keys()]
                table_data = [headers]
                # Add data rows with formatted values
                for item in data:
                    row = [self._format_value(item.get(header.lower().replace(' ', '_'), '')) 
                          for header in headers]
                    table_data.append(row)
            else:
                # Simple list
                table_data = [["Item", "Value"]]
                for item in data:
                    table_data.append(["", self._format_value(item)])
        elif isinstance(data, dict):
            # Dictionary becomes two-column table with formatted headers and values
            table_data = [["Field", "Value"]]
            for key, value in data.items():
                table_data.append([self._format_header(key), self._format_value(value)])
        else:
            # Single value
            table_data = [["Value"], [self._format_value(data)]]

        # Calculate column widths based on content
        col_widths = [doc.width / len(table_data[0])] * len(table_data[0])

        # Create table with calculated widths
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Enhanced table styling
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            
            # Grid styling
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBEFORE', (0, 0), (0, -1), 1.5, colors.HexColor('#2c3e50')),
            ('LINEAFTER', (-1, 0), (-1, -1), 1.5, colors.HexColor('#2c3e50')),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#2c3e50')),
            ('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.HexColor('#2c3e50')),
            
            # Alternating row colors
            *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9f9f9')) 
              for i in range(2, len(table_data), 2)]
        ]))
        elements.append(table)

        # Build PDF
        doc.build(elements)
        return buffer.getvalue()

class ExporterFactory:
    """Factory for creating exporters"""
    
    @staticmethod
    def create_exporter(format_type):
        format_type = format_type.upper()
        if format_type == 'JSON':
            return JSONExporter()
        elif format_type == 'CSV':
            return CSVExporter()
        elif format_type == 'PDF':
            return PDFExporter()
        else:
            raise ValueError(f"Unsupported format type: {format_type}") 