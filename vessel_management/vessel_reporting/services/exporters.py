class BaseExporter:
    """Base class for data export operations"""
    
    def __init__(self, data):
        self.data = data
    
    def export(self):
        """Export the data in the specified format"""
        raise NotImplementedError


class JSONExporter(BaseExporter):
    """Exports data in JSON format"""
    
    def export(self):
        """Export data as JSON"""
        return self.data


class CSVExporter(BaseExporter):
    """Exports data in CSV format"""
    
    def export(self):
        """Export data as CSV"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        if self.data:
            writer.writerow(self.data[0].keys())
            
            # Write data rows
            for row in self.data:
                writer.writerow(row.values())
        
        return output.getvalue()


class PDFExporter(BaseExporter):
    """Exports data in PDF format"""
    
    def export(self):
        """Export data as PDF"""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        import io
        
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []
        
        # Convert data to table format
        if self.data:
            # Get headers
            headers = list(self.data[0].keys())
            
            # Prepare table data
            table_data = [headers]
            for row in self.data:
                table_data.append([row[header] for header in headers])
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        # Build PDF
        doc.build(elements)
        return output.getvalue()


class ExporterFactory:
    """Factory class for creating exporters"""
    
    @staticmethod
    def create_exporter(data, format_type):
        """Create an exporter instance based on the format type"""
        exporters = {
            'json': JSONExporter,
            'csv': CSVExporter,
            'pdf': PDFExporter
        }
        
        exporter_class = exporters.get(format_type.lower())
        if not exporter_class:
            raise ValueError(f"Unsupported export format: {format_type}")
        
        return exporter_class(data) 