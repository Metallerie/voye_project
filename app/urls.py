from django.urls import path
from .views import document_view  # Assurez-vous que cette ligne est correcte

urlpatterns = [
    path('document/', document_view, name='document_view'),
]
