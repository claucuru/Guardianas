from rest_framework import serializers
from application.models import PerfilUsuario, Canal, Suscripcion, Zona, Incidencia, Acompañamiento
from rest_framework_gis.serializers import GeoFeatureModelSerializer

class PerfilUsuarioSerializer (serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = ['id', 'nombreUsuario', 'disponible', 'user']

class CanalSerializer (serializers.ModelSerializer):
    class Meta:
        model = Canal
        fields = ['id', 'nombreCanal']

class SuscripcionSerializer (serializers.ModelSerializer):
    class Meta:
        model = Suscripcion
        fields = ['id', 'canal', 'usuario', 'fechaDeSuscripcion']
    
class ZonaSerializer(GeoFeatureModelSerializer):
    total_gravedad = serializers.SerializerMethodField()
    class Meta:
        model = Zona
        geo_field = "area"
        fields = ("id", "nombre", "total_gravedad")

    def get_total_gravedad(self, obj):
        return obj.total_gravedad if hasattr(obj, "total_gravedad") and obj.total_gravedad else 0

class IncidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incidencia
        fields = ['id', 'zona', 'gravedad', 'descripcion', 'fecha']

class AcompañamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model: Acompañamiento
        fields = ['id', 'acompañante', 'solicitante', 'fecha_comienzo', 'tiempo_estimado', 'fecha_fin', 'max_tiempo_act', 'origen', 'destino', 'estado' ]