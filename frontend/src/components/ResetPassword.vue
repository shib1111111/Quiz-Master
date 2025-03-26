<template>
    <div class="container-fluid vh-100 d-flex justify-content-end align-items-center">
      <div class="col-md-6 col-lg-4 p-4 bg-light rounded shadow">
        <h2 class="text-center mb-4">Reset Password</h2>
        <Alert v-if="alertMessage" :message="alertMessage" :type="alertType" @close="alertMessage = ''" />
        <form @submit.prevent="handleResetPassword">
          <div class="mb-3">
            <input v-model="form.otp" type="text" class="form-control" placeholder="OTP" required />
          </div>
          <div class="mb-3">
            <input v-model="form.new_password" type="password" class="form-control" placeholder="New Password" required />
          </div>
          <div class="mb-3">
            <input v-model="form.confirmPassword" type="password" class="form-control" placeholder="Re-enter Password" required />
          </div>
          <div class="mb-3">
            <select v-model="form.role" class="form-select" required>
              <option value="" disabled>Select Role</option>
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <button type="submit" class="btn btn-primary w-100">Reset Password</button>
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
          otp: '',
          new_password: '',
          confirmPassword: '',
          role: ''
        },
        alertMessage: '',
        alertType: 'info'
      };
    },
    methods: {
      validateForm() {
        if (!this.form.otp || !this.form.new_password || !this.form.role) {
          this.alertMessage = 'OTP, new password, and role are required.';
          this.alertType = 'error';
          return false;
        }
        if (this.form.new_password !== this.form.confirmPassword) {
          this.alertMessage = 'Passwords do not match.';
          this.alertType = 'error';
          return false;
        }
        if (this.form.new_password.length < 6) {
          this.alertMessage = 'Password must be at least 6 characters.';
          this.alertType = 'error';
          return false;
        }
        return true;
      },
      async handleResetPassword() {
        if (!this.validateForm()) return;
  
        const endpoint = this.form.role === 'user' ? '/reset_password/user' : '/reset_password/admin';
        try {
          const response = await axios.post(`${BASE_URL}${endpoint}`, {
            otp: this.form.otp,
            new_password: this.form.new_password
          });
          this.alertMessage = response.data.msg;
          this.alertType = 'success';
          setTimeout(() => this.$router.push('/login'), 2000);
        } catch (error) {
          this.alertMessage = error.response?.data.msg || 'Reset failed.';
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