from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StoreViewSet, CreditRequestViewSet, ChargeView

router = DefaultRouter()
router.register(r'stores', StoreViewSet)
router.register(r'credit-request', CreditRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('charge/', ChargeView.as_view(), name='charge'),
]
