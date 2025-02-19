from django.urls import path
from .views import document_view

urlpatterns = [
    path('document_view/', document_view, name='document_view'),
]
