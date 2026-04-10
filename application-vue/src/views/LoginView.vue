<template>
  <div class="auth-screen">
    <div class="auth-card">
      <div class="auth-logo">
        <span class="logo-icon">🛡</span>
        <h1>Guardianas</h1>
      </div>

      <div class="auth-tabs">
        <button :class="['tab', { active: authTab === 'login' }]" @click="authTab = 'login'">
          Iniciar sesión
        </button>
        <button :class="['tab', { active: authTab === 'registro' }]" @click="authTab = 'registro'">
          Registrarse
        </button>
      </div>

      <transition name="fade" mode="out-in">
        <LoginForm
          v-if="authTab === 'login'"
          key="login"
          :error="loginError"
          :cargando="loginCargando"
          @submit="handleLogin"
        />
        <RegisterForm
          v-else
          key="registro"
          :error="registroError"
          :ok="registroOk"
          :cargando="registroCargando"
          @submit="handleRegistro"
        />
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import LoginForm from '@/components/LoginForm.vue'
import RegisterForm from '@/components/RegisterForm.vue'

const router = useRouter()
const authTab = ref('login')

const {
  loginError, loginCargando,
  registroError, registroOk, registroCargando,
  login, enviarRegistro,
} = useAuth()

async function handleLogin({ username, password }) {
  await login(username, password)
  // useAuth pone isAuthenticated a true si va bien,
  // el router guard en App.vue o router/index.js redirige a '/'
  router.push('/')
}

async function handleRegistro(datosRegistro) {
  const resultado = await enviarRegistro(datosRegistro)
  if (resultado === 'ok') {
    setTimeout(() => { authTab.value = 'login' }, 2000)
  }
  // si es 'pendiente' se muestra el mensaje y se queda en la pantalla
}
</script>