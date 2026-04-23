<template>
  <header class="top-bar">
    <div class="top-bar-left">
      <span class="logo-icon">🛡</span>
      <span class="app-title">Guardianas</span>
    </div>
    <div class="top-bar-right">
      <button class="btn-acompañamiento"  @click="$emit('pedir-acompañamiento')">
         Pedir acompañamiento
      </button>

      <span class="username-badge">{{ username }}</span>

      <button class="bell-btn" @click="$emit('toggle-solicitudes')">
        🔔
        <span v-if="numSolicitudes" class="badge">{{ numSolicitudes }}</span>
      </button>

      <button class="btn-logout" @click="$emit('logout')">Cerrar sesión</button>
    </div>
  </header>
</template>

<script setup>
defineProps({
  username: { type: String, default: ''},
  numSolicitudes: { type: Number , default: 0},
})

defineEmits(['toggle-solicitudes', 'logout', 'pedir-acompañamiento'])
</script>

<style scoped>
 
/* ----- Botón pedir acompañamiento ------------------------------------- */
.btn-acompañamiento {
  background: linear-gradient(135deg, var(--accent-strong), var(--accent));
  color: white;
  border: none;
  border-radius: 20px;
  padding: 7px 16px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity .2s, transform .1s;
  white-space: nowrap;
}

.btn-acompañamiento:hover { opacity: 0.88; transform: translateY(-1px); }
@media (max-width: 600px) {
  .top-bar-right {
    gap: 6px;
  }

  .btn-acompañamiento {
    font-size: 0.75rem;
    padding: 5px 10px;
  }

  .username-badge {
    display: none; /* ocupa espacio pero aporta poco en móvil */
  }

  .btn-logout {
    font-size: 0.75rem;
    padding: 5px 10px;
  }
}

@media (max-width: 400px) {
  .btn-acompañamiento span {
    display: none;
  }

  .btn-logout {
    display: none; /* si sigue sin caber, ocúltalo también */
  }
}

</style>