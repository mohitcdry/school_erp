from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import StudentProfile, FeeStructure, Receipt, BillItem

# Student Profile Admin
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'classroom', 'roll_number', 'is_active', 'date_enrolled', 'total_bills', 'total_due')
    list_filter = ('classroom', 'is_active', 'date_enrolled')
    search_fields = ('student_id', 'name', 'registration_no')
    ordering = ('classroom', 'roll_number')
    date_hierarchy = 'date_enrolled'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('student_id', 'name', 'registration_no')
        }),
        ('Academic Details', {
            'fields': ('classroom', 'roll_number', 'date_enrolled')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def total_bills(self, obj):
        count = obj.receipt_set.count()
        if count > 0:
            url = reverse('admin:core_receipt_changelist') + f'?student__id__exact={obj.id}'
            return format_html('<a href="{}">{} bills</a>', url, count)
        return '0 bills'
    total_bills.short_description = 'Bills'
    
    def total_due(self, obj):
        try:
            bills = obj.receipt_set.all()
            total = sum(bill.total_amount - bill.paid_amount for bill in bills)
            if total > 0:
                return format_html('<span style="color: red;">Rs.{}</span>', f'{total:.2f}')
            elif total < 0:
                return format_html('<span style="color: green;">Rs.{}</span>', f'{abs(total):.2f}')
            return 'Rs.0.00'
        except Exception:
            return 'Rs.0.00'
    total_due.short_description = 'Total Due'

# Fee Structure Admin
@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('classroom', 'fee_type', 'amount_display', 'created_at')
    list_filter = ('classroom', 'fee_type', 'created_at')
    search_fields = ('classroom', 'fee_type')
    ordering = ('classroom', 'fee_type')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Fee Details', {
            'fields': ('classroom', 'fee_type', 'amount')
        }),
    )
    
    def amount_display(self, obj):
        return f'Rs.{obj.amount:.2f}'
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'

# Bill Item Inline for Payment Bill
class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 1
    fields = ('fee_heading', 'amount', 'order')
    ordering = ('order',)

# Payment Bill Admin
@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('bill_number', 'student_link', 'status_display', 'total_amount_display', 
                    'paid_amount_display', 'due_amount_display', 'date_generated')
    list_filter = ('status', 'date_generated', 'student__classroom')
    search_fields = ('bill_number', 'student__name', 'student__student_id')
    ordering = ('-date_generated',)
    date_hierarchy = 'date_generated'
    inlines = [BillItemInline]
    
    fieldsets = (
        ('Bill Information', {
            'fields': ('bill_number', 'student')
        }),
        ('Payment Details', {
            'fields': ('total_amount', 'paid_amount', 'status')
        }),
        ('Additional Information', {
            'fields': ('pan_number', 'remarks'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('status',)  # Status is auto-calculated
    
    def student_link(self, obj):
        url = reverse('admin:core_studentprofile_change', args=[obj.student.id])
        return format_html('<a href="{}">{}</a>', url, obj.student.name)
    student_link.short_description = 'Student'
    student_link.admin_order_field = 'student__name'
    
    def status_display(self, obj):
        colors = {
            'PENDING': 'red',
            'PARTIAL': 'orange', 
            'PAID': 'green'
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_status_display())
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def total_amount_display(self, obj):
        return f'Rs.{obj.total_amount:.2f}'
    total_amount_display.short_description = 'Total Amount'
    total_amount_display.admin_order_field = 'total_amount'
    
    def paid_amount_display(self, obj):
        return f'Rs.{obj.paid_amount:.2f}'
    paid_amount_display.short_description = 'Paid Amount'
    paid_amount_display.admin_order_field = 'paid_amount'
    
    def due_amount_display(self, obj):
        try:
            due = obj.due_amount
            if due > 0:
                return format_html('<span style="color: red; font-weight: bold;">Rs.{}</span>', f'{due:.2f}')
            elif due < 0:
                return format_html('<span style="color: green; font-weight: bold;">Rs.{}</span>', f'{abs(due):.2f}')
            return 'Rs.0.00'
        except Exception:
            return 'Rs.0.00'
    due_amount_display.short_description = 'Due Amount'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('student')

# Bill Item Admin
@admin.register(BillItem)
class BillItemAdmin(admin.ModelAdmin):
    list_display = ('bill_link', 'fee_heading', 'amount_display', 'order')
    list_filter = ('fee_heading', 'bill__status')
    search_fields = ('bill__bill_number', 'fee_heading', 'bill__student__name')
    ordering = ('bill', 'order')
    
    def bill_link(self, obj):
        try:
            url = reverse('admin:core_receipt_change', args=[obj.bill.id])  # Fixed: lowercase receipt
            return format_html('<a href="{}">{}</a>', url, obj.bill.bill_number)
        except Exception:
            return obj.bill.bill_number if obj.bill else 'No Bill'
    bill_link.short_description = 'Bill'
    bill_link.admin_order_field = 'bill__bill_number'
    
    def amount_display(self, obj):
        return f'Rs.{obj.amount:.2f}'
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'

# Customize Admin Site
admin.site.site_header = "🏫 School ERP Administration"
admin.site.site_title = "School ERP Admin"
admin.site.index_title = "Welcome to School ERP Administration Panel"