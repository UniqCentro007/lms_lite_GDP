from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
import io
import uuid


class Certificate(models.Model):
    """
    Certificate model for course completion certificates.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
        limit_choices_to={'role': 'student'}
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    enrollment = models.ForeignKey(
        'enrollments.Enrollment',
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    certificate_number = models.CharField(max_length=100, unique=True, blank=True)
    pdf_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    is_approved = models.BooleanField(default=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='approved_certificates',
        blank=True,
        null=True,
        limit_choices_to={'role': 'admin'}
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'certificates'
        unique_together = ['student', 'course']
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"Certificate - {self.student.username} - {self.course.title}"
    
    def generate_certificate_number(self):
        """Generate a unique certificate number."""
        if not self.certificate_number:
            self.certificate_number = f"CERT-{uuid.uuid4().hex[:12].upper()}-{self.course.id}-{self.student.id}"
        return self.certificate_number
    
    def generate_pdf(self):
        """Generate PDF certificate using ReportLab."""
        from django.conf import settings
        from django.utils import timezone
        
        # Generate certificate number
        self.generate_certificate_number()
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=36,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor('#424242'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#212121'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        cert_number_style = ParagraphStyle(
            'CertNumber',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#757575'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Build PDF content
        elements.append(Spacer(1, 1.5*inch))
        
        # Title
        elements.append(Paragraph("CERTIFICATE OF COMPLETION", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Subtitle
        elements.append(Paragraph("This is to certify that", subtitle_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Student name
        student_name = f"{self.student.get_full_name() or self.student.username}"
        name_style = ParagraphStyle(
            'NameStyle',
            parent=styles['Heading2'],
            fontSize=28,
            textColor=colors.HexColor('#0d47a1'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph(student_name, name_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Course completion text
        completion_text = f"has successfully completed the course<br/>{self.course.title}"
        elements.append(Paragraph(completion_text, body_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Date
        date_text = f"Issued on {timezone.now().strftime('%B %d, %Y')}"
        elements.append(Paragraph(date_text, body_style))
        elements.append(Spacer(1, 0.4*inch))
        
        # Certificate number
        elements.append(Paragraph(f"Certificate Number: {self.certificate_number}", cert_number_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Save to file field
        filename = f"certificate_{self.certificate_number}.pdf"
        self.pdf_file.save(filename, ContentFile(pdf_content), save=False)
        
        return self.pdf_file

