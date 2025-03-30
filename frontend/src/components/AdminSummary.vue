<!-- src/views/AdminSummary.vue -->
<template>
  <div class="container-fluid mt-5">
    <Alert v-if="alertMessage" :message="alertMessage" :type="alertType" @close="alertMessage = ''" />
    <Navbar @search="handleSearch" />

    <div class="row mt-4">
      <div class="col-12">
        <div class="row g-4 mb-4">
          <div class="col-md-3 col-sm-6">
            <div class="card stat-card">
              <div class="card-body">
                <h5>Total Users</h5>
                <p>{{ summaryData.system_stats.total_users }}</p>
              </div>
            </div>
          </div>
          <div class="col-md-3 col-sm-6">
            <div class="card stat-card">
              <div class="card-body">
                <h5>Active Users</h5>
                <p>{{ summaryData.system_stats.active_users }}</p>
              </div>
            </div>
          </div>
          <div class="col-md-3 col-sm-6">
            <div class="card stat-card">
              <div class="card-body">
                <h5>Total Quizzes</h5>
                <p>{{ summaryData.system_stats.total_quizzes }}</p>
              </div>
            </div>
          </div>
          <div class="col-md-3 col-sm-6">
            <div class="card stat-card">
              <div class="card-body">
                <h5>Total Revenue</h5>
                <p>₹{{ summaryData.revenue.total.toFixed(2) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts -->
        <div class="row g-4">
          <!-- User Performance Distribution -->
          <div class="col-lg-6 col-md-12">
            <div class="card chart-card">
              <div class="card-body">
                <h5 class="card-title">User Performance Distribution</h5>
                <canvas ref="performanceChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Subject Total Scores -->
          <div class="col-lg-6 col-md-12">
            <div class="card chart-card">
              <div class="card-body">
                <h5 class="card-title">Subject Total Scores</h5>
                <canvas ref="subjectChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Monthly Engagement -->
          <div class="col-lg-6 col-md-12">
            <div class="card chart-card">
              <div class="card-body">
                <h5 class="card-title">Monthly User Engagement</h5>
                <canvas ref="monthlyChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Difficulty Total Scores -->
          <div class="col-lg-6 col-md-12">
            <div class="card chart-card">
              <div class="card-body">
                <h5 class="card-title">Difficulty Total Scores</h5>
                <canvas ref="difficultyChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Quiz Popularity -->
          <div class="col-lg-6 col-md-12">
            <div class="card chart-card">
              <div class="card-body">
                <h5 class="card-title">Top Quiz Popularity</h5>
                <canvas ref="popularityChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Revenue by Quiz -->
          <div class="col-lg-6 col-md-12">
            <div class="card chart-card">
              <div class="card-body">
                <h5 class="card-title">Revenue by Quiz</h5>
                <canvas ref="revenueChart"></canvas>
              </div>
            </div>
          </div>
        </div>

        <!-- Report Download -->
        <div class="mt-6 text-center">
          <h4 style="color: #4b2ecc;">Download Detailed Reports</h4>
          <br />
          <button class="btn btn-primary me-3" @click="downloadReport('system_summary')">System Summary</button>
          <button class="btn btn-success me-3" @click="downloadReport('subject_analysis')">Subject Analysis</button>
          <button class="btn btn-info me-3" @click="downloadReport('revenue_report')">Revenue Report</button>
          <button class="btn btn-warning me-3" @click="downloadReport('quiz_popularity')">Quiz Popularity</button>
          <button class="btn btn-secondary me-3" @click="downloadReport('user_engagement')">User Engagement</button>
          <button class="btn btn-dark" @click="triggerAllUsersQuizExport">All Users Quiz Data</button>
        </div>
        <br />
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
import axios from 'axios';
import Alert from '@/components/Alert.vue';
import Navbar from '@/components/Navbar.vue';
import { useStore } from 'vuex';

Chart.register(...registerables);

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

export default {
  name: 'AdminSummary',
  components: { Alert, Navbar },
  setup() {
    const store = useStore();
    return { store };
  },
  data() {
    return {
      alertMessage: '',
      alertType: 'info',
      summaryData: {
        system_stats: { total_users: 0, active_users: 0, total_quizzes: 0, total_subjects: 0, total_questions: 0 },
        performance: {},
        monthly_engagement: {},
        subject_performance: {},
        revenue: { total: 0, by_quiz: {} },
        quiz_popularity: {},
        difficulty_analysis: {}
      },
      charts: {},
    };
  },
  methods: {
    async triggerAllUsersQuizExport() {
    try {
      const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
      const response = await axios.post(`${BASE_URL}/dashboard/admin/export_all_users_quiz_data`, {}, config);
      this.alertMessage = response.data.msg;
      this.alertType = 'success';
      alert(response.data.msg || 'Export job started. Check your email soon!');

    } catch (error) {
    const errorMsg = error.response?.data?.msg || 'Couldn’t trigger all users quiz data export.';
    alert(errorMsg);
    console.error('Export error:', error);
  }
},

    async fetchSummaryData() {
      try {
        const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
        const response = await axios.get(`${BASE_URL}/dashboard/admin/summary`, config);
        this.summaryData = response.data;
        this.renderCharts();
      } catch (error) {
        this.handleError(error, 'Oops! Couldn’t load admin summary.');
      }
    },
    renderCharts() {
      const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { color: '#333', font: { size: 14 } } },
          tooltip: { backgroundColor: '#4b2ecc', titleColor: '#fff', bodyColor: '#fff', padding: 10 }
        }
      };

      // User Performance Distribution (Pie Chart)
      this.charts.performance = new Chart(this.$refs.performanceChart, {
        type: 'pie',
        data: {
          labels: Object.keys(this.summaryData.performance),
          datasets: [{
            data: Object.values(this.summaryData.performance),
            backgroundColor: ['#00c4cc', '#6b48ff', '#ffca28', '#ff5722'],
            hoverOffset: 10
          }]
        },
        options: chartOptions
      });

      // Subject Total Scores (Bar Chart)
      this.charts.subject = new Chart(this.$refs.subjectChart, {
        type: 'bar',
        data: {
          labels: Object.keys(this.summaryData.subject_performance),
          datasets: [{
            label: 'Total Score',
            data: Object.values(this.summaryData.subject_performance).map(s => s.total_score),
            backgroundColor: '#4b2ecc',
            hoverBackgroundColor: '#6b48ff'
          }]
        },
        options: {
          ...chartOptions,
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Total Score' } },
            x: { title: { display: true, text: 'Subjects' } }
          }
        }
      });

      // Monthly Engagement (Bar Chart)
      const monthlyData = Array(12).fill(0);
      Object.entries(this.summaryData.monthly_engagement).forEach(([month, count]) => {
        monthlyData[parseInt(month) - 1] = count;
      });
      this.charts.monthly = new Chart(this.$refs.monthlyChart, {
        type: 'bar',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
          datasets: [{
            label: 'Quiz Attempts',
            data: monthlyData,
            backgroundColor: '#6b48ff',
            hoverBackgroundColor: '#7c5aff'
          }]
        },
        options: {
          ...chartOptions,
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Total Attempts' } },
            x: { title: { display: true, text: 'Month' } }
          }
        }
      });

      // Difficulty Total Scores (Bar Chart)
      this.charts.difficulty = new Chart(this.$refs.difficultyChart, {
        type: 'bar',
        data: {
          labels: Object.keys(this.summaryData.difficulty_analysis),
          datasets: [{
            label: 'Total Score',
            data: Object.values(this.summaryData.difficulty_analysis).map(d => d.total_score),
            backgroundColor: '#00c4cc',
            hoverBackgroundColor: '#00d4dd'
          }]
        },
        options: {
          ...chartOptions,
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Total Score' } },
            x: { title: { display: true, text: 'Difficulty Level' } }
          }
        }
      });

      // Quiz Popularity (Bar Chart - Top 5)
      const topQuizzes = Object.entries(this.summaryData.quiz_popularity)
        .sort((a, b) => b[1].attempts - a[1].attempts)
        .slice(0, 5);
      this.charts.popularity = new Chart(this.$refs.popularityChart, {
        type: 'bar',
        data: {
          labels: topQuizzes.map(([quizId]) => `Quiz ${quizId}`),
          datasets: [{
            label: 'Attempts',
            data: topQuizzes.map(([, data]) => data.attempts),
            backgroundColor: '#ffca28',
            hoverBackgroundColor: '#ffd54f'
          }]
        },
        options: {
          ...chartOptions,
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Total Attempts' } },
            x: { title: { display: true, text: 'Quiz ID' } }
          }
        }
      });

      // Revenue by Quiz (Bar Chart - Top 5)
      const topRevenueQuizzes = Object.entries(this.summaryData.revenue.by_quiz)
        .sort((a, b) => b[1].amount - a[1].amount)
        .slice(0, 5);
      this.charts.revenue = new Chart(this.$refs.revenueChart, {
        type: 'bar',
        data: {
          labels: topRevenueQuizzes.map(([quizId]) => `Quiz ${quizId}`),
          datasets: [{
            label: 'Revenue (₹)',
            data: topRevenueQuizzes.map(([, data]) => data.amount),
            backgroundColor: '#ff5722',
            hoverBackgroundColor: '#ff7043'
          }]
        },
        options: {
          ...chartOptions,
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Revenue (₹)' } },
            x: { title: { display: true, text: 'Quiz ID' } }
          }
        }
      });
    },
    async downloadReport(reportType) {
      try {
        let csvContent, filename;
        switch (reportType) {
          case 'system_summary':
            csvContent = "Metric,Value\n";
            csvContent += `Total Users,${this.summaryData.system_stats.total_users}\n`;
            csvContent += `Active Users,${this.summaryData.system_stats.active_users}\n`;
            csvContent += `Total Quizzes,${this.summaryData.system_stats.total_quizzes}\n`;
            csvContent += `Total Subjects,${this.summaryData.system_stats.total_subjects}\n`;
            csvContent += `Total Questions,${this.summaryData.system_stats.total_questions}\n`;
            csvContent += `Total Revenue,${this.summaryData.revenue.total}\n`;
            filename = `system_summary_${new Date().toISOString().split('T')[0]}.csv`;
            break;

          case 'subject_analysis':
            csvContent = "Subject,Total Score,Total Attempts\n";
            Object.entries(this.summaryData.subject_performance).forEach(([subject, data]) => {
              csvContent += `${subject},${data.total_score},${data.attempts}\n`;
            });
            filename = `subject_analysis_${new Date().toISOString().split('T')[0]}.csv`;
            break;

          case 'revenue_report':
            csvContent = "Quiz ID,Total Revenue,Payment Count\n";
            Object.entries(this.summaryData.revenue.by_quiz).forEach(([quizId, data]) => {
              csvContent += `${quizId},${data.amount},${data.count}\n`;
            });
            csvContent += `Total,${this.summaryData.revenue.total},${Object.values(this.summaryData.revenue.by_quiz).reduce((sum, d) => sum + d.count, 0)}\n`;
            filename = `revenue_report_${new Date().toISOString().split('T')[0]}.csv`;
            break;

          case 'quiz_popularity':
            csvContent = "Quiz ID,Total Attempts,Total Time Taken (s)\n";
            Object.entries(this.summaryData.quiz_popularity).forEach(([quizId, data]) => {
              csvContent += `${quizId},${data.attempts},${data.total_time}\n`;
            });
            filename = `quiz_popularity_${new Date().toISOString().split('T')[0]}.csv`;
            break;

          case 'user_engagement':
            csvContent = "Month,Total Attempts\n";
            const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            Object.entries(this.summaryData.monthly_engagement).forEach(([month, count]) => {
              csvContent += `${monthNames[parseInt(month) - 1]},${count}\n`;
            });
            filename = `user_engagement_${new Date().toISOString().split('T')[0]}.csv`;
            break;
        }

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (error) {
        this.handleError(error, `Couldn’t download your ${reportType} report.`);
      }
    },
    handleError(error, defaultMsg) {
      this.alertMessage = error.response?.data?.msg || defaultMsg;
      this.alertType = 'error';
      if (error.response?.status === 401) {
        this.store.commit('clearAuth');
        setTimeout(() => this.$router.push('/login'), 1000);
      }
    },
    handleSearch(query) {
      // Placeholder for future search functionality
    },
  },
  async created() {
    const access_token = this.store.state.access_token;
    if (!access_token) {
      this.$router.push('/login');
      return;
    }
    await this.fetchSummaryData();
  },
  beforeUnmount() {
    Object.values(this.charts).forEach(chart => chart.destroy());
  },
};
</script>

<style scoped>
.container-fluid {
  padding: 0 20px;
}

.stat-card {
  border: none;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-card h5 {
  color: #4b2ecc;
  font-weight: 600;
  margin-bottom: 10px;
}

.stat-card p {
  font-size: 1.5rem;
  color: #333;
  margin: 0;
}

.chart-card {
  border: none;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.15);
}

.card-body {
  padding: 20px;
}

.card-title {
  color: #4b2ecc;
  font-weight: 600;
  margin-bottom: 15px;
  font-size: 1.25rem;
}

canvas {
  max-height: 300px;
}

.btn-primary {
  background: linear-gradient(135deg, #6b48ff, #4b2ecc);
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  transition: background 0.3s ease, transform 0.2s ease;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #7c5aff, #6b48ff);
  transform: scale(1.05);
}
.btn-dark {
  background: linear-gradient(135deg, #343a40, #212529);
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  transition: background 0.3s ease, transform 0.2s ease;
  color: #fff;
}

.btn-dark:hover {
  background: linear-gradient(135deg, #495057, #343a40);
  transform: scale(1.05);
}
.btn-success {
  background: linear-gradient(135deg, #00c4cc, #009fa6);
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  transition: background 0.3s ease, transform 0.2s ease;
}

.btn-success:hover {
  background: linear-gradient(135deg, #00d4dd, #00b0b8);
  transform: scale(1.05);
}

.btn-info {
  background: linear-gradient(135deg, #17a2b8, #117a8b);
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  transition: background 0.3s ease, transform 0.2s ease;
}

.btn-info:hover {
  background: linear-gradient(135deg, #1cc3db, #17a2b8);
  transform: scale(1.05);
}

.btn-warning {
  background: linear-gradient(135deg, #ffca28, #e0a800);
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  transition: background 0.3s ease, transform 0.2s ease;
}

.btn-warning:hover {
  background: linear-gradient(135deg, #ffd54f, #ffca28);
  transform: scale(1.05);
}

.btn-secondary {
  background: linear-gradient(135deg, #6c757d, #545b62);
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  transition: background 0.3s ease, transform 0.2s ease;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #868e96, #6c757d);
  transform: scale(1.05);
}

@media (max-width: 768px) {
  .stat-card, .chart-card {
    margin-bottom: 20px;
  }

  canvas {
    max-height: 250px;
  }

  .btn-primary, .btn-success, .btn-info, .btn-warning, .btn-secondary {
    width: 100%;
    margin-bottom: 10px;
  }
}
</style>
