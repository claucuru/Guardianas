# populate_models.py
import os
import django
import datetime


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from application.models import PerfilUsuario, Ubicacion
from django.contrib.gis.geos import Point, Polygon
from django.contrib.auth.models import User
from application.models import Zona

# Borrar datos previos
PerfilUsuario.objects.all().delete()
User.objects.all().delete()
Zona.objects.all().delete()

# Crear usuarios
u1 = User.objects.create_user(username='Maria', password='123')
u2 = User.objects.create_user(username='Lucia', password='123')
u3 = User.objects.create_user(username='Angel', password='123')
u4 = User.objects.create_user(username='Telma', password='123')
u5 = User.objects.create_user(username='Alicia', password='123')


p1 = PerfilUsuario.objects.create(user=u1, nombreUsuario="maria", nombre_completo="Maria", fecha_nacimiento=datetime.date(2003, 2, 1), disponible="True", genero="F")
p2 = PerfilUsuario.objects.create(user=u2, nombreUsuario="lucia", nombre_completo="Lucia", fecha_nacimiento=datetime.date(2003, 2, 1), disponible="True", genero="F")
p3 = PerfilUsuario.objects.create(user=u3, nombreUsuario="angel", nombre_completo="Angel", fecha_nacimiento=datetime.date(2003, 2, 1), disponible="True", genero="M")
p4 = PerfilUsuario.objects.create(user=u4, nombreUsuario="telma", nombre_completo="Telma", fecha_nacimiento=datetime.date(2003, 2, 1), disponible="True", genero="F")
p5 = PerfilUsuario.objects.create(user=u5, nombreUsuario="alicia", nombre_completo="Alicia", fecha_nacimiento=datetime.date(2003, 2, 1), disponible="True", genero="F")
p4.disponible = True
p4.save()
p5.disponible = True
p5.save()


Ubicacion.objects.create(
    usuario=p4,
    posicion=Point(40.5049, -3.6973),
    disponible=True,
)




zona1 = Zona.objects.create(
    nombre="Zona Centro",
    area=Polygon((
        (-3.7038, 40.4168),
        (-3.7030, 40.4168),
        (-3.7030, 40.4175),
        (-3.7038, 40.4175),
        (-3.7038, 40.4168),
    ))
)

zona2 = Zona.objects.create(
    nombre="Zona Norte",
    area=Polygon((
        (-3.70, 40.45),
        (-3.69, 40.45),
        (-3.69, 40.46),
        (-3.70, 40.46),
        (-3.70, 40.45),
    ))
)
