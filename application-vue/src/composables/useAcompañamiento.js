import { ref } from 'vue'
import api from '@/services/api'

export function useAcompañamiento(acompañamientoModalRef) {
    const mostrarModalAcompañamiento = ref(false)
    const nuevoAcompañamientoCercano = ref(null)
    const disponible = ref(false)

    async function cargarPerfil() {
        const res = await api.get('api/v1/perfil/')
        disponible.value = res.data.disponible
    }

    async function handleToggleDisponible() {
        console.log('handleToggleDisponible llamado, disponible actual:', disponible.value)
        
        try {
            const payload = {}
            if(!disponible.value) {
                const pos = await new Promise((res, rej) => 
                    navigator.geolocation.getCurrentPosition(res, rej, {timeout: 6000 })
                )
                payload.lat = pos.coords.latitude
                payload.lng = pos.coords.longitude
            }
            const res = await api.post('api/v1/acompañamientos/disponible/', payload)
            disponible.value = res.data.disponible
        
        } catch (err){
            console.error('Error en handleToggleDisponible: ', err)
        }
    }

    async function handleAcompañamientoSolicitado(acompañamientoId) {
        console.log('Acompañamiento solicitado:', acompañamientoId)
        await acompañamientoModalRef.value?.cargar()
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
        acompañamientoModalRef.value?.notificarAcompañantePropuesto(data.acompañante_nombre || data.acompañante)
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
        disponible,
        cargarPerfil,
        handleToggleDisponible,
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