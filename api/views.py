from datetime import date, timedelta, timezone
import random

from django.db import models
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from application.models import RegistroPendiente, Ubicacion, PerfilUsuario, Valoracion, Zona, Incidencia, Acompañamiento, CandidatoAcompañamiento
from .serializers import  PerfilUsuarioSerializer, ZonaSerializer, IncidenciaSerializer, AcompañamientoSerializer
from django.db.models import Sum
from django.contrib.gis.measure import D, Distance
from django.contrib.gis.geos import Point
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .consumers import send_notificacion, send_notificacion_acompañamiento, send_notificacion_acompañamiento_confirmado, send_notificacion_acompañante_propuesto, send_notificacion_cancelacion, send_notificacion_finalizado, send_alerta_panico, send_acompañamiento_finalizado
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime




@api_view(['POST'])
def incioSesion(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "username": user.username
        })
    
    return Response(
        {"error": "Credenciales incorrectas"},
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
def verificar_identidad(request):
    image_dni = request.FILES.get('dni')
    genero = request.user.genero
    masculino = False
    if genero == "H":
        masculino = True

    return Response({"genero": genero, "masculino": masculino})

@api_view(['POST'])
def registrar_usuario(request):
    print("DATOS RECIBIDOS:", request.data) 
    genero = request.data.get('genero')
    usuario = request.data.get('usuario')
    contraseña = request.data.get('contraseña')
    email = request.data.get('email', '')
    fecha_nacimiento_str = request.data.get('fecha_nacimiento')
    fecha_nacimiento = date.fromisoformat(fecha_nacimiento_str)

    if genero == 'M':
        nombre1 = request.data.get("mujer1")
        nombre2 = request.data.get("mujer2")
        try:
            mujer1 = PerfilUsuario.objects.get(nombreUsuario__iexact=nombre1)
            mujer2 = PerfilUsuario.objects.get(nombreUsuario__iexact=nombre2)
        except PerfilUsuario.DoesNotExist:
            return Response(
                {"error": "Uno de los usuarios no existe"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if mujer1 == mujer2:
            return Response({
                "error": "Las dos usuarias deben ser personas distintas"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Comprobamos que los dos usuario sean mujeres
        for m in [mujer1, mujer2]:
            if m.genero is None:
                return Response(
                    {"error": f"{m.nombreUsuario} no tiene género registrado"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if m.genero == "M":
                return Response(
                    {"error": f"{m.nombreUsuario} no es una mujer"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        registroPendiente = RegistroPendiente.objects.create(
            mujer1=mujer1,
            mujer2=mujer2,
            usuario=usuario,
            contraseña=contraseña,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero,
        )

        send_notificacion(mujer1.id, registroPendiente)
        send_notificacion(mujer2.id, registroPendiente)

        return Response({"status": "pendiente_aprobacion"})

    else:

        nombre_completo = request.data.get('nombre_completo', '')

        if User.objects.filter(username=usuario).exists():
            return Response(
                {"error": "El nombre de usuario ya está en uso"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(
            username=usuario,
            password=contraseña,
            email=email
        )
        
        user.perfilusuario.nombre_completo = nombre_completo
        user.perfilusuario.fecha_nacimiento = fecha_nacimiento
        user.perfilusuario.save()


        return Response({"status": "registrado"})


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def responder_solicitud_registro(request, pendiente_id):
    
    try:
        pendiente = RegistroPendiente.objects.get(id=pendiente_id)
    except RegistroPendiente.DoesNotExist:
        return Response({"error": "Solicitud no encontrada"}, status=404)
    
    if pendiente.solicitud_expirada():
        pendiente.delete()
        return Response({"error": "La solicitud ya ha expirado"}, status=400)
    
    decision = request.data.get('acepta')
    perfil_actual = request.user.perfilusuario

    if perfil_actual == pendiente.mujer1:
        pendiente.m1_acepto = decision
    elif perfil_actual == pendiente.mujer2:
        pendiente.m2_acepto = decision
    else:
        return Response(
            {"error": "No tienes permiso para responder esta solicitud"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    pendiente.save()

    if pendiente.m1_acepto == True and pendiente.m2_acepto == True:
        if not User.objects.filter(username=pendiente.usuario).exists():
            user = User.objects.create_user(
                username=pendiente.usuario,
                password=pendiente.contraseña,
                email=pendiente.email
            )

            user.perfilusuario.fecha_nacimiento = pendiente.fecha_nacimiento
            user.perfilusuario.genero = pendiente.genero
            user.perfilusuario.save()
        
        pendiente.delete()
        return Response({"status": "usuario_creado"})
    return Response({"status": "respuesta_guardada"})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def mis_solicitudes_pendientes(request):
    """ Devuelve las solicitudes que esperan respuesta del usuario autenticado. """
    perfil = request.user.perfilusuario
    solicitudes = RegistroPendiente.objects.filter(
        models.Q(mujer1=perfil, m1_acepto__isnull=True) | models.Q(mujer2=perfil, m2_acepto__isnull=True),
    )

    data = [
        {
            "id": s.id,
            "usuario_solicitante": s.usuario,
            "fecha_nacimiento": s.fecha_nacimiento,
            "caduca_en": s.caduca_en,
        }
        for s in solicitudes
        if not s.solicitud_expirada()
    ]

    return Response(data)

def añadir_ruido(coord, metros=100):
    """ Desplaza una coordenada alrededor de 400 metros en dirección aleatoria """
    delta = metros /111_000
    return coord + random.uniform(-delta, delta)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def pedir_acompañamiento(request):
    """ Solicitante crea un acompañamiento. Se notifican a los usuarios cercanos disponibles."""
    import pytz
    hora_españa = pytz.timezone('Europe/Madrid')

    origen_lat = request.data.get('origen_lat')    
    origen_lng = request.data.get('origen_lng')
    destino_lat = request.data.get('destino_lat')
    destino_lng = request.data.get('destino_lng')    
    hora_str = request.data.get('hora_solicitada')
    perfil = request.user.perfilusuario

    # Comprobamos si el solicitante tiene ya un acompañamiento activo
    activo = Acompañamiento.objects.filter(
        solicitante=perfil,
        estado__in=['SOLICITADO', 'ACEPTADO', 'ASIGNADO'],
        caduca_en__gt=timezone.now(),
    ).exists()

    if activo:
        return Response(
            {"error": "Ya tienes un acompañamiento activo"},
            status=400
        )

    if not all([origen_lat, origen_lng, destino_lat, destino_lng]):
        return Response({"error": "Faltan coordenadas"}, status=400)
    
    origen = Point(float(origen_lng), float(origen_lat), srid=4326)
    destino = Point(float(destino_lng), float(destino_lat), srid=4326)
    tipo = request.data.get('tipo', 'FISICO')

    acompañamiento = Acompañamiento.objects.create(
        solicitante=request.user.perfilusuario,
        origen=origen,
        destino=destino,
        estado="SOLICITADO",
        tipo=tipo,
    )

    hora_solicitada = None
    if hora_str:
        try:
            hora_solicitada = datetime.strptime(hora_str, '%H:%M').time()
            acompañamiento.hora_solicitada = hora_solicitada
        except ValueError:
            pass


    hora_fin_str = request.data.get('hora_fin')
    if hora_fin_str:
        try:         
            hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()
            hoy = timezone.now().astimezone(hora_españa).date()
            # fecha_fin = timezone.make_aware(datetime.combine(hoy, hora_fin))
            fecha_fin = hora_españa.localize(datetime.combine(hoy, hora_fin))
            acompañamiento.hora_fin_estimada = hora_fin
            acompañamiento.fecha_fin = fecha_fin
        except ValueError:
            pass
    
    acompañamiento.save()
    
    if tipo == 'VIRTUAL':
        # Acompañamiento virtual. Notificar a todos los usuarios disponibles
        acompañantes_cercanos = Ubicacion.objects.filter(
            disponible=True,
            usuario__disponible= True,
        ).exclude(
            usuario=request.user.perfilusuario
        ).select_related('usuario')
    else:
        # Acompañamiento físico. Notificar solo a personas en un radio de 2km
        acompañantes_cercanos = Ubicacion.objects.filter(
            disponible=True,
            usuario__disponible= True,
        ).exclude(
            usuario=request.user.perfilusuario
        ).filter(
            posicion__distance_lte=(origen, D(km=2))
        ).select_related('usuario')
    
    for ubi in acompañantes_cercanos:
        send_notificacion_acompañamiento(ubi.usuario.user.id, acompañamiento)
    print(f"Acompañantes encontradas: {acompañantes_cercanos.count()}")

    return Response({"id": acompañamiento.id, "estado": acompañamiento.estado})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def mis_acompañamientos(request):
    finalizar_acompañamientos_expirados()

    ahora = timezone.now()
    perfil = request.user.perfilusuario
    # Los acompañamientos que he solicitado yo no cancelados
    solicitados = Acompañamiento.objects.filter(
        solicitante=perfil,
        caduca_en__gt=ahora,
    ).exclude(estado='CANCELADO').order_by('-fecha_comienzo')

    # Cancelados recientes en la última hora para mostrar la notificación
    cancelados_recientes = Acompañamiento.objects.filter(
        models.Q(solicitante=perfil) | models.Q(acompañante=perfil),
        estado='CANCELADO',
        fecha_comienzo__gt= ahora - timedelta(hours=1),
    ).order_by('-fecha_comienzo')

    # Las solicitudes de acompañamiento que me han llegado a mí 
    try: 
        ubicacion_perfil = Ubicacion.objects.get(usuario=perfil)
        print(f"Ubicacion de {perfil.nombreUsuario}: x={ubicacion_perfil.posicion.x}, y = {ubicacion_perfil.posicion.y}")
        disponibles = Acompañamiento.objects.filter(
            estado__in=['SOLICITADO', 'ACEPTADO'],
            caduca_en__gt=ahora,
        ).exclude(solicitante=perfil).filter(origen__distance_lte=(ubicacion_perfil.posicion, D(km=2))).order_by('-fecha_comienzo')
    except Ubicacion.DoesNotExist:
        print(f"{perfil.nombreUsuario} NO TIENE UBI EN LA BD")
        disponibles = Acompañamiento.objects.filter(
            estado='SOLICITADO',
            caduca_en__gt=ahora,
        ).exclude(solicitante=perfil).order_by('-fecha_comienzo')

    
    def serializar(a, es_mio):
        # Se mandan las coordenadas exactas cuando el acompañamiento esté en estado ASIGNADO y es mi solicitud o soy el acompañante confirmado

        soy_acompañante_confirmado = (
            a.acompañante and a.acompañante == perfil and a.estado in ('ASIGNADO')
        )
        coordenadas_exactas = (es_mio and a.estado in ('ASIGNADO')) or soy_acompañante_confirmado
        ya_valoro = a.valoraciones.filter(valorador=perfil).exists()

        if coordenadas_exactas:
            origen_lat = a.origen.y
            origen_lng = a.origen.x
            destino_lat = a.destino.y
            destino_lng = a.destino.x
        else:
            origen_lat = añadir_ruido(a.origen.y)
            origen_lng = añadir_ruido(a.origen.x)
            destino_lat = añadir_ruido(a.destino.y)
            destino_lng = añadir_ruido(a.destino.x)

        return {
            "id": a.id,
            "tipo": a.tipo,
            "cancelado_por": a.cancelado_por,
            "estado": a.estado,
            "es_mio": es_mio,
            "solicitante": a.solicitante.nombreUsuario,
            "solicitante_nombre": a.solicitante.nombre_completo or a.solicitante.nombreUsuario,
            "acompañante": a.acompañante.nombreUsuario if a.acompañante else None,
            "acompañante_nombre": a.acompañante.nombre_completo if a.acompañante else None,
            "origen_lat": round(origen_lat, 5),
            "origen_lng": round(origen_lng, 5),
            "destino_lat": round(destino_lat, 5),
            "destino_lng": round(destino_lng, 5),
            "coordenadas_exactas": coordenadas_exactas,
            "fecha": a.fecha_comienzo.isoformat(),
            "hora_solicitada": a.hora_solicitada.strftime('%H:%M') if a.hora_solicitada else None,
            "hora_fin_estimada": a.hora_fin_estimada.strftime('%H:%M') if a.hora_fin_estimada else None,
            "ya_valoro": ya_valoro,
        }
    
    como_acompañante = Acompañamiento.objects.filter(
        acompañante=perfil, 
        estado__in = ('ASIGNADO','FINALIZADO'),
        caduca_en__gt = ahora,
    )
    return Response({
        "solicitados": [serializar(a, True) for a in solicitados],
        "disponibles": [serializar(a, False) for a in disponibles],
        "como_acompañante": [serializar(a, False) for a in como_acompañante],
        "cancelados_recientes": [serializar(a, a.solicitante == perfil) for a in cancelados_recientes],
    })

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def cancelar_acompañamiento(request, acompañamiento_id):
    perfil = request.user.perfilusuario

    try:
        acompañamiento = Acompañamiento.objects.get(
            id=acompañamiento_id,
            estado__in= ['SOLICITADO', 'ACEPTADO', 'ASIGNADO']
        )
    except Acompañamiento.DoesNotExist:
        return Response({"error": "El acompañamiento no ha sido encontrado"}, status=404)
    
    es_solicitante = acompañamiento.solicitante == perfil
    es_acompañante = acompañamiento.acompañante == perfil

    if not es_solicitante and not es_acompañante:
        return Response({"error": "No tienes permiso"}, status=403)

    # Cancelamos el acompañamiento
    acompañamiento.estado = 'CANCELADO'
    acompañamiento.cancelado_por = 'solicitante' if es_solicitante else 'acompañante' 
    acompañamiento.save()

    if es_solicitante and acompañamiento.acompañante:
        # Notificamos al acompañante en caso de que sea el solicitante quien cancela el acompañamiento
        send_notificacion_cancelacion(
            acompañamiento.acompañante.user.id,
            acompañamiento,
            cancelado_por='solicitante',
            nombre=perfil.nombre_completo or perfil.nombreUsuario,
        )
    elif es_acompañante:
        # Notificamos al solicitante en caso de que sea el acompañante confirmado quien cancela el acompañamiento
        send_notificacion_cancelacion(
            acompañamiento.solicitante.user.id, 
            acompañamiento,
            cancelado_por='acompañante',
            nombre=perfil.nombre_completo or perfil.nombreUsuario,
        )
    return Response({"status": "cancelado"})

@api_view(['POST']) 
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def reenviar_acompañamiento(request, acompañamiento_id):
    """ El solicitante reenvía su solicitud tras una cancelación del acompañante. """
    perfil = request.user.perfilusuario
    try:
        acompañamiento = Acompañamiento.objects.get(
            id=acompañamiento_id,
            solicitante=perfil,
            estado='CANCELADO',
            cancelado_por='acompañante'
        )
    except Acompañamiento.DoesNotExist:
        return Response({"error": "No encontrado"}, status=404)
    
    acompañamiento.acompañante = None
    acompañamiento.estado = 'SOLICITADO'
    acompañamiento.cancelado_por = None
    acompañamiento.save()

    # Renotificamos a las usuarias cercanas
    acompañantes_cercanos = Ubicacion.objects.filter(
        disponible=True,
        usuario__disponible=True,
    ).exclude(usuario=perfil).filter(
        posicion__distance_lte=(acompañamiento.origen, D(km=2))
    ).select_related('usuario')

    for ubi in acompañantes_cercanos:
        send_notificacion_acompañamiento(ubi.usuario.user.id, acompañamiento)
    
    return Response({"status": "reenviado"})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def mi_perfil(request):
    perfil = request.user.perfilusuario
    serializer = PerfilUsuarioSerializer(perfil)
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def usuario_acepta_acompañamiento(request, acompañamiento_id):
    """ Un usuario disponible acepta el acompañamiento """

    try: 
        acompañamiento = Acompañamiento.objects.get(id=acompañamiento_id, estado__in=["SOLICITADO", "ACEPTADO"])
    except Acompañamiento.DoesNotExist:
        return Response({"error": "Acompañamiento no disponible"}, status=404)
    
    perfil = request.user.perfilusuario
    
    candidato, creado = CandidatoAcompañamiento.objects.get_or_create(
        acompañamiento=acompañamiento,
        candidato=perfil,
    )
    
    if acompañamiento.estado == "SOLICITADO":
        acompañamiento.acompañante = perfil
        acompañamiento.estado = "ACEPTADO"
        acompañamiento.save()
        send_notificacion_acompañante_propuesto(acompañamiento.solicitante.user.id, acompañamiento)

    return Response({"status": "candidatura_registrada"})
 
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def solicitante_responde_acompañante(request, acompañamiento_id):
    try:
        acompañamiento = Acompañamiento.objects.get(id=acompañamiento_id, solicitante=request.user.perfilusuario)
    except Acompañamiento.DoesNotExist:
        return Response({"error": "Acompañamiento no encontrado"})
    
    acepta = request.data.get('acepta')
    if acepta:
        acompañamiento.estado = "ASIGNADO"
        acompañamiento.save()
        
        # Limpiamos la cola de candidatos ya que no hace falta
        acompañamiento.candidatos.all().delete()
        
        # Notificamos al acompañante de que ha sido confirmado
        send_notificacion_acompañamiento_confirmado(
            acompañamiento.acompañante.user.id, acompañamiento
        )
        
        return Response({"status": "acompañamiento_asignado"})
    else:
        # El solicitante rechaza el conductor
        perfil_rechazado = acompañamiento.acompañante
        
        # Eliminamos al candidato rechazado de la cola
        acompañamiento.candidatos.filter(candidato=perfil_rechazado).delete()
        
        # Buscamos el siguiente en la cola
        siguiente = acompañamiento.candidatos.exclude(
            candidato=perfil_rechazado
        ).first()

        if siguiente:
            # Si hay alguien esperando lo proponemos directamente
            acompañamiento.acompañante = siguiente.candidato
            acompañamiento.estado = "ACEPTADO"
            acompañamiento.save()
            send_notificacion_acompañante_propuesto(acompañamiento.solicitante.user.id, acompañamiento)
        else:
            # La cola está vacía, por lo que volvemos a estado SOLICITADO y esperamos nuevas aceptaciones
            acompañamiento.acompañante = None
            acompañamiento.estado = "SOLICITADO"
            acompañamiento.save()

        return Response({"status": "acompañante_rechazado"})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def mis_acompañamientos_activos(request):
    """ Devuelve acompañamientos activos del usuario (como solicitante o acompañante) """
    perfil = request.user.perfilusuario
    acompañamientos = Acompañamiento.objects.filter(
        models.Q(solicitante=perfil) | models.Q(acompañante=perfil)
    ).exclude(estado__in=["FINALIZADO", "CANCELADO"])

    data = [{
        "id": a.id,
        "estado": a.estado,
        "es_mio": a.solicitante == perfil,
        "acompañante": a.acompañante.nombreUsuario if a.acompañante else None,
        "solicitante": a.solicitante.nombreUsuario,
        "destino_lat": round(a.destino.y, 2),
        "destino_lng": round(a.destino.x, 2),
        "fecha": a.fecha_comienzo,
    } for a in acompañamientos] 

    return Response(data)


class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    queryset = PerfilUsuario.objects.all()
    serializer_class = PerfilUsuarioSerializer

@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(
            user=instance,
            nombreUsuario = instance.username
        )

class IncidenciaViewSet(viewsets.ModelViewSet):
    queryset = Incidencia.objects.all()
    serializer_class = IncidenciaSerializer

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)
    

class ZonaViewSet(viewsets.ModelViewSet):
    queryset = Zona.objects.all()
    serializer_class = ZonaSerializer

    def get_queryset(self):
        return Zona.objects.annotate(
            total_gravedad=Sum("incidencias__gravedad")
        )

    def create(self, request, *args, **kwargs):
        print(request.data)
        return super().create(request, *args, **kwargs)

class AcompañamientoViewSet(viewsets.ModelViewSet):
    queryset = Acompañamiento.objects.all()
    serializer_class = AcompañamientoSerializer

    def perform_create(self, serializer):
        acompañamiento = serializer.save(solicitante=self.request.user)
        self.buscar_acompañantes_cercanos(acompañamiento)

    def buscar_acompañantes_cercanos(self, acompañamiento):
        origen = acompañamiento.origen
        acompañantes = Ubicacion.objects.filter(
            disponible=True,
            usuario__disponible =True,
        ).annotate(
            distancia=Distance('posicion', origen)
        ).order_by('distancia')[:5]

        print ("Acompañantes cercanos: ", acompañantes)
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def actualizar_ubicacion(request):
    perfil = request.user.perfilusuario
    lat = request.data.get('lat')
    lng = request.data.get('lng')

    if not lat or not lng:
        return Response({"error": "Faltan coordenadas"}, status=400)
    Ubicacion.objects.update_or_create(
        usuario=perfil,
        defaults={
            'posicion': Point(float(lng), float(lat), srid=4326),
            'disponible': True,
        }
    )

    return Response({"status": "ok"})
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def marcar_hora_fin(request, acompañamiento_id):
    perfil = request.user.perfilusuario
    try:
        acompañamiento = Acompañamiento.objects.get(id=acompañamiento_id, solicitante=perfil, estado='ASIGNADO')
    except Acompañamiento.DoesNotExist:
        return Response({"error": "Acompañamiento no encontrado"}, status=404)
    
    hora_str = request.data.get('hora_fin')
    try:
        hora_fin = datetime.strptime(hora_str, '%H:%M').time()
    except (ValueError, TypeError):
        return Response({"error": "Hora inválida"}, status=400)
    
    import pytz
    hora_españa = pytz.timezone('Europe/Madrid')
    hora_fin = datetime.strptime(hora_str, '%H:%M').time()
    hoy = timezone.now().astimezone(hora_españa).date()
    fecha_fin = hora_españa.localize(datetime.combine(hoy, hora_fin))
    acompañamiento.hora_fin_estimada = hora_fin
    acompañamiento.fecha_fin = fecha_fin
    acompañamiento.save()

    return Response({"status": "hora_fin_guardada", "fecha_fin": fecha_fin})

def finalizar_acompañamientos_expirados():
    ahora = timezone.now()
    expirados = Acompañamiento.objects.filter(
        estado='ASIGNADO',
        fecha_fin__lte=ahora,
    )

    for a in expirados:
        a.estado = 'FINALIZADO'
        a.save()
        # Notificar al usuario para que valore
        send_notificacion_finalizado(a.solicitante.user.id, a)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def valorar_acompañamiento(request, acompañamiento_id):
    perfil = request.user.perfilusuario
    try:
        acompañamiento = Acompañamiento.objects.get(
            id=acompañamiento_id,
            # solicitante=perfil,
            estado='FINALIZADO'
        )
    except Acompañamiento.DoesNotExist:
        return Response({"error": "Acompañamiento no encontrado"}, status=404)
    
    es_solicitante = acompañamiento.solicitante == perfil
    es_acompañante = acompañamiento.acompañante == perfil

    if not es_solicitante and not es_acompañante:
        return Response({"error": "No tienes permiso"}, status=403)
    
    # Comprobamos si ya se había valorado
    if acompañamiento.valoraciones.filter(valorador=perfil).exists():
        return Response({"error": "Ya has valorado este acompañamiento"}, status=400)
    
    puntuacion = request.data.get('puntuacion')
    
    try:
        puntuacion = int(puntuacion)
    except(TypeError, ValueError):
        return Response({"error": "Puntuación inválida"}, status=400)
    
    valorado = acompañamiento.acompañante if es_solicitante else acompañamiento.solicitante
    
    Valoracion.objects.create(
        acompañamiento=acompañamiento,
        valorador=perfil,
        valorado=valorado,
        puntuacion=int(puntuacion),
        comentario=request.data.get('comentario', ''),
    )

    return Response({"status": "valorado"})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def ver_perfil_usuario(request, nombre_usuario):
    try:
        perfil = PerfilUsuario.objects.get(nombreUsuario=nombre_usuario)
    except PerfilUsuario.DoesNotExist:
        return Response({"error": "No encontrado"}, status=404)
    
    return Response({
        "nombreUsuario": perfil.nombreUsuario,
        "nombre_completo": perfil.nombre_completo,
        "puntuacion_media": perfil.puntuacion_media,
        "num_acompañamientos": perfil.num_acompañamientos,
        "genero": perfil.genero,
    })

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def activar_panico(request, acompañamiento_id):
    perfil = request.user.perfilusuario
    try: 
        acompañamiento = Acompañamiento.objects.get(
            id=acompañamiento_id,
            solicitante=perfil,
            estado='ASIGNADO',
            tipo="VIRTUAL",
        )
        print(f"tipo={acompañamiento.tipo}, estado={acompañamiento.estado}, solicitante={acompañamiento.solicitante}, perfil={perfil}")
    except Acompañamiento.DoesNotExist:
        return Response({"error": "No encontrado"}, status=404)
    
    lat = request.data.get('lat')
    lng = request.data.get('lng')
    
    acompañamiento.panico_activado = True
    if lat and lng:
        acompañamiento.panico = Point(float(lng), float(lat), srid=4326)
    
    acompañamiento.save()
    print(f"Acompañante: {acompañamiento.acompañante}")
    if acompañamiento.acompañante:
        print(f"Enviando pánico a user_{acompañamiento.acompañante.user.id}")
        send_alerta_panico(
            acompañamiento.acompañante.user.id,
            acompañamiento,
            lat=acompañamiento.panico.y if acompañamiento.panico else None,
            lng = acompañamiento.panico.x if acompañamiento.panico else None,
        )
    
    return Response({"status": "panico_activado"})

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def finalizar_acompañamiento(request, acompañamiento_id):
    perfil = request.user.perfilusuario
    try:
        acompañamiento = Acompañamiento.objects.get(
            id=acompañamiento_id,
            solicitante=perfil,
            estado='ASIGNADO',
            tipo='VIRTUAL',
        )
    except Acompañamiento.DoesNotExist:
        return Response({"error": "No encontrado"}, status=404)

    acompañamiento.estado = 'FINALIZADO'
    acompañamiento.save()

    if acompañamiento.acompañante:
        send_acompañamiento_finalizado(acompañamiento.acompañante.user.id, acompañamiento)
    send_notificacion_finalizado(acompañamiento.solicitante.user.id, acompañamiento)

    return Response({"status": "acompañamiento_finalizado"})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def obtener_ubicacion_panico(request, acompañamiento_id):
    perfil = request.user.perfilusuario
    try:
        acompañamiento = Acompañamiento.objects.get(
            id=acompañamiento_id,
            acompañante=perfil,
            tipo='VIRTUAL',
        )
    except Acompañamiento.DoesNotExist:
        return Response({"error": "No encontrado"}, status=404)

    return Response({
        "panico_activado": acompañamiento.panico_activado,
        "lat": acompañamiento.panico.y if acompañamiento.panico else None,
        "lng": acompañamiento.panico.x if acompañamiento.panico else None,
        "solicitante": acompañamiento.solicitante.nombre_completo or acompañamiento.solicitante.nombreUsuario,
    })
