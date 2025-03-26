<template>
  <div class="container-fluid mt-5">
    <Alert v-if="alertMessage" :message="alertMessage" :type="alertType" @close="alertMessage = ''" />
    <Navbar @search="handleSearch" />

    <div class="row mt-4">
      <div class="col-12 mt-3">
        <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap">
          <button class="btn btn-primary" @click="openCreateSubjectModal">+ Add Subject</button>
          <div class="sort-controls">
            <label for="sortBy" class="me-2">Sort Subjects By:</label>
            <select v-model="sortBy" @change="sortSubjects" class="form-select d-inline w-auto">
              <option value="name">Name</option>
              <option value="chapters">Chapter Count</option>
              <option value="questions">Total Questions</option>
            </select>
          </div>
        </div>

        <div v-if="paginatedSubjects.length === 0" class="text-muted text-center py-4">
          No subjects available. Click "Add Subject" to get started!
        </div>

        <div class="row">
          <div v-for="subject in paginatedSubjects" :key="subject.id" class="col-12 col-md-6 col-lg-4 mb-4">
            <div class="card shadow-sm h-100 subject-card">
              <div class="card-header d-flex justify-content-between align-items-center bg-primary text-white">
                <h5 class="mb-0">{{ subject.name }}</h5>
                <div>
                  <button class="btn btn-sm btn-warning me-2" @click="openEditSubjectModal(subject)">Edit</button>
                  <button class="btn btn-sm btn-danger" @click="deleteSubject(subject.id)">Delete</button>
                </div>
              </div>
              <div class="card-body d-flex flex-column">
                <p class="description">{{ subject.description || 'No description available' }}</p>

                <div class="mt-3 flex-grow-1">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="chapter-title">Chapters ({{ subject.chapters.length }})</h6>
                    <button class="btn btn-sm btn-primary" @click="openCreateChapterModal(subject.id)">+ Add Chapter</button>
                  </div>

                  <div v-if="subject.chapters.length === 0" class="no-chapters text-center py-3">
                    <i class="fas fa-exclamation-circle text-warning"></i>
                    <p>No chapters available</p>
                    <div>
                      <button class="btn btn-sm btn-primary me-2" @click="openCreateChapterModal(subject.id)">Add Chapter</button>
                    </div>
                  </div>

                  <ul class="list-group chapter-list" v-else>
                    <li v-for="chapter in paginatedChapters(subject)" :key="chapter.id" class="list-group-item chapter-item">
                      <div class="d-flex justify-content-between align-items-center flex-wrap">
                        <div class="chapter-info">
                          <strong>{{ chapter.name }}</strong>
                          <span class="badge bg-info ms-2">{{ chapter.questionsCount }} Questions</span>
                          <span v-if="chapter.questionsCount === 0" class="badge bg-warning ms-2">No Questions</span>
                        </div>
                        <div class="chapter-actions">
                          <button class="btn btn-sm btn-warning me-2" @click="openEditChapterModal(chapter)">Edit</button>
                          <button class="btn btn-sm btn-danger" @click="deleteChapter(chapter.id)">Delete</button>
                        </div>
                      </div>
                    </li>
                  </ul>

                  <nav v-if="chapterTotalPages(subject) > 1" class="chapter-pagination mt-2">
                    <ul class="pagination pagination-sm justify-content-center">
                      <li class="page-item" :class="{ disabled: chapterPages[subject.id] === 0 }">
                        <button class="page-link" @click="chapterPages[subject.id]--">&laquo;</button>
                      </li>
                      <li v-for="page in chapterTotalPages(subject)" :key="page" class="page-item" :class="{ active: chapterPages[subject.id] === page - 1 }">
                        <button class="page-link" @click="chapterPages[subject.id] = page - 1">{{ page }}</button>
                      </li>
                      <li class="page-item" :class="{ disabled: chapterPages[subject.id] === chapterTotalPages(subject) - 1 }">
                        <button class="page-link" @click="chapterPages[subject.id]++">&raquo;</button>
                      </li>
                    </ul>
                  </nav>
                </div>
              </div>
            </div>
          </div>
        </div>

        <nav v-if="totalPages > 1" aria-label="Subject navigation" class="mt-4">
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

    <!-- Subject Modal -->
    <div class="modal fade" id="subjectModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">{{ isEditMode ? 'Edit Subject' : 'Create Subject' }}</h5>
            <button type="button" class="btn-close btn-close-white" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveSubject">
              <div class="mb-3">
                <label for="subjectName" class="form-label">Name</label>
                <input v-model="subjectForm.name" type="text" class="form-control" id="subjectName" required>
              </div>
              <div class="mb-3">
                <label for="subjectDescription" class="form-label">Description</label>
                <textarea v-model="subjectForm.description" class="form-control" id="subjectDescription"></textarea>
              </div>
              <button type="submit" class="btn btn-primary w-100">{{ isEditMode ? 'Update' : 'Create' }}</button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Chapter Modal -->
    <div class="modal fade" id="chapterModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">{{ isEditMode ? 'Edit Chapter' : 'Create Chapter' }}</h5>
            <button type="button" class="btn-close btn-close-white" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveChapter">
              <div class="mb-3">
                <label for="chapterName" class="form-label">Name</label>
                <input v-model="chapterForm.name" type="text" class="form-control" id="chapterName" required>
              </div>
              <div class="mb-3">
                <label for="chapterDescription" class="form-label">Description</label>
                <textarea v-model="chapterForm.description" class="form-control" id="chapterDescription"></textarea>
              </div>
              <button type="submit" class="btn btn-primary w-100">{{ isEditMode ? 'Update' : 'Create' }}</button>
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
import bootstrap from 'bootstrap/dist/js/bootstrap.bundle.min.js';

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
      subjects: [],
      searchQuery: '',
      subjectForm: { id: null, name: '', description: '' },
      chapterForm: { id: null, subject_id: null, name: '', description: '' },
      isEditMode: false,
      sortBy: 'name',
      currentPage: 0,
      itemsPerPage: 6,
      chapterItemsPerPage: 3,
      chapterPages: {},
    };
  },
  computed: {
    filteredSubjects() {
      let filtered = [...this.subjects];
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(subject =>
          subject.name.toLowerCase().includes(query) ||
          subject.description?.toLowerCase().includes(query) ||
          subject.chapters.some(chapter =>
            chapter.name.toLowerCase().includes(query) ||
            chapter.description?.toLowerCase().includes(query) ||
            chapter.questionsCount.toString().includes(query)
          )
        );
      }
      return filtered;
    },
    sortedSubjects() {
      const subjects = [...this.filteredSubjects];
      if (this.sortBy === 'name') {
        return subjects.sort((a, b) => a.name.localeCompare(b.name));
      } else if (this.sortBy === 'chapters') {
        return subjects.sort((a, b) => b.chapters.length - a.chapters.length);
      } else if (this.sortBy === 'questions') {
        return subjects.sort((a, b) => {
          const aQuestions = a.chapters.reduce((sum, ch) => sum + ch.questionsCount, 0);
          const bQuestions = b.chapters.reduce((sum, ch) => sum + ch.questionsCount, 0);
          return bQuestions - aQuestions;
        });
      }
      return subjects;
    },
    paginatedSubjects() {
      const start = this.currentPage * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.sortedSubjects.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.sortedSubjects.length / this.itemsPerPage);
    },
  },
  methods: {
    async fetchAllData() {
      try {
        const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
        const response = await axios.get(`${BASE_URL}/admin/all-data`, config);
        const { subjects, chapters, questions } = response.data;

        this.subjects = subjects.map(subject => {
          const subjectChapters = chapters.filter(chapter => chapter.subject_id === subject.id).map(chapter => ({
            ...chapter,
            questionsCount: questions.filter(q => {
              const quiz = response.data.quizzes.find(quiz => quiz.id === q.quiz_id);
              return quiz && quiz.chapter_id === chapter.id;
            }).length,
          }));
          return { ...subject, chapters: subjectChapters };
        });
        this.subjects.forEach(subject => {
          this.chapterPages[subject.id] = this.chapterPages[subject.id] || 0;
        });
      } catch (error) {
        this.handleError(error, 'Failed to load data');
      }
    },
    paginatedChapters(subject) {
      const start = (this.chapterPages[subject.id] || 0) * this.chapterItemsPerPage;
      const end = start + this.chapterItemsPerPage;
      return subject.chapters.slice(start, end);
    },
    chapterTotalPages(subject) {
      return Math.ceil(subject.chapters.length / this.chapterItemsPerPage);
    },
    handleSearch(query) {
      this.searchQuery = query;
      this.currentPage = 0;
      this.subjects.forEach(subject => this.chapterPages[subject.id] = 0);
    },
    sortSubjects() {
      this.currentPage = 0;
    },
    openCreateSubjectModal() {
      this.isEditMode = false;
      this.subjectForm = { id: null, name: '', description: '' };
      new bootstrap.Modal(document.getElementById('subjectModal')).show();
    },
    openEditSubjectModal(subject) {
      this.isEditMode = true;
      this.subjectForm = { ...subject };
      new bootstrap.Modal(document.getElementById('subjectModal')).show();
    },
    openCreateChapterModal(subjectId) {
      this.isEditMode = false;
      this.chapterForm = { id: null, subject_id: subjectId, name: '', description: '' };
      new bootstrap.Modal(document.getElementById('chapterModal')).show();
    },
    openEditChapterModal(chapter) {
      this.isEditMode = true;
      this.chapterForm = { ...chapter };
      new bootstrap.Modal(document.getElementById('chapterModal')).show();
    },
    closeModal() {
      bootstrap.Modal.getInstance(document.getElementById('subjectModal'))?.hide();
      bootstrap.Modal.getInstance(document.getElementById('chapterModal'))?.hide();
    },
    async saveSubject() {
      try {
        const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
        const url = this.isEditMode ? `${BASE_URL}/subjects/${this.subjectForm.id}` : `${BASE_URL}/subjects`;
        const method = this.isEditMode ? 'put' : 'post';
        await axios[method](url, this.subjectForm, config);
        this.alertMessage = `Subject ${this.isEditMode ? 'updated' : 'created'} successfully!`;
        this.alertType = 'success';
        await this.fetchAllData();
        this.closeModal();
      } catch (error) {
        this.handleError(error, `Failed to ${this.isEditMode ? 'update' : 'create'} subject`);
      }
    },
    async saveChapter() {
      try {
        const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
        const url = this.isEditMode ? `${BASE_URL}/chapters/${this.chapterForm.id}` : `${BASE_URL}/subjects/${this.chapterForm.subject_id}/chapters`;
        const method = this.isEditMode ? 'put' : 'post';
        await axios[method](url, this.chapterForm, config);
        this.alertMessage = `Chapter ${this.isEditMode ? 'updated' : 'created'} successfully!`;
        this.alertType = 'success';
        await this.fetchAllData();
        this.closeModal();
      } catch (error) {
        this.handleError(error, `Failed to ${this.isEditMode ? 'update' : 'create'} chapter`);
      }
    },
    async deleteSubject(subjectId) {
      if (confirm('Are you sure you want to delete this subject?')) {
        try {
          const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
          await axios.delete(`${BASE_URL}/subjects/${subjectId}`, config);
          this.alertMessage = 'Subject deleted successfully!';
          this.alertType = 'success';
          await this.fetchAllData();
        } catch (error) {
          this.handleError(error, 'Failed to delete subject');
        }
      }
    },
    async deleteChapter(chapterId) {
      if (confirm('Are you sure you want to delete this chapter?')) {
        try {
          const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
          await axios.delete(`${BASE_URL}/chapters/${chapterId}`, config);
          this.alertMessage = 'Chapter deleted successfully!';
          this.alertType = 'success';
          await this.fetchAllData();
        } catch (error) {
          this.handleError(error, 'Failed to delete chapter');
        }
      }
    },
    handleError(error, defaultMsg) {
      this.alertMessage = error.response?.data?.error || defaultMsg;
      this.alertType = 'error';
      if (error.response?.status === 401) {
        this.store.commit('clearAuth');
        setTimeout(() => this.$router.push('/login'), 1000);
      }
    },
  },
  async created() {
    const access_token = this.store.state.access_token;
    const role = this.store.state.role;

    if (!access_token || role !== 'admin') {
      this.$router.push('/login');
      return;
    }

    await this.fetchAllData();
  },
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

  .chapter-actions {
    margin-top: 10px;
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