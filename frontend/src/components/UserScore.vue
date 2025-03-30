<template>
  <div class="container-fluid mt-5">
    <Alert v-if="alertMessage" :message="alertMessage" :type="alertType" @close="alertMessage = ''" />
    <Navbar @search="handleSearch" />

    <div class="row mt-4">
      <div class="col-12 mt-3">
        <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap">
          <div class="sort-controls">
            <label for="sortBy" class="me-2">Sort By:</label>
            <select v-model="sortBy" @change="sortData" class="form-select d-inline w-auto">
              <option value="subject">Subject</option>
              <option value="chapter">Chapter</option>
              <option value="date">Date</option>
              <option value="score">Score</option>
              <option value="performance">Performance</option>
            </select>
          </div>
          <button class="btn btn-sm btn-success" @click="downloadAll">Download All Data</button>
        </div>

        <div v-if="Object.keys(scores.subjects).length === 0" class="text-muted text-center py-4">
          No quiz scores available yet!
        </div>

        <!-- Subjects Cluster -->
        <div class="accordion mb-4" id="subjectsAccordion">
          <div v-for="(subjectData, subject) in paginatedSubjects" :key="subject" class="accordion-item">
            <h2 class="accordion-header subject-header" :id="'heading-' + subject">
              <div class="d-flex justify-content-between align-items-center w-100">
                <button class="accordion-button flex-grow-1" type="button" data-bs-toggle="collapse" :data-bs-target="'#collapse-' + subject" aria-expanded="true" :aria-controls="'collapse-' + subject">
                  {{ subject }} ({{ subjectData.length }} Attempts)
                </button>
                <button class="btn btn-sm btn-success ms-2 me-2" @click="downloadSubject(subject, subjectData)">Download</button>
              </div>
            </h2>
            <div :id="'collapse-' + subject" class="accordion-collapse collapse show" :aria-labelledby="'heading-' + subject" data-bs-parent="#subjectsAccordion">
              <div class="accordion-body">
                <div class="chapter-list">
                  <div v-for="(chapterData, chapter) in groupByChapter(subjectData)" :key="chapter" class="chapter-item">
                    <h6 class="chapter-header d-flex justify-content-between align-items-center">
                      <span>{{ chapter }}</span>
                      <button class="btn btn-sm btn-success ms-2" @click="downloadChapter(subject, chapter, chapterData)">Download</button>
                    </h6>
                    <div class="row">
                      <div v-for="attempt in paginatedChapterQuizzes(chapterData)" :key="attempt.attempt_id" class="col-md-6 col-12 mb-3 mx-auto">
                        <div class="card quiz-card" :class="getPerformanceClass(attempt.performance_tag)">
                          <div class="card-body">
                            <p><strong>Quiz ID:</strong> {{ attempt.quiz_id }} | <strong>Attempts:</strong> <span class="badge bg-info">{{ attempt.total_attempts }}</span></p>
                            <p><strong>Performance:</strong> <span :class="['badge', getPerformanceClass(attempt.performance_tag)]">{{ attempt.performance_tag }}</span> | <strong>Score:</strong> {{ attempt.score }} / {{ attempt.full_score }}</p>
                            <p><strong>Date:</strong> {{ formatDate(attempt.date) }}</p>
                            <div class="d-flex justify-content-end">
                              <button class="btn btn-sm btn-info me-2" @click="openInfoModal(attempt)">i</button>
                              <button v-if="attempt.total_attempts > 1" class="btn btn-sm btn-primary me-2" @click="openAttemptsModal(attempt.quiz_id)">Previous Attempts</button>
                              <button class="btn btn-sm btn-success" @click="downloadLatestAttempt(attempt)">Download Latest</button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <nav v-if="chapterTotalPages(chapterData) > 1" class="mt-3">
                      <ul class="pagination justify-content-center">
                        <li class="page-item" :class="{ disabled: chapterPages[chapter] === 0 }">
                          <button class="page-link" @click="chapterPages[chapter]--">«</button>
                        </li>
                        <li v-for="page in chapterTotalPages(chapterData)" :key="page" class="page-item" :class="{ active: chapterPages[chapter] === page - 1 }">
                          <button class="page-link" @click="chapterPages[chapter] = page - 1">{{ page }}</button>
                        </li>
                        <li class="page-item" :class="{ disabled: chapterPages[chapter] === chapterTotalPages(chapterData) - 1 }">
                          <button class="page-link" @click="chapterPages[chapter]++">»</button>
                        </li>
                      </ul>
                    </nav>
                  </div>
                </div>
                <nav v-if="subjectTotalPages > 1" class="mt-3">
                  <ul class="pagination justify-content-center">
                    <li class="page-item" :class="{ disabled: currentPage === 0 }">
                      <button class="page-link" @click="currentPage--">«</button>
                    </li>
                    <li v-for="page in subjectTotalPages" :key="page" class="page-item" :class="{ active: currentPage === page - 1 }">
                      <button class="page-link" @click="currentPage = page - 1">{{ page }}</button>
                    </li>
                    <li class="page-item" :class="{ disabled: currentPage === subjectTotalPages - 1 }">
                      <button class="page-link" @click="currentPage++">»</button>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </div>

        <!-- Months Cluster -->
        <div class="accordion mb-4" id="monthsAccordion">
          <div v-for="(monthData, month) in validMonths" :key="month" class="accordion-item">
            <h2 class="accordion-header month-header" :id="'heading-' + month">
              <div class="d-flex justify-content-between align-items-center w-100">
                <button class="accordion-button flex-grow-1" type="button" data-bs-toggle="collapse" :data-bs-target="'#collapse-' + month" aria-expanded="true" :aria-controls="'collapse-' + month">
                  {{ capitalize(month) }} Month ({{ monthData.length }} Attempts)
                </button>
                <button class="btn btn-sm btn-success ms-2 me-2" @click="downloadMonth(month, monthData)">Download</button>
              </div>
            </h2>
            <div :id="'collapse-' + month" class="accordion-collapse collapse show" :aria-labelledby="'heading-' + month" data-bs-parent="#monthsAccordion">
              <div class="accordion-body">
                <div class="row">
                  <div v-for="attempt in paginatedMonthQuizzes(month)" :key="attempt.attempt_id" class="col-md-6 col-12 mb-3 mx-auto">
                    <div class="card quiz-card" :class="getPerformanceClass(attempt.performance_tag)">
                      <div class="card-body">
                        <p><strong>Quiz ID:</strong> {{ attempt.quiz_id }} | <strong>Attempts:</strong> <span class="badge bg-info">{{ attempt.total_attempts }}</span></p>
                        <p><strong>Performance:</strong> <span :class="['badge', getPerformanceClass(attempt.performance_tag)]">{{ attempt.performance_tag }}</span> | <strong>Score:</strong> {{ attempt.score }} / {{ attempt.full_score }}</p>
                        <p><strong>Subject:</strong> {{ attempt.subject }} | <strong>Chapter:</strong> {{ attempt.chapter }}</p>
                        <p><strong>Date:</strong> {{ formatDate(attempt.date) }}</p>
                        <div class="d-flex justify-content-end">
                          <button class="btn btn-sm btn-info me-2" @click="openInfoModal(attempt)">i</button>
                          <button v-if="attempt.total_attempts > 1" class="btn btn-sm btn-primary me-2" @click="openAttemptsModal(attempt.quiz_id)">Previous Attempts</button>
                          <button class="btn btn-sm btn-success" @click="downloadLatestAttempt(attempt)">Download Latest</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <nav v-if="monthTotalPages(month) > 1" class="mt-3">
                  <ul class="pagination justify-content-center">
                    <li class="page-item" :class="{ disabled: monthPages[month] === 0 }">
                      <button class="page-link" @click="monthPages[month]--">«</button>
                    </li>
                    <li v-for="page in monthTotalPages(month)" :key="page" class="page-item" :class="{ active: monthPages[month] === page - 1 }">
                      <button class="page-link" @click="monthPages[month] = page - 1">{{ page }}</button>
                    </li>
                    <li class="page-item" :class="{ disabled: monthPages[month] === monthTotalPages(month) - 1 }">
                      <button class="page-link" @click="monthPages[month]++">»</button>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Info Modal -->
    <div class="modal fade" id="infoModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-info text-white">
            <h5 class="modal-title">Current Attempt Details (Quiz ID: {{ selectedAttempt?.quiz_id }})</h5>
            <button type="button" class="btn-close btn-close-white" @click="closeModal('infoModal')"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedAttempt">
              <p><strong>Total Questions:</strong> {{ selectedAttempt.quiz_meta_data.total_questions_count }}</p>
              <p><strong>Full Score:</strong> {{ selectedAttempt.quiz_meta_data.full_score }}</p>
              <p><strong>Attempted Questions:</strong> {{ selectedAttempt.quiz_meta_data.total_attempted_qn }}</p>
              <p><strong>Correct Answers:</strong> {{ selectedAttempt.quiz_meta_data.total_correct_ans }}</p>
              <p><strong>Wrong Answers:</strong> {{ selectedAttempt.quiz_meta_data.total_wrong_ans }}</p>
              <p><strong>Score Earned:</strong> {{ selectedAttempt.quiz_meta_data.total_score_earned }}</p>
              <p><strong>Marked for Review:</strong> {{ selectedAttempt.quiz_meta_data.total_marked_for_review_qn }}</p>
              <p><strong>Skipped Questions:</strong> {{ selectedAttempt.quiz_meta_data.total_skipped_qn }}</p>
              <p><strong>Deleted Answers:</strong> {{ selectedAttempt.quiz_meta_data.total_deleted_answers }}</p>
              <p><strong>Total Time Taken:</strong> {{ selectedAttempt.quiz_meta_data.total_time_taken }}s</p>
              <p><strong>Answering Duration:</strong> {{ selectedAttempt.quiz_meta_data.total_answering_duration ? selectedAttempt.quiz_meta_data.total_answering_duration + 's' : 'N/A' }}</p>
              <p><strong>Attempt Time:</strong> {{ formatDate(selectedAttempt.quiz_meta_data.attempt_time) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Attempts Modal -->
    <div class="modal fade" id="attemptsModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Previous Attempts (Quiz ID: {{ selectedQuizId }})</h5>
            <button type="button" class="btn-close btn-close-white" @click="closeModal('attemptsModal')"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3 d-flex justify-content-between align-items-center">
              <div>
                <label for="attemptsSortBy" class="me-2">Sort By:</label>
                <select v-model="attemptsSortBy" class="form-select d-inline w-auto">
                  <option value="date">Date</option>
                  <option value="score">Score</option>
                  <option value="performance">Performance</option>
                </select>
              </div>
              <button class="btn btn-sm btn-success" @click="downloadAttemptsCSV">Download Previous Attempts</button>
            </div>
            <div class="row">
              <div v-for="attempt in paginatedAttempts" :key="attempt.attempt_id" class="col-md-6 col-12 mb-3 mx-auto">
                <div class="card attempt-card" :class="getPerformanceClass(attempt.performance_tag)">
                  <div class="card-body">
                    <p><strong>Score:</strong> {{ attempt.score }} / {{ attempt.full_score }}</p>
                    <p><strong>Start Time:</strong> {{ formatDate(attempt.start_time) }}</p>
                    <p><strong>End Time:</strong> {{ formatDate(attempt.end_time) }}</p>
                    <p><strong>Total Questions:</strong> {{ attempt.total_questions_count }}</p>
                    <p><strong>Attempted:</strong> {{ attempt.total_attempted_qn }}</p>
                    <p><strong>Correct:</strong> {{ attempt.total_correct_ans }}</p>
                    <p><strong>Wrong:</strong> {{ attempt.total_wrong_ans }}</p>
                    <p><strong>Score Earned:</strong> {{ attempt.total_score_earned }}</p>
                    <p><strong>Marked for Review:</strong> {{ attempt.total_marked_for_review_qn }}</p>
                    <p><strong>Skipped:</strong> {{ attempt.total_skipped_qn }}</p>
                    <p><strong>Deleted Answers:</strong> {{ attempt.total_deleted_answers }}</p>
                    <p><strong>Total Time Taken:</strong> {{ attempt.total_time_taken }}s</p>
                    <p><strong>Answering Duration:</strong> {{ attempt.total_answering_duration ? attempt.total_answering_duration + 's' : 'N/A' }}</p>
                    <p><strong>Attempt Time:</strong> {{ formatDate(attempt.attempt_time) }}</p>
                    <p><strong>Performance:</strong> <span :class="['badge', getPerformanceClass(attempt.performance_tag)]">{{ attempt.performance_tag }}</span></p>
                  </div>
                </div>
              </div>
            </div>
            <nav v-if="attemptsTotalPages > 1" class="mt-3">
              <ul class="pagination pagination-sm justify-content-center">
                <li class="page-item" :class="{ disabled: attemptsPage === 0 }">
                  <button class="page-link" @click="attemptsPage--">«</button>
                </li>
                <li v-for="page in attemptsTotalPages" :key="page" class="page-item" :class="{ active: attemptsPage === page - 1 }">
                  <button class="page-link" @click="attemptsPage = page - 1">{{ page }}</button>
                </li>
                <li class="page-item" :class="{ disabled: attemptsPage === attemptsTotalPages - 1 }">
                  <button class="page-link" @click="attemptsPage++">»</button>
                </li>
              </ul>
            </nav>
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
  name: 'UserScore',
  components: { Alert, Navbar },
  setup() {
    const store = useStore();
    return { store };
  },
  data() {
    return {
      alertMessage: '',
      alertType: 'info',
      scores: { subjects: {}, chapters: {}, months: { current: [], previous: [], older: [] }, total_completed: 0 },
      searchQuery: '',
      sortBy: 'subject',
      currentPage: 0,
      itemsPerPage: 2,
      chapterPages: {},
      chapterItemsPerPage: 2,
      monthPages: { current: 0, previous: 0, older: 0 },
      monthItemsPerPage: 2,
      selectedQuizId: null,
      selectedAttempts: [],
      selectedAttempt: null,
      attemptsPage: 0,
      attemptsPerPage: 2,
      attemptsSortBy: 'date',
    };
  },
  computed: {
    filteredSubjects() {
      let filtered = { ...this.scores.subjects };
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = Object.fromEntries(
          Object.entries(filtered).filter(([subject, attempts]) =>
            subject.toLowerCase().includes(query) ||
            attempts.some(a => a.chapter.toLowerCase().includes(query) || a.date.toLowerCase().includes(query))
          )
        );
      }
      return filtered;
    },
    sortedSubjects() {
      const subjects = { ...this.filteredSubjects };
      Object.keys(subjects).forEach(subject => {
        subjects[subject].sort((a, b) => {
          if (this.sortBy === 'subject') return a.subject.localeCompare(b.subject);
          if (this.sortBy === 'chapter') return a.chapter.localeCompare(b.chapter);
          if (this.sortBy === 'date') return new Date(b.date) - new Date(a.date);
          if (this.sortBy === 'score') return b.score - a.score;
          if (this.sortBy === 'performance') return this.performanceValue(b.performance_tag) - this.performanceValue(a.performance_tag);
          return 0;
        });
      });
      return subjects;
    },
    paginatedSubjects() {
      const start = this.currentPage * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      const sorted = Object.entries(this.sortedSubjects);
      return Object.fromEntries(sorted.slice(start, end));
    },
    subjectTotalPages() {
      return Math.ceil(Object.keys(this.sortedSubjects).length / this.itemsPerPage);
    },
    validMonths() {
      return Object.fromEntries(
        Object.entries(this.scores.months).filter(([month]) => typeof month === 'string' && ['current', 'previous', 'older'].includes(month))
      );
    },
    sortedAttempts() {
      const attempts = [...this.selectedAttempts];
      attempts.sort((a, b) => {
        if (this.attemptsSortBy === 'date') return new Date(b.attempt_time) - new Date(a.attempt_time);
        if (this.attemptsSortBy === 'score') return b.score - a.score;
        if (this.attemptsSortBy === 'performance') return this.performanceValue(b.performance_tag) - this.performanceValue(a.performance_tag);
        return 0;
      });
      return attempts;
    },
    paginatedAttempts() {
      const start = this.attemptsPage * this.attemptsPerPage;
      const end = start + this.attemptsPerPage;
      return this.sortedAttempts.slice(start, end);
    },
    attemptsTotalPages() {
      return Math.ceil(this.selectedAttempts.length / this.attemptsPerPage);
    },
  },
  watch: {
    attemptsSortBy() {
      this.attemptsPage = 0;
    },
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString);
      const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric',
        hour12: true,
      };
      return date.toLocaleString('en-US', options);
    },
    uniqueQuizzes(data) {
      const quizMap = new Map();
      data.forEach(attempt => {
        if (!quizMap.has(attempt.quiz_id) || new Date(attempt.date) > new Date(quizMap.get(attempt.quiz_id).date)) {
          quizMap.set(attempt.quiz_id, attempt);
        }
      });
      return Array.from(quizMap.values());
    },
    paginatedChapterQuizzes(chapterData) {
      const chapter = chapterData[0]?.chapter || 'unknown';
      if (!this.chapterPages[chapter]) this.chapterPages[chapter] = 0;
      const start = this.chapterPages[chapter] * this.chapterItemsPerPage;
      const end = start + this.chapterItemsPerPage;
      return this.uniqueQuizzes(chapterData).slice(start, end);
    },
    chapterTotalPages(chapterData) {
      return Math.ceil(this.uniqueQuizzes(chapterData).length / this.chapterItemsPerPage);
    },
    paginatedMonthQuizzes(month) {
      if (typeof month !== 'string' || !this.scores.months[month]) return [];
      const start = this.monthPages[month] * this.monthItemsPerPage;
      const end = start + this.monthItemsPerPage;
      return this.uniqueQuizzes(this.scores.months[month]).slice(start, end);
    },
    monthTotalPages(month) {
      if (typeof month !== 'string' || !this.scores.months[month]) return 0;
      return Math.ceil(this.uniqueQuizzes(this.scores.months[month]).length / this.monthItemsPerPage);
    },
    async fetchScores() {
      try {
        const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
        const response = await axios.get(`${BASE_URL}/dashboard/user/scores`, config);
        this.scores = response.data;
        this.monthPages = { current: 0, previous: 0, older: 0 };
        Object.keys(this.scores.subjects).forEach(subject => {
          Object.keys(this.groupByChapter(this.scores.subjects[subject])).forEach(chapter => {
            this.$set(this.chapterPages, chapter, 0);
          });
        });
      } catch (error) {
        console.log (error, 'Failed to load scores');
      }
    },
    async fetchQuizAttempts(quizId) {
      try {
        const config = { headers: { Authorization: `Bearer ${this.store.state.access_token}` } };
        const response = await axios.get(
          `${BASE_URL}/dashboard/user/quiz/${quizId}/attempts?exclude_latest=true`,
          config
        );
        this.selectedAttempts = response.data.attempts;
      } catch (error) {
        this.handleError(error, 'Failed to load quiz attempts');
      }
    },
    groupByChapter(subjectData) {
      const chapters = {};
      subjectData.forEach(attempt => {
        chapters[attempt.chapter] = chapters[attempt.chapter] || [];
        chapters[attempt.chapter].push(attempt);
      });
      return chapters;
    },
    performanceValue(tag) {
      return { Outstanding: 4, Good: 3, Pass: 2, Fail: 1 }[tag] || 0;
    },
    getPerformanceClass(tag) {
      return {
        'bg-success': tag === 'Outstanding',
        'bg-info': tag === 'Good',
        'bg-warning': tag === 'Pass',
        'bg-danger': tag === 'Fail',
      };
    },
    capitalize(str) {
      return typeof str === 'string' ? str.charAt(0).toUpperCase() + str.slice(1) : 'Unknown';
    },
    handleSearch(query) {
      this.searchQuery = query;
      this.currentPage = 0;
      this.monthPages = { current: 0, previous: 0, older: 0 };
      this.chapterPages = {};
    },
    sortData() {
      this.currentPage = 0;
    },
    openInfoModal(attempt) {
      this.selectedAttempt = attempt;
      new bootstrap.Modal(document.getElementById('infoModal')).show();
    },
    openAttemptsModal(quizId) {
      this.selectedQuizId = quizId;
      this.attemptsPage = 0;
      this.fetchQuizAttempts(quizId);
      new bootstrap.Modal(document.getElementById('attemptsModal')).show();
    },
    closeModal(modalId) {
      bootstrap.Modal.getInstance(document.getElementById(modalId))?.hide();
    },
    handleError(error, defaultMsg) {
      this.alertMessage = error.response?.data?.msg || defaultMsg;
      this.alertType = 'error';
      if (error.response?.status === 401) {
        this.store.commit('clearAuth');
        setTimeout(() => this.$router.push('/login'), 1000);
      }
    },
    downloadCSV(content, filename) {
      const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },
    downloadLatestAttempt(attempt) {
      const headers = ['Quiz ID', 'Attempt ID', 'Score', 'Total Score', 'Date', 'Performance'];
      const row = [
        attempt.quiz_id,
        attempt.attempt_id,
        attempt.score,
        attempt.full_score,
        this.formatDate(attempt.date),
        attempt.performance_tag || 'N/A'
      ];
      const csvContent = [headers.join(','), row.join(',')].join('\n');
      this.downloadCSV(csvContent, `quiz_${attempt.quiz_id}_latest.csv`);
    },
    downloadSubject(subject, subjectData) {
      const headers = ['Subject', 'Quiz ID', 'Attempt ID', 'Score', 'Total Score', 'Date', 'Chapter', 'Performance'];
      const csvRows = [headers.join(',')];
      subjectData.forEach(attempt => {
        csvRows.push([
          subject,
          attempt.quiz_id,
          attempt.attempt_id,
          attempt.score,
          attempt.full_score,
          this.formatDate(attempt.date),
          attempt.chapter,
          attempt.performance_tag || 'N/A'
        ].join(','));
      });
      this.downloadCSV(csvRows.join('\n'), `${subject}_data.csv`);
    },
    downloadChapter(subject, chapter, chapterData) {
      const headers = ['Subject', 'Chapter', 'Quiz ID', 'Attempt ID', 'Score', 'Total Score', 'Date', 'Performance'];
      const csvRows = [headers.join(',')];
      chapterData.forEach(attempt => {
        csvRows.push([
          subject,
          chapter,
          attempt.quiz_id,
          attempt.attempt_id,
          attempt.score,
          attempt.full_score,
          this.formatDate(attempt.date),
          attempt.performance_tag || 'N/A'
        ].join(','));
      });
      this.downloadCSV(csvRows.join('\n'), `${subject}_${chapter}_data.csv`);
    },
    downloadMonth(month, monthData) {
      const headers = ['Month', 'Quiz ID', 'Attempt ID', 'Score', 'Total Score', 'Date', 'Subject', 'Chapter', 'Performance'];
      const csvRows = [headers.join(',')];
      monthData.forEach(attempt => {
        csvRows.push([
          month,
          attempt.quiz_id,
          attempt.attempt_id,
          attempt.score,
          attempt.full_score,
          this.formatDate(attempt.date),
          attempt.subject,
          attempt.chapter,
          attempt.performance_tag || 'N/A'
        ].join(','));
      });
      this.downloadCSV(csvRows.join('\n'), `${month}_month_data.csv`);
    },
    downloadAll() {
      const headers = ['Subject', 'Chapter', 'Quiz ID', 'Attempt ID', 'Score', 'Total Score', 'Date', 'Performance'];
      const csvRows = [headers.join(',')];
      Object.entries(this.scores.subjects).forEach(([subject, attempts]) => {
        attempts.forEach(attempt => {
          csvRows.push([
            subject,
            attempt.chapter,
            attempt.quiz_id,
            attempt.attempt_id,
            attempt.score,
            attempt.full_score,
            this.formatDate(attempt.date),
            attempt.performance_tag || 'N/A'
          ].join(','));
        });
      });
      this.downloadCSV(csvRows.join('\n'), 'all_quiz_data.csv');
    },
    downloadAttemptsCSV() {
      const headers = [
        'Attempt ID', 'Score', 'Total Score', 'Start Time', 'End Time', 'Total Questions', 
        'Attempted', 'Correct', 'Wrong', 'Score Earned', 'Marked for Review', 'Skipped', 
        'Deleted Answers', 'Total Time Taken', 'Answering Duration', 'Attempt Time', 'Performance'
      ];
      const csvRows = [headers.join(',')];
      this.selectedAttempts.forEach(attempt => {
        csvRows.push([
          attempt.attempt_id,
          attempt.score,
          attempt.full_score,
          this.formatDate(attempt.start_time),
          this.formatDate(attempt.end_time),
          attempt.total_questions_count,
          attempt.total_attempted_qn,
          attempt.total_correct_ans,
          attempt.total_wrong_ans,
          attempt.total_score_earned,
          attempt.total_marked_for_review_qn,
          attempt.total_skipped_qn,
          attempt.total_deleted_answers,
          attempt.total_time_taken,
          attempt.total_answering_duration || 'N/A',
          this.formatDate(attempt.attempt_time),
          attempt.performance_tag
        ].join(','));
      });
      this.downloadCSV(csvRows.join('\n'), `quiz_${this.selectedQuizId}_previous_attempts.csv`);
    },
  },
  async created() {
    const access_token = this.store.state.access_token;
    if (!access_token) {
      this.$router.push('/login');
      return;
    }
    await this.fetchScores();
  },
};
</script>

<style scoped>
.container-fluid {
  padding: 0 20px;
}

.subject-header .accordion-button {
  background: linear-gradient(135deg, #00c4cc, #009fa6);
  color: white;
  border-radius: 8px 8px 0 0;
  transition: background 0.3s ease;
}

.subject-header .accordion-button:not(.collapsed) {
  background: linear-gradient(135deg, #009fa6, #007b82);
}

.subject-header .accordion-button:hover {
  background: linear-gradient(135deg, #00e0e8, #00c4cc);
}

.subject-header .d-flex {
  padding: 0; /* Remove padding to align with button */
}

.chapter-header {
  background: linear-gradient(135deg, #6b48ff, #4b2ecc);
  color: white;
  padding: 5px 10px;
  border-radius: 5px;
  margin-bottom: 10px;
}

.chapter-header:hover {
  background: linear-gradient(135deg, #7c5aff, #6b48ff);
}

.month-header .accordion-button {
  background: linear-gradient(135deg, #ff8c00, #ff6200);
  color: white;
  border-radius: 8px 8px 0 0;
  transition: background 0.3s ease;
}

.month-header .accordion-button:not(.collapsed) {
  background: linear-gradient(135deg, #ff6200, #e55b00);
}

.month-header .accordion-button:hover {
  background: linear-gradient(135deg, #ffa500, #ff8c00);
}

.month-header .d-flex {
  padding: 0; /* Remove padding to align with button */
}

.chapter-item {
  margin-bottom: 20px;
}

.quiz-card, .attempt-card {
  border: none;
  border-left: 5px solid;
  border-radius: 10px;
  background: linear-gradient(135deg, #ffffff, #f9f9f9);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease;
}

.quiz-card:hover, .attempt-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
}

.quiz-card.bg-success, .attempt-card.bg-success { border-left-color: #28a745; }
.quiz-card.bg-info, .attempt-card.bg-info { border-left-color: #17a2b8; }
.quiz-card.bg-warning, .attempt-card.bg-warning { border-left-color: #ffc107; }
.quiz-card.bg-danger, .attempt-card.bg-danger { border-left-color: #dc3545; }

.card-body {
  padding: 15px;
}

.card-body p {
  margin: 5px 0;
  color: #333;
}

.btn-info {
  background: linear-gradient(135deg, #00c4cc, #009fa6);
  border: none;
  color: white;
  padding: 5px 10px;
  font-size: 0.9rem;
  border-radius: 5px;
}

.btn-info:hover {
  background: linear-gradient(135deg, #00a9b0, #00868c);
}

.btn-primary {
  background: linear-gradient(135deg, #6b48ff, #4b2ecc);
  border: none;
  border-radius: 5px;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #7c5aff, #6b48ff);
}

.btn-success {
  background: linear-gradient(135deg, #28a745, #218838);
  border: none;
  border-radius: 5px;
  padding: 5px 10px; /* Consistent padding with headers */
  font-size: 0.9rem; /* Match header text size */
}

.btn-success:hover {
  background: linear-gradient(135deg, #34c759, #28a745);
}

.modal-header.bg-info {
  background: linear-gradient(135deg, #00c4cc, #009fa6);
}

.modal-header.bg-primary {
  background: linear-gradient(135deg, #6b48ff, #4b2ecc);
}

.pagination .page-link {
  color: #6b48ff;
  border: none;
  margin: 0 3px;
  border-radius: 6px;
  transition: background 0.2s ease, color 0.2s ease;
}

.pagination .page-item.active .page-link {
  background: #6b48ff;
  color: white;
}

.pagination .page-link:hover {
  background: #e9e4ff;
  color: #4b2ecc;
}

.form-select {
  border-radius: 6px;
  border-color: #6b48ff;
  transition: border-color 0.3s ease;
}

.form-select:focus {
  border-color: #4b2ecc;
  box-shadow: 0 0 5px rgba(75, 46, 204, 0.5);
}

.sort-controls {
  margin-top: 10px;
}

@media (max-width: 768px) {
  .sort-controls {
    width: 100%;
    justify-content: flex-start;
  }

  .card-body {
    padding: 10px;
  }

  .d-flex {
    flex-direction: column;
    align-items: flex-start;
  }

  .btn-success {
    margin-top: 5px;
  }
}

@media (max-width: 576px) {
  .accordion-button {
    font-size: 0.9rem;
  }

  .btn-sm {
    padding: 4px 8px;
    font-size: 0.85rem;
  }

  .pagination {
    flex-wrap: wrap;
  }
}
</style>