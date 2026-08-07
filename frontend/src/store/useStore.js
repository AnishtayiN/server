import { create } from 'zustand'
import api from '../api/client'

export const useStore = create((set) => ({
  user: null,
  users: [],
  stats: null,
  loading: false,
  isAuthenticated: !!localStorage.getItem('token'),

  login: async (username, password) => {
    const res = await api.post('/auth/login', { username, password })
    localStorage.setItem('token', res.data.access_token)
    set({ isAuthenticated: true, user: { username } })
    return true
  },

  logout: () => {
    localStorage.removeItem('token')
    set({ isAuthenticated: false, user: null })
  },

  fetchUsers: async () => {
    set({ loading: true })
    try {
      const res = await api.get('/users')
      set({ users: res.data, loading: false })
    } catch {
      set({ loading: false })
    }
  },

  fetchStats: async () => {
    try {
      const res = await api.get('/system/stats')
      set({ stats: res.data })
    } catch {}
  },

  createUser: async (data) => {
    await api.post('/users', data)
    await useStore.getState().fetchUsers()
  },

  deleteUser: async (id) => {
    await api.delete(`/users/${id}`)
    await useStore.getState().fetchUsers()
  }
}))
