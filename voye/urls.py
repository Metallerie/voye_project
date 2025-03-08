from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from voye_app.views import DocumentViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]