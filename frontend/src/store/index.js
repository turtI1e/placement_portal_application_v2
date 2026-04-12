import { createStore } from 'vuex'
import axios from '../plugins/axios'

export default createStore({
  state: {
    user: null,
    access_token: sessionStorage.getItem('access_token') || null,
    user_role: sessionStorage.getItem('user_role') || null
  },
  mutations: {
    setUser(state, user) { state.user = user },
    setAccessToken(state, token) { 
      state.access_token = token
      if (token) {
        sessionStorage.setItem('access_token', token)
      } else {
        sessionStorage.removeItem('access_token')
      }
    },
    setUserRole(state, role) {
      state.user_role = role
      if (role) {
        sessionStorage.setItem('user_role', role)
      } else {
        sessionStorage.removeItem('user_role')
      }
    }
  },
  actions: {
    async login({ commit }, credentials) {
      const response = await axios.post('/auth/login', credentials)
      const { token, role } = response.data
      commit('setAccessToken', token)
      commit('setUserRole', role)
      return role
    },
    logout({ commit }) {
      commit('setAccessToken', null)
      commit('setUserRole', null)
      commit('setUser', null)
    }
  },
  getters: {
    isAuthenticated: state => !!state.access_token,
    userRole: state => state.user_role
  }
})
