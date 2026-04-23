<template>
    <transition name="modal-fade">
        <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
            <div class="modal">
                <div class="modal-header">
                    <div class="avatar">{{ iniciales }}</div>
                    <div class="header-info">
                        <h2 class="modal-titulo">{{ perfil?.nombre_completo || perfil?.nombreUsuario }}</h2>
                        <span class="modal-sub">@{{ perfil?.nombreUsuario }}</span>
                    </div>
                        <button class="btn-cerrar-modal" @click="$emit('close')">✕</button>
                </div>
                <div class="modal-body" v-if="perfil">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <span class="stat-valor">{{ perfil.num_acompañamientos }}</span>
                            <span class="stat-label">Acompañamientos</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-valor">{{ perfil.puntuacion_media ?? '-' }}</span>
                            <span class="stat-label">Puntuacion media</span>
                        </div>
                    </div>
                    <div class="estrellas-row">
                        <span v-for="n in 5" :key="n" class="estrella" :class="{ activa: n <= Math.round(perfil.puntuacion_media || 0)}">★</span>
                        <span class="estrellas-texto"> {{ perfil.puntuacion_media ? `${perfil.puntuacion_media} / 5` : 'Aún no hay valoraciones' }} </span>
                    </div>
                </div>
                <div v-else class="modal-body cargando">
                    <div class="spinner-wrap">
                        <span class="spinner"></span>
                        <span style="color:var(--muted); font-size:0.85rem">Cargando perfil...</span>
                    </div>     
                </div>
            </div>
        </div>
    </transition>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import api from '@/services/api'

const props = defineProps({
  visible: { type: Boolean, default: false },
  nombreUsuario: { type: String, default: null }
})
defineEmits(['close'])

const perfil = ref(null)

const iniciales = computed(() => {
  if (!perfil.value) return '?'
  const nombre = perfil.value.nombre_completo || perfil.value.nombreUsuario || ''
  return nombre.split(' ').map(p => p[0]).slice(0, 2).join('').toUpperCase()
})

watch(() => props.visible, async (v) => {
  if (!v || !props.nombreUsuario) return
  perfil.value = null
  const res = await api.get(`api/v1/perfil/${props.nombreUsuario}/`)
  perfil.value = res.data
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 5, 15, 0.55);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  padding: 1rem;
}

.modal {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 20px;
  width: 100%;
  max-width: 360px;
  box-shadow: 0 32px 80px rgba(0,0,0,0.4);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 1.2rem 1.4rem;
  border-bottom: 1px solid var(--border);
  background: linear-gradient(135deg, rgba(155,113,178,0.08), transparent);
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(155, 113, 178, 0.15);
  border: 1px solid rgba(155, 113, 178, 0.3);
  color: var(--accent-strong);
  font-weight: 700;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.modal-titulo {
  font-size: 1rem;
  color: var(--accent-strong);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.modal-sub {
  font-size: 0.75rem;
  color: var(--muted);
}

.btn-cerrar-modal {
  background: transparent;
  border: none;
  font-size: 1rem;
  color: var(--muted);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background .15s;
  flex-shrink: 0;
}
.btn-cerrar-modal:hover { background: var(--border); color: var(--text); }

.modal-body {
  padding: 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.stat-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-valor {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent-strong);
}

.stat-label {
  font-size: 0.72rem;
  color: var(--muted);
  text-align: center;
}

.estrellas-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.estrella {
  font-size: 1.3rem;
  color: var(--border);
  transition: color .15s;
}
.estrella.activa { color: #f5b800; }

.estrellas-texto {
  font-size: 0.8rem;
  color: var(--muted);
  margin-left: 6px;
}

.cargando {
  align-items: center;
  justify-content: center;
  min-height: 120px;
}

.spinner-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity .25s ease;
}
.modal-fade-enter-active .modal, .modal-fade-leave-active .modal {
  transition: transform .25s ease;
}
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-from .modal, .modal-fade-leave-to .modal {
  transform: translateY(16px) scale(0.97);
}
</style>