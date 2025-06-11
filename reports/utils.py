from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def amount_to_words(amount):
    """Convert numeric amount to words (basic implementation)"""
    try:
        amount = int(float(amount))
        
        # Basic implementation - you can enhance this
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
                'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
                'Seventeen', 'Eighteen', 'Nineteen']
        
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        if amount == 0:
            return "Zero Rupees Only"
        
        def convert_hundreds(n):
            result = ""
            if n >= 100:
                result += ones[n // 100] + " Hundred "
                n %= 100
            if n >= 20:
                result += tens[n // 10] + " "
                n %= 10
            if n > 0:
                result += ones[n] + " "
            return result
        
        if amount < 1000:
            return convert_hundreds(amount).strip() + " Rupees Only"
        elif amount < 100000:
            thousands = amount // 1000
            remainder = amount % 1000
            result = convert_hundreds(thousands).strip() + " Thousand "
            if remainder > 0:
                result += convert_hundreds(remainder).strip()
            return result.strip() + " Rupees Only"
        elif amount < 10000000:
            lakhs = amount // 100000
            remainder = amount % 100000
            result = convert_hundreds(lakhs).strip() + " Lakh "
            if remainder >= 1000:
                thousands = remainder // 1000
                result += convert_hundreds(thousands).strip() + " Thousand "
                remainder %= 1000
            if remainder > 0:
                result += convert_hundreds(remainder).strip()
            return result.strip() + " Rupees Only"
        else:
            return f"Rupees {amount:,} Only"
            
    except (ValueError, TypeError):
        return f"Rupees {amount} Only"


def generate_admit_card_pdf(student):
    """Generate admit card PDF for a student"""
    try:
        template = get_template('reports/admit_card.html')
        context = {
            'student': student,
            'current_year': student.date_enrolled.year if student.date_enrolled else 2024,
        }
        
        html_string = template.render(context)
        
        font_config = FontConfiguration()
        html = HTML(string=html_string, base_url='.')
        css = CSS(string='''
            @page { size: A4; margin: 1cm; }
            body { font-family: Arial, sans-serif; font-size: 12px; }
            .admit-card { border: 3px solid #000; }
            .header { text-align: center; background-color: #f0f0f0; padding: 15px; }
            .student-section { display: flex; gap: 20px; margin: 20px 0; }
            .student-details { flex: 1; background-color: #f9f9f9; padding: 15px; }
            .photo-section { width: 120px; height: 150px; border: 2px solid #000; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #000; padding: 8px; }
        ''')
        
        pdf = html.write_pdf(stylesheets=[css], font_config=font_config)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="admit_card_{student.student_id}.pdf"'
        return response
        
    except Exception as e:
        logger.error(f"Error generating admit card PDF: {e}")
        response = HttpResponse("Error generating PDF", status=500)
        return response

def generate_fee_card_pdf(bill):
    """Generate fee card PDF"""
    try:
        template = get_template('reports/fee_card.html')
        context = {
            'bill': bill,
            'student': bill.student,
            'items': bill.items.all(),
            'amount_in_words': amount_to_words(bill.total_amount),
            'document_type': 'Fee Card',
        }
        
        html_string = template.render(context)
        
        font_config = FontConfiguration()
        html = HTML(string=html_string, base_url='.')
        css = CSS(string='''
            @page { size: A4; margin: 1cm; }
            body { font-family: Arial, sans-serif; font-size: 12px; }
            .header { text-align: center; margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            th, td { border: 1px solid #000; padding: 8px; text-align: left; }
            .amount { text-align: right; font-weight: bold; }
            .summary table { margin-top: 20px; border: 2px solid #000; }
        ''')
        
        pdf = html.write_pdf(stylesheets=[css], font_config=font_config)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="fee_card_{bill.bill_number}.pdf"'
        return response
        
    except Exception as e:
        logger.error(f"Error generating fee card PDF: {e}")
        response = HttpResponse("Error generating PDF", status=500)
        return response

def generate_receipt_pdf(bill):
    """Generate receipt PDF"""
    try:
        template = get_template('reports/receipt.html')
        context = {
            'bill': bill,
            'student': bill.student,
            'items': bill.items.all(),
            'amount_in_words': amount_to_words(bill.paid_amount),
            'document_type': 'Receipt',
        }
        
        html_string = template.render(context)
        
        font_config = FontConfiguration()
        html = HTML(string=html_string, base_url='.')
        css = CSS(string='''
            @page { size: A4; margin: 1cm; }
            body { font-family: Arial, sans-serif; font-size: 12px; }
            .header { text-align: center; margin-bottom: 20px; }
            .receipt-info { margin: 20px 0; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #000; padding: 8px; }
            .amount { text-align: right; font-weight: bold; }
        ''')
        
        pdf = html.write_pdf(stylesheets=[css], font_config=font_config)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{bill.bill_number}.pdf"'
        return response
        
    except Exception as e:
        logger.error(f"Error generating receipt PDF for bill {bill.bill_number}: {str(e)}", exc_info=True)
        response = HttpResponse(f"Unable to generate receipt. Please contact support. Error ID: {bill.bill_number}", status=500)
        return response

# Utility function for bulk report generation
def generate_bulk_receipts(bills_queryset):
    """Generate multiple receipts in a single PDF with exact same format"""
    try:
        # Pre-calculate amount in words for each bill
        bills_with_words = []
        for bill in bills_queryset:
            bill.amount_in_words = amount_to_words(bill.paid_amount)
            bills_with_words.append(bill)
        
        template = get_template('reports/bulk_receipts.html')
        context = {
            'bills': bills_with_words,
            'total_bills': bills_queryset.count(),
        }
        
        html_string = template.render(context)
        
        font_config = FontConfiguration()
        html = HTML(string=html_string, base_url='.')
        
        # Use same CSS as individual receipts
        css = CSS(string='''
            @page { size: A4; margin: 1cm; }
            body { font-family: Arial, sans-serif; font-size: 12px; line-height: 1.4; }
            .page-break { page-break-after: always; }
        ''')
        
        pdf = html.write_pdf(stylesheets=[css], font_config=font_config)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="bulk_receipts_{bills_queryset.count()}_receipts.pdf"'
        return response
        
    except Exception as e:
        logger.error(f"Error generating bulk receipts PDF: {e}")
        response = HttpResponse("Error generating PDF", status=500)
        return response