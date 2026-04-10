<template>
  <div class="solicitudes-panel">
    <h3>Solicitudes de aval pendientes</h3>
    <div v-for="s in solicitudes" :key="s.id" class="solicitud-card">
      <div class="solicitud-info">
        <span class="solicitud-nombre">{{ s.usuario_solicitante }}</span>
        <span class="solicitud-meta">Nacido/a el {{ s.fecha_nacimiento }}</span>
        <span class="solicitud-caduca">Caduca: {{ formatFecha(s.caduca_en) }}</span>
      </div>
      <div class="solicitud-acciones">
        <button class="btn-aceptar" @click="$emit('responder', { id: s.id, acepta: true })">✓ Aceptar</button>
<button class="btn-rechazar" @click="$emit('responder', { id: s.id, acepta: false })">✕ Rechazar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  solicitudes: Array,
})

defineEmits(['responder'])

function formatFecha(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' })
}
</script>