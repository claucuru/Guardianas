import { ref } from 'vue'

export function useWebSocket({ onSolicitudRegistro, onNuevoAcompañamiento, onAcompañantePropuesto, onAcompañamientoConfirmado, onAcompañanteAsignado }) {
  const socket = ref(null)

  function connect() {
    const token = localStorage.getItem('token')
    socket.value = new WebSocket(`ws://localhost:8000/ws/notificaciones/?token=${token}`)

    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
       console.log('WS mensaje recibido:', data)
      if (data.type === 'solicitudRegistro') onSolicitudRegistro?.()
      if (data.type === 'nuevo_acompañamiento') onNuevoAcompañamiento?.(data)
      if (data.type === 'acompañanteAsignado') onAcompañanteAsignado?.()
      if (data.type === 'acompañante_propuesto') onAcompañantePropuesto?.(data)
      if (data.type === 'acompañamiento_confirmado') onAcompañamientoConfirmado?.(data)
      if (data.type === 'acompañante_asignado') onAcompañanteAsignado?.(data)

    }
  }

  function disconnect() {
    socket.value?.close()
    socket.value = null
  }

  return { connect, disconnect }
}



