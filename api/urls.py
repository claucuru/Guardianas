from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PerfilUsuarioViewSet, CanalViewSet, SuscripcionViewSet, ZonaViewSet, IncidenciaViewSet, incioSesion


router = DefaultRouter()
router.register(r'usuarios', PerfilUsuarioViewSet)
router.register(r'canales', CanalViewSet)
router.register(r'suscripciones', SuscripcionViewSet)
router.register(r'zonas', ZonaViewSet)
router.register(r'incidencias', IncidenciaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/login/', incioSesion)
]