<template>
  <div class="incidencia-form card">
    <h3>Nueva Incidencia</h3>
    <div class="field">
      <label>Zona</label>
      <select
        :value="zonaSeleccionada"
        @change="$emit('update:zonaSeleccionada', +$event.target.value)"
      >
        <option v-for="zona in zonas" :key="zona.id" :value="zona.id">
          {{ zona.nombre }}
        </option>
      </select>
    </div>
    <div class="field">
      <label>Gravedad</label>
      <div class="gravedad-selector">
        <button
          v-for="n in 5" :key="n"
          :class="['grav-btn', { selected: gravedadSeleccionada === n }]"
          @click="$emit('update:gravedadSeleccionada', n)"
        >
          {{ n }}
        </button>
      </div>
    </div>
    <div class="field">
      <label>Descripción</label>
      <input
        :value="descripcion"
        placeholder="Describe la incidencia…"
        @input="$emit('update:descripcion', $event.target.value)"
      />
    </div>
    <button class="btn-primary" @click="$emit('crear')">Crear Incidencia</button>
  </div>
</template>

<script setup>
defineProps({
  zonas: Array,
  zonaSeleccionada: Number,
  gravedadSeleccionada: Number,
  descripcion: String,
})

defineEmits(['update:zonaSeleccionada', 'update:gravedadSeleccionada', 'update:descripcion', 'crear'])
</script>