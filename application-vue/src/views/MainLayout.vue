<template>
  <div class="app-layout">
    <TopBar
      :username="currentUsername"
      :num-solicitudes="solicitudesPendientes.length"
      @toggle-solicitudes="togglePanelSolicitudes"
      @logout="handleLogout"
      @pedir-acompañamiento="abrirModalAcompañamiento"
    />

    <transition name="slide-down">
      <SolicitudesPanel
        v-if="mostrarPanelSolicitudes && solicitudesPendientes.length"
        :solicitudes="solicitudesPendientes"
        @responder="handleResponderSolicitud"
      />
    </transition>

    <main class="main-content">
      <div class="tables-container">
        <AcompañamientosPanel
          ref="acompañamientosPanelRef"
          @aceptar="handleAceptarDesdePanel"
          @responder="handleResponderAcompañamiento"
          @ver-perfil="handleVerPerfil"
        />
        <IncidenciasTable
          :incidencias="incidenciasFiltradas"
          :zona-filtro="zonaFiltro"
          @limpiar-filtro="zonaFiltro = null"
        />
      </div>

      <div class="bottom-section">
        <IncidenciaForm
          :zonas="zonas"
          :zona-seleccionada="zonaSeleccionada"
          :gravedad-seleccionada="gravedadSeleccionada"
          :descripcion="descripcion"
          @update:zona-seleccionada="(val) => { console.log('zona recibida:', val); zonaSeleccionada = val }"
          @update:gravedad-seleccionada="gravedadSeleccionada = $event"
          @update:descripcion="descripcion = $event"
          @crear="handleCrearIncidencia"
        />
        <MapaZonas
          :zonas="zonas"
          :incidencias="incidencias"
          :zona-activa="zonaActiva"
          @mapa-listo="handleMapaListo"
          @zona-guardada="handleZonaGuardada"
          @cerrar-panel="zonaActiva = null"
        />
      </div>
    </main>

    <transition name="toast">
      <div v-if="nuevoAcompañamientoCercano" class="toast toast-info">
        <div style="display:flex; flex-direction:column;gap:2px">
           <span style ="font-weight:7000"> Nuevo acompañamiento disponible</span>
           <span style="font-size:0.8rem; opacity:0.8"> {{ nuevoAcompañamientoCercano.solicitante_nombre }}</span>
        </div>
           <button @click="verDetallesAcompañamiento">Ver detalles</button>
           <button @click="aceptarAcompañamientoComoAcompañante">Aceptar</button>
           <button style="background:transparent; border:none; color:var(--muted); cursor:pointer"
           @click="nuevoAcompañamientoCercano = null">✕</button>
      </div>
    </transition>
    <AcompañamientoModal
      :visible="mostrarModalAcompañamiento"
      :tipo="tipoAcompañamiento"
      ref="acompañamientoModalRef"
      @close="mostrarModalAcompañamiento = false"
      @acompañamiento-solicitado="handleAcompañamientoSolicitado"
    />
    <PerfilModal 
      :visible="perfilModalVisible"
      :nombre-usuario="perfilModalUsuario"
      @close="perfilModalVisible = false"
    />
    <Menu 
      @pedir-acompañamiento="() => { tipoAcompañamiento = 'FISICO'; abrirModalAcompañamiento() }"
      @pedir-acompañamiento-virtual="() => { tipoAcompañamiento = 'VIRTUAL'; abrirModalAcompañamiento() }"
    />
    <AlertaPanico
      v-if="alertaPanico"
      :datos="alertaPanico"
      @cerrar="alertaPanico = null"
    />
  </div>


</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'

import { useAuth } from '@/composables/useAuth'
import { useIncidencias } from '@/composables/useIncidencias'
import { useZonas } from '@/composables/useZonas'
import { useAcompañamiento } from '@/composables/useAcompañamiento'
import { useWebSocket } from '@/composables/useWebSocket'
import api from '@/services/api'

import TopBar from '@/components/TopBar.vue'
import SolicitudesPanel from '@/components/SolicitudesPanel.vue'
import UsuariosTable from '@/components/UsuariosTable.vue'
import IncidenciasTable from '@/components/IncidenciasTable.vue'
import IncidenciaForm from '@/components/IncidenciaForm.vue'
import MapaZonas from '@/components/MapaZonas.vue'
import AcompañamientoModal from '@/components/AcompañamientoModal.vue'
import AcompañamientosPanel from '@/components/AcompañamientosPanel.vue'
import PerfilModal from '@/components/PerfilModal.vue'
import Menu from '@/components/Menu.vue'
import AlertaPanico from '@/components/AlertaPanico.vue'

const router = useRouter()

// ----- AUTH ------------------------------------------------
const {
  currentUsername, solicitudesPendientes,
  logout, cargarSolicitudesPendientes, responderSolicitud,
} = useAuth()

const mostrarPanelSolicitudes = ref(false)

function togglePanelSolicitudes() {
  mostrarPanelSolicitudes.value = !mostrarPanelSolicitudes.value
  if (mostrarPanelSolicitudes.value) cargarSolicitudesPendientes()
}

async function handleLogout() {
  logout()
  router.push('/login')
}

async function handleResponderSolicitud({ id, acepta }) {
  const status = await responderSolicitud(id, acepta)
  if (status === 'usuario_creado') alert('Usuario creado. Ya puede iniciar sesión.')
  else if (status === 'rechazado') alert('Solicitud rechazada.')
  else alert('Respuesta guardada. Esperando al otro avalador.')
}

// ----- USUARIOS ------------------------------------------------
const usuarios = ref([])
const perfilModalVisible = ref(false)
const perfilModalUsuario = ref(null)

async function cargarUsuarios() {
  const res = await api.get('api/v1/usuarios/')
  usuarios.value = res.data
}

function handleVerPerfil(nombreUsuario) {
  perfilModalUsuario.value = nombreUsuario
  perfilModalVisible.value = true
}


// ----- INCIDENCIAS ------------------------------------------------
const {
  incidencias, zonaSeleccionada, gravedadSeleccionada, descripcion,
  cargarIncidencias, agregarIncidencia,
} = useIncidencias()

// ----- ZONAS & MAPA ------------------------------------------------
const mapRef     = ref(null)
const zonaActiva = ref(null)
const zonaFiltro = ref(null)

const { zonas, cargarZonas, guardarZona, nombreNuevaZona, nuevasCoordenadas } = useZonas(
  mapRef,
  (zona) => { zonaActiva.value = zona }
)

function handleMapaListo(mapInstance) {
  mapRef.value = mapInstance
  cargarZonas()
}

async function handleCrearIncidencia() {
  await agregarIncidencia(() => cargarZonas())
}

async function handleZonaGuardada({ nombre, coordenadas }) {
  nombreNuevaZona.value   = nombre
  nuevasCoordenadas.value = coordenadas
  await guardarZona()
}

const incidenciasFiltradas = computed(() =>
  zonaFiltro.value
    ? incidencias.value.filter(i => i.zona === zonaFiltro.value.id)
    : incidencias.value
)

// ----- ACOMPAÑAMIENTO ------------------------------------------------
const acompañamientoModalRef = ref(null)
const acompañamientosPanelRef = ref(null)
const tipoAcompañamiento = ref('FISICO')
const alertaPanico = ref(null)

const {
  mostrarModalAcompañamiento,
  nuevoAcompañamientoCercano,
  cargarPerfil,
  handleAcompañamientoSolicitado,
  aceptarAcompañamientoComoAcompañante,
  acompañamientosIgnorados,
  ignorarAcompañamiento,
  onNuevoAcompañamiento,
  onAcompañantePropuesto,
  onAcompañamientoConfirmado,
  onAcompañamientoFinalizado,
  abrirModalAcompañamiento,
} = useAcompañamiento(acompañamientoModalRef, acompañamientosPanelRef)

async function handleAceptarDesdePanel(acompañamientoId) {
    try {
    await api.post(`api/v1/acompañamientos/${acompañamientoId}/aceptar/`)
    acompañamientosPanelRef.value?.cargar()
  } catch (err) {
    console.error('Error aceptar:', err.response?.data)  // <-- esto
  }
}

async function handleResponderAcompañamiento({id, acepta}) {
  await api.post(`api/v1/acompañamientos/${id}/responder/`, { acepta })
  acompañamientosPanelRef.value?.cargar()
}

// ----- WEBSOCKET ------------------------------------------------
const { connect, disconnect } = useWebSocket({
  onSolicitudRegistro: () => {
    cargarSolicitudesPendientes()
    mostrarPanelSolicitudes.value = true
  },
  onNuevoAcompañamiento: (data) => {
    if (acompañamientosIgnorados.has(data.acompañamiento_id)) return
    onNuevoAcompañamiento(data)
    acompañamientosPanelRef.value?.cargar()
  },
  onAcompañantePropuesto: (data) => {
    onAcompañantePropuesto(data)  
    acompañamientosPanelRef.value?.cargar()
  },
  onAcompañamientoConfirmado: (data) => {
    onAcompañamientoConfirmado(data)
    acompañamientosPanelRef.value?.cargar()
  },
  onAcompañamientoFinalizado: (data) => {
    acompañamientosPanelRef.value?.cargar()
  },
  onAlertaPanico: (data) => {
    alertaPanico.value = data
    acompañamientosPanelRef.value?.cargar()
  },
  onAcompañamientoFinalizadoAcompañante: (data) => {
  acompañamientosPanelRef.value?.cargar()
},
  
})

// ------ CICLO DE VIDA -----------------------------------------
onMounted(async () => {
  await Promise.all([
    cargarUsuarios(),
    cargarIncidencias(),
    cargarSolicitudesPendientes(),
    cargarPerfil(),
    // cargarZonas(),
  ])
  connect()
})

onUnmounted(() => disconnect())
</script>