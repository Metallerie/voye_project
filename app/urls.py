from django.urls import path
<<<<<<< Updated upstream
from . import views

urlpatterns = [
    path('document/', views.document_view, name='document_view'),
    path('', views.index, name='index'),
=======
from . import views  # Import complet du module views

urlpatterns = [
    path('document/', views.document_view, name='document_view'),
    path('', views.index, name='index'),  # Route principale pour la page d'accueil
>>>>>>> Stashed changes
    path('run_gpt/', views.run_gpt_engineer, name='run_gpt'),
]
