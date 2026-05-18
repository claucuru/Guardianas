<template>
    <div class="panico-overlay">
        <div class="panico-modal">
            <div class="panico-header">
                <span class="panico-icono">🚨</span>
                <div>
                    <h2 class="panico-titulo">Alerta SOS</h2>
                    <p class="panico-sub">{{ datos.solicitante_nombre }} ha activado una alerta de pánico</p>
                </div>
                <button class="btn-cerrar-panico" @click="$emit('cerrar')">✕</button>
            </div>
            <div v-if="datos.lat && datos.lng" :id="mapId" class="panico-mapa"</div>
            <p v-else class="panico-sin-ubicacion">No se pudo obtener la ubicación exacta</p>
            <a href="tel:112" class="btn-emergencias">Llamar al 112</a>
        </div>
    </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import L from 'leaflet'

const props = defineProps({
  datos: { type: Object, required: true }
})
defineEmits(['cerrar'])

const mapId = `panico-mapa-${Math.random().toString(36).slice(2)}`
let mapa = null

onMounted(() => {
  if (!props.datos.lat || !props.datos.lng) return
  mapa = L.map(mapId, { zoomControl: true, attributionControl: false })
    .setView([props.datos.lat, props.datos.lng], 16)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(mapa)

  L.marker([props.datos.lat, props.datos.lng], {
    icon: L.divIcon({ className: '', html: '<div style="font-size:24px">🚨</div>', iconAnchor: [12, 24] })
  }).addTo(mapa).bindPopup('Última ubicación conocida').openPopup()

  L.circle([props.datos.lat, props.datos.lng], {
    radius: 50, color: '#dc3545', fillColor: '#dc3545', fillOpacity: 0.15, weight: 2
  }).addTo(mapa)
})

onUnmounted(() => mapa?.remove())
</script>

<style scoped>
.panico-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.panico-modal {
  background: var(--surface);
  border: 2px solid #dc3545;
  border-radius: 20px;
  width: 100%;
  max-width: 440px;
  overflow: hidden;
  box-shadow: 0 0 40px rgba(220, 53, 69, 0.4);
  display: flex;
  flex-direction: column;
  gap: 0;
}

.panico-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 1.2rem 1.4rem;
  background: rgba(220, 53, 69, 0.08);
  border-bottom: 1px solid rgba(220, 53, 69, 0.25);
}

.panico-icono { font-size: 1.8rem; }

.panico-titulo {
  margin: 0;
  font-size: 1.05rem;
  color: #dc3545;
}

.panico-sub {
  margin: 2px 0 0;
  font-size: 0.8rem;
  color: var(--muted);
}

.btn-cerrar-panico {
  margin-left: auto;
  background: transparent;
  border: none;
  font-size: 1rem;
  color: var(--muted);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
}
.btn-cerrar-panico:hover { background: var(--border); }

.panico-mapa {
  width: 100%;
  height: 260px;
}

.panico-sin-ubicacion {
  text-align: center;
  color: var(--muted);
  font-size: 0.85rem;
  padding: 2rem;
}

.btn-emergencias {
  display: block;
  margin: 1rem 1.4rem 1.4rem;
  background: #dc3545;
  color: white;
  text-align: center;
  padding: 14px;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 700;
  text-decoration: none;
  transition: opacity .2s;
}
.btn-emergencias:hover { opacity: 0.88; }
</style>


