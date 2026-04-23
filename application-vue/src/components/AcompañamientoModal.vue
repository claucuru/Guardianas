<template>
  <transition name="modal-fade">
    <div v-if="visible" class="modal-overlay" @click.self="cerrar">
      <div class="modal">

        <div class="modal-header">
          <div>
            <h2 class="modal-titulo">Pedir acompañamiento</h2>
            <p class="modal-sub">Elige tu punto de encuentro y destino en el mapa</p>
          </div>
          <button class="btn-cerrar-modal" @click="cerrar">✕</button>
        </div>

        <!-- Formulario -->
        <div v-if="paso === 'formulario'" class="modal-body">

          <div class="mapa-instrucciones">
            <span class="instruccion" :class="{ activa: seleccionando === 'origen' }">
              Punto de encuentro
            </span>
            <span class="instruccion-sep">→</span>
            <span class="instruccion" :class="{ activa: seleccionando === 'destino' }">
              Destino
            </span>
          </div>

          <div id="mapa-modal" class="mapa-modal"></div>

          <div class="coordenadas-resumen">
            <div class="coord-item" :class="{ ok: origenLat }">
              <span class="coord-label">Encuentro</span>
              <span class="coord-valor">
                {{ origenLat ? `${origenLat.toFixed(4)}, ${origenLng.toFixed(4)}` : 'Sin seleccionar' }}
              </span>
            </div>
            <div class="coord-item" :class="{ ok: destinoLat }">
              <span class="coord-label">Destino</span>
              <span class="coord-valor">
                {{ destinoLat ? `${destinoLat.toFixed(4)}, ${destinoLng.toFixed(4)}` : 'Sin seleccionar' }}
              </span>
            </div>
          </div>

          <!-- Selector de hora -->
          <div class="hora-selector">
            <label class="hora-label">¿A qué hora necesitas el acompañamiento?</label>
            <div class="hora-opciones">
              <button class="hora-opt" :class="{ activa: horaMode === 'ahora' }"
              @click="horaMode = 'ahora'; horaPersonalizada =''">
                Ahora
              </button>
              <button class="hora-opt" :class="{ activa: horaMode === 'personalizada' }" @click="horaMode = 'personalizada'">
                Elegir hora
              </button>
            </div>
            <input  v-if="horaMode === 'personalizada'" v-model="horaPersonalizada" type="time" class="hora-input"/>
          </div>
          <div class="hora-selector">
            <label class="hora-label">¿A qué hora terminará el acompañamiento?</label>
            <input v-model="horaFin" type="time" class="hora-input"/>
          </div>

          <p v-if="errorUbicacion" class="error-msg">{{ errorUbicacion }}</p>

          <div class="modal-btns">
            <button class="btn-ghost" @click="usarUbicacionActual" :disabled="cargandoGps">
              <span v-if="cargandoGps" class="spinner"></span>
              <span v-else>Usar mi ubicación</span>
            </button>
            <button
              class="btn-primary btn-full" :disabled="cargando || !origenLat || !destinoLat" @click="pedirAcompañamiento">
              <span v-if="cargando" class="spinner"></span>
              <span v-else>Solicitar acompañamiento</span>
            </button>
          </div>
        </div>

        <!-- Esperando -->
        <div v-else-if="paso === 'esperando'" class="modal-body modal-estado">
          <p class="estado-titulo">Buscando acompañante cercana...</p>
          <p class="estado-sub">Se notificará a usuarias disponibles en un radio de 2 km</p>
          <button class="btn-ghost btn-full" style="margin-top:1rem" @click="cancelar">
            Cancelar solicitud
          </button>
        </div>

        <!-- Acompañante propuesto -->
        <div v-else-if="paso === 'acompañante_propuesto'" class="modal-body modal-estado">
          <p class="estado-titulo">¡Usuario disponible!</p>
          <div class="acompañante-card">
            <span class="acompañante-nombre">{{ acompañantePropuesta }}</span>
            <p class="acompañante-sub">Ha aceptado acompañarte</p>
          </div>
          <div class="btns-respuesta">
            <button class="btn-aceptar-acompañamiento btn-full" @click="responder(true)">✓ Aceptar</button>
            <button class="btn-rechazar-acompañamiento btn-full" @click="responder(false)">✗ Buscar otra</button>
          </div>
        </div>

        <!-- Confirmado -->
        <div v-else-if="paso === 'asignado'" class="modal-body modal-estado">
          <p class="estado-titulo">¡Acompañamiento confirmado!</p>
          <p class="estado-sub">Se ha compartido tu ubicación exacta con tu acompañante</p>
          <button class="btn-primary btn-full" style="margin-top:1rem" @click="cerrar">Cerrar</button>
        </div>

      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import L from 'leaflet'
import api from '@/services/api'

const props = defineProps({ visible: { type: Boolean, default: false } })
const emit = defineEmits(['close', 'acompañamiento-solicitado'])

const iconoOrigen = L.divIcon({
    className: '',
    html: '<div style="font-size:20px">📍</div>',
    iconAnchor: [10, 20]
})

const iconoDestino = L.divIcon({
  className: '',
  html: '<div style="font-size:20px">🏁</div>',
  iconAnchor: [10, 20]
})

const paso = ref('formulario')
const origenLat = ref(null)
const origenLng = ref(null)
const destinoLat = ref(null)
const destinoLng = ref(null)
const errorUbicacion = ref('')
const cargando = ref(false)
const cargandoGps = ref(false)
const acompañamientoId = ref(null)
const acompañantePropuesta = ref('')
const seleccionando = ref('origen') // 'origen' | 'destino'
const horaMode = ref('ahora')
const horaPersonalizada = ref('')
const horaFin = ref('')

let mapaModal = null
let marcadorOrigen = null
let marcadorDestino = null
let lineaRuta = null

// Inicializar mapa cuando el modal se abre
watch(() => props.visible, async (v) => {
  if (!v) return
  await nextTick()
  if (mapaModal) { mapaModal.invalidateSize(); return }

  mapaModal = L.map('mapa-modal').setView([40.4168, -3.7038], 13)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(mapaModal)

  mapaModal.on('click', (e) => {
    const { lat, lng } = e.latlng
    if (seleccionando.value === 'origen') {
      setOrigen(lat, lng)
      seleccionando.value = 'destino'
    } else {
      setDestino(lat, lng)
      dibujarLinea()
    }
  })

  // Intentar centrar en ubicación actual al abrir
  usarUbicacionActual()
})

function setOrigen(lat, lng) {
  origenLat.value = lat
  origenLng.value = lng

  if(marcadorOrigen) marcadorOrigen.setLatLng([lat, lng])
  else marcadorOrigen = L.marker([lat, lng], { draggable: true, icon: iconoOrigen })
    .addTo(mapaModal)
    .bindTooltip('Punto de encuentro', { permanent: true, direction: 'top'})
    .on('dragend', e => {
      origenLat.value = e.target.getLatLng().lat
      origenLng.value = e.target.getLatLng().lng
      dibujarLinea()
    })
}

function setDestino(lat, lng) {
  destinoLat.value = lat
  destinoLng.value = lng

  if(marcadorDestino) marcadorDestino.setLatLng([lat, lng])
  else marcadorDestino = L.marker([lat, lng], { draggable: true, icon: iconoDestino })
    .addTo(mapaModal)
    .bindTooltip('Destino', { permanent: true, direction: 'top'})
    .on('dragend', e => {
      destinoLat.value = e.target.getLatLng().lat
      destinoLng.value = e.target.getLatLng().lng
      dibujarLinea()
    })
}

function dibujarLinea() {
  if(!origenLat.value || !destinoLat.value) return 
  const puntos = [
    [origenLat.value, origenLng.value],
    [destinoLat.value, destinoLng.value]
  ]
  if (lineaRuta) lineaRuta.setLatLngs(puntos)
  else lineaRuta = L.polyline(puntos, {
    color: '#9B71B2', weight: 3, dashArray: '6 6', opacity: 0.7
  }).addTo(mapaModal)

  mapaModal.fitBounds(L.latLngBounds(puntos), { padding: [40, 40] })
}

async function usarUbicacionActual() {
  cargandoGps.value = true
  errorUbicacion.value = ''
  try {
    const pos = await new Promise((res, rej) =>
      navigator.geolocation.getCurrentPosition(res, rej, { timeout: 6000 })
    )
    const { latitude: lat, longitude: lng } = pos.coords
    setOrigen(lat, lng)

    if (mapaModal) mapaModal.setView([lat, lng], 15)
    seleccionando.value = 'destino'
  } catch {
    errorUbicacion.value = 'No se pudo obtener tu ubicación. Activa el GPS o selecciona en el mapa.'
  } finally {
    cargandoGps.value = false
  }
}



async function pedirAcompañamiento() {
  cargando.value = true
  errorUbicacion.value = ''
  try {
    const payload = {
      origen_lat: origenLat.value,
      origen_lng: origenLng.value,
      destino_lat: destinoLat.value,
      destino_lng: destinoLng.value,
      hora_fin: horaFin.value || null,
    }

    
    if (horaMode.value === 'personalizada' && horaPersonalizada.value) {
      payload.hora_solicitada = horaPersonalizada.value
    }

    console.log('Payload enviado:', payload)
    const res = await api.post('api/v1/acompañamientos/pedir/', payload)
    acompañamientoId.value = res.data.id
    paso.value = 'esperando'
    emit('acompañamiento-solicitado', res.data.id)
  } catch (err){
    console.error('Error:', err)
    console.error('Response data:', err.response?.data)
    errorUbicacion.value = 'Error al solicitar. Inténtalo de nuevo.'
  } finally {
    cargando.value = false
  }
}

async function cancelar() {
  if (acompañamientoId.value) {
    await api.post(`api/v1/acompañamientos/${acompañamientoId.value}/cancelar/`).catch(() => {})
  }
  resetear()
  emit('close')
}

async function responder(acepta) {
  await api.post(`api/v1/acompañamientos/${acompañamientoId.value}/responder/`, { acepta })
  if (acepta) paso.value = 'asignado'
  else {
    acompañantePropuesta.value = ''
    paso.value = 'esperando'
  }
}

function cerrar() {
  emit('close')
}

function resetear() {
  paso.value = 'formulario'
  origenLat.value = null; origenLng.value = null
  destinoLat.value = null; destinoLng.value = null
  errorUbicacion.value = ''
  acompañamientoId.value = null
  acompañantePropuesta.value = ''
  seleccionando.value = 'origen'
  horaMode.value = 'ahora'
  horaPersonalizada.value = ''
  horaFin.value = ''
  // Limpiar marcadores
  if (marcadorOrigen)  { mapaModal?.removeLayer(marcadorOrigen);  marcadorOrigen = null }
  if (marcadorDestino) { mapaModal?.removeLayer(marcadorDestino); marcadorDestino = null }
  if (lineaRuta) { mapaModal?.removeLayer(lineaRuta); lineaRuta = null}
}

// Expuesto para el padre
function notificarAcompañantePropuesta(nombre) {
  acompañantePropuesta.value = nombre
  paso.value = 'acompañante_propuesto'
}
function notificarAcompañamientoConfirmado() {
  paso.value = 'asignado'
}
defineExpose({ notificarAcompañantePropuesta, notificarAcompañamientoConfirmado })
</script>

<style scoped>

/* ---- Hora selector ---------------------------------------- */
.hora-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.hora-label {
  font-size: 0.8rem;
  color: var(--muted);
}
.hora-opciones {
  display: flex;
  gap: 8px;
}
.hora-opt {
  flex: 1;
  padding: 7px 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--muted);
  font-size: 0.82rem;
  cursor: pointer;
  transition: all .2s;
}
.hora-opt.activa {
  border-color: var(--accent-strong);
  color: var(--accent-strong);
  background: rgba(155, 113, 178, 0.08);
  font-weight: 600;
}
.hora-input {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--accent-strong);
  background: var(--card);
  color: var(--text);
  font-size: 0.88rem;
  width: 100%;
  box-sizing: border-box;
}

.mapa-modal {
  width: 100%;
  height: 280px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border);
  z-index: 0;
}

.mapa-instrucciones {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  margin-bottom: 4px;
}

.instruccion {
  padding: 4px 10px;
  border-radius: 20px;
  border: 1px solid var(--border);
  color: var(--muted);
  transition: all .2s;
}

.instruccion.activa {
  border-color: var(--accent-strong);
  color: var(--accent-strong);
  background: rgba(155, 113, 178, 0.08);
  font-weight: 600;
}

.instruccion-sep { color: var(--muted); }

.coordenadas-resumen {
  display: flex;
  gap: 10px;
}

.coord-item {
  flex: 1;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
  font-size: 0.78rem;
  transition: border-color .2s;
}

.coord-item.ok { border-color: var(--green); }

.coord-label {
  display: block;
  color: var(--muted);
  margin-bottom: 2px;
}

.coord-valor { color: var(--text); font-weight: 600; }

.modal-btns {
  display: flex;
  gap: 8px;
}

.modal-btns .btn-ghost {
  white-space: nowrap;
  flex-shrink: 0;
}

/* ----- Overlay ------------------------------------------ */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 5, 15, 0.55);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
}

/* ----- Modal -------------------------------------------- */
.modal {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 20px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 32px 80px rgba(0,0,0,0.4);
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 1.2rem 1.4rem;
  border-bottom: 1px solid var(--border);
  background: linear-gradient(135deg, rgba(155,113,178,0.08), transparent);
}

.modal-titulo {
  font-size: 1.1rem;
  color: var(--accent-strong);
  margin: 0;
}

.modal-sub {
  font-size: 0.78rem;
  color: var(--muted);
  margin: 0;
}

.btn-cerrar-modal {
  margin-left: auto;
  background: transparent;
  border: none;
  font-size: 1rem;
  color: var(--muted);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background .15s;
}
.btn-cerrar-modal:hover { background: var(--border); color: var(--text); }

.modal-body {
  padding: 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* ----- Estado ------------------------------------------- */
.modal-estado {
  align-items: center;
  text-align: center;
  padding: 2rem 1.4rem;
}

.estado-titulo {
  font-size: 1.05rem;
  color: var(--accent-strong);
  margin: 0;
}

.estado-sub {
  font-size: 0.82rem;
  color: var(--muted);
  line-height: 1.5;
  max-width: 280px;
  margin: 0;
}

/* ----- Acompañante card --------------------------------- */
.acompañante-card {
  background: rgba(155, 113, 178, 0.08);
  border: 1px solid rgba(155, 113, 178, 0.25);
  border-radius: 12px;
  padding: 12px 20px;
  width: 100%;
}

.acompañante-nombre {
  font-size: 1rem;
  font-weight: 700;
  color: var(--accent-strong);
}

.acompañante-sub {
  font-size: 0.78rem;
  color: var(--muted);
  margin: 2px 0 0;
}

/* ----- Botones respuesta -------------------------------- */
.btns-respuesta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.btn-aceptar-acompañamiento {
  background: rgba(95, 143, 123, 0.12);
  border: 1px solid var(--green);
  color: var(--green);
  border-radius: 8px;
  padding: 11px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background .2s;
}
.btn-aceptar-acompañamiento:hover { background: rgba(95,143,123,0.22); }

.btn-rechazar-acompañamiento {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--muted);
  border-radius: 8px;
  padding: 11px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all .2s;
}
.btn-rechazar-acompañamiento:hover { border-color: var(--danger); color: var(--danger); }

.btn-full { width: 100%; }

/* ----- Transición --------------------------------------- */
.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity .25s ease;
}
.modal-fade-enter-active .modal, .modal-fade-leave-active .modal {
  transition: transform .25s ease;
}
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-from .modal, .modal-fade-leave-to .modal {
  transform: translateY(16px) scale(0.97);
}
.mapa-modal { width: 100%; height: 280px; border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }
</style>