from django.urls import path
from . import views

urlpatterns = [
    path('document/', views.document_view, name='document_view'),
    path('', views.index, name='index'),
    path('run_gpt/', views.run_gpt_engineer, name='run_gpt'),
]
