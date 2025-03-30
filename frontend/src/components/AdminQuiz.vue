<template>
  <div class="container-fluid mt-4">
    <!-- Loader Overlay -->
    <div v-if="isLoading" class="loader-overlay">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <Alert v-if="alertMessage" :message="alertMessage" :type="alertType" @close="alertMessage = ''" />
    <Navbar @search="handleSearch" />

    <div class="row">
      <div class="col-12">
        <div class="quiz-section">
          <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap">
            <button class="btn btn-success btn-sm" @click="openCreateQuizModal">+ Add Quiz</button>
            <div class="sort-controls">
              <label for="sortBy" class="me-2">Sort By:</label>
              <select v-model="sortBy" @change="sortQuizzes" class="form-select d-inline w-auto">
                <option value="subject">Subject</option>
                <option value="chapter">Chapter</option>
                <option value="date">Date</option>
                <option value="difficulty">Difficulty</option>
                <option value="duration">Duration</option>
              </select>
            </div>
          </div>

          <div v-if="filteredQuizzes.length === 0 && !isLoading" class="text-muted text-center py-4">
            No quizzes available. Click "Add Quiz" to get started!
          </div>

          <div class="row">
            <div v-for="(quiz, index) in paginatedQuizzes" :key="quiz.id" class="col-md-6 col-12 mb-4">
              <div class="card quiz-card h-100 shadow-sm">
                <div class="card-header d-flex justify-content-between align-items-center bg-primary text-white">
                  <h5 class="mb-0">
                    Quiz {{ index + currentPage * itemsPerPage + 1 }}
                    ({{ getChapterName(quiz.chapter_id) }}, {{ getSubjectName(quiz.chapter_id) }})
                  </h5>
                  <div>
                    <button class="btn btn-sm btn-info me-2" @click="toggleVisibility(quiz)">
                      {{ quiz.visibility ? 'Hide' : 'Show' }}
                    </button>
                    <button class="btn btn-sm btn-secondary me-2" @click="togglePayment(quiz)">
                      {{ quiz.pay_required ? 'Make Free' : 'Make Paid' }}
                    </button>
                    <button class="btn btn-sm btn-warning me-2" @click="editQuiz(quiz)">Edit</button>
                    <button class="btn btn-sm btn-danger" @click="deleteQuiz(quiz.id)">Delete</button>
                  </div>
                </div>
                <div class="card-body d-flex flex-column">
                  <p class="mb-3 description">
                    <span><strong>Date: </strong>{{ quiz.date_of_quiz || 'Not Set' }}</span>
                    <span v-if="isPastDate(quiz.date_of_quiz)" class="badge bg-danger ms-2">
                      Past Date
                    </span>
                    <span class="ms-2">|</span>
                    <span class="ms-2"><strong>Duration:</strong> <span :class="getDurationClass(quiz.time_duration)">{{ quiz.time_duration }} mins</span></span>
                    <span class="ms-2">|</span>
                    <span class="ms-2"><strong>Difficulty:</strong> <span :class="getDifficultyClass(quiz.overall_difficulty)">{{ quiz.overall_difficulty || 'Not Set' }}</span></span>
                    <span class="ms-2">|</span>
                    <span class="ms-2"><strong>Visibility:</strong> <span :class="quiz.visibility ? 'text-success' : 'text-danger'">{{ quiz.visibility ? 'Visible' : 'Hidden' }}</span></span>
                    <span class="ms-2">|</span>
                    <span class="ms-2"><strong>Payment: </strong> 
                      <span :class="quiz.pay_required ? 'text-warning' : 'text-success'">
                        {{ quiz.pay_required ? `Paid (₹${quiz.pay_amount})` : 'Free' }}
                      </span>
                    </span>
                  </p>

                  <div class="mt-3 flex-grow-1">
                    <h6 class="chapter-title">Questions ({{ quiz.questions.length }})</h6>
                    <div v-if="quiz.questions.length === 0" class="no-chapters text-center py-3">
                      <i class="fas fa-exclamation-circle text-warning"></i>
                      <p>No questions available</p>
                      <button class="btn btn-sm btn-primary" @click="openCreateQuestionModal(quiz.id)">
                        + Add Question
                      </button>
                    </div>
                    <table v-else class="table table-responsive table-striped question-table">
                      <thead>
                        <tr>
                          <th>#</th>
                          <th>Question</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(question, qIndex) in paginatedQuestions(quiz)" :key="question.id" class="question-row">
                          <td>{{ qIndex + 1 + quiz.currentQuestionPage * quiz.itemsPerQuestionPage }}</td>
                          <td>{{ question.question_statement }}</td>
                          <td>
                            <button class="btn btn-sm btn-warning me-2" @click="editQuestion(question)">Edit</button>
                            <button class="btn btn-sm btn-danger" @click="deleteQuestion(question.id)">Delete</button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <nav v-if="totalQuestionPages(quiz) > 1" class="chapter-pagination mt-2">
                      <ul class="pagination pagination-sm justify-content-center">
                        <li class="page-item" :class="{ disabled: quiz.currentQuestionPage === 0 }">
                          <button class="page-link" @click="changeQuestionPage(quiz, quiz.currentQuestionPage - 1)">«</button>
                        </li>
                        <li v-for="page in totalQuestionPages(quiz)" :key="page" class="page-item" :class="{ active: quiz.currentQuestionPage === page - 1 }">
                          <button class="page-link" @click="changeQuestionPage(quiz, page - 1)">{{ page }}</button>
                        </li>
                        <li class="page-item" :class="{ disabled: quiz.currentQuestionPage === totalQuestionPages(quiz) - 1 }">
                          <button class="page-link" @click="changeQuestionPage(quiz, quiz.currentQuestionPage + 1)">»</button>
                        </li>
                      </ul>
                    </nav>
                    <button class="btn btn-sm btn-primary mt-2" @click="openCreateQuestionModal(quiz.id)">
                      + Add Question
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <nav v-if="totalPages > 1" aria-label="Page navigation" class="mt-4">
            <ul class="pagination justify-content-center">
              <li class="page-item" :class="{ disabled: currentPage === 0 }">
                <button class="page-link" @click="currentPage--">Previous</button>
              </li>
              <li v-for="page in totalPages" :key="page" class="page-item" :class="{ active: currentPage === page - 1 }">
                <button class="page-link" @click="currentPage = page - 1">{{ page }}</button>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages - 1 }">
                <button class="page-link" @click="currentPage++">Next</button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>

    <div class="modal fade" id="quizModal" tabindex="-1" aria-labelledby="quizModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title" id="quizModalLabel">{{ modalQuiz.id ? 'Edit Quiz' : 'Add Quiz' }}</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveQuiz">
              <div class="mb-3">
                <label class="form-label">Chapter</label>
                <select v-model="modalQuiz.chapter_id" class="form-select" required>
                  <option v-for="chapter in allChapters" :key="chapter.id" :value="chapter.id">
                    {{ chapter.name }} ({{ getSubjectName(chapter.id) }})
                  </option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Date of Quiz</label>
                <input v-model="modalQuiz.date_of_quiz" type="date" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Duration (mins)</label>
                <input v-model="modalQuiz.time_duration" type="number" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Overall Difficulty</label>
                <select v-model="modalQuiz.overall_difficulty" class="form-select">
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Visibility</label>
                <select v-model="modalQuiz.visibility" class="form-select">
                  <option :value="true">Visible</option>
                  <option :value="false">Hidden</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Payment Required</label>
                <select v-model="modalQuiz.pay_required" class="form-select">
                  <option :value="true">Yes</option>
                  <option :value="false">No</option>
                </select>
              </div>
              <div class="mb-3" v-if="modalQuiz.pay_required">
                <label class="form-label">Payment Amount (₹)</label>
                <input v-model="modalQuiz.pay_amount" type="number" step="0.01" min="0" class="form-control" required />
              </div>
              <button type="submit" class="btn btn-primary w-100">Save</button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="questionModal" tabindex="-1" aria-labelledby="questionModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title" id="questionModalLabel">{{ modalQuestion.id ? 'Edit Question' : 'Add Question' }}</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveQuestion">
              <div class="mb-3">
                <label class="form-label">Question Statement</label>
                <textarea v-model="modalQuestion.question_statement" class="form-control" required></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Option 1</label>
                <input v-model="modalQuestion.option1" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Option 2</label>
                <input v-model="modalQuestion.option2" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Option 3</label>
                <input v-model="modalQuestion.option3" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Option 4</label>
                <input v-model="modalQuestion.option4" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Correct Option</label>
                <select v-model="modalQuestion.correct_option" class="form-select" required>
                  <option value="option1">Option 1</option>
                  <option value="option2">Option 2</option>
                  <option value="option3">Option 3</option>
                  <option value="option4">Option 4</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Difficulty</label>
                <select v-model="modalQuestion.difficulty" class="form-select">
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
              <button type="submit" class="btn btn-primary w-100">Save</button>
            </form>
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
import { Modal } from 'bootstrap';
import { reactive } from 'vue';

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;
// const CURRENT_DATE = new Date().toISOString().split('T')[0];
const CURRENT_DATE = new Date(); 
console.log(CURRENT_DATE);

export default {
  components: { Alert, Navbar },
  setup() {
    const store = useStore();
    return { store };
  },
  data() {
    return {
      subjects: [],
      allChapters: [],
      quizzes: [],
      modalQuiz: { 
        id: null, 
        chapter_id: null, 
        date_of_quiz: '', 
        time_duration: '', 
        overall_difficulty: 'easy', 
        visibility: false,
        pay_required: false,
        pay_amount: 0.0
      },
      modalQuestion: {
        id: null,
        quiz_id: null,
        question_statement: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: '',
        difficulty: 'easy',
      },
      alertMessage: '',
      alertType: 'info',
      quizModal: null,
      questionModal: null,
      sortBy: 'subject',
      searchQuery: '',
      currentPage: 0,
      itemsPerPage: 6,
      isLoading: false,
    };
  },
  computed: {
    filteredQuizzes() {
      let filtered = [...this.quizzes];
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(quiz => {
          const chapter = this.allChapters.find(c => c.id === quiz.chapter_id);
          const subject = this.subjects.find(s => s.id === chapter?.subject_id);
          const visibilityStr = quiz.visibility ? 'visible show' : 'hidden hide';
          const paymentStr = quiz.pay_required ? 'paid' : 'free unpaid';
          return (
            subject?.name.toLowerCase().includes(query) ||
            chapter?.name.toLowerCase().includes(query) ||
            quiz.date_of_quiz?.toLowerCase().includes(query) ||
            quiz.overall_difficulty?.toLowerCase().includes(query) ||
            quiz.time_duration?.toString().includes(query) ||
            visibilityStr.toLowerCase().includes(query) ||
            paymentStr.toLowerCase().includes(query) ||
            quiz.pay_amount?.toString().includes(query)
          );
        });
      }
      return filtered;
    },
    sortedQuizzes() {
      const quizzes = [...this.filteredQuizzes];
      if (this.sortBy === 'subject') {
        return quizzes.sort((a, b) => {
          const subjectA = this.getSubjectName(a.chapter_id);
          const subjectB = this.getSubjectName(b.chapter_id);
          return subjectA.localeCompare(subjectB) || this.getChapterName(a.chapter_id).localeCompare(this.getChapterName(b.chapter_id));
        });
      } else if (this.sortBy === 'chapter') {
        return quizzes.sort((a, b) => this.getChapterName(a.chapter_id).localeCompare(this.getChapterName(b.chapter_id)));
      } else if (this.sortBy === 'date') {
        return quizzes.sort((a, b) => new Date(a.date_of_quiz || '9999-12-31') - new Date(b.date_of_quiz || '9999-12-31'));
      } else if (this.sortBy === 'difficulty') {
        const order = { easy: 1, medium: 2, hard: 3 };
        return quizzes.sort((a, b) => (order[a.overall_difficulty] || 0) - (order[b.overall_difficulty] || 0));
      } else if (this.sortBy === 'duration') {
        return quizzes.sort((a, b) => (a.time_duration || 0) - (b.time_duration || 0));
      }
      return quizzes;
    },
    paginatedQuizzes() {
      const start = this.currentPage * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.sortedQuizzes.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.sortedQuizzes.length / this.itemsPerPage);
    },
  },
  async created() {
    if (!this.store.state.access_token || this.store.state.role !== 'admin') {
      this.$router.push('/login');
      return;
    }
    await this.fetchAllData();
    this.quizModal = new Modal(document.getElementById('quizModal'));
    this.questionModal = new Modal(document.getElementById('questionModal'));
  },
  methods: {
    async fetchAllData() {
      this.isLoading = true;
      try {
        const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
        const response = await axios.get(`${BASE_URL}/admin/all-data`, config);
        const { subjects, chapters, quizzes, questions } = response.data;

        this.subjects = subjects;
        this.allChapters = chapters;
        this.quizzes = quizzes.map(quiz => reactive({
          ...quiz,
          questions: questions.filter(q => q.quiz_id === quiz.id),
          currentQuestionPage: 0,
          itemsPerQuestionPage: 3,
        }));
      } catch (error) {
        this.handleError(error, 'Failed to fetch data');
      } finally {
        this.isLoading = false;
      }
    },
    sortQuizzes() {
      this.currentPage = 0;
    },
    handleSearch(query) {
      this.searchQuery = query;
      this.currentPage = 0;
    },
    openCreateQuizModal() {
      this.modalQuiz = { 
        id: null, 
        chapter_id: this.allChapters[0]?.id || null, 
        date_of_quiz: '', 
        time_duration: '', 
        overall_difficulty: 'easy', 
        visibility: false,
        pay_required: false,
        pay_amount: 0.0
      };
      this.quizModal.show();
    },
    editQuiz(quiz) {
      this.modalQuiz = { ...quiz };
      this.quizModal.show();
    },
    async saveQuiz() {
      try {
        const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
        const quizData = {
          ...this.modalQuiz,
          date_of_quiz: new Date(this.modalQuiz.date_of_quiz).toISOString().split('T')[0],
          pay_amount: parseFloat(this.modalQuiz.pay_amount) || 0.0
        };
        if (this.modalQuiz.id) {
          await axios.put(`${BASE_URL}/quizzes/${this.modalQuiz.id}`, quizData, config);
        } else {
          await axios.post(`${BASE_URL}/chapters/${this.modalQuiz.chapter_id}/quizzes`, quizData, config);
        }
        this.quizModal.hide();
        await this.fetchAllData();
      } catch (error) {
        this.handleError(error, 'Failed to save quiz');
      }
    },
    async deleteQuiz(quizId) {
      const confirmed = window.confirm('Are you sure you want to delete this quiz?');
      if (!confirmed) return;
      try {
        const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
        const response = await axios.delete(`${BASE_URL}/quizzes/${quizId}`, config);
        if (response.status === 200) {
          this.alertMessage = 'Quiz deleted successfully';
          this.alertType = 'success';
          await this.fetchAllData();
        }
      } catch (error) {
        this.handleError(error, 'Failed to delete quiz');
      }
    },
    async toggleVisibility(quiz) {
      try {
        const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
        const response = await axios.patch(`${BASE_URL}/quizzes/${quiz.id}/toggle_visibility`, {}, config);
        if (response.status === 200) {
          this.alertMessage = `Quiz visibility set to ${response.data.visibility ? 'Visible' : 'Hidden'}`;
          this.alertType = 'success';
          await this.fetchAllData();
        }
      } catch (error) {
        this.handleError(error, 'Failed to toggle visibility');
      }
    },
    async togglePayment(quiz) {
      try {
        const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
        const response = await axios.patch(`${BASE_URL}/quizzes/${quiz.id}/toggle_payment`, {}, config);
        if (response.status === 200) {
          this.alertMessage = `Quiz payment status set to ${response.data.pay_required ? 'Paid' : 'Free'}`;
          this.alertType = 'success';
          await this.fetchAllData();
        }
      } catch (error) {
        this.handleError(error, 'Failed to toggle payment status');
      }
    },
    openCreateQuestionModal(quizId) {
      this.modalQuestion = {
        id: null,
        quiz_id: quizId,
        question_statement: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: 'option1',
        difficulty: 'easy',
      };
      this.questionModal.show();
    },
    editQuestion(question) {
      this.modalQuestion = { ...question };
      this.questionModal.show();
    },
    async saveQuestion() {
      try {
        const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
        if (this.modalQuestion.id) {
          await axios.put(`${BASE_URL}/questions/${this.modalQuestion.id}`, this.modalQuestion, config);
        } else {
          await axios.post(`${BASE_URL}/quizzes/${this.modalQuestion.quiz_id}/questions`, this.modalQuestion, config);
        }
        this.questionModal.hide();
        await this.fetchAllData();
      } catch (error) {
        this.handleError(error, 'Failed to save question');
      }
    },
    async deleteQuestion(questionId) {
      const confirmed = window.confirm('Are you sure you want to delete this question?');
      if (!confirmed) return;
      try {
        const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
        const response = await axios.delete(`${BASE_URL}/questions/${questionId}`, config);
        if (response.status === 200) {
          this.alertMessage = 'Question deleted successfully';
          this.alertType = 'success';
          await this.fetchAllData();
        }
      } catch (error) {
        this.handleError(error, 'Failed to delete question');
      }
    },
    getChapterName(chapterId) {
      const chapter = this.allChapters.find(c => c.id === chapterId);
      return chapter ? chapter.name : 'Unknown';
    },
    getSubjectName(chapterId) {
      const chapter = this.allChapters.find(c => c.id === chapterId);
      if (!chapter) return 'Unknown';
      const subject = this.subjects.find(s => s.id === chapter.subject_id);
      return subject ? subject.name : 'Unknown';
    },
    handleError(error, message) {
      console.error(`${message}:`, error);
      this.alertMessage = `${message}: ${error.response?.data.error || error.message}`;
      this.alertType = 'error';
      if (error.response?.status === 401) {
        this.store.commit('clearAuth');
        setTimeout(() => this.$router.push('/login'), 1000);
      }
    },
    isPastDate(date) {
      const currentDateOnly = new Date(CURRENT_DATE.setHours(0, 0, 0, 0));
      const quizDateOnly = new Date(new Date(date).setHours(0, 0, 0, 0));
      return quizDateOnly < currentDateOnly; 
    },
    getDifficultyClass(difficulty) {
      switch (difficulty?.toLowerCase()) {
        case 'easy': return 'text-success';
        case 'medium': return 'text-warning';
        case 'hard': return 'text-danger';
        default: return 'text-muted';
      }
    },
    getDurationClass(duration) {
      if (!duration) return 'text-muted';
      if (duration <= 30) return 'text-primary';
      if (duration <= 60) return 'text-info';
      return 'text-dark';
    },
    paginatedQuestions(quiz) {
      const start = quiz.currentQuestionPage * quiz.itemsPerQuestionPage;
      const end = start + quiz.itemsPerQuestionPage;
      return quiz.questions.slice(start, end);
    },
    totalQuestionPages(quiz) {
      return Math.ceil(quiz.questions.length / quiz.itemsPerQuestionPage);
    },
    changeQuestionPage(quiz, newPage) {
      if (newPage >= 0 && newPage < this.totalQuestionPages(quiz)) {
        quiz.currentQuestionPage = newPage;
      }
    },
  },
};
</script>

<style scoped>
.quiz-section {
  width: 100%;
}

.quiz-card {
  border: none;
  border-radius: 8px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background: #fff;
}

.quiz-card:hover {
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
}

.chapter-title {
  color: #333;
  font-weight: 600;
}

.question-table {
  border: 1px solid #eee;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
}

.question-row {
  transition: background-color 0.2s ease;
}

.question-row:hover {
  background-color: #f8f9fa;
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

.btn-success {
  background: linear-gradient(135deg, #28a745, #1e7e34);
  border: none;
}

.btn-success:hover {
  background: linear-gradient(135deg, #1e7e34, #155724);
}

.btn-primary {
  background: linear-gradient(135deg, #007bff, #0056b3);
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #0056b3, #003d80);
}

.btn-warning {
  background: linear-gradient(135deg, #ffc107, #e0a800);
  border: none;
  color: #212529;
}

.btn-warning:hover {
  background: linear-gradient(135deg, #e0a800, #c69500);
}

.btn-danger {
  background: linear-gradient(135deg, #dc3545, #b02a37);
  border: none;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #b02a37, #911d27);
}

.btn-info {
  background: linear-gradient(135deg, #17a2b8, #117a8b);
  border: none;
}

.btn-info:hover {
  background: linear-gradient(135deg, #117a8b, #0c5d6b);
}

.btn-secondary {
  background: linear-gradient(135deg, #6c757d, #545b62);
  border: none;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #545b62, #3d4449);
}

.pagination .page-link {
  color: #007bff;
  border: none;
  margin: 0 2px;
  border-radius: 4px;
}

.pagination .page-item.active .page-link {
  background: #007bff;
  color: white;
}

.pagination .page-link:hover {
  background: #e9ecef;
}

.chapter-pagination .page-link {
  padding: 4px 10px;
}

.form-select {
  border-radius: 4px;
}

.form-select:focus {
  border-color: #007bff;
  box-shadow: 0 0 8px rgba(0, 123, 255, 0.3);
}

.sort-controls {
  margin-top: 10px;
}

.text-success { color: #28a745 !important; }
.text-warning { color: #e67e22 !important; }
.text-danger { color: #dc3545 !important; }
.text-primary { color: #007bff !important; }
.text-info { color: #17a2b8 !important; }
.text-dark { color: #343a40 !important; }
.text-muted { color: #6c757d !important; }

/* Loader Styles */
.loader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .card-header div {
    margin-top: 10px;
  }

  .question-row td {
    padding: 8px;
  }

  .sort-controls {
    width: 100%;
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

  .pagination {
    flex-wrap: wrap;
  }
}
</style>

