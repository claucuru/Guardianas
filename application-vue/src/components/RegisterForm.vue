<template>
  <div class="auth-form">
    <div class="field-row">
      <div class="field">
        <label>Nombre completo</label>
        <input v-model="form.nombre_completo" placeholder="Ana García" />
      </div>
      <div class="field">
        <label>Usuario</label>
        <input v-model="form.usuario" placeholder="ana_garcia" />
      </div>
    </div>
    <div class="field">
      <label>Email</label>
      <input type="email" v-model="form.email" placeholder="ana@email.com" />
    </div>
    <div class="field-row">
      <div class="field">
        <label>Contraseña</label>
        <input type="password" v-model="form.contraseña" placeholder="••••••••" />
      </div>
      <div class="field">
        <label>Fecha de nacimiento</label>
        <input type="date" v-model="form.fecha_nacimiento" />
      </div>
    </div>
    <div class="field">
      <label>Género</label>
      <select v-model="form.genero">
        <option value="M">Hombre</option>
        <option value="F">Mujer</option>
      </select>
    </div>

    <transition name="slide">
      <div v-if="esHombre" class="avales-block">
        <div class="avales-header">
          <p>Eres de género masculino. Necesitas dos usuarias registradas que avalen tu cuenta.</p>
        </div>
        <div class="field">
          <label>Usuaria avaladora 1</label>
          <input v-model="form.mujer1" placeholder="Nombre usuaria 1" />
        </div>
        <div class="field">
          <label>Usuaria avaladora 2</label>
          <input v-model="form.mujer2" placeholder="Nombre usuaria 2" />
        </div>
      </div>
    </transition>

    <button class="btn-primary" @click="submit" :disabled="cargando">
      <span v-if="cargando" class="spinner"></span>
      <span v-else>Crear cuenta</span>
    </button>
    <p v-if="error" class="error-msg">{{ error }}</p>
    <p v-if="ok" class="ok-msg">{{ ok }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

defineProps({
  error: String,
  ok: String,
  cargando: Boolean,
})

const emit = defineEmits(['submit'])

const form = ref({
  nombre_completo: '',
  usuario: '',
  email: '',
  contraseña: '',
  fecha_nacimiento: '',
  genero: 'M',
  mujer1: '',
  mujer2: '',
})

const esHombre = computed(() => form.value.genero === 'M')

function submit() {
  emit('submit', { ...form.value })
}
</script>