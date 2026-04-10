import { ref } from 'vue'
import api from '../services/api'
import L from 'leaflet'

function getColor(d) {
  return d > 20 ? '#800026' : d > 15 ? '#BD0026' : d > 10 ? '#e37b1a'
       : d > 5  ? '#fcb92a' : d > 2  ? '#f0fd3c' : d > 0  ? '#4c8afe' : '#a0ecff'
}

export function useZonas(mapRef, onZonaClick) {
  const zonas = ref([])
  const zonasLayer = ref(null)
  const nombreNuevaZona = ref('')
  const nuevasCoordenadas = ref(null)
  const mostrarFormularioZona = ref(false)

  async function cargarZonas() {
    try {
      const res = await api.get('api/v1/zonas/')
      const geojson = res.data
      zonas.value = geojson.features.map(f => ({ id: f.id, nombre: f.properties.nombre, coordenadas: f.geometry, }))
      if (zonasLayer.value) mapRef.value.removeLayer(zonasLayer.value)
      zonasLayer.value = L.geoJSON(geojson, {
        style(feature) {
          return {
            fillColor: getColor(feature.properties.total_gravedad || 0),
            weight: 2, color: 'black', fillOpacity: 0.6,
          }
        },
        onEachFeature: (feature, layer) => {
          layer.bindPopup(`<strong>${feature.properties.nombre}</strong><br/>
            Total gravedad: ${feature.properties.total_gravedad || 0}`)
          layer.on('click', () => {
            console.log('clic en feature:', feature)
            if (onZonaClick) onZonaClick({
                id: feature.id,
                nombre: feature.properties.nombre,
            })
          })
        },
      }).addTo(mapRef.value)
      mapRef.value.fitBounds(zonasLayer.value.getBounds())
    } catch (e) {
      console.error('Error cargando zonas:', e)
    }
  }

  async function guardarZona() {
    if (!nombreNuevaZona.value || !nuevasCoordenadas.value) {
      alert('Faltan datos')
      return
    }
    await api.post('api/v1/zonas/', {
      type: 'Feature',
      geometry: nuevasCoordenadas.value,
      properties: { nombre: nombreNuevaZona.value },
    })
    nombreNuevaZona.value = ''
    nuevasCoordenadas.value = null
    mostrarFormularioZona.value = false
    await cargarZonas()
  }

  return {
    zonas, nombreNuevaZona, nuevasCoordenadas, mostrarFormularioZona,
    cargarZonas, guardarZona,
  }
}