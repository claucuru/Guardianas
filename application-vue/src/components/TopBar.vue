<template>
  <header class="top-bar">
    <div class="top-bar-left">
      <svg class="logo-icon" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2L3 6v6c0 5.25 3.75 10.15 9 11.35C17.25 22.15 21 17.25 21 12V6l-9-4z"/>
      </svg>
      <span class="app-title">Guardianas</span>
    </div>
    <div class="top-bar-right">
      <button class="bell-btn" @click="$emit('toggle-solicitudes')">
        🔔
        <span v-if="numSolicitudes" class="badge">{{ numSolicitudes }}</span>
      </button>
      <span class="username-badge">{{ username }}</span>
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
    display: none;
  }
}

</style>