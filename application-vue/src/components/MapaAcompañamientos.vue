<template>
    <div :id="mapId" class="acomp-mapa"></div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import L from 'leaflet'

const props = defineProps({
  origenLat:  Number,
  origenLng:  Number,
  destinoLat: Number,
  destinoLng: Number,
  exacto:     { type: Boolean, default: false },  // si false, muestra zona difusa
})

const mapId = `acomp-mapa-${Math.random().toString(36).slice(2)}`
let mapa = null

onMounted(() => {
  const centro = [(props.origenLat + props.destinoLat) / 2, (props.origenLng + props.destinoLng) / 2,]

  mapa = L.map(mapId, {
    zoomControl: true, attributionControl: false,
    dragging: true, scrollWheelZoom: true, doubleClickZoom: true,
    touchZoom: true, keyboard: false,
  }).setView(centro, 14)


  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(mapa)

  const iconOrigen = L.divIcon({ className: '', html: '<div style="font-size:16px">📍</div>', iconAnchor: [8, 16] })
  const iconDestino = L.divIcon({ className: '', html: '<div style="font-size:16px">🏁</div>', iconAnchor: [8, 16] })

  if (props.exacto) {
    L.marker([props.origenLat, props.origenLng], { icon: iconOrigen }).addTo(mapa)
    L.marker([props.destinoLat, props.destinoLng], { icon: iconDestino }).addTo(mapa)
    L.polyline([
      [props.origenLat, props.origenLng],
      [props.destinoLat, props.destinoLng]
    ], { color: '#9B71B2', weight: 2, dashArray: '5 5' }).addTo(mapa)

    mapa.fitBounds([
      [props.origenLat, props.origenLng],
      [props.destinoLat, props.destinoLng]
    ], { padding: [20, 20] })

  } else {
    // Círculo difuso para mostrar una ubicación aproximada
    L.circle([props.origenLat, props.origenLng], {
      radius: 200,
      color: '#9B71B2', fillColor: '#9B71B2',
      fillOpacity: 0.15, weight: 1.5,
    }).addTo(mapa)

    L.circle([props.destinoLat, props.destinoLng], { 
      radius: 200, color: '#E07B5A', fillColor: '#E07B5A',
      fillOpacity: 0.15, weight: 1.5,
    }).addTo(mapa)

    L.polyline([
      [props.origenLat, props.origenLng],
      [props.destinoLat, props.destinoLng]
    ], { color: '#9B71B2', weight: 2, dashArray: '5 5', opacity: 0.5 }).addTo(mapa)

    const delta = 0.002
    mapa.fitBounds([
      [Math.min(props.origenLat, props.destinoLat) - delta, Math.min(props.origenLng, props.destinoLng) - delta], 
      [Math.max(props.origenLat, props.destinoLat) + delta, Math.max(props.origenLng, props.destinoLng) + delta],
    ], { padding: [10, 10] })
  }
})

onUnmounted(() => { mapa?.remove() })
</script>

<style scoped>
.acomp-mapa {
  width: 100%;
  height: 130px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border);
}
</style>