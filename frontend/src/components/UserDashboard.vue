<template>
  <div class="container-fluid mt-3 mt-md-5">
    <Navbar :cart-count="cartCount" @search="handleSearch" />
    <Alert v-if="alertMessage" :message="alertMessage" :type="alertType" @close="alertMessage = ''" />

    <!-- Loading Spinner -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Quiz Sections with Pagination -->
    <div class="row g-3 g-md-4" v-if="!loading">
      <QuizSection title="Today's Paid Quizzes" bg-class="bg-warning" :quizzes="paginatedTodayPaidQuizzes"
        :total-items="filteredTodayPaidQuizzes.length" :current-page="todayPaidPage" @page-change="page => todayPaidPage = page"
        @view-metadata="showQuizMetadata" @start-quiz="startQuiz" @add-to-cart="addToCart" />
      <QuizSection title="Today's Free Quizzes" bg-class="bg-success" :quizzes="paginatedTodayFreeQuizzes"
        :total-items="filteredTodayFreeQuizzes.length" :current-page="todayFreePage" @page-change="page => todayFreePage = page"
        @view-metadata="showQuizMetadata" @start-quiz="startQuiz" />
      <QuizSection title="Practice Quizzes" bg-class="bg-info" :quizzes="paginatedPracticeQuizzes"
        :total-items="filteredPracticeQuizzes.length" :current-page="practicePage" @page-change="page => practicePage = page"
        @view-metadata="showQuizMetadata" @start-quiz="startQuiz" />
      <QuizSection title="Upcoming Paid Quizzes" bg-class="bg-primary" :quizzes="paginatedUpcomingPaidQuizzes"
        :total-items="filteredUpcomingPaidQuizzes.length" :current-page="upcomingPaidPage" @page-change="page => upcomingPaidPage = page"
        @view-metadata="showQuizMetadata" @add-to-cart="addToCart" />
      <QuizSection title="Upcoming Free Quizzes" bg-class="bg-secondary" :quizzes="paginatedUpcomingFreeQuizzes"
        :total-items="filteredUpcomingFreeQuizzes.length" :current-page="upcomingFreePage" @page-change="page => upcomingFreePage = page"
        @view-metadata="showQuizMetadata" />
      <QuizSection title="Purchased Quizzes" bg-class="bg-success" :quizzes="paginatedPurchasedQuizzes"
        :total-items="filteredPurchasedQuizzes.length" :current-page="purchasedPage" @page-change="page => purchasedPage = page"
        @view-metadata="showQuizMetadata" @start-quiz="startQuiz" />
      <QuizSection title="Not Purchased Quizzes" bg-class="bg-danger" :quizzes="paginatedNotPurchasedQuizzes"
        :total-items="filteredNotPurchasedQuizzes.length" :current-page="notPurchasedPage" @page-change="page => notPurchasedPage = page"
        @view-metadata="showQuizMetadata" @add-to-cart="addToCart" />
    </div>

    <!-- Quiz Metadata Modal -->
    <div class="modal fade" :class="{ 'show d-block': showModal }" tabindex="-1" role="dialog">
      <div class="modal-dialog" role="document">
        <div class="modal-content subject-card">
          <div class="modal-header card-header bg-info text-white">
            <h5 class="modal-title">Quiz Metadata</h5>
            <button type="button" class="btn-close" @click="showModal = false"></button>
          </div>
          <div class="modal-body card-body">
            <p><strong>ID:</strong> {{ metadata.quiz_id }}</p>
            <p><strong>Subject:</strong> {{ metadata.subject }}</p>
            <p><strong>Chapter:</strong> {{ metadata.chapter }}</p>
            <p><strong>Questions:</strong> {{ metadata.number_of_questions }}</p>
            <p><strong>Date:</strong> {{ metadata.date }}</p>
            <p><strong>Duration:</strong> {{ metadata.duration }}</p>
            <p><strong>Difficulty:</strong> {{ metadata.overall_difficulty }}</p> <!-- Changed from difficulty -->
            <p><strong>Price:</strong> ${{ metadata.pay_amount || '0.00' }}</p> <!-- Changed from price -->
            <p v-if="metadata.in_cart" class="text-success fw-bold">In Cart - Go to Cart</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showModal = false">Close</button>
            <button v-if="metadata.date <= today" class="btn btn-success" @click="startQuiz(metadata.quiz_id)">Start Quiz</button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade" :class="{ 'show': showModal }" v-if="showModal" @click="showModal = false"></div>
  </div>
</template>

<script>
import axios from 'axios';
import Alert from '@/components/Alert.vue';
import Navbar from '@/components/Navbar.vue';
import QuizSection from '@/components/QuizSection.vue';
import { useStore } from 'vuex';

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

export default {
  components: { Alert, Navbar, QuizSection },
  setup() {
    const store = useStore();
    return { store };
  },
  data() {
    return {
      alertMessage: '',
      alertType: 'info',
      loading: true,
      searchQuery: '',
      username: '',
      allQuizzes: [],
      cartCount: 0,
      showModal: false,
      metadata: {},
      today: new Date().toISOString().split('T')[0],
      itemsPerPage: 6, // Number of quizzes per page
      todayPaidPage: 1,
      todayFreePage: 1,
      practicePage: 1,
      upcomingPaidPage: 1,
      upcomingFreePage: 1,
      purchasedPage: 1,
      notPurchasedPage: 1,
    };
  },
  computed: {
    filteredTodayPaidQuizzes() {
      const filtered = this.allQuizzes.filter(q => q.date === this.today && q.pay_required);
      return this.sortByPurchased(filtered);
    },
    filteredTodayFreeQuizzes() {
      return this.filterQuizzes(this.allQuizzes.filter(q => q.date === this.today && !q.pay_required));
    },
    filteredPracticeQuizzes() {
      return this.filterQuizzes(this.allQuizzes.filter(q => q.date < this.today));
    },
    filteredUpcomingPaidQuizzes() {
      return this.filterQuizzes(this.allQuizzes.filter(q => q.date > this.today && q.pay_required));
    },
    filteredUpcomingFreeQuizzes() {
      return this.filterQuizzes(this.allQuizzes.filter(q => q.date > this.today && !q.pay_required));
    },
    filteredPurchasedQuizzes() {
      return this.filterQuizzes(this.allQuizzes.filter(q => q.pay_required && q.paid));
    },
    filteredNotPurchasedQuizzes() {
      return this.filterQuizzes(this.allQuizzes.filter(q => q.pay_required && !q.paid));
    },
    paginatedTodayPaidQuizzes() {
      return this.paginate(this.filteredTodayPaidQuizzes, this.todayPaidPage);
    },
    paginatedTodayFreeQuizzes() {
      return this.paginate(this.filteredTodayFreeQuizzes, this.todayFreePage);
    },
    paginatedPracticeQuizzes() {
      return this.paginate(this.filteredPracticeQuizzes, this.practicePage);
    },
    paginatedUpcomingPaidQuizzes() {
      return this.paginate(this.filteredUpcomingPaidQuizzes, this.upcomingPaidPage);
    },
    paginatedUpcomingFreeQuizzes() {
      return this.paginate(this.filteredUpcomingFreeQuizzes, this.upcomingFreePage);
    },
    paginatedPurchasedQuizzes() {
      return this.paginate(this.filteredPurchasedQuizzes, this.purchasedPage);
    },
    paginatedNotPurchasedQuizzes() {
      return this.paginate(this.filteredNotPurchasedQuizzes, this.notPurchasedPage);
    },
  },
  async created() {
    const access_token = this.store.state.access_token;
    const role = this.store.state.role;

    if (!access_token || role !== 'user') {
      this.$router.push('/login');
      return;
    }

    try {
      const dashboardResponse = await axios.get(`${BASE_URL}/dashboard/user`, {
        headers: { Authorization: `Bearer ${access_token}` },
      });
      this.username = dashboardResponse.data.msg.split(' ')[1];
      await this.fetchQuizzes(access_token);
    } catch (error) {
      if (error.response?.status === 401) {
        this.alertMessage = 'Session expired. Redirecting to login...';
        this.alertType = 'warning';
        setTimeout(() => this.$router.push('/login'), 1000);
      } else {
        this.alertMessage = 'Failed to load dashboard or quizzes.';
        this.alertType = 'error';
      }
      this.store.commit('clearAuth');
    }
  },
  methods: {
    async fetchQuizzes(access_token) {
      try {
        const response = await axios.get(`${BASE_URL}/dashboard/user/quizzes`, {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        this.allQuizzes = response.data.quizzes;
        this.cartCount = response.data.cart_count;
      } catch (error) {
        throw error;
      } finally {
        setTimeout(() => (this.loading = false), 500);
      }
    },
    handleSearch(query) {
      this.searchQuery = query;
      // Reset pagination to page 1 when search changes
      this.todayPaidPage = 1;
      this.todayFreePage = 1;
      this.practicePage = 1;
      this.upcomingPaidPage = 1;
      this.upcomingFreePage = 1;
      this.purchasedPage = 1;
      this.notPurchasedPage = 1;
    },
    filterQuizzes(quizzes) {
      if (!this.searchQuery) return quizzes;
      const query = this.searchQuery.toLowerCase();
      return quizzes.filter(q =>
        q.quiz_id.toString().includes(query) ||
        q.subject.toLowerCase().includes(query) ||
        q.chapter.toLowerCase().includes(query) ||
        q.date.includes(query) ||
        q.duration.toLowerCase().includes(query) ||
        (q.paid ? 'purchased' : 'not purchased').includes(query) ||
        (q.in_cart ? 'cart' : '').includes(query)
      );
    },
    sortByPurchased(quizzes) {
      return quizzes.sort((a, b) => b.paid - a.paid);
    },
    paginate(quizzes, page) {
      const start = (page - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return quizzes.slice(start, end);
    },
    async showQuizMetadata(quizId) {
      try {
        const response = await axios.get(`${BASE_URL}/dashboard/user/quiz/${quizId}/metadata`, {
          headers: { Authorization: `Bearer ${this.store.state.access_token}` },
        });
        this.metadata = response.data.quiz_metadata;
        this.showModal = true;
      } catch (error) {
        this.alertMessage = error.response?.data.msg || 'Failed to load quiz metadata.';
        this.alertType = 'error';
      }
    },
    async addToCart(quizId) {
      try {
        const response = await axios.post(`${BASE_URL}/dashboard/user/quiz/${quizId}/add-to-cart`, {}, {
          headers: { Authorization: `Bearer ${this.store.state.access_token}` },
        });
        this.alertMessage = response.data.msg;
        this.alertType = 'success';
        await this.fetchQuizzes(this.store.state.access_token);
      } catch (error) {
        this.alertMessage = error.response?.data.msg || 'Failed to add to cart.';
        this.alertType = 'error';
      }
    },
    
    async startQuiz(quizId) {
      try {
        const response = await axios.post(`${BASE_URL}/dashboard/user/quiz/${quizId}/open_instructions`, {}, {
          headers: { Authorization: `Bearer ${this.store.state.access_token}` },
        });
        const { quiz_attempt_id, access_token, duration_minutes } = response.data;
        this.showModal = false;
        this.$router.push({
          path: `/quiz/${quizId}/attempt/${quiz_attempt_id}/instructions`,
          query: { access_token, duration: duration_minutes },
        });
      } catch (error) {
        this.alertMessage = error.response?.data.msg || 'Failed to open instructions quiz.';
        this.alertType = 'error';
      }
    },
  },
};
</script>

<style scoped>
.container-fluid {
  padding: 0 15px;
}

.subject-card {
  border: none;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.subject-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.card-header {
  border-radius: 8px 8px 0 0;
  padding: 10px 15px;
}

.card-body {
  padding: 15px;
}

.btn {
  border-radius: 4px;
  padding: 5px 10px;
  font-weight: 500;
}

.btn-primary { background: linear-gradient(135deg, #007bff, #0056b3); border: none; color: #fff; }
.btn-primary:hover { background: linear-gradient(135deg, #0056b3, #003d80); }
.btn-success { background: linear-gradient(135deg, #28a745, #1e7e34); border: none; color: #fff; }
.btn-success:hover { background: linear-gradient(135deg, #1e7e34, #155724); }
.btn-warning { background: linear-gradient(135deg, #ffc107, #e0a800); border: none; color: #212529; }
.btn-warning:hover { background: linear-gradient(135deg, #e0a800, #c69500); }
.btn-secondary { background: linear-gradient(135deg, #6c757d, #5a6268); border: none; color: #fff; }
.btn-secondary:hover { background: linear-gradient(135deg, #5a6268, #495057); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }

.no-quizzes {
  background: #fff3e0;
  color: #e67e22;
  padding: 15px;
  text-align: center;
}

@media (max-width: 767px) {
  .container-fluid { padding: 0 10px; }
  .card-body { padding: 10px; }
  .btn { padding: 4px 8px; font-size: 0.85rem; }
}

.modal.show .modal-dialog { transform: translate(0, 0); }
.modal-backdrop.show { opacity: 0.5; }
</style>