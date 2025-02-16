from django.urls import path
from .views import document_view

urlpatterns = [
    path('document_views/', document_view, name='document_view'),
]
