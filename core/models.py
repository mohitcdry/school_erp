from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.

class StudentProfile(models.Model):
    student_id = models.CharField(max_length=50,unique=True)
    # user = models.OneToOneField(User, on_delete= models.CASCADE)
    name = models.CharField(max_length=255)
    registration_no = models.CharField(max_length=50, unique=True)
    roll_number = models.IntegerField()
    classroom = models.CharField(max_length=100)
    date_enrolled = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.student_id}"
    

class FeeStructure(models.Model):
    classroom = models.CharField(max_length=100)
    fee_type = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together =("classroom", "fee_type")

    def __str__(self):
        return f"{self.classroom} - {self.fee_type}: ₹{self.amount}"

class Receipt(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PARTIAL", "Partially Paid"),
        ("PAID", "FULLY Paid"),
    ]

    bill_number = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    date_generated = models.DateTimeField(auto_now_add=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # due_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    remarks = models.TextField(blank=True, null=True)

    @property
    def due_amount(self):
        return self.total_amount - self.paid_amount

    def save(self, *args, **kwargs):
        # self.due_amount = self.total_amount - self.paid_amount
        if self.paid_amount >= self.total_amount:
            self.status = "PAID"
        elif self.paid_amount > 0:
            self.status = "PARTIAL"
        else:
            self.status = "PENDING"
        super().save(*args, **kwargs)

    def clean(self):
        if self.paid_amount > self.total_amount:
            raise ValidationError("Paid amount cannot exceed total amount")
        if self.total_amount <= 0:
            raise ValidationError("Total amount must be positive")

    def __str__(self):
        return f"{self.bill_number} - {self.student.name} ({self.status})"

class BillItem(models.Model):
    bill = models.ForeignKey(Receipt, on_delete = models.CASCADE, related_name = "items")
    fee_heading = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.fee_heading}: ₹{self.amount}"

    def save(self, *args, **kwargs):
        if self.order == 0:
            last_item = BillItem.objects.filter(bill = self.bill).order_by("-order").first()
            if last_item:
                self.order = last_item.order +1
            else:
                self.order = 1
            # self.order = (last_item.order +1) if last_item else 1
        super().save(*args, **kwargs)