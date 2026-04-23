<template>
  <div class="table-section card">
    <h2>Incidencias</h2>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Gravedad</th><th>Descripción</th><th>Zona</th><th>Fecha</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="i in incidencias" :key="i.id">
            <td>
              <span :class="['gravedad-badge', `g${i.gravedad}`]">{{ i.gravedad }}</span>
            </td>
            <td>{{ i.descripcion }}</td>
            <td>{{ i.zona_nombre }}</td>
            <td>{{ formatFecha(i.fecha) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  incidencias: Array,
  zonaFiltro: {
    type: Object, default: null
  },
})
const emit = defineEmits(['limpiar-filtro'])

function formatFecha(fecha) {
  if (!fecha) return '—'
  return new Date(fecha).toLocaleDateString('es-ES', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

</script>

<style scoped>
<style scoped>
.table-wrapper {
  overflow: hidden;
  border-radius: 8px;
}

td:last-child, th:last-child {
  white-space: nowrap;
}
</style>

