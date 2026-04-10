<template>
  <header class="top-bar">
    <div class="top-bar-left">
      <span class="logo-icon">🛡</span>
      <span class="app-title">Guardianas</span>
    </div>
    <div class="top-bar-right">
       <!--- Disponible ---->
       <button
         class="toggle-disponible"
         :class="{ activo: disponible }"
         @click="$emit('toggle-disponible')"
         :title="disponible ? 'Estás disponible como acompañante' : 'No estás disponible'">
         <span class="toggle-dot"></span>
         <span class="toggle-label">{{ disponible ? 'Disponible' : 'No disponible' }}  </span>
      </button>
      
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
  disponible: { type: Boolean, default: false},
})

defineEmits(['toggle-solicitudes', 'logout', 'pedir-acompañamiento', 'toggle-disponible'])
</script>

<style scoped>
/* ----- Toggle disponible -------------------------- */
.toggle-disponible {
  display: flex;
  align-items: center;
  gap: 7px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 5px 12px 5px 8px;
  cursor: pointer;
  font-size: 0.8rem;
  color: var(--muted);
  transition: all .2s;
}
 
.toggle-disponible.activo {
  border-color: var(--green);
  color: var(--green);
  background: rgba(95, 143, 123, 0.08);
}
 
.toggle-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--muted);
  transition: background .2s;
  flex-shrink: 0;
}
 
.toggle-disponible.activo .toggle-dot {
  background: var(--green);
  box-shadow: 0 0 0 3px rgba(95, 143, 123, 0.2);
}
 
.toggle-label { font-weight: 600; white-space: nowrap; }
 
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
</style>