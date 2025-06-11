from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('admit-card/<int:student_id>/', views.generate_admit_card, name='admit_card'),
    path('fee-card/<int:bill_id>/', views.generate_fee_card, name='fee_card'),
    path('receipt/<int:bill_id>/', views.generate_receipt, name='receipt'),
    path('bulk-reports/', views.generate_bulk_reports, name='bulk_reports'),
]