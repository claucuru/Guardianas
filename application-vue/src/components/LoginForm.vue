<template>
  <div class="auth-form">
    <div class="field">
      <label>Usuario</label>
      <input v-model="username" placeholder="tu_usuario" @keyup.enter="submit" />
    </div>
    <div class="field">
      <label>Contraseña</label>
      <input type="password" v-model="password" placeholder="••••••••" @keyup.enter="submit" />
    </div>
    <button class="btn-primary" @click="submit" :disabled="cargando">
      <span v-if="cargando" class="spinner"></span>
      <span v-else>Entrar</span>
    </button>
    <p v-if="error" class="error-msg">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  error: String,
  cargando: Boolean,
})

const emit = defineEmits(['submit'])
const username = ref('')
const password = ref('')

function submit() {
  emit('submit', { username: username.value, password: password.value })
}
</script>