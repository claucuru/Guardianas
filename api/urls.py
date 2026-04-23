from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PerfilUsuarioViewSet, ZonaViewSet, IncidenciaViewSet, incioSesion


router = DefaultRouter()
router.register(r'usuarios', PerfilUsuarioViewSet)
router.register(r'zonas', ZonaViewSet)
router.register(r'incidencias', IncidenciaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/login/', incioSesion)
]