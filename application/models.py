from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

# Create your models here.
class PerfilUsuario(models.Model):
    GENERO_CHOICES = [
        ("M", "Hombre"),
        ("F", "Mujer"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombreUsuario = models.CharField(max_length=100, unique=True)
    nombre_completo = models.CharField(max_length=100, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    disponible = models.BooleanField(default=False) # para acompañantes
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.nombreUsuario

class Canal (models.Model):
    id = models.IntegerField(primary_key=True)
    nombreCanal = models.CharField(max_length=100)

    def __str__(self):
        return self.nombreCanal

class Suscripcion(models.Model):
    id = models.IntegerField(primary_key=True)
    canal = models.ForeignKey(Canal, on_delete=models.CASCADE)
    usuario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE)
    fechaDeSuscripcion = models.DateField()

    def __str__(self):
        return f"{self.usuario} suscrito al canal {self.canal} el {self.fechaDeSuscripcion}"
    

class Zona(models.Model):
    nombre = models.CharField(max_length=100)
    area = models.PolygonField(srid=4326)

    def __str__(self):
        return self.nombre

class Incidencia (models.Model):
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE, related_name="incidencias")
    gravedad = models.IntegerField()
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

class Ubicacion(models.Model):
    usuario = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE)
    posicion = models.PointField(srid=4326)
    disponible = models.BooleanField(default=True)

def expiracion()   :
    return timezone.now() + timedelta(hours=72)
def expiracion_acompañamiento():
    return timezone.now() + timedelta(hours=3)

class Acompañamiento(models.Model):
    """Modelo que representa un acompañamiento"""

    acompañante = models.ForeignKey(
        PerfilUsuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="acompañamientos_aceptados"
    )

    solicitante = models.ForeignKey(
            PerfilUsuario, on_delete=models.CASCADE, related_name="acompañamientos_solicitados"
    )

    fecha_comienzo = models.DateTimeField(auto_now_add=True) #creado
    tiempo_estimado = models.DurationField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    max_tiempo_act = models.IntegerField(default=43200)
    origen = models.PointField(srid=4326)
    destino = models.PointField(srid=4326)
    estado = models.CharField(
        max_length=20,
        choices=[
            ("SOLICITADO", "Solicitado"),
            ("ACEPTADO", "Aceptado por acompañante"),
            ("ASIGNADO", "Confirmado por solicitante"),
            ("EN_CURSO", "En curso"),
            ("FINALIZADO", "Finalizado"),
            ("CANCELADO", "Cancelado"),
        ],
        default="buscando"
    )
    cancelado_por = models.CharField(max_length=20, null=True, blank=True)

    caduca_en = models.DateTimeField(default=expiracion_acompañamiento)
    hora_solicitada = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Solicitante {self.solicitante}, Acompañante {self.acompañante or 'sin asignar'}"
    
    def getParticipantes(self):
        return [self.solicitante, self.acompañante]
    def expirado(self):
        return timezone.now() > self.caduca_en



class RegistroPendiente(models.Model):
    usuario = models.CharField(max_length=100)
    email = models.EmailField()
    contraseña = models.CharField(max_length=225)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=2)
    mujer1 = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='mujer_1')
    mujer2 = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='mujer_2')
    m1_acepto = models.BooleanField(null=True)
    m2_acepto = models.BooleanField(null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    caduca_en = models.DateTimeField(default=expiracion)

    def solicitud_expirada(self):
        return timezone.now() > self.caduca_en
    
class CandidatoAcompañamiento(models.Model):
    acompañamiento = models.ForeignKey(Acompañamiento, on_delete=models.CASCADE, related_name='candidatos')
    candidato = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='candidaturas')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        # FIFO, el primero en aceptar es el primero en la cola
        ordering = ['fecha']
        unique_together = [('acompañamiento', 'candidato')]