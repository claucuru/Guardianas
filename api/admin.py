from django.contrib import admin

# Register your models here.
from application.models import PerfilUsuario, Zona, Incidencia, Ubicacion, Acompañamiento, RegistroPendiente, CandidatoAcompañamiento

admin.site.register(PerfilUsuario)
admin.site.register(Zona)
admin.site.register(Incidencia)
admin.site.register(Ubicacion)
admin.site.register(Acompañamiento)
admin.site.register(CandidatoAcompañamiento)
admin.site.register(RegistroPendiente)
