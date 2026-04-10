from django.contrib import admin

# Register your models here.
from application.models import PerfilUsuario, Canal, Suscripcion, Zona, Incidencia

admin.site.register(Canal)
admin.site.register(PerfilUsuario)
admin.site.register(Suscripcion)
admin.site.register(Zona)
admin.site.register(Incidencia)


