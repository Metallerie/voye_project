from django.contrib import admin
from django.urls import include, path
from voye_app.views import document_view, previous_document, next_document, document_list, hello_world

urlpatterns = [
    path('admin/', admin.site.urls),
    path('document/', document_view, name='document_view'),
    path('document/previous/', previous_document, name='previous_document'),
    path('document/next/', next_document, name='next_document'),
    path('documents/', document_list, name='document_list'),
    path('hello-world/', hello_world, name='hello_world'),
]
