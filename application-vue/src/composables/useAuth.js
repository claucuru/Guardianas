import { ref } from 'vue'
import api from '../services/api'

export function useAuth() {
  const isAuthenticated = ref(!!localStorage.getItem('token'))
  const currentUsername = ref(localStorage.getItem('username') || '')
  const loginError = ref('')
  const loginCargando = ref(false)
  const registroError = ref('')
  const registroOk = ref('')
  const registroCargando = ref(false)
  const solicitudesPendientes = ref([])

  const token = localStorage.getItem('token')
  if(token) {
    api.defaults.headers.common['Authorization'] = 'Token ' + token
  }

  async function login(username, password) {
    loginError.value = ''
    loginCargando.value = true
    // console.log("Login como:", this.username, "token:", token)
    try {
      const res = await api.post('api/login/', { username, password })
      const token = res.data.token
      localStorage.setItem('token', token)
      localStorage.setItem('username', res.data.username)
      api.defaults.headers.common['Authorization'] = 'Token ' + token
      currentUsername.value = res.data.username
      isAuthenticated.value = true
    } catch {
      loginError.value = 'Usuario o contraseña incorrectos'
    } finally {
      loginCargando.value = false
    }
  }

  function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    isAuthenticated.value = false
    currentUsername.value = ''
  }

  async function enviarRegistro(registro) {
    registroError.value = ''
    registroOk.value = ''
    registroCargando.value = true
    try {
      const res = await api.post('api/registro/', registro)
      if (res.data.status === 'pendiente_aprobacion') {
        registroOk.value = 'Solicitud enviada. Las avaladoras deben aceptarla.'
        return 'pendiente'
      } else {
        registroOk.value = 'Cuenta creada. Ya puedes iniciar sesión.'
        return 'ok'
      }
    } catch (e) {
      registroError.value = e.response?.data?.error || 'Error al registrar'
      return 'error'
    } finally {
      registroCargando.value = false
    }
  }

  async function cargarSolicitudesPendientes() {
    try {
      const res = await api.get('api/solicitudes-pendientes/')
      solicitudesPendientes.value = res.data
    } catch (e) {
      console.error('Error cargando solicitudes:', e)
    }
  }

  async function responderSolicitud(id, acepta) {
    console.log("URL llamada:", `api/solicitudes/${id}/responder/`)
    console.log("ID recibido:", id, typeof id)
    const res = await api.post(`api/solicitudes/${id}/responder/`, { acepta })
    await cargarSolicitudesPendientes()
    return res.data.status
  }

  return {
    isAuthenticated, currentUsername,
    loginError, loginCargando,
    registroError, registroOk, registroCargando,
    solicitudesPendientes,
    login, logout, enviarRegistro,
    cargarSolicitudesPendientes, responderSolicitud,
  }
}