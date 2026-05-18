import { ref } from 'vue'

export function useWebSocket({ onSolicitudRegistro, onNuevoAcompañamiento, onAcompañantePropuesto, onAcompañamientoConfirmado, onAcompañanteAsignado, onAcompañamientoFinalizado, onAlertaPanico, onAcompañamientoFinalizadoAcompañante }) {
  const socket = ref(null)

  function connect() {
    const token = localStorage.getItem('token')
    // socket.value = new WebSocket(`ws://localhost:8000/ws/notificaciones/?token=${token}`)
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/notificaciones/?token=${token}`
    socket.value = new WebSocket(wsUrl)

    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
       console.log('WS mensaje recibido:', data)
      if (data.type === 'solicitudRegistro') onSolicitudRegistro?.()
      if (data.type === 'nuevo_acompañamiento') onNuevoAcompañamiento?.(data)
      if (data.type === 'acompañanteAsignado') onAcompañanteAsignado?.()
      if (data.type === 'acompañante_propuesto') onAcompañantePropuesto?.(data)
      if (data.type === 'acompañamiento_confirmado') onAcompañamientoConfirmado?.(data)
      if (data.type === 'acompañante_asignado') onAcompañanteAsignado?.(data)
      if (data.type === 'acompañamiento_finalizado') onAcompañamientoFinalizado?.(data)
      if (data.type === 'alerta_panico') onAlertaPanico?.(data)
      if (data.type === 'viaje_finalizado') onAcompañamientoFinalizadoAcompañante?.(data)

    }
  }

  function disconnect() {
    socket.value?.close()
    socket.value = null
  }

  return { connect, disconnect }
}



