<template>
    <div class="fab-wrapper">
        <Transition name="fab-items">
            <div v-if="open" class="fab-menu">
                    <button class="fab-label" @click="$emit('pedir-acompañamiento'); open = false">Acompañamiento físico</button>
                    <button class="fab-label" @click="$emit('pedir-acompañamiento-virtual'); open = false">Acompañamiento virtual</button>
            </div>
        </Transition>
        <button class="fab-main" @click="open = !open">
            <span v-if="!open">👥</span>
            <span v-else>✕</span>
        </button>
    </div>
</template>

<script setup>
import { ref } from 'vue'

defineEmits(['pedir-acompañamiento', 'pedir-acompañamiento-virtual'])
const open = ref(false)
</script>

<style scoped>
.fab-wrapper {
  position: fixed;
  bottom: 24px;
  right: 20px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
  z-index: 400;
}

.fab-main {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-strong), var(--accent));
  border: none;
  font-size: 22px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}
.fab-main:active { transform: scale(0.93); }

.fab-menu {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.fab-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.fab-label {
  background: linear-gradient(135deg, var(--accent-strong), var(--accent));
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 14px;
  font-weight: 500;
  color: white;
  border: none;
  white-space: nowrap;
  transition: opacity 0.2s;
  cursor: pointer;
}

.fab-label:active { opacity: 0.85; }


.fab-items-enter-active,
.fab-items-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.fab-items-enter-from,
.fab-items-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>