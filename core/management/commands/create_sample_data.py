from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from authentication.models import User  # ✅ Import from authentication app
from core.models import Receipt, StudentProfile, FeeStructure, BillItem
from datetime import date
from django.db import transaction
from decimal import Decimal


class Command(BaseCommand):
    help = "Create sample data for testing"

    def handle(self, *args, **options):
        # Clear existing data OUTSIDE of transaction to avoid blocking
        self.stdout.write("Clearing existing data...")
        try:
            BillItem.objects.all().delete()
            Receipt.objects.all().delete()
            FeeStructure.objects.all().delete()
            StudentProfile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()  # Keep superuser if exists
            self.stdout.write("Existing data cleared successfully.")
        except Exception as e:
            self.stdout.write(f"Note: {str(e)} - Some tables may not exist yet.")

        # Now create data in a new transaction
        try:
            with transaction.atomic():
                # Create users using get_or_create to avoid duplicates
                admin, created = User.objects.get_or_create(
                    username="admin",
                    defaults={
                        "email": "admin@school.com",
                        "role": "SUPERADMIN",
                        "first_name": "Admin",
                        "last_name": "User",
                        "is_staff": True,
                        "is_superuser": True,
                        "is_active": True,
                    },
                )
                if created:
                    admin.set_password("admin123")
                    admin.save()
                    self.stdout.write(f"✅ Created admin user: {admin.username}")
                else:
                    self.stdout.write(f"ℹ️  Admin user already exists: {admin.username}")

                teacher, created = User.objects.get_or_create(
                    username="teacher",
                    defaults={
                        "email": "teacher@school.com",
                        "role": "TEACHER",
                        "first_name": "Jane",
                        "last_name": "Teacher",
                        "is_active": True,
                    },
                )
                if created:
                    teacher.set_password("teacher123")
                    teacher.save()
                    self.stdout.write(f"✅ Created teacher user: {teacher.username}")
                else:
                    self.stdout.write(
                        f"ℹ️  Teacher user already exists: {teacher.username}"
                    )

                accountant, created = User.objects.get_or_create(
                    username="accountant",
                    defaults={
                        "email": "accountant@school.com",
                        "role": "ACCOUNTANT",
                        "first_name": "John",
                        "last_name": "Accountant",
                        "is_active": True,
                    },
                )
                if created:
                    accountant.set_password("accountant123")
                    accountant.save()
                    self.stdout.write(
                        f"✅ Created accountant user: {accountant.username}"
                    )
                else:
                    self.stdout.write(
                        f"ℹ️  Accountant user already exists: {accountant.username}"
                    )

                # ✅ Create students using ONLY existing fields
                student1, created = StudentProfile.objects.get_or_create(
                    student_id="STU001",
                    defaults={
                        "name": "Ram Bahadur Shrestha",
                        "registration_no": "REG2081001",
                        "roll_number": 1,
                        "classroom": "Class 10",
                        "date_enrolled": date(2024, 1, 15),
                        "is_active": True,
                        # ❌ REMOVED: 'phone_number': '9841234567',
                        # ❌ REMOVED: 'address': 'Kathmandu-5, Nepal'
                    },
                )
                if created:
                    self.stdout.write(f"✅ Created student: {student1.name}")
                else:
                    self.stdout.write(f"ℹ️  Student already exists: {student1.name}")

                student2, created = StudentProfile.objects.get_or_create(
                    student_id="STU002",
                    defaults={
                        "name": "Sita Kumari Tamang",
                        "registration_no": "REG2081002",
                        "roll_number": 2,
                        "classroom": "Class 10",
                        "date_enrolled": date(2024, 1, 16),
                        "is_active": True,
                    },
                )
                if created:
                    self.stdout.write(f"✅ Created student: {student2.name}")

                student3, created = StudentProfile.objects.get_or_create(
                    student_id="STU003",
                    defaults={
                        "name": "Krishna Prasad Sharma",
                        "registration_no": "REG2081003",
                        "roll_number": 3,
                        "classroom": "Class 9",
                        "date_enrolled": date(2024, 1, 17),
                        "is_active": True,
                    },
                )
                if created:
                    self.stdout.write(f"✅ Created student: {student3.name}")

                student4, created = StudentProfile.objects.get_or_create(
                    student_id="STU004",
                    defaults={
                        "name": "Gita Rani Thapa",
                        "registration_no": "REG2081004",
                        "roll_number": 4,
                        "classroom": "Class 8",
                        "date_enrolled": date(2024, 1, 18),
                        "is_active": True,
                    },
                )
                if created:
                    self.stdout.write(f"✅ Created student: {student4.name}")

                student5, created = StudentProfile.objects.get_or_create(
                    student_id="STU005",
                    defaults={
                        "name": "Hari Maya Gurung",
                        "registration_no": "REG2081005",
                        "roll_number": 5,
                        "classroom": "Class 9",
                        "date_enrolled": date(2024, 1, 19),
                        "is_active": True,
                    },
                )
                if created:
                    self.stdout.write(f"✅ Created student: {student5.name}")

                fees = [
                    ("Class 10", "Tuition Fee", 5000.00),
                    ("Class 10", "Exam Fee", 1500.00),
                    ("Class 10", "Library Fee", 500.00),
                    ("Class 10", "Sports Fee", 800.00),
                    ("Class 9", "Tuition Fee", 4500.00),
                    ("Class 9", "Exam Fee", 1200.00),
                    ("Class 9", "Lab Fee", 600.00),
                    ("Class 8", "Tuition Fee", 4000.00),
                    ("Class 8", "Exam Fee", 1000.00),
                    ("Class 8", "Activity Fee", 700.00),
                ]

                for classroom, fee_type_name, amount in fees:
                    fee_structure, created = FeeStructure.objects.get_or_create(
                        classroom=classroom,
                        fee_type=fee_type_name, 
                        defaults={
                            "amount": Decimal(str(amount)),
                        },
                    )
                    if created:
                        self.stdout.write(
                            f"✅ Created fee structure: {fee_type_name} for {classroom}"
                        )
                    else:
                        self.stdout.write(
                            f"ℹ️  Fee structure already exists: {fee_type_name} for {classroom}"
                        )

                # Create receipts for students
                # Receipt 1 - Class 10 student (Partially paid)
                bill1, created = Receipt.objects.get_or_create(
                    bill_number="BIL2024001",
                    defaults={
                        "student": student1,
                        "total_amount": Decimal("7800.00"),
                        "paid_amount": Decimal("5000.00"),
                        "status": "PARTIALLY_PAID",
                        "date_generated": date(2024, 1, 20),
                        "remarks": "Partial payment received",
                    },
                )
                if created:
                    self.stdout.write(f"✅ Created receipt: {bill1.bill_number}")

                # Create bill items for first receipt
                items_bill1 = [
                    ("Tuition Fee", Decimal("5000.00")),
                    ("Exam Fee", Decimal("1500.00")),
                    ("Library Fee", Decimal("500.00")),
                    ("Sports Fee", Decimal("800.00")),
                ]

                for fee_type_name, amount in items_bill1:  # ✅ Changed variable name
                    bill_item = BillItem.objects.create(
                        bill=bill1,
                        fee_heading=fee_type_name,  # ✅ Check if BillItem uses fee_heading or fee_type
                        amount=amount,
                        # description=f"{fee_type_name} for {student1.classroom}",
                    )
                    self.stdout.write(
                        f"   ✅ Added item: {fee_type_name} - Rs.{amount}"
                    )
                # Receipt 2 - Class 10 student (Fully paid)
                bill2, created = Receipt.objects.get_or_create(
                    bill_number="BIL2024002",
                    defaults={
                        "student": student2,
                        "total_amount": Decimal("6500.00"),
                        "paid_amount": Decimal("6500.00"),
                        "status": "PAID",
                        "date_generated": date(2024, 1, 25),
                        "remarks": "Full payment received",
                    },
                )
                if created:
                    self.stdout.write(f"✅ Created receipt: {bill2.bill_number}")

                items_bill2 = [
                    ("Tuition Fee", Decimal("5000.00")),
                    ("Exam Fee", Decimal("1500.00")),
                ]

                for fee_heading, amount in items_bill2:
                    BillItem.objects.create(
                        bill=bill2,
                        fee_heading=fee_heading,
                        amount=amount,
                        # description=f"{fee_heading} for {student2.classroom}",
                    )

                # Receipt 3 - Class 9 student (Pending)
                bill3, created = Receipt.objects.get_or_create(
                    bill_number="BIL2024003",
                    defaults={
                        "student": student3,
                        "total_amount": Decimal("6300.00"),
                        "paid_amount": Decimal("0.00"),
                        "status": "PENDING",
                        "date_generated": date(2024, 2, 1),
                        "remarks": "Payment pending",
                    },
                )
                if created:
                    self.stdout.write(f"✅ Created receipt: {bill3.bill_number}")

                items_bill3 = [
                    ("Tuition Fee", Decimal("4500.00")),
                    ("Exam Fee", Decimal("1200.00")),
                    ("Lab Fee", Decimal("600.00")),
                ]

                for fee_heading, amount in items_bill3:
                    BillItem.objects.create(
                        bill=bill3,
                        fee_heading=fee_heading,
                        amount=amount,
                        # description=f"{fee_heading} for {student3.classroom}",
                    )

                # Receipt 4 - Class 8 student (Partially paid)
                bill4, created = Receipt.objects.get_or_create(
                    bill_number="BIL2024004",
                    defaults={
                        "student": student4,
                        "total_amount": Decimal("5000.00"),
                        "paid_amount": Decimal("2000.00"),
                        "status": "PARTIALLY_PAID",
                        "date_generated": date(2024, 2, 5),
                        "remarks": "Installment payment",
                    },
                )
                if created:
                    self.stdout.write(f"✅ Created receipt: {bill4.bill_number}")

                items_bill4 = [
                    ("Tuition Fee", Decimal("4000.00")),
                    ("Exam Fee", Decimal("1000.00")),
                ]

                for fee_heading, amount in items_bill4:
                    BillItem.objects.create(
                        bill=bill4,
                        fee_heading=fee_heading,
                        amount=amount,
                        # description=f"{fee_heading} for {student4.classroom}",
                    )

                # Receipt 5 - Class 9 student (Paid)
                bill5, created = Receipt.objects.get_or_create(
                    bill_number="BIL2024005",
                    defaults={
                        "student": student5,
                        "total_amount": Decimal("5100.00"),
                        "paid_amount": Decimal("5100.00"),
                        "status": "PAID",
                        "date_generated": date(2024, 2, 10),
                        "remarks": "Full payment received",
                    },
                )
                if created:
                    self.stdout.write(f"✅ Created receipt: {bill5.bill_number}")

                items_bill5 = [
                    ("Tuition Fee", Decimal("4500.00")),
                    ("Lab Fee", Decimal("600.00")),
                ]

                for fee_heading, amount in items_bill5:
                    BillItem.objects.create(
                        bill=bill5,
                        fee_heading=fee_heading,
                        amount=amount,
                        # description=f"{fee_heading} for {student5.classroom}",
                    )

            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS("🎉 Sample data setup completed successfully!")
            )
            self.stdout.write("")
            self.stdout.write("📋 Sample login credentials:")
            self.stdout.write("👤 Admin: admin / admin123")
            self.stdout.write("👨‍🏫 Teacher: teacher / teacher123")
            self.stdout.write("💰 Accountant: accountant / accountant123")
            self.stdout.write("")
            self.stdout.write("📊 Sample data created:")
            self.stdout.write(f"   • {User.objects.count()} users")
            self.stdout.write(f"   • {StudentProfile.objects.count()} students")
            self.stdout.write(f"   • {FeeStructure.objects.count()} fee structures")
            self.stdout.write(f"   • {Receipt.objects.count()} receipts")
            self.stdout.write(f"   • {BillItem.objects.count()} bill items")
            self.stdout.write("")
            self.stdout.write("🔍 Sample data breakdown:")
            self.stdout.write(
                f'   • Class 10: {StudentProfile.objects.filter(classroom="Class 10").count()} students'
            )
            self.stdout.write(
                f'   • Class 9: {StudentProfile.objects.filter(classroom="Class 9").count()} students'
            )
            self.stdout.write(
                f'   • Class 8: {StudentProfile.objects.filter(classroom="Class 8").count()} students'
            )
            self.stdout.write(
                f'   • Paid receipts: {Receipt.objects.filter(status="PAID").count()}'
            )
            self.stdout.write(
                f'   • Pending receipts: {Receipt.objects.filter(status="PENDING").count()}'
            )
            self.stdout.write(
                f'   • Partially paid: {Receipt.objects.filter(status="PARTIALLY_PAID").count()}'
            )
            self.stdout.write("")
            self.stdout.write("🌐 Test your API at: http://127.0.0.1:8000/api/")
            self.stdout.write("🔧 Django Admin at: http://127.0.0.1:8000/admin/")
            self.stdout.write("📚 API Docs at: http://127.0.0.1:8000/docs/")
            self.stdout.write("")
            self.stdout.write("🚀 Ready to test your School ERP prototype!")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error creating sample data: {str(e)}")
            )
            import traceback

            self.stdout.write(traceback.format_exc())
