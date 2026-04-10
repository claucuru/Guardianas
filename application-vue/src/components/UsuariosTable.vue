<template>
  <div class="table-section">
    <h2>Acompañamientos recibidos</h2>
    <table>
      <thead>
        <tr><th>Nombre del solicitante</th><th>Acciones</th></tr>
      </thead>
      <tbody>
        <tr v-for="a in acompañamientos" :key="u.id">
          <td>{{ a.solicitante_nombre }}</td>
          <td>
            <button @click="verDetallesAcompañamiento">Ver detalles</button>
            <button @click="aceptarAcompañamientoComoAcompañante">Aceptar</button>
            <button @click="rechazar">Rechazar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAcompañamiento } from '@/composables/useAcompañamiento'
import { useWebSocket }   from '@/composables/useWebSocket'
import api from '@/services/api'
import AcompañamientoModal from '@/components/AcompañamientoModal.vue'

defineProps({
  acompañamientos: Array,
})

const nuevoId = ref('')
const nuevoNombre = ref('')

</script>