from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, ReceiptViewSet, BillItemViewSet, FeeStructureViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'receipts', ReceiptViewSet)
router.register(r"bill-items", BillItemViewSet)
router.register(r"fee-structures", FeeStructureViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
