// store/index.js
import { createStore } from 'vuex';
import axios from 'axios';

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

export default createStore({
  state: {
    access_token: localStorage.getItem('access_token') || null, // Renamed for clarity
    refresh_token: localStorage.getItem('refresh_token') || null, // Add refresh token
    role: localStorage.getItem('role') || null
  },
  mutations: {
    setAuth(state, { access_token, refresh_token, role }) {
      state.access_token = access_token;
      state.refresh_token = refresh_token;
      state.role = role;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('role', role);
    },
    setAccessToken(state, access_token) { // New mutation for refreshing access token
      state.access_token = access_token;
      localStorage.setItem('access_token', access_token);
    },
    clearAuth(state) {
      state.access_token = null;
      state.refresh_token = null;
      state.role = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('role');
    }
  },
  actions: {
    initializeAuth({ commit }) {
      const access_token = localStorage.getItem('access_token');
      const refresh_token = localStorage.getItem('refresh_token');
      const role = localStorage.getItem('role');
      if (access_token && refresh_token && role) {
        commit('setAuth', { access_token, refresh_token, role });
      }
    },
    async refreshToken({ commit, state }) {
      try {
        const response = await axios.post(`${BASE_URL}/refresh`, {}, {
          headers: { Authorization: `Bearer ${state.refresh_token}` }
        });
        commit('setAccessToken', response.data.access_token);
        return response.data.access_token;
      } catch (error) {
        commit('clearAuth');
        throw error; // Trigger logout if refresh fails
      }
    }
  }
});