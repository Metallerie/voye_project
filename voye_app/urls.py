from django.urls import path
from voye_app.views import document_view, previous_document, next_document, document_list, hello_world

urlpatterns = [
    path('document/<int:pk>/', document_view, name='document_view'),
    path('document/<int:pk>/previous/', previous_document, name='previous_document'),
    path('document/<int:pk>/next/', next_document, name='next_document'),
    path('documents/', document_list, name='document_list'),  # Ajoutez ceci pour la liste des documents
    path('hello-world/', hello_world, name='hello_world'),  # Ajoutez ceci pour la nouvelle vue

]
