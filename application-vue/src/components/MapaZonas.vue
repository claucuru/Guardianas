<template>
  <div class="map-section card" style="position:relative; overflow:hidden">
    <div class="map-header">
      <h3>Zonas</h3>
      <div style="display:flex; gap:8px; align-items:center">
        <span v-if="localizando" class="spinner"></span>
      </div>
    </div>

    <div id="map"></div>

    <!-- Panel de ayuda -->
    <transition name="fade">
      <div v-if="!mostrarFormulario && !dibujando && !props.zonaActiva" class="zona-hint">
        <p class="zona-hint-text">
          ¿Quieres registrar una incidencia? Muévete por el mapa a ver si existe
          una zona cercana. Si no, activa el modo dibujo.
        </p>
        <button class="btn-primary" style="margin-top:10px" @click="activarDibujo">
          Dibujar zona nueva
        </button>
      </div>
    </transition>

    <!-- Formulario zona nueva -->
    <transition name="fade">
      <div v-if="mostrarFormulario" class="zona-form card">
        <h3>Nueva Zona</h3>
        <div class="field">
          <label>Nombre</label>
          <input v-model="nombreLocal" placeholder="Nombre de la zona" autofocus />
        </div>
        <p v-if="zonasCercanas.length" class="zona-aviso">
          Hay {{ zonasCercanas.length }} zona(s) cercana(s):
          <strong>{{ zonasCercanas.map(z => z.nombre).join(', ') }}</strong>.
          ¿Seguro que quieres crear una nueva?
        </p>
        <div class="zona-form-btns">
          <button class="btn-primary" :disabled="!nombreLocal.trim()" @click="guardar">Guardar</button>
          <button class="btn-ghost" @click="cancelar">Cancelar</button>
        </div>
      </div>
    </transition>

    <!-- Panel lateral de incidencias -->
    <transition name="slide-panel">
      <div v-if="props.zonaActiva" class="incidencias-panel">
        <div class="incidencias-panel-header">
          <div>
            <p class="incidencias-panel-titulo">{{ props.zonaActiva.nombre }}</p>
            <p class="incidencias-panel-sub">{{ incidenciasZona.length }} incidencia(s)</p>
          </div>
          <button class="btn-cerrar" @click="emit('cerrar-panel')">✕</button>
        </div>

        <div class="incidencias-panel-body">
          <div v-if="incidenciasZona.length === 0" class="incidencias-vacio">
            <p>No hay incidencias registradas en esta zona.</p>
          </div>
          <div v-for="inc in incidenciasZona" :key="inc.id" class="incidencia-item">
            <div class="incidencia-item-top">
              <span :class="`gravedad-badge g${inc.gravedad}`">G{{ inc.gravedad }}</span>
              <span class="incidencia-fecha">{{ formatFecha(inc.fecha) }}</span>
            </div>
            <p class="incidencia-desc">{{ inc.descripcion || '(sin descripción)' }}</p>
            <p class="incidencia-usuario">{{ inc.usuario ?? inc.creado_por ?? '—' }}</p>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-draw'
import 'leaflet-draw/dist/leaflet.draw.css'

const props = defineProps({
  incidencias: { type: Array,  default: () => ([]) },
  zonaActiva:  { type: Object, default: null },
})

const emit = defineEmits(['mapa-listo', 'zona-guardada', 'agregar-', 'cerrar-panel'])

// ---- formulario ----------------------------------------------
const mostrarFormulario     = ref(false)
const dibujando             = ref(false)
const nombreLocal           = ref('')
const coordenadasPendientes = ref(null)
const capaPendiente         = ref(null)
const zonasCercanas         = ref([])
const localizando           = ref(false)

// ---- panel de incidencias -----------------------------------
const incidenciasZona = computed(() => {
  if (!props.zonaActiva) return []
  return props.incidencias.filter(i => i.zona === props.zonaActiva.id)
})

function formatFecha(fecha) {
  if (!fecha) return '—'
  return new Date(fecha).toLocaleDateString('es-ES', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

// ---- mapa ----------------------------------------------------
let map        = null
let drawnItems = null
let zonasLayer = null

onMounted(() => {
  map = L.map('map').setView([40.4168, -3.7038], 6)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
  }).addTo(map)

  zonasLayer = new L.FeatureGroup().addTo(map)
  drawnItems = new L.FeatureGroup().addTo(map)

  map.on(L.Draw.Event.CREATED, (e) => {
    dibujando.value             = false
    drawnItems.addLayer(e.layer)
    capaPendiente.value         = e.layer
    coordenadasPendientes.value = e.layer.toGeoJSON().geometry
    zonasCercanas.value         = encontrarZonasCercanas(e.layer)
    mostrarFormulario.value     = true
  })

  map.on(L.Draw.Event.DRAWSTART, () => { dibujando.value = true })
  map.on(L.Draw.Event.DRAWSTOP,  () => { dibujando.value = false })

  localizarUsuario()
  emit('mapa-listo', map)
})

function localizarUsuario() {
  if (!navigator.geolocation) return
  localizando.value = true
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      localizando.value = false
      const { latitude: lat, longitude: lng } = pos.coords
      map.setView([lat, lng], 15)
      L.circleMarker([lat, lng], {
        radius: 8, color: '#9B71B2',
        fillColor: '#9B71B2', fillOpacity: 0.35, weight: 2,
      }).addTo(map).bindTooltip('Tu ubicación', { permanent: false })
    },
    () => { localizando.value = false },
    { timeout: 8000, enableHighAccuracy: true }
  )
}

function encontrarZonasCercanas(capaActual) {
  const bounds = capaActual.getBounds()
  const cercanas = []
  zonasLayer.eachLayer((capa) => {
    if (capa.getBounds && capa.getBounds().intersects(bounds)) {
      cercanas.push({ nombre: 'zona existente' })
    }
  })
  return cercanas
}

function activarDibujo() {
  dibujando.value = true
  new L.Draw.Polygon(map, {
    shapeOptions: { color: '#9B71B2', weight: 2, fillOpacity: 0.15 },
  }).enable()
}

function guardar() {
  if (!nombreLocal.value.trim()) return
  emit('zona-guardada', {
    nombre: nombreLocal.value.trim(),
    coordenadas: coordenadasPendientes.value,
  })
  if (capaPendiente.value) {
    drawnItems.removeLayer(capaPendiente.value)
    capaPendiente.value.addTo(zonasLayer)
  }
  resetFormulario()
}

function cancelar() {
  if (capaPendiente.value) drawnItems.removeLayer(capaPendiente.value)
  resetFormulario()
}

function resetFormulario() {
  mostrarFormulario.value     = false
  dibujando.value             = false
  nombreLocal.value           = ''
  coordenadasPendientes.value = null
  capaPendiente.value         = null
  zonasCercanas.value         = []
}
</script>

<style scoped>
.incidencias-panel {
  position: absolute;
  top: 0; right: 0;
  width: 300px;
  height: 100%;
  background: var(--surface);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  box-shadow: -6px 0 24px rgba(0,0,0,0.12);
}
.incidencias-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.incidencias-panel-titulo {
  font-family: 'Rozha One', serif;
  font-size: 1rem;
  color: var(--accent-strong);
  margin-bottom: 2px;
}
.incidencias-panel-sub { font-size: 0.75rem; color: var(--muted); }
.btn-cerrar {
  background: transparent; border: none;
  font-size: 1rem; color: var(--muted);
  cursor: pointer; padding: 2px 6px;
  border-radius: 6px; transition: background .15s; flex-shrink: 0;
}
.btn-cerrar:hover { background: var(--border); color: var(--text); }
.incidencias-panel-body {
  flex: 1; overflow-y: auto; padding: 0.75rem;
  display: flex; flex-direction: column; gap: 8px;
}
.incidencias-vacio {
  display: flex; align-items: center; justify-content: center;
  height: 100%; color: var(--muted); font-size: 0.85rem;
  text-align: center; padding: 2rem;
}
.incidencia-item {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 10px; padding: 10px 12px;
  display: flex; flex-direction: column; gap: 5px;
}
.incidencia-item-top { display: flex; justify-content: space-between; align-items: center; }
.incidencia-fecha  { font-size: 0.72rem; color: var(--muted); }
.incidencia-desc   { font-size: 0.85rem; color: var(--text); line-height: 1.4; }
.incidencia-usuario { font-size: 0.75rem; color: var(--muted); }

.slide-panel-enter-active,
.slide-panel-leave-active { transition: transform 0.28s ease; }
.slide-panel-enter-from,
.slide-panel-leave-to     { transform: translateX(100%); }
</style>