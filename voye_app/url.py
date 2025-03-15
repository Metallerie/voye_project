from django.urls import path
from . import views

urlpatterns = [
    path('document/<int:pk>/', views.document_view, name='document_view'),
    path('document/<int:pk>/previous/', views.previous_document, name='previous_document'),
    path('document/<int:pk>/next/', views.next_document, name='next_document'),
]
