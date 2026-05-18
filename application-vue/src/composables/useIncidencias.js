import { ref } from 'vue'
import api from '../services/api'

export function useIncidencias() {
  const incidencias = ref([])
  const zonaSeleccionada = ref(null)
  const gravedadSeleccionada = ref(1)
  const descripcion = ref('')

  async function cargarIncidencias() {
    const res = await api.get('api/v1/incidencias/')
    incidencias.value = res.data
  }

  async function agregarIncidencia(onSuccess) {
    console.log('zonaSeleccionada al crear: ', zonaSeleccionada.value)
    if (!zonaSeleccionada.value) {
      alert('Selecciona una zona')
      return
    }
    try {
      await api.post('api/v1/incidencias/', {
        zona: zonaSeleccionada.value,
        gravedad: gravedadSeleccionada.value,
        descripcion: descripcion.value,
      })
      descripcion.value = ''
      gravedadSeleccionada.value = 1
      zonaSeleccionada.value = null
      await cargarIncidencias()
      onSuccess?.()   // Recargamos las zonas
    } catch (e) {
      console.error('Error al crear incidencia:', e)
    }
  }

  return {
    incidencias, zonaSeleccionada, gravedadSeleccionada, descripcion,
    cargarIncidencias, agregarIncidencia,
  }
}