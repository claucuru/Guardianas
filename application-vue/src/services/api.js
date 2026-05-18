import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

// Inyecta el token en cada petición automáticamente
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Token ${token}`
  return config
})

export default api