<template>
  <div class="table-section">
    <h2>Incidencias</h2>
    <table>
      <thead>
        <tr>
          <th>ID</th><th>Descripción</th><th>Gravedad</th><th>Zona</th><th>Fecha</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="i in incidencias" :key="i.id">
          <td>{{ i.id }}</td>
          <td>{{ i.descripcion }}</td>
          <td>
            <span :class="['gravedad-badge', `g${i.gravedad}`]">{{ i.gravedad }}</span>
          </td>
          <td>{{ i.zona }}</td>
          <td>{{ i.fecha }}</td>
        </tr>
      </tbody>
    </table>
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
</script>
