<template>
  <div class="container-fluid vh-100 d-flex justify-content-end align-items-center">
    <div class="col-md-6 col-lg-4 p-4 bg-light rounded shadow">
      <h2 class="text-center mb-4">Login</h2>
      <Alert v-if="alertMessage" :message="alertMessage" :type="alertType" @close="alertMessage = ''" />
      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <input v-model="form.email" type="email" class="form-control" placeholder="Email" required />
        </div>
        <div class="mb-3">
          <input v-model="form.password" type="password" class="form-control" placeholder="Password" required />
        </div>
        <div class="mb-3">
          <select v-model="form.role" class="form-select" required>
            <option value="" disabled>Select Role</option>
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <button type="submit" class="btn btn-primary w-100">Login</button>
      </form>
      <p class="mt-3 text-center">
        New user? <router-link to="/signup">Sign up here</router-link><br />
        Forgot password? <router-link to="/forgot-password">Reset here</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Alert from '@/components/Alert.vue';
import { useStore } from 'vuex';

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

export default {
  components: { Alert },
  setup() {
    const store = useStore();
    return { store };
  },
  data() {
    return {
      form: {
        email: '',
        password: '',
        role: ''
      },
      alertMessage: '',
      alertType: 'info'
    };
  },
  methods: {
    validateForm() {
      if (!this.form.email || !this.form.password || !this.form.role) {
        this.alertMessage = 'All fields are required.';
        this.alertType = 'error';
        return false;
      }
      if (!/^\S+@\S+\.\S+$/.test(this.form.email)) {
        this.alertMessage = 'Invalid email format.';
        this.alertType = 'error';
        return false;
      }
      return true;
    },
    async handleLogin() {
      if (!this.validateForm()) return;

      const endpoint = this.form.role === 'user' ? '/login/user' : '/login/admin';
      try {
        const response = await axios.post(`${BASE_URL}${endpoint}`, {
          email: this.form.email,
          password: this.form.password
        });
        this.store.commit('setAuth', {
          access_token: response.data.access_token,
          refresh_token: response.data.refresh_token, 
          role: response.data.role
        });
        this.alertMessage = response.data.msg;
        this.alertType = 'success';
        const redirect = this.form.role === 'user' ? '/user-dashboard' : '/admin-dashboard';
        setTimeout(() => this.$router.push(redirect), 1000);
      } catch (error) {
        this.alertMessage = error.response?.data.msg || 'Login failed.';
        this.alertType = 'error';
      }
    }
  }
};
</script>
<style scoped>
@media (max-width: 768px) {
  .card {
    margin: 20px;
  }
}
</style>