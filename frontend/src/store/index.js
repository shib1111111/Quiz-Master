// store/index.js
import { createStore } from 'vuex';
import axios from 'axios';


const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

export default createStore({
  state: {
    access_token: localStorage.getItem('access_token') || null, 
    refresh_token: localStorage.getItem('refresh_token') || null, 
    role: localStorage.getItem('role') || null,
    stripePublicKey: localStorage.getItem('stripePublicKey') || '', 
    cartCount: 0 
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
    setAccessToken(state, access_token) { 
      state.access_token = access_token;
      localStorage.setItem('access_token', access_token);
    },
    setStripePublicKey(state, key) { 
      state.stripePublicKey = key;
      localStorage.setItem('stripePublicKey', key); 
    },
    updateCartCount(state, count) { 
      state.cartCount = count;
    },
    clearAuth(state) {
      state.access_token = null;
      state.refresh_token = null;
      state.role = null;
      state.stripePublicKey = ''; 
      state.cartCount = 0; 
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('role');
      localStorage.removeItem('stripePublicKey');
    }
  },

  actions: {
    initializeAuth({ commit }) {
      const access_token = localStorage.getItem('access_token');
      const refresh_token = localStorage.getItem('refresh_token');
      const role = localStorage.getItem('role');
      const stripePublicKey = localStorage.getItem('stripePublicKey');
      if (access_token && refresh_token && role) {
        commit('setAuth', { access_token, refresh_token, role });
        if (stripePublicKey) {
          commit('setStripePublicKey', stripePublicKey);
        }
        if (role === 'user') {
          dispatch('updateCartCount'); // Fetch cart count on init for users
        }
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
    },
    async fetchStripePublicKey({ commit, state }) { // New action to fetch key if missing
      if (!state.stripePublicKey) {
        try {
          const response = await axios.get(`${BASE_URL}/dashboard/user/cart`, {
            headers: { Authorization: `Bearer ${state.access_token}` }
          });
          if (response.data.stripe_public_key) {
            commit('setStripePublicKey', response.data.stripe_public_key);
          }
        } catch (error) {
          console.error('Failed to fetch Stripe public key:', error);
        }
      }
    },
    async updateCartCount({ commit, state }) {
      try {
        const response = await axios.get(`${BASE_URL}/dashboard/user/cart`, {
          headers: { Authorization: `Bearer ${state.access_token}` }
        });
        const cartCount = response.data.items?.length || response.data.count || 0;
        commit('updateCartCount', cartCount);
      } catch (error) {
        console.error('Failed to update cart count:', error);
        // Optionally set cart count to 0 on error
        commit('updateCartCount', 0);
      }
    }
  }
});