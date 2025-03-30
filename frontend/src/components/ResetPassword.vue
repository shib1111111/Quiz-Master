<template>
  <div class="reset-password-container">
    <header class="header">
      <h1 class="app-title">Quiz Master</h1>
    </header>
    <main class="main-content">
      <div class="row">
        <div class="col-md-6 left-section">
          <div class="intro-container">
            <h2 class="intro-title">Reset & Retry</h2>
            <img
              src="/src/assets/frontpage_fig.jpg"
              alt="Reset Password for Quiz Master"
              class="left-image"
            />
            <p class="intro-text">
              Enter your OTP and set a new password to get back in the game!
            </p>
          </div>
        </div>
        <div class="col-md-6 right-section">
          <div class="reset-password-form">
            <h2 class="form-title">Reset Password</h2>
            <Alert
              v-if="alertMessage"
              :message="alertMessage"
              :type="alertType"
              @close="alertMessage = ''"
            />
            <form @submit.prevent="handleResetPassword">
              <div class="mb-3">
                <input
                  v-model="form.otp"
                  type="text"
                  class="form-control custom-input"
                  placeholder="OTP"
                  required
                />
              </div>
              <div class="mb-3">
                <input
                  v-model="form.new_password"
                  type="password"
                  class="form-control custom-input"
                  placeholder="New Password"
                  required
                />
              </div>
              <div class="mb-3">
                <input
                  v-model="form.confirmPassword"
                  type="password"
                  class="form-control custom-input"
                  placeholder="Re-enter Password"
                  required
                />
              </div>
              <div class="mb-3">
                <select v-model="form.role" class="form-select custom-input" required>
                  <option value="" disabled>Select Role</option>
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <button type="submit" class="btn reset-btn w-100"><span>Reset Password</span></button>
            </form>
            <p class="mt-3 text-center login-link">
              Back to
              <router-link to="/login" class="login-link-hover">Login</router-link>
            </p>
          </div>
        </div>
      </div>
    </main>
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
        role: 'user'
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
.reset-password-container {
  min-height: 100vh;
  position: relative;
  display: flex;
  flex-direction: column;
}
.header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  text-align: center;
  z-index: 1;
}

.app-title {
  margin: 0;
  color: #1a365d;
  font-size: 3.4rem;
  font-weight: 700;
}
.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 80px;
  padding-bottom: 30px;
}

.row {
  width: 100%;
  max-width: 1200px;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
}

.left-section {
  flex: 1;
  min-width: 300px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 20px;
  padding-right: 80px;
}

.intro-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.intro-title {
  font-size: 1.8rem;
  color: #1a365d;
  margin-bottom: 15px;
  font-weight: 600;
}

.left-image {
  max-width: 90%;
  height: auto;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  margin-bottom: 15px;
}

.left-image:hover {
  transform: scale(1.02);
}

.intro-text {
  text-align: center;
  color: #2d3748;
  font-size: 1rem;
  line-height: 1.5;
  font-weight: 500;
}
.right-section {
  flex: 1;
  min-width: 300px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 20px;
  padding-left: 80px;
}

.reset-password-form {
  background: rgba(255, 255, 255, 0.95);
  padding: 25px;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.form-title {
  text-align: center;
  color: #2c7a7b;
  font-size: 1.8rem;
  margin-bottom: 20px;
}

.custom-input {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 10px;
  width: 100%;
  font-size: 1rem;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.custom-input:focus {
  border-color: #3182ce;
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.2);
  outline: none;
}

.reset-btn {
  background-color: #3182ce;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 12px 20px;
  font-weight: 600;
  font-size: 1rem;
  transform: skewX(-15deg);
  display: inline-block;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.reset-btn span {
  display: block;
  transform: skewX(15deg);
}

.reset-btn:hover {
  background-color: #2b6cb0;
  transform: skewX(-15deg) translateY(-2px);
}

.login-link {
  color: #4a5568;
  font-size: 0.9rem;
}

.login-link-hover {
  color: #3182ce;
  text-decoration: none;
  transition: color 0.3s ease;
}

.login-link-hover:hover {
  color: #2b6cb0;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .row {
    flex-direction: column;
    padding: 0 10px;
  }
  .left-section,
  .right-section {
    min-width: 100%;
    padding: 10px;
    justify-content: center;
    padding-left: 20px;
    padding-right: 20px;
  }
  .intro-container {
    padding: 0 10px;
  }
  .left-image {
    max-width: 100%;
  }
  .reset-password-form {
    margin: 0;
    max-width: 100%;
  }
  .app-title {
    font-size: 2.5rem;
  }
  .main-content {
    padding-top: 70px;
  }
}

@media (max-width: 576px) {
  .app-title {
    font-size: 2rem;
  }
  .form-title {
    font-size: 1.5rem;
  }
  .intro-title {
    font-size: 1.6rem;
  }
  .intro-text {
    font-size: 0.9rem;
  }
  .custom-input,
  .reset-btn {
    padding: 8px;
    font-size: 0.9rem;
  }
  .main-content {
    padding-top: 60px;
  }
}
</style>