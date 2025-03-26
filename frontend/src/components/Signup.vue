<template>
  <div class="container-fluid vh-100 d-flex justify-content-end align-items-center">
    <div class="col-md-6 col-lg-4 p-4 bg-light rounded shadow">
      <h2 class="text-center mb-4">Sign Up</h2>
      <Alert v-if="alertMessage" :message="alertMessage" :type="alertType" @close="alertMessage = ''" />
      <form @submit.prevent="handleSignup">
        <div class="mb-3">
          <input v-model="form.username" type="text" class="form-control" placeholder="Username" required />
        </div>
        <div class="mb-3">
          <input v-model="form.email" type="email" class="form-control" placeholder="Email" required />
        </div>
        <div class="mb-3">
          <input v-model="form.password" type="password" class="form-control" placeholder="Password" required />
        </div>
        <div class="mb-3">
          <input v-model="form.confirmPassword" type="password" class="form-control" placeholder="Re-enter Password" required />
        </div>
        <div class="mb-3">
          <input v-model="form.full_name" type="text" class="form-control" placeholder="Full Name" required />
        </div>
        <div class="mb-3">
          <input v-model="form.dob" type="date" class="form-control" required />
        </div>
        <div class="mb-3">
          <input v-model="form.qualification" type="text" class="form-control" placeholder="Qualification" required />
        </div>
        <button type="submit" class="btn btn-primary w-100">Sign Up</button>
      </form>
      <p class="mt-3 text-center">
        Already a user? <router-link to="/login">Login here</router-link>
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
        password: '',
        confirmPassword: '',
        full_name: '',
        dob: '',
        qualification: ''
      },
      alertMessage: '',
      alertType: 'info'
    };
  },
  methods: {
    validateForm() {
      if (!this.form.username || !this.form.email || !this.form.password || !this.form.full_name || !this.form.dob || !this.form.qualification) {
        this.alertMessage = 'All fields are required.';
        this.alertType = 'error';
        return false;
      }
      if (!/^\S+@\S+\.\S+$/.test(this.form.email)) {
        this.alertMessage = 'Invalid email format.';
        this.alertType = 'error';
        return false;
      }
      if (this.form.password !== this.form.confirmPassword) {
        this.alertMessage = 'Passwords do not match.';
        this.alertType = 'error';
        return false;
      }
      if (this.form.password.length < 6) {
        this.alertMessage = 'Password must be at least 6 characters.';
        this.alertType = 'error';
        return false;
      }
      return true;
    },
    async handleSignup() {
      if (!this.validateForm()) return;

      try {
        const response = await axios.post(`${BASE_URL}/signup/user`, this.form);
        this.alertMessage = response.data.msg;
        this.alertType = 'success';
        setTimeout(() => this.$router.push('/login'), 2000);
      } catch (error) {
        this.alertMessage = error.response?.data.msg || 'Signup failed.';
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