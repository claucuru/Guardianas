<template>
    <div class="acomp-panel card">
        <div class="acomp-panel-header">
            <h3>Acompañamientos</h3>
            <div class="acomp-tabs">
                <button :class="{ activa: tab === 'solicitados' }"   @click="tab = 'solicitados'">
                  Mis solicitudes
                  <span v-if="solicitados.length" class="tab-badge">{{ solicitados.length }}</span>
                </button>
                <button :class="{ activa: tab === 'disponibles' }" @click="tab = 'disponibles'">
                    Disponibles 
                    <span v-if="disponibles.length" class="tab-badge">{{ disponibles.length }}</span>
                </button>
                <button
                  v-if="comoAcompañante.length" :class="{activa: tab === 'acompañando' }" @click="tab = 'acompañando'">
                  Acompañando
                  <span class="tab-badge">{{ comoAcompañante.length }}</span>
                </button>
            </div>
        </div> 
      
        <div class="acomp-panel-body">
           <!-- Notificaciones de cancelación -->
           <div v-for="c in canceladosRecientes" :key="`cancel-${c.id}`" class="acomp-cancelacion-notif">
            <div class="cancelacion-contenido">
              <span v-if="c.cancelado_por === 'acompañante'" class="cancelacion-texto">
                Se ha cancelado el acompañamiento
              </span>
              <span v-else class="cancelacion-texto">
                Se ha cancelado el acompañamiento
              </span>
            </div>
            <div v-if="c.cancelado_por === 'acompañante' && c.es_mio" class="cancelacion-btns">
              <button class="btn-reenviar" @click="reenviarSolicitud(c.id)">
                Reenviar solicitud
              </button>
              <button class="btn-cerrar-notif" @click="cerrarNotificacion(c.id)">
                Cancelar
              </button>
            </div>
            <button v-else class="btn-cerrar-notif" @click="cerrarNotificacion(c.id)">
              Cerrar
            </button>
          </div> 
          <!-- Mis solicitudes -->
          <div v-if="tab === 'solicitados'">
              <div v-if="solicitados.length === 0" class="acomp-vacio">
                  No tienes solicitudes activas
              </div>
              <div v-for="a in solicitados" :key="a.id" class="acomp-item">
                  <div class="acomp-item-top">
                      <span :class="`estado-badge estado-${estadoClass(a.estado)}`">{{ estadoLabel(a.estado) }}</span>
                      <span class="acomp-fecha">{{ a.fecha }}</span>
                  </div>
                  <MapaAcompañamientos
                    v-if="a.origen_lat && a.destino_lat"
                    :origen-lat="a.origen_lat"
                    :origen-lng="a.origen_lng"
                    :destino-lat="a.destino_lat"
                    :destino-lng="a.destino_lng"
                    :exacto="a.coordenadas_exactas"
                  />
                  <div v-if="a.hora_solicitada" class="acomp-hora">
                    {{ a.hora_solicitada }}
                  </div>
                  <div v-if="a.acompañante && a.estado === 'ACEPTADO'" class="acomp-propuesta">
                    <div class="acomp-persona">
                      <span class="acomp-persona-label">Acompañante propuesta</span>
                      <span class="acomp-persona-nombre">{{ a.acompañante_nombre || a.acompañante }}</span>
                    </div>
                    <div class="acomp-propuesta-btns">
                      <button class="btn-ver-perfil" @click="() => { console.log('a:', a); emit('ver-perfil', a.acompañante)}">
                        Ver perfil
                      </button>
                      <button class="btn-aceptar-acomp" @click="$emit('responder', { id: a.id, acepta: true})">
                        ✓ Aceptar
                      </button>
                      <button class="btn-rechazar-acomp" @click="$emit('responder', { id: a.id, acepta: false})">
                        ✗ Rechazar
                      </button>
                    </div>
                  </div>
                  <div v-if="a.acompañante && a.estado === 'ASIGNADO'" class="acomp-persona">
                      <span class="acomp-persona-label">Acompañante</span>
                      <span class="acomp-persona-nombre">{{ a.acompañante_nombre || a.acompañante }}</span>
                      <button class="btn-ver-perfil" @click="emit('ver-perfil', a.acompañante)">
                        Ver perfil
                      </button>
                  </div>
                  <div v-else-if="a.estado === 'SOLICITADO'" class="acomp-buscando">
                      Buscando acompañante...
                  </div>
                  <!-- Botón cancelar (solicitante) -->
                  <button v-if="['SOLICITADO', 'ACEPTADO', 'ASIGNADO'].includes(a.estado)" class="btn-cancelar-acomp" @click="cancelarAcompañamiento(a.id)">
                    Cancelar acompañamiento
                  </button>
              </div>
            </div>
            <!-- Disponibles -->
            <div v-if="tab === 'disponibles'">
                <div v-if="disponibles.length === 0" class="acomp-vacio">
                    No hay solicitudes cercanas disponibles
                </div>
                <div v-for="a in disponibles" :key="a.id" class="acomp-item">
                    <div class="acomp-item-top">
                        <span class="acomp-solicitante">{{ a.solicitante_nombre || a.solicitante }}</span>
                        <span class="acomp-fecha">{{ a.fecha }}</span>
                    </div>
                    <MapaAcompañamientos
                      v-if="a.origen_lat && a.destino_lat"
                      :origen-lat="a.origen_lat"
                      :origen-lng="a.origen_lng"
                      :destino-lat="a.destino_lat"
                      :destino-lng="a.destino_lng"
                      :exacto="false"
                    />
                    <div v-if="a.hora_solicitada" class="acomp-hora">
                      {{ a.hora_solicitada }}
                    </div>
                    <button class="btn-aceptar-acomp" @click="$emit('aceptar', a.id)">
                        Aceptar acompañamiento
                    </button>
                </div>
            </div>
            <!-- Acompañando -->
            <div v-if="tab === 'acompañando'">
              <div v-if="comoAcompañante.length === 0" class="acomp-vacio">
                No tienes acompañamientos activos
              </div>
              <div v-for="a in comoAcompañante" :key="a.id" class="acomp-item">
                <div class="acomp-item-top">
                  <span :class="`estado-badge estado-${estadoClass(a.estado)}`">
                    {{ estadoLabel(a.estado) }}
                  </span>
                  <span class="acomp-fecha">{{ a.fecha }}</span>
                </div>
                <div class="acomp-persona">
                  <span class="acomp-persona-label">Solicitante</span>
                  <span class="acomp-persona-nombre">{{ a.solicitante_nombre || a.Solicitante }}</span>
                  <button class="btn-ver-perfil" @click="emit('ver-perfil', a.solicitante)">
                    Ver perfil
                  </button>
                </div>
                <MapaAcompañamientos
                      v-if="a.origen_lat && a.destino_lat"
                      :origen-lat="a.origen_lat"
                      :origen-lng="a.origen_lng"
                      :destino-lat="a.destino_lat"
                      :destino-lng="a.destino_lng"
                      :exacto="a.coordenadas_exactas"
                />
                <div v-if="a.hora_solicitada" class="acomp-hora">
                  {{ a.hora_solicitada }}
                </div>
                <!-- Boton de cancelar del acompañante -->
                <button v-if="['ACEPTADO', 'ASIGNADO'].includes(a.estado)" class="btn-cancelar-acomp" @click="cancelarAcompañamiento(a.id)">
                  Cancelar acompañamiento
                </button>
              </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import api from '@/services/api'
import MapaAcompañamientos from './MapaAcompañamientos.vue'

const emit = defineEmits(['aceptar', 'responder', 'ver-perfil'])

const tab = ref('solicitados')
const solicitados = ref([])
const disponibles = ref([])
const comoAcompañante = ref([])
const canceladosRecientes = ref([])
//ID de notificaciones de cancelacion descartadas localmente
const notificacionesCerradas = ref(new Set(
  JSON.parse(localStorage.getItem('cancelaciones_cerradas') || '[]')
))

let intervalo = null

function estadoLabel(estado) {
    if (!estado) return '-'
  const labels = {
    SOLICITADO: 'Buscando',
    ACEPTADO:   'Propuesta',
    ASIGNADO:   'Confirmado',
    EN_CURSO:   'En curso',
    FINALIZADO: 'Finalizado',
  }
  return labels[estado] || estado
}

function estadoClass(estado) {
  if (!estado || typeof estado !== 'string') return ''
  return estado.toLowerCase()
}

async function cargar() {
  const res = await api.get('api/v1/acompañamientos/mis/')
  solicitados.value = res.data.solicitados
  disponibles.value = res.data.disponibles
  comoAcompañante.value = res.data.como_acompañante || []

  // Filtramos las que el usuario ya cerró en esta sesión
  canceladosRecientes.value = (res.data.cancelados_recientes || []).filter(c => !notificacionesCerradas.value.has(c.id))
}

function cerrarNotificacion(id) {
  notificacionesCerradas.value.add(id)
  localStorage.setItem('cancelaciones_cerradas', JSON.stringify([...notificacionesCerradas.value]))
  canceladosRecientes.value = canceladosRecientes.value.filter(c => c.id !== id)
}

async function reenviarSolicitud(acompañamientoId) {
  try {
    await api.post(`api/v1/acompañamientos/${acompañamientoId}/reenviar/`)
    cerrarNotificacion(acompañamientoId)
    await cargar()
  } catch {
    console.error('Error al reenviar solicitud')
  }
}

async function cancelarAcompañamiento(id) {
  try {
    await api.post(`api/v1/acompañamientos/${id}/cancelar/`)
    await cargar()
  } catch {
    console.error('Error al cancelar')
  }
}


onMounted(() => {
  cargar()
  intervalo = setInterval(cargar, 30_000)
})

onUnmounted(() => {
  clearInterval(intervalo)
})

function irATab(nombre) {
  tab.value = nombre
}
defineExpose({ cargar, irATab })
</script>

<style scoped>

.acomp-cancelacion-notif {
    background: rgba(220, 80, 60, 0.08);
    border: 1px solid rgba(220, 80, 60, 0.3);
    border-radius: 10px;
    padding: 10px 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 4px;
}

.cancelacion-texto {
    font-size: 0.75rem;
    color: var(--danger);
    font-weight: 500;
}

.cancelacion-btns {
    display: flex;
    gap: 6px;
}

.btn-reenviar {
    flex: 1;
    background: rgba(95, 143, 123, 0.12);
    border: 1px solid var(--green);
    color: var(--green);
    border-radius: 8px;
    padding: 7px;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    transition: background .2s;
}
.btn-reenviar:hover { background: rgba(95, 143, 123, 0.22); }

btn-cerrar-notif {
    flex: 1;
    background: transparent;
    border: 1px solid var(--border);
    color: var(--muted);
    border-radius: 8px;
    padding: 7px;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all .2s;
}
.btn-cerrar-notif:hover { border-color: var(--danger); color: var(--danger); }

/* === Botón cancelar === */
.btn-cancelar-acomp {
    margin-top: 4px;
    background: transparent;
    border: 1px solid var(--border);
    color: var(--muted);
    border-radius: 8px;
    padding: 7px;
    font-size: 0.78rem;
    cursor: pointer;
    transition: all .2s;
    width: 100%;
}
.btn-cancelar-acomp:hover { border-color: var(--danger); color: var(--danger); }


.acomp-hora {
    font-size: 0.78rem;
    color: var(--muted);
}


.acomp-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 300px;
}

.acomp-panel-header {
  padding: 1rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.acomp-panel-header h3 {
  margin: 0;
  font-size: 0.95rem;
  color: var(--accent-strong);
}

.acomp-tabs {
  display: flex;
  gap: 6px;
}

.acomp-tabs button {
  flex: 1;
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--muted);
  font-size: 0.78rem;
  cursor: pointer;
  transition: all .2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.acomp-tabs button.activa {
  border-color: var(--accent-strong);
  color: var(--accent-strong);
  background: rgba(155, 113, 178, 0.08);
  font-weight: 600;
}

.tab-badge {
  background: var(--accent-strong);
  color: white;
  border-radius: 10px;
  padding: 1px 6px;
  font-size: 0.7rem;
}

.acomp-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.acomp-vacio {
  text-align: center;
  color: var(--muted);
  font-size: 0.85rem;
  padding: 2rem;
}

.acomp-item {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.acomp-item-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.acomp-fecha {
  font-size: 0.72rem;
  color: var(--muted);
}

.acomp-coords {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.78rem;
  color: var(--muted);
}

.acomp-persona {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
}

.acomp-persona-label {
  color: var(--muted);
}

.acomp-persona-nombre {
  font-weight: 600;
  color: var(--accent-strong);
}

.acomp-buscando {
  font-size: 0.78rem;
  color: var(--muted);
  font-style: italic;
}

.acomp-solicitante {
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--text);
}

.estado-badge {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
}

.acomp-propuesta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.acomp-propuesta-btns {
  display: flex;
  gap: 6px;
}

.btn-ver-perfil {
  flex: 1;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--muted);
  border-radius: 8px;
  padding: 7px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all .2s;
}
.btn-ver-perfil:hover { border-color: var(--accent-strong); color: var(--accent-strong); }

.btn-rechazar-acomp {
  flex: 1;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--muted);
  border-radius: 8px;
  padding: 7px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all .2s;
}
.btn-rechazar-acomp:hover { border-color: var(--danger); color: var(--danger); }

.btn-aceptar-acomp {
  flex: 1;
}

.estado-solicitado { background: rgba(252, 185, 42, 0.15); color: #b8860b; }
.estado-aceptado   { background: rgba(155, 113, 178, 0.15); color: var(--accent-strong); }
.estado-asignado   { background: rgba(95, 143, 123, 0.15); color: var(--green); }
.estado-en_curso   { background: rgba(95, 143, 123, 0.2); color: var(--green); }
.estado-finalizado { background: var(--border); color: var(--muted); }

.btn-aceptar-acomp {
  margin-top: 4px;
  background: rgba(95, 143, 123, 0.12);
  border: 1px solid var(--green);
  color: var(--green);
  border-radius: 8px;
  padding: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background .2s;
}
.btn-aceptar-acomp:hover { background: rgba(95,143,123,0.22); }
</style>




