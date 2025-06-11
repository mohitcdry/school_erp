from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from core.models import Receipt, StudentProfile
from .utils import (
    generate_admit_card_pdf, 
    generate_fee_card_pdf, 
    generate_receipt_pdf,
    generate_bulk_receipts
)
import logging

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET"])
def generate_admit_card(request, student_id):
    """Generate admit card PDF"""
    try:
        student = get_object_or_404(StudentProfile, id=student_id)
        
        # Check permissions
        if not request.user.is_staff and request.user.role not in ['SUPERADMIN', 'ACCOUNTANT']:
            return HttpResponse("Permission denied", status=403)
        
        return generate_admit_card_pdf(student)
        
    except Exception as e:
        logger.error(f"Error in generate_admit_card view: {e}")
        return HttpResponse("Error generating admit card", status=500)

@login_required
@require_http_methods(["GET"])
def generate_fee_card(request, bill_id):
    """Generate fee card PDF"""
    try:
        bill = get_object_or_404(Receipt, id=bill_id)
        
        # Check permissions
        if not request.user.is_staff and request.user.role not in ['SUPERADMIN', 'ACCOUNTANT']:
            return HttpResponse("Permission denied", status=403)
        
        return generate_fee_card_pdf(bill)
        
    except Exception as e:
        logger.error(f"Error in generate_fee_card view: {e}")
        return HttpResponse("Error generating fee card", status=500)

@login_required
@require_http_methods(["GET"])
def generate_receipt(request, bill_id):
    """Generate receipt PDF"""
    try:
        bill = get_object_or_404(Receipt, id=bill_id)
        
        # Check permissions
        if not request.user.is_staff and request.user.role not in ['SUPERADMIN', 'ACCOUNTANT']:
            return HttpResponse("Permission denied", status=403)
        
        return generate_receipt_pdf(bill)
        
    except Exception as e:
        logger.error(f"Error in generate_receipt view: {e}")
        return HttpResponse("Error generating receipt", status=500)

@login_required
@require_http_methods(["POST"])
def generate_bulk_reports(request):
    """Generate bulk reports"""
    try:
        bill_ids = request.POST.getlist('bill_ids')
        report_type = request.POST.get('report_type', 'receipt')
        
        if not bill_ids:
            return JsonResponse({'error': 'No bills selected'}, status=400)
        
        # Check permissions
        if not request.user.is_staff and request.user.role not in ['SUPERADMIN', 'ACCOUNTANT']:
            return HttpResponse("Permission denied", status=403)
        
        bills = Receipt.objects.filter(id__in=bill_ids)
        
        if report_type == 'bulk_receipts':
            return generate_bulk_receipts(bills)
        else:
            return JsonResponse({'error': 'Invalid report type'}, status=400)
        
    except Exception as e:
        logger.error(f"Error in generate_bulk_reports view: {e}")
        return HttpResponse("Error generating bulk reports", status=500)

@login_required
def reports_dashboard(request):
    """Reports dashboard view"""
    context = {
        'total_students': StudentProfile.objects.count(),
        'total_receipts': Receipt.objects.count(),
        'pending_receipts': Receipt.objects.filter(status='PENDING').count(),
        'paid_receipts': Receipt.objects.filter(status='PAID').count(),
    }
    return render(request, 'reports/dashboard.html', context)