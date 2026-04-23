import { ref } from 'vue'
import api from '@/services/api'

export function useAcompañamiento(acompañamientoModalRef, acompañamientosPanelRef) {
    const mostrarModalAcompañamiento = ref(false)
    const nuevoAcompañamientoCercano = ref(null)

    async function cargarUbicacion() {
        try {
            const pos = await new Promise((res, rej) => 
            navigator.geolocation.getCurrentPosition(res, rej, { timeout: 6000})
            )
            await api.post('api/v1/ubicacion/actualizar/', {
            lat: pos.coords.latitude,
            lng: pos.coords.longitude,
            })
        } catch {
            console.warn('No se pudo obtener ubicacion')
        }
    }
    async function cargarPerfil() {
        const res = await api.get('api/v1/perfil/')
        await cargarUbicacion()
    }

    async function handleAcompañamientoSolicitado(acompañamientoId) {
        console.log('Acompañamiento solicitado:', acompañamientoId)
        await acompañamientosPanelRef.value?.cargar()
        acompañamientosPanelRef.value?.irATab('solicitados')
    }

    async function aceptarAcompañamientoComoAcompañante() {
        if(!nuevoAcompañamientoCercano.value) return
        await api.post(`api/v1/acompañamientos/${nuevoAcompañamientoCercano.value.acompañamiento_id}/aceptar/`)
        nuevoAcompañamientoCercano.value = null
    }

    // ----- Funciones para manejar el WebSocket -------
    const acompañamientosIgnorados = new Set(
        JSON.parse(localStorage.getItem('acomp_ignorados') || '[]')
    )

    function ignorarAcompañamiento(id) {
        acompañamientosIgnorados.add(id)
        localStorage.setItem('acomp_ignorados', JSON.stringify([...acompañamientosIgnorados]))
    }
    function onNuevoAcompañamiento(data) {
        nuevoAcompañamientoCercano.value = data
        // // Refrescar panel
        // acompañamientosPanelRef.value?.cargar()
    }

    function onAcompañantePropuesto(data) {
        acompañamientoModalRef.value?.notificarAcompañantePropuesta(data.acompañante_nombre || data.acompañante)
        //abrimos el widget de la solicitud de acompañamiento al recibir un mensaje de un acompañante
        mostrarModalAcompañamiento.value = true
    }

    function onAcompañamientoConfirmado() {
        acompañamientoModalRef.value?.notificarAcompañamientoConfirmado()
    }

    function abrirModalAcompañamiento() {
        console.log('abriendo modal')
        mostrarModalAcompañamiento.value = true
    }

    return {
        mostrarModalAcompañamiento,
        nuevoAcompañamientoCercano,
        cargarPerfil,
        handleAcompañamientoSolicitado,
        aceptarAcompañamientoComoAcompañante,
        acompañamientosIgnorados,
        ignorarAcompañamiento,
        onNuevoAcompañamiento,
        onAcompañamientoConfirmado,
        onAcompañantePropuesto,
        abrirModalAcompañamiento,
    }
}