from rest_framework import serializers
from .models import StudentProfile, FeeStructure, Receipt, BillItem

class StudentProfileSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = "__all__"

    def validate_student_id(self, value):
        if StudentProfile.objects.filter(student_id=value).exists():
            raise serializers.ValidationError("A student with this ID already exists.")
        return value
    
    def validate_registration_no(self, value):
        if StudentProfile.objects.filter(registration_no = value).exists():
            raise serializers.ValidationError("A student with this registration number already exists.")
        return value

    def validate_roll_number(self, value):
        if value <= 0:
            raise serializers.ValidationError("Roll number must be positive.")
        return value


class BillItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = BillItem
        fields = ["fee_heading", "amount"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value


class ReceiptSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True, read_only=True)
    student_name = serializers.CharField(source="student.name", read_only=True)

    class Meta:
        model = Receipt
        fields = "__all__"

    def validate_total_amount(self, value): 
        if value <= 0:
            raise serializers.ValidationError("Total amount must be positive.")
        return value
    
    def validate_paid_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Paid amount cannot be negative.")
        return value

    def validate(self, data):
        total_amount = data.get('total_amount')
        paid_amount = data.get('paid_amount', 0)
        
        if paid_amount > total_amount:
            raise serializers.ValidationError("Paid amount cannot exceed total amount.")
        
        return data


class FeeStructureSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeeStructure
        fields = "__all__"

    def validate_amount(self, value):
        """Ensure fee amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Fee amount must be positive.")
        return value

    def validate(self, data):
        classroom = data.get('classroom')
        fee_type = data.get('fee_type')
        if self.instance is None:
            if FeeStructure.objects.filter(classroom=classroom, fee_type=fee_type).exists():
                raise serializers.ValidationError(
                    f"Fee structure for {fee_type} in {classroom} already exists."
            )
        return data