from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

class NotificacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        print(f"WEB SOCKET connect: {self.user}, autenticado: {self.user.is_authenticated}")

        if not self.user.is_authenticated:
            print("WS rechazado: no autenticado")
            await self.close()
            return
        
        self.group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"WS aceptado: grupo {self.group_name}")
    
    async def disconnect(self, code):
        print(f"WEB SOCKET disconnect: código {code}, grupo{getattr(self, 'group_name', 'sin grupo')}")
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def notificacion_registro(self, event):
        await self.send(text_data=json.dumps({
            "type": "solicitudRegistro",
            "mensaje": event["mensaje"],
            "pendiente_id": event["pendiente_id"]
        }))
    
    async def nuevo_acompañamiento(self, event):
        print(f"Consumer recibe un nuevo_acompañamiento: {event}")
        try:
            await self.send(text_data=json.dumps ({
                "type": "nuevo_acompañamiento",
                "acompañamiento_id": event.get("acompañamiento_id"),
                "solicitante": event.get("solicitante"),
                "destino_lat": event.get("destino_lat"),
                "destino_lng": event.get("destino_lng"),
                "fecha": event.get("fecha"),
                # **event
            }))
        except Exception as e:
            print(f"Error enviando nuevo_acompañamiento: {e}")
    
    async def acompañante_propuesto(self, event):
        await self.send(text_data=json.dumps({
            "type": "acompañante_propuesto",
            **event
        }))

    async def acompañamiento_confirmado (self, event):
        await self.send(text_data=json.dumps ({
            "type": "acompañamiento_confirmado",
            **event
        }))
    
    async def notificacion_cancelacion(self, event):
        await self.send(text_data=json.dumps ({
            "type": "notificacion_cancelacion",
            "acompañamiento_id": event.get("acompañamiento_id"),
            "cancelado_por": event.get("cancelado_por"),
            "nombre": event.get("nombre"),
        }))
    
    async def acompañamiento_finalizado(self, event):
        await self.send(text_data=json.dumps({
            "type": "acompañamiento_finalizado",
            "acompañamiento_id": event.get("acompañameinto_id"),
        }))
    
    async def alerta_panico(self, event):
        print(f"Consumer alerta_panico enviando a {self.user}: {event}")
        await self.send(text_data=json.dumps({
            "type": "alerta_panico",
            "acompañamiento_id": event.get("acompañamiento_id"),
            "solicitante": event.get("solicitante"),
            "lat": event.get("lat"),
            "lng": event.get("lng"),
        }))
    
    async def acompañamiento_finalizado(self, event):
        await self.send(text_data=json.dumps({
            "type": "acompañamiento_finalizado",
            "acompañamiento_id": event.get("acompañamiento_id"),
        }))

def send_acompañamiento_finalizado(usuario_id, acompañamiento):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send) (
        f"user_{usuario_id}", {
            "type": "acompañamiento_finalizado",
            "acompañamiento_id": acompañamiento.id,
        }
    )

def send_alerta_panico(usuario_id, acompañamiento, lat, lng):
    print(f"send_alerta_panico → user_{usuario_id}, lat={lat}, lng={lng}")
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send) (
        f"user_{usuario_id}", {
            "type": "alerta_panico",
            "acompañamiento_id": acompañamiento.id,
            "solicitante": acompañamiento.solicitante.nombre_completo or acompañamiento.solicitante.nombreUsuario,
            "lat": lat,
            "lng": lng,
        }
    )

def send_notificacion(usuario_id, pendiente):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{usuario_id}",
        {
            "type": "notificacion_registro",
            "mensaje": f"{pendiente.usuario} quiere registrarse y te ha puesto como usuaria referente",
            "pendiente_id": pendiente.id
        }
    )

def send_notificacion_acompañamiento(usuario_id, acompañamiento):
    """ Notifica a un usuario disponible de un nuevo acompañamiento cercano """
    channel_layer = get_channel_layer()
    group_name = f"user_{usuario_id}"
    async_to_sync(channel_layer.group_send)(group_name, {
        "type": "nuevo_acompañamiento",
        "acompañamiento_id": acompañamiento.id,
        "solicitante": acompañamiento.solicitante.nombreUsuario,
        "solicitante_nombre": acompañamiento.solicitante.nombre_completo or acompañamiento.solicitante.nombreUsuario,
        "destino_lat": round(acompañamiento.destino.y, 2),
        "destino_lng": round(acompañamiento.destino.x, 2),
        "origen_lat": round(acompañamiento.origen.y, 2),
        "origen_lng": round(acompañamiento.origen.x, 2),
        "fecha": str(acompañamiento.fecha_comienzo),
    })

def send_notificacion_acompañante_propuesto(usuario_id, acompañamiento):
    """Notifica al solicitante que un usuario ha aceptado."""
    channel_layer = get_channel_layer()
    group_name = f"user_{usuario_id}"
    async_to_sync(channel_layer.group_send)(group_name, {
        "type": "acompañante_propuesto",
        "acompañamiento_id": acompañamiento.id,
        "acompañante": acompañamiento.acompañante.nombreUsuario,
        "acompañante_nombre": acompañamiento.acompañante.nombre_completo or acompañamiento.acompañante.nombreUsuario,
})

def send_notificacion_acompañamiento_confirmado(usuario_id, acompañamiento):
    """ Notifica al acompañante que el solicitante le confirmó """
    channel_layer = get_channel_layer()
    group_name = f"user_{usuario_id}"
    async_to_sync(channel_layer.group_send)(group_name, {
        "type": "acompañamiento_confirmado",
        "acompañamiento_id": acompañamiento.id,
        "solicitante": acompañamiento.solicitante.nombreUsuario,
    })

def send_notificacion_cancelacion(user_id, acompañamiento, cancelado_por, nombre):
    """ Notifica de que el acompañamiento ha sido cancelado """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}', {
            'type': 'notificacion_cancelacion',
            'acompañamiento_id': acompañamiento.id,
            'cancelado_por': cancelado_por,
            'nombre': nombre,
        }
    )

def send_notificacion_finalizado(usuario_id, acompañamiento):
    """ Notifica al solicitante de que el acompañamiento ha finalizado y puede valorar al acompañante"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send) (
        f"user_{usuario_id}", {
            "type": "acompañamiento_finalizado",
            "acompañamiento_id": acompañamiento.id,
        }
    )

