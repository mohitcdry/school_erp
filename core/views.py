from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import StudentProfile, Receipt, FeeStructure, BillItem 
from .serializers import StudentProfileSerializer, ReceiptSerializer, FeeStructureSerializer, BillItemSerializer  
import logging

logger = logging.getLogger(__name__)

class StudentViewSet(viewsets.ModelViewSet):
    """
    Simplified for prototype:
    - All authenticated users can view students
    - Only SUPERADMIN can create/update/delete
    """
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]  
    
    def get_queryset(self):
        """Simple role-based filtering"""
        user = self.request.user
        if user.role == 'SUPERADMIN':
            return StudentProfile.objects.all()
        elif user.role in ['TEACHER', 'ACCOUNTANT']:
            return StudentProfile.objects.all()  
        else:
            return StudentProfile.objects.none()

    def create(self, request, *args, **kwargs):
        """Only SUPERADMIN can create students"""
        if request.user.role != 'SUPERADMIN':
            return Response({'error': 'Only SUPERADMIN can create students'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Only SUPERADMIN can update students"""
        if request.user.role != 'SUPERADMIN':
            return Response({'error': 'Only SUPERADMIN can update students'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Only SUPERADMIN can delete students"""
        if request.user.role != 'SUPERADMIN':
            return Response({'error': 'Only SUPERADMIN can delete students'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def active_students(self, request):
        """Get only active students"""
        active_students = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_classroom(self, request):
        """Get students by classroom"""
        classroom = request.query_params.get('classroom')
        if not classroom:
            return Response({'error': 'Classroom parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset()
        students = queryset.filter(classroom=classroom)
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def generate_admit_card(self, request, pk=None):
        """Generate admit card PDF - Teachers and SUPERADMIN only"""
        if request.user.role not in ['SUPERADMIN', 'TEACHER']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        student = self.get_object()
        try:
            from reports.utils import generate_admit_card_pdf
            pdf_response = generate_admit_card_pdf(student)
            return pdf_response
        except ImportError as e:
            logger.error(f"Failed to import admit card generator: {e}")
            return Response(
                {'message': 'Admit card generation not available yet'}, 
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
        except Exception as e:
            logger.error(f"Error generating admit card for student {student.student_id}: {e}")
            return Response(
                {'error': 'Failed to generate admit card'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FeeStructureViewSet(viewsets.ModelViewSet):
    """
    Simplified for prototype:
    - SUPERADMIN and ACCOUNTANT can view/manage fees
    - TEACHER can only view
    """
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Simple role-based filtering"""
        user = self.request.user
        if user.role in ['SUPERADMIN', 'ACCOUNTANT']:
            return FeeStructure.objects.all()
        elif user.role == 'TEACHER':
            return FeeStructure.objects.all() 
        else:
            return FeeStructure.objects.none()

    def create(self, request, *args, **kwargs):
        """Only SUPERADMIN can create fee structures"""
        if request.user.role != 'SUPERADMIN':
            return Response({'error': 'Only SUPERADMIN can create fee structures'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Only SUPERADMIN can update fee structures"""
        if request.user.role != 'SUPERADMIN':
            return Response({'error': 'Only SUPERADMIN can update fee structures'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Only SUPERADMIN can delete fee structures"""
        if request.user.role != 'SUPERADMIN':
            return Response({'error': 'Only SUPERADMIN can delete fee structures'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def by_classroom(self, request):
        """Get fee structure by classroom"""
        classroom = request.query_params.get('classroom')
        if not classroom:
            return Response({'error': 'Classroom parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        fees = self.get_queryset().filter(classroom=classroom)
        serializer = self.get_serializer(fees, many=True)
        return Response(serializer.data)


class ReceiptViewSet(viewsets.ModelViewSet):
    """
    Simplified for prototype:
    - SUPERADMIN and ACCOUNTANT can manage receipts
    - TEACHER can only view
    """
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Simple role-based filtering"""
        user = self.request.user
        if user.role in ['SUPERADMIN', 'ACCOUNTANT']:
            return Receipt.objects.all()
        elif user.role == 'TEACHER':
            return Receipt.objects.all()  
        else:
            return Receipt.objects.none()

    def create(self, request, *args, **kwargs):
        """Only SUPERADMIN and ACCOUNTANT can create receipts"""
        if request.user.role not in ['SUPERADMIN', 'ACCOUNTANT']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Only SUPERADMIN and ACCOUNTANT can update receipts"""
        if request.user.role not in ['SUPERADMIN', 'ACCOUNTANT']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Only SUPERADMIN can delete receipts"""
        if request.user.role != 'SUPERADMIN':
            return Response({'error': 'Only SUPERADMIN can delete receipts'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def generate_fee_card(self, request, pk=None):
        """Generate fee card PDF"""
        bill = self.get_object()
        try:
            from reports.utils import generate_fee_card_pdf
            pdf_response = generate_fee_card_pdf(bill)
            return pdf_response
        except ImportError as e:
            logger.error(f"Failed to import fee card generator: {e}")
            return Response(
                {'message': 'Fee card generation not available yet'}, 
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
        except Exception as e:
            logger.error(f"Error generating fee card for bill {bill.bill_number}: {e}")
            return Response(
                {'error': 'Failed to generate fee card'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def generate_receipt(self, request, pk=None):
        """Generate payment receipt PDF"""
        bill = self.get_object()
        try:
            from reports.utils import generate_receipt_pdf
            pdf_response = generate_receipt_pdf(bill)
            return pdf_response
        except ImportError as e:
            logger.error(f"Failed to import receipt generator: {e}")
            return Response(
                {'message': 'Receipt generation not available yet'}, 
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
        except Exception as e:
            logger.error(f"Error generating receipt for bill {bill.bill_number}: {e}")
            return Response(
                {'error': 'Failed to generate receipt'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def pending_bills(self, request):
        """Get all pending payment bills"""
        try:
            pending_bills = self.get_queryset().filter(status='PENDING')
            serializer = self.get_serializer(pending_bills, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching pending bills: {e}")
            return Response(
                {'error': 'Failed to fetch pending bills'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """Get bills by student ID"""
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response({'error': 'Student ID parameter required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            student = StudentProfile.objects.get(student_id=student_id)
            bills = self.get_queryset().filter(student=student)
            serializer = self.get_serializer(bills, many=True)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching bills for student {student_id}: {e}")
            return Response(
                {'error': 'Failed to fetch student bills'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark a bill as fully paid - SUPERADMIN and ACCOUNTANT only"""
        if request.user.role not in ['SUPERADMIN', 'ACCOUNTANT']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
        bill = self.get_object()
        try:
            old_amount = bill.paid_amount
            bill.paid_amount = bill.total_amount
            bill.save()
            
            logger.info(f"Bill {bill.bill_number} marked as fully paid by user {request.user.username}")
            
            serializer = self.get_serializer(bill)
            return Response({
                'message': 'Bill marked as fully paid',
                'data': serializer.data
            })
        except Exception as e:
            logger.error(f"Error marking bill {bill.bill_number} as paid: {e}")
            return Response(
                {'error': 'Failed to update payment status'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def update_payment(self, request, pk=None):
        """Update payment amount - SUPERADMIN and ACCOUNTANT only"""
        if request.user.role not in ['SUPERADMIN', 'ACCOUNTANT']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
        bill = self.get_object()
        paid_amount = request.data.get('paid_amount')
    
        if paid_amount is None:
            return Response({'error': 'Paid amount is required'}, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            paid_amount = float(paid_amount)
        
            if paid_amount < 0:
                return Response({'error': 'Paid amount cannot be negative'}, status=status.HTTP_400_BAD_REQUEST)
            if paid_amount > bill.total_amount:
                return Response({'error': f'Paid amount cannot exceed total amount of Rs.{bill.total_amount}'}, status=status.HTTP_400_BAD_REQUEST)
        
            old_amount = bill.paid_amount
            bill.paid_amount = paid_amount
            bill.save()
        
            logger.info(f"Payment updated for bill {bill.bill_number}: {old_amount} -> {paid_amount} by user {request.user.username}")
        
            serializer = self.get_serializer(bill)
            return Response({
                'message': 'Payment updated successfully',
                'data': serializer.data
            })
        
        except ValueError:
            return Response({'error': 'Invalid paid amount format'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating payment for bill {bill.bill_number}: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BillItemViewSet(viewsets.ModelViewSet):
    """
    Simplified for prototype:
    - SUPERADMIN and ACCOUNTANT can manage bill items
    - TEACHER can only view
    """
    queryset = BillItem.objects.all()
    serializer_class = BillItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Simple role-based filtering"""
        user = self.request.user
        if user.role in ['SUPERADMIN', 'ACCOUNTANT']:
            queryset = BillItem.objects.all()
        elif user.role == 'TEACHER':
            queryset = BillItem.objects.all()  
        else:
            queryset = BillItem.objects.none()

        # Filter by bill_id if provided
        bill_id = self.request.query_params.get('bill_id')
        if bill_id:
            try:
                queryset = queryset.filter(bill_id=bill_id)
            except ValueError:
                queryset = BillItem.objects.none()
        return queryset

    def create(self, request, *args, **kwargs):
        """Only SUPERADMIN and ACCOUNTANT can create bill items"""
        if request.user.role not in ['SUPERADMIN', 'ACCOUNTANT']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Only SUPERADMIN and ACCOUNTANT can update bill items"""
        if request.user.role not in ['SUPERADMIN', 'ACCOUNTANT']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Only SUPERADMIN can delete bill items"""
        if request.user.role != 'SUPERADMIN':
            return Response({'error': 'Only SUPERADMIN can delete bill items'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)