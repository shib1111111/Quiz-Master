<template>
    <div class="container-fluid vh-100 d-flex justify-content-end align-items-center">
      <div class="col-md-6 col-lg-4 p-4 bg-light rounded shadow">
        <h2 class="text-center mb-4">Forgot Password</h2>
        <Alert v-if="alertMessage" :message="alertMessage" :type="alertType" @close="alertMessage = ''" />
        <form @submit.prevent="handleForgotPassword">
          <div class="mb-3">
            <input v-model="form.username" type="text" class="form-control" placeholder="Username" />
          </div>
          <div class="mb-3">
            <input v-model="form.email" type="email" class="form-control" placeholder="Email" />
          </div>
          <div class="mb-3">
            <select v-model="form.role" class="form-select" required>
              <option value="" disabled>Select Role</option>
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <button type="submit" class="btn btn-primary w-100">Request OTP</button>
        </form>
        <p class="mt-3 text-center">
          Back to <router-link to="/login">Login</router-link>
        </p>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import Alert from '@/components/Alert.vue';
  
  const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;
  
  export default {
    components: { Alert },
    data() {
      return {
        form: {
          username: '',
          email: '',
          role: ''
        },
        alertMessage: '',
        alertType: 'info'
      };
    },
    methods: {
      validateForm() {
        if (!this.form.username && !this.form.email) {
          this.alertMessage = 'Provide at least username or email.';
          this.alertType = 'error';
          return false;
        }
        if (!this.form.role) {
          this.alertMessage = 'Please select a role.';
          this.alertType = 'error';
          return false;
        }
        if (this.form.email && !/^\S+@\S+\.\S+$/.test(this.form.email)) {
          this.alertMessage = 'Invalid email format.';
          this.alertType = 'error';
          return false;
        }
        return true;
      },
      async handleForgotPassword() {
        if (!this.validateForm()) return;
  
        const endpoint = this.form.role === 'user' ? '/forgot_password/user' : '/forgot_password/admin';
        try {
          const response = await axios.post(`${BASE_URL}${endpoint}`, {
            username: this.form.username,
            email: this.form.email
          });
          this.alertMessage = response.data.msg;
          this.alertType = 'success';
          setTimeout(() => this.$router.push('/reset-password'), 2000);
        } catch (error) {
          this.alertMessage = error.response?.data.msg || 'Request failed.';
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