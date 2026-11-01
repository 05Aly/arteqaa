from celery import shared_task
from reportlab.pdfgen import canvas
from django.conf import settings
import os

@shared_task
def generate_certificate(user_full_name, course_title, output_path):
    c = canvas.Canvas(output_path)
    c.setFont("Helvetica", 30)
    c.drawCentredString(300, 500, "Certificate of Completion")
    c.setFont("Helvetica", 20)
    c.drawCentredString(300, 450, f"This is to certify that")
    c.setFont("Helvetica-Bold", 25)
    c.drawCentredString(300, 400, user_full_name)
    c.setFont("Helvetica", 20)
    c.drawCentredString(300, 350, f"has successfully completed the course")
    c.setFont("Helvetica-Bold", 25)
    c.drawCentredString(300, 300, course_title)
    c.save()
    return output_path
