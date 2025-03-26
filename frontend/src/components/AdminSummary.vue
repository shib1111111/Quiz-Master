<template>
    <div class="container mt-5">
      <Alert v-if="alertMessage" :message="alertMessage" :type="alertType" @close="alertMessage = ''" />
      <Navbar />
      <div class="row">
        <div class="col-md-12">
          <h2>Summary Charts</h2>
          <div class="mb-4">
            <h3>Subject-wise Top Scores</h3>
            <canvas id="topScoresChart"></canvas>
          </div>
          <div>
            <h3>Subject-wise User Attempts</h3>
            <canvas id="userAttemptsChart"></canvas>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  
  <script>
  import axios from 'axios';
  import Chart from 'chart.js/auto';
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
        topScores: [],
        userAttempts: [],
        alertMessage: '',
        alertType: 'info'
      };
    },
    async created() {
      if (!this.store.state.access_token || this.store.state.role !== 'admin') {
        this.$router.push('/login');
        return;
      }
      await this.fetchSummaryData();
      this.renderCharts();
    },
    methods: {
      async fetchSummaryData() {
        try {
          const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
          const topScoresResponse = await axios.get(`${BASE_URL}/summary/top-scores`, config);
          this.topScores = topScoresResponse.data;
          const attemptsResponse = await axios.get(`${BASE_URL}/summary/user-attempts`, config);
          this.userAttempts = attemptsResponse.data;
        } catch (error) {
          this.handleError(error, 'Failed to fetch summary data');
        }
      },
      renderCharts() {
        const topScoresCtx = document.getElementById('topScoresChart').getContext('2d');
        new Chart(topScoresCtx, {
          type: 'bar',
          data: {
            labels: this.topScores.map(s => s.subject),
            datasets: [{
              label: 'Top Score',
              data: this.topScores.map(s => s.top_score),
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1
            }]
          },
          options: {
            scales: { y: { beginAtZero: true } }
          }
        });
  
        const attemptsCtx = document.getElementById('userAttemptsChart').getContext('2d');
        new Chart(attemptsCtx, {
          type: 'pie',
          data: {
            labels: this.userAttempts.map(s => s.subject),
            datasets: [{
              label: 'Attempts',
              data: this.userAttempts.map(s => s.attempts),
              backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)'
              ],
              borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)'
              ],
              borderWidth: 1
            }]
          }
        });
      },
      handleError(error, message) {
        console.error(`${message}:`, error);
        this.alertMessage = `${message}: ${error.response?.data.msg || error.message}`;
        this.alertType = 'error';
        if (error.response?.status === 401) {
          this.store.commit('clearAuth');
          setTimeout(() => this.$router.push('/login'), 1000);
        }
      }
    }
  };
  </script>