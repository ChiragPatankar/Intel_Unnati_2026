"""
PDF Generator Service
Generates filled PDF forms using ReportLab
"""
import io
from typing import Dict, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime

from app.services.form_templates import FormTemplatesService


class PDFGeneratorService:
    """Service for generating filled PDF forms"""
    
    def __init__(self):
        self.form_templates = FormTemplatesService()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='FormTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#475569'),
            fontName='Helvetica-Bold',
            spaceAfter=4
        ))
        
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#0f172a'),
            fontName='Helvetica',
            spaceAfter=12,
            leftIndent=20
        ))
    
    def generate_filled_form(
        self,
        form_id: str,
        form_data: Dict[str, str],
        extracted_entities: Optional[Dict] = None
    ) -> bytes:
        """
        Generate a filled PDF form
        
        Args:
            form_id: The form template ID
            form_data: Dictionary of form field values
            extracted_entities: Original extracted entities (for reference)
            
        Returns:
            PDF file as bytes
        """
        template = self.form_templates.get_template(form_id)
        if not template:
            raise ValueError(f"Form template '{form_id}' not found")
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build PDF content
        story = []
        
        # Title
        title = Paragraph(template.name, self.styles['FormTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Form ID and Date
        form_info = [
            f"<b>Form ID:</b> {form_id.upper()}",
            f"<b>Generated:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        ]
        info_table = Table([[Paragraph(info, self.styles['Normal']) for info in form_info]], colWidths=[3*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#64748b')),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Form Fields
        for field_name, field_config in template.fields.items():
            # Handle both direct value and dict with value
            raw_value = form_data.get(field_name, "")
            if isinstance(raw_value, dict):
                value = raw_value.get("value", "")
            else:
                value = str(raw_value) if raw_value else ""
            
            # Field Label
            label = Paragraph(
                f"<b>{field_config['label']}</b>",
                self.styles['FieldLabel']
            )
            story.append(label)
            
            # Field Value
            if value:
                # Format value based on type
                if field_config.get('type') == 'date' and value:
                    # Try to format date
                    formatted_value = str(value)
                elif field_config.get('type') == 'textarea':
                    formatted_value = str(value).replace('\n', '<br/>')
                else:
                    formatted_value = str(value)
                
                value_para = Paragraph(
                    formatted_value,
                    self.styles['FieldValue']
                )
            else:
                value_para = Paragraph(
                    "<i>Not provided</i>",
                    self.styles['FieldValue']
                )
            
            story.append(value_para)
            story.append(Spacer(1, 0.15*inch))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        footer = Paragraph(
            "<i>This form was auto-generated by Form Filling Assistant. "
            "Please review all information before submission.</i>",
            self.styles['Normal']
        )
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def generate_preview_html(
        self,
        form_id: str,
        form_data: Dict[str, any]
    ) -> str:
        """
        Generate HTML preview of the form (for frontend display)
        
        Args:
            form_id: The form template ID
            form_data: Dictionary of form field values
            
        Returns:
            HTML string
        """
        template = self.form_templates.get_template(form_id)
        if not template:
            return "<p>Form template not found</p>"
        
        html = f"""
        <div class="form-preview">
            <div class="form-header">
                <h2>{template.name}</h2>
                <p class="form-id">Form ID: {form_id.upper()}</p>
            </div>
            <div class="form-fields">
        """
        
        for field_name, field_config in template.fields.items():
            value = form_data.get(field_name, "")
            required_badge = '<span class="required-badge">Required</span>' if field_config.get('required') else ''
            
            html += f"""
                <div class="form-field">
                    <label>
                        {field_config['label']}
                        {required_badge}
                    </label>
                    <div class="field-value">
                        {value if value else '<span class="empty">Not provided</span>'}
                    </div>
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html


# Singleton instance
pdf_generator_service = PDFGeneratorService()

