<template>
  <div class="container-fluid mt-5">
    <Alert v-if="alertMessage" :message="alertMessage" :type="alertType" @close="alertMessage = ''" />
    <Navbar @search="handleSearch" />

    <div class="row mt-4">
      <div class="col-12">
        <!-- Graph Container -->
        <div class="row g-4">
          <!-- Your Success Levels (Pie Chart) -->
          <div class="col-lg-6 col-md-12">
            <div class="card chart-card">
              <div class="card-body">
                <h5 class="card-title">Your Overall Success Levels</h5>
                <canvas ref="performanceChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Subject Mastery (Bar Chart) -->
          <div class="col-lg-6 col-md-12">
            <div class="card chart-card">
              <div class="card-body">
                <h5 class="card-title">Your Mastery Across Subjects</h5>
                <canvas ref="subjectChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Monthly Engagement (Bar Chart) -->
          <div class="col-lg-6 col-md-12">
            <div class="card chart-card">
              <div class="card-body">
                <h5 class="card-title">Your Year-long Engagement</h5>
                <canvas ref="monthlyChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Weekly Engagement (Bar Chart) -->
          <div class="col-lg-6 col-md-12">
            <div class="card chart-card">
              <div class="card-body">
                <h5 class="card-title">Your Weekly Engagement</h5>
                <canvas ref="weeklyChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Chapter-wise Activity (Bar Chart) -->
          <div class="col-lg-6 col-md-12">
            <div class="card chart-card">
              <div class="card-body">
                <h5 class="card-title">Your Activity by Chapter</h5>
                <canvas ref="chapterChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Quiz-wise Reattempts (Bar Chart) -->
          <div class="col-lg-6 col-md-12">
            <div class="card chart-card">
              <div class="card-body">
                <h5 class="card-title">Your Quiz Reattempts</h5>
                <canvas ref="reattemptChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Time Efficiency (Bar Chart) -->
          <div class="col-lg-6 col-md-12">
            <div class="card chart-card">
              <div class="card-body">
                <h5 class="card-title">Your Overall Time Efficiency</h5>
                <canvas ref="timeChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Speed vs Precision Balance (Pie Chart) -->
          <div class="col-lg-6 col-md-12">
            <div class="card chart-card">
              <div class="card-body">
                <h5 class="card-title">Your Speed vs Precision Balance</h5>
                <canvas ref="timeVsAccuracyChart"></canvas>
              </div>
            </div>
          </div>
        </div>

        <!-- Report Download Buttons -->
        <div class="mt-5 text-center">
          <h4 style="color: #4b2ecc;">Grab Your Detailed Reports</h4>
          <button class="btn btn-primary me-3" @click="exportQuizAttempts">My Quiz Attempts</button>
          <button class="btn btn-success" @click="downloadReport('subject_performance')">My Subject Insights</button>
          <br />
        </div>
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
  name: 'UserSummary',
  components: { Alert, Navbar },
  setup() {
    const store = useStore();
    return { store };
  },
  data() {
    return {
      alertMessage: '',
      alertType: 'info',
      scoresData: {
        subjects: {},
        chapters: {},
        months: { current: [], previous: [], older: [] },
        total_completed: 0
      },
      charts: {},
    };
  },
  methods: {
    async exportQuizAttempts() {
  try {
    const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
    const response = await axios.post(`${BASE_URL}/dashboard/user/export_quiz_attempts`, {}, config);
    alert(response.data.msg || 'Export job started. Check your email soon!');

  } catch (error) {
    const errorMsg = error.response?.data?.msg || 'Failed to trigger quiz attempts export.';
    alert(errorMsg);
    console.error('Export error:', error);
  }
},
    async fetchScoresData() {
      try {
        const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
        const response = await axios.get(`${BASE_URL}/dashboard/user/scores`, config);
        this.scoresData = response.data;
        this.renderCharts();
      } catch (error) {
        this.handleError(error, 'Oops! Couldn’t load your summary.');
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

      // Your Overall Success Levels (Pie Chart)
      const performanceData = { Outstanding: 0, Good: 0, Pass: 0, Fail: 0 };
      Object.values(this.scoresData.months).flat().forEach(attempt => {
        performanceData[attempt.performance_tag] += 1;
      });
      this.charts.performance = new Chart(this.$refs.performanceChart, {
        type: 'pie',
        data: {
          labels: Object.keys(performanceData),
          datasets: [{
            data: Object.values(performanceData),
            backgroundColor: ['#00c4cc', '#6b48ff', '#ffca28', '#ff5722'],
            hoverOffset: 10
          }]
        },
        options: chartOptions
      });

      // Your Mastery Across Subjects (Bar Chart)
      const subjectScores = {};
      Object.entries(this.scoresData.subjects).forEach(([subject, attempts]) => {
        const avgScore = attempts.reduce((sum, a) => sum + a.score, 0) / attempts.length;
        subjectScores[subject] = avgScore;
      });
      this.charts.subject = new Chart(this.$refs.subjectChart, {
        type: 'bar',
        data: {
          labels: Object.keys(subjectScores),
          datasets: [{
            label: 'Average Score',
            data: Object.values(subjectScores),
            backgroundColor: '#4b2ecc',
            hoverBackgroundColor: '#6b48ff'
          }]
        },
        options: {
          ...chartOptions,
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Average Score' } },
            x: { title: { display: true, text: 'Subjects' } }
          }
        }
      });

      // Your Year-long Engagement (Bar Chart)
      const monthlyData = Array(12).fill(0);
      Object.values(this.scoresData.months).flat().forEach(attempt => {
        if (attempt.month) monthlyData[attempt.month - 1] += 1;
      });
      this.charts.monthly = new Chart(this.$refs.monthlyChart, {
        type: 'bar',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
          datasets: [{
            label: 'Quizzes Taken',
            data: monthlyData,
            backgroundColor: '#6b48ff',
            hoverBackgroundColor: '#7c5aff'
          }]
        },
        options: {
          ...chartOptions,
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Total Quizzes' } },
            x: { title: { display: true, text: 'Month' } }
          }
        }
      });

      // Your Weekly Engagement (Bar Chart)
      const weeklyData = Array(4).fill(0); // Assuming 4 weeks in a month
      Object.values(this.scoresData.months).flat().forEach(attempt => {
        if (attempt.date) {
          const date = new Date(attempt.date);
          const week = Math.floor(date.getDate() / 7); // Simple week calculation (0-3)
          weeklyData[week] += 1;
        }
      });
      this.charts.weekly = new Chart(this.$refs.weeklyChart, {
        type: 'bar',
        data: {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
          datasets: [{
            label: 'Quizzes Taken',
            data: weeklyData,
            backgroundColor: '#00c4cc',
            hoverBackgroundColor: '#00d4dd'
          }]
        },
        options: {
          ...chartOptions,
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Total Quizzes' } },
            x: { title: { display: true, text: 'Weeks' } }
          }
        }
      });

      // Your Activity by Chapter (Bar Chart)
      const chapterCounts = {};
      Object.entries(this.scoresData.chapters).forEach(([chapter, attempts]) => {
        chapterCounts[chapter] = attempts.length;
      });
      this.charts.chapter = new Chart(this.$refs.chapterChart, {
        type: 'bar',
        data: {
          labels: Object.keys(chapterCounts),
          datasets: [{
            label: 'Quizzes Taken',
            data: Object.values(chapterCounts),
            backgroundColor: '#00c4cc',
            hoverBackgroundColor: '#00d4dd'
          }]
        },
        options: {
          ...chartOptions,
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Total Quizzes' } },
            x: { title: { display: true, text: 'Chapters' } }
          }
        }
      });

      // Your Quiz Reattempts (Bar Chart)
      const reattemptData = {};
      Object.values(this.scoresData.months).flat().forEach(attempt => {
        const quizId = attempt.quiz_id;
        reattemptData[quizId] = (reattemptData[quizId] || 0) + 1;
      });
      const topReattemptedQuizzes = Object.entries(reattemptData)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5); // Top 5 most reattempted quizzes
      this.charts.reattempt = new Chart(this.$refs.reattemptChart, {
        type: 'bar',
        data: {
          labels: topReattemptedQuizzes.map(([quizId]) => `Quiz ${quizId}`),
          datasets: [{
            label: 'Reattempt Count',
            data: topReattemptedQuizzes.map(([, count]) => count),
            backgroundColor: '#ff5722',
            hoverBackgroundColor: '#ff7043'
          }]
        },
        options: {
          ...chartOptions,
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Number of Reattempts' } },
            x: { title: { display: true, text: 'Quiz ID' } }
          }
        }
      });

      // Your Overall Time Efficiency (Bar Chart)
      const timeBuckets = { 'Quick (0-60s)': 0, 'Steady (61-120s)': 0, 'Focused (121-180s)': 0, 'Deep Dive (181+s)': 0 };
      Object.values(this.scoresData.months).flat().forEach(attempt => {
        const time = attempt.quiz_meta_data.total_time_taken;
        if (time <= 60) timeBuckets['Quick (0-60s)'] += 1;
        else if (time <= 120) timeBuckets['Steady (61-120s)'] += 1;
        else if (time <= 180) timeBuckets['Focused (121-180s)'] += 1;
        else timeBuckets['Deep Dive (181+s)'] += 1;
      });
      this.charts.time = new Chart(this.$refs.timeChart, {
        type: 'bar',
        data: {
          labels: Object.keys(timeBuckets),
          datasets: [{
            label: 'Quiz Count',
            data: Object.values(timeBuckets),
            backgroundColor: '#ffca28',
            hoverBackgroundColor: '#ffd54f'
          }]
        },
        options: {
          ...chartOptions,
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Total Quizzes' } },
            x: { title: { display: true, text: 'Time Spent' } }
          }
        }
      });

      // Your Speed vs Precision Balance (Pie Chart)
      const allAttempts = Object.values(this.scoresData.months).flat();
      const totalTime = allAttempts.reduce((sum, a) => sum + a.quiz_meta_data.total_time_taken, 0);
      const totalCorrect = allAttempts.reduce((sum, a) => sum + a.quiz_meta_data.total_correct_ans, 0);
      const totalQuestions = allAttempts.reduce((sum, a) => sum + a.quiz_meta_data.total_questions_count, 0);
      const avgTime = totalTime / allAttempts.length;
      const accuracy = (totalCorrect / totalQuestions) * 100;
      const timeVsAccuracyData = {
        'Speed Focus': avgTime,
        'Precision Focus': accuracy
      };
      const normalizedTime = (avgTime / (avgTime + accuracy)) * 100;
      const normalizedAccuracy = (accuracy / (avgTime + accuracy)) * 100;
      this.charts.timeVsAccuracy = new Chart(this.$refs.timeVsAccuracyChart, {
        type: 'pie',
        data: {
          labels: ['Speed Focus', 'Precision Focus'],
          datasets: [{
            data: [normalizedTime, normalizedAccuracy],
            backgroundColor: ['#6b48ff', '#ff5722'],
            hoverOffset: 10
          }]
        },
        options: chartOptions
      });
    },
    async downloadReport(reportType) {
      try {
        let csvContent, filename;
        if (reportType === 'quiz_attempts') {
          csvContent = "Attempt ID,Quiz ID,Score,Time Taken (s),Start Time,Success Level\n";
          Object.values(this.scoresData.months).flat().forEach(attempt => {
            csvContent += `${attempt.attempt_id},${attempt.quiz_id},${attempt.score},${attempt.quiz_meta_data.total_time_taken},${attempt.date},${attempt.performance_tag}\n`;
          });
          filename = `my_quiz_attempts_${new Date().toISOString().split('T')[0]}.csv`;
        } else if (reportType === 'subject_performance') {
          csvContent = "Subject,Average Score\n";
          Object.entries(this.scoresData.subjects).forEach(([subject, attempts]) => {
            const avgScore = attempts.reduce((sum, a) => sum + a.score, 0) / attempts.length;
            csvContent += `${subject},${avgScore.toFixed(2)}\n`;
          });
          filename = `my_subject_insights_${new Date().toISOString().split('T')[0]}.csv`;
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
        this.handleError(error, `Couldn’t download your ${reportType === 'quiz_attempts' ? 'quiz attempts' : 'subject insights'} report.`);
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
    await this.fetchScoresData();
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

@media (max-width: 768px) {
  .chart-card {
    margin-bottom: 20px;
  }

  canvas {
    max-height: 250px;
  }

  .btn-primary, .btn-success {
    width: 100%;
    margin-bottom: 10px;
  }
}

@media (max-width: 576px) {
  .card-title {
    font-size: 1.1rem;
  }

  .btn-primary, .btn-success {
    padding: 8px 15px;
    font-size: 0.9rem;
  }
}
</style>