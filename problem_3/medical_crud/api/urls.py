from django.urls import path
from .views import BulkElementCreateView
from .views import (
    DeviceListCreateView, DeviceRetrieveUpdateDestroyView,
    ElementListCreateView, ElementRetrieveUpdateDestroyView
)

urlpatterns = [
    path('devices/', DeviceListCreateView.as_view(), name='device-list-create'),
    path('devices/<int:pk>/', DeviceRetrieveUpdateDestroyView.as_view(), name='device-detail'),
    path('elements/', ElementListCreateView.as_view(), name='element-list-create'),
    path('elements/<int:pk>/', ElementRetrieveUpdateDestroyView.as_view(), name='element-detail'),
    path('elements/bulk/', BulkElementCreateView.as_view(), name='bulk-element-create'),
]
