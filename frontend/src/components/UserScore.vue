<template>
    <div class="container-fluid mt-5">
      <Navbar />
      <Alert v-if="alertMessage" :message="alertMessage" :type="alertType" @close="alertMessage = ''" />
      <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
        <ul class="navbar-nav me-auto">
          <li class="nav-item"><router-link class="nav-link" to="/user-dashboard">Home</router-link></li>
          <li class="nav-item"><router-link class="nav-link" to="/user-scores">Scores</router-link></li>
        </ul>
        <button class="btn btn-danger" @click="handleLogout">Logout</button>
      </nav>
      <div class="row">
        <div class="col-md-12">
          <h2 class="chapter-title">Your Quiz Scores</h2>
          <p class="description">Review your past quiz performances below.</p>
        </div>
      </div>
      
      <div class="row mt-4">
        <div class="col-md-12">
          <div class="subject-card">
            <div class="card-header bg-warning text-dark">
              <h3>Scores</h3>
            </div>
            <div class="card-body">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>Quiz ID</th>
                    <th>Number of Questions</th>
                    <th>Date</th>
                    <th>Score</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="score in quizScores" :key="score.quiz_id" class="chapter-item">
                    <td>{{ score.quiz_id }}</td>
                    <td>{{ score.number_of_questions }}</td>
                    <td>{{ score.date }}</td>
                    <td>{{ score.score }}</td>
                  </tr>
                  <tr v-if="quizScores.length === 0">
                    <td colspan="4" class="text-center no-chapters">
                      <i class="bi bi-exclamation-triangle"></i><br>No scores available yet.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import Alert from '@/components/Alert.vue';
  import Navbar from '@/components/Navbar.vue';
  import { useStore } from 'vuex';
  
  const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;
  
  export default {
    components: { Alert, Navbar },
    setup() {
      const store = useStore();
      return { store };
    },
    data() {
      return {
        alertMessage: '',
        alertType: 'info',
        quizScores: []
      };
    },
    async created() {
      const access_token = this.store.state.access_token;
      const role = this.store.state.role;
  
      if (!access_token || role !== 'user') {
        this.$router.push('/login');
        return;
      }
  
      try {
        const response = await axios.get(`${BASE_URL}/dashboard/user/scores`);
        this.quizScores = response.data.scores;
      } catch (error) {
        if (error.response?.status === 401) {
          this.alertMessage = 'Session expired. Redirecting to login...';
          this.alertType = 'warning';
          setTimeout(() => this.$router.push('/login'), 1000);
        } else {
          this.alertMessage = error.response?.data.msg || 'Failed to load scores.';
          this.alertType = 'error';
        }
        this.store.commit('clearAuth');
      }
    },
    methods: {
      async handleLogout() {
        try {
          await axios.post(`${BASE_URL}/logout/user`, {});
          this.store.commit('clearAuth');
          this.$router.push('/login');
        } catch (error) {
          this.alertMessage = 'Logout failed.';
          this.alertType = 'error';
          this.store.commit('clearAuth');
          this.$router.push('/login');
        }
      }
    }
  };
  </script>
  
  <style scoped>
  /* Base styles */
  .container-fluid {
    padding: 0 20px;
  }
  
  .subject-card {
    border: none;
    border-radius: 8px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    background: #fff;
  }
  
  .subject-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  }
  
  .card-header {
    border-radius: 8px 8px 0 0;
    padding: 15px;
  }
  
  .card-body {
    padding: 20px;
  }
  
  .description {
    color: #666;
    font-size: 0.95rem;
    margin-bottom: 15px;
  }
  
  .chapter-title {
    color: #333;
    font-weight: 600;
  }
  
  .chapter-list {
    border: 1px solid #eee;
    border-radius: 4px;
    max-height: 300px;
    overflow-y: auto;
  }
  
  .chapter-item {
    padding: 12px 15px;
    transition: background-color 0.2s ease;
  }
  
  .chapter-item:hover {
    background-color: #f8f9fa;
  }
  
  .chapter-info strong {
    color: #2c3e50;
  }
  
  .no-chapters {
    background: #fff3e0;
    border-radius: 4px;
    color: #e67e22;
  }
  
  .no-chapters i {
    font-size: 1.5rem;
    margin-bottom: 10px;
  }
  
  .btn {
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: 500;
  }
  
  .btn-danger {
    background: linear-gradient(135deg, #dc3545, #b02a37);
    border: none;
  }
  
  .btn-danger:hover {
    background: linear-gradient(135deg, #b02a37, #911d27);
  }
  
  .table th, .table td {
    vertical-align: middle;
  }
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
    .card-header {
      flex-direction: column;
      align-items: flex-start;
    }
  
    .card-header div {
      margin-top: 10px;
    }
  
    .chapter-item {
      flex-direction: column;
      align-items: flex-start;
    }
  }
  
  @media (max-width: 576px) {
    .btn-sm {
      padding: 4px 8px;
      font-size: 0.85rem;
    }
  
    .chapter-title {
      font-size: 1rem;
    }
  }
  </style>