import axios from 'axios'
import router from '../router'
import store from '../store'

const axiosInstance = axios.create({
  baseURL: '/api'
})

axiosInstance.interceptors.request.use(config => {
  const token = sessionStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

axiosInstance.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      store.dispatch('logout')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default axiosInstance
