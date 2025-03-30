<template>
  <div class="exam-container">
    <div class="question-section">
      <h2 class="question-title">Question {{ currentQuestionIndex + 1 }} / {{ questions.length }}</h2>
      <p class="question-text">{{ currentQuestion.question_statement }}</p>
      <div class="options">
        <label 
          v-for="(option, index) in currentQuestion.options" 
          :key="index" 
          class="option"
        >
          <input 
            type="radio" 
            :value="option" 
            v-model="selectedOption" 
            class="option-input"
          >
          <span class="option-text">{{ option }}</span>
        </label>
      </div>
    </div>
    
    <div class="sidebar">
      <div class="timer">
        Time Remaining: <span class="time">{{ timeRemaining }}</span>
      </div>
      <div class="buttons">
        <button @click="saveAndNext" class="btn btn-primary">Save & Next</button>
        <button @click="markForReview" class="btn btn-warning">Mark for Review</button>
        <button @click="clearResponse" class="btn btn-secondary">Clear Response</button>
        <button @click="deleteAnswer" class="btn btn-danger">Delete Answer</button>
        <button @click="confirmSubmit" class="btn btn-success">Submit Exam</button>
      </div>
      <div class="question-tabs">
        <button 
          v-for="(q, index) in questions" 
          :key="q.id" 
          @click="navigateToQuestion(index)"
          :class="{
            'tab': true,
            'answered': answeredQuestions.includes(q.id),
            'review': reviewQuestions.includes(q.id),
            'active': index === currentQuestionIndex
          }"
        >
          {{ index + 1 }}
        </button>
      </div>
    </div>
    <div v-if="showSubmitConfirm" class="modal">
      <div class="modal-content">
        <h3>Confirm Submission</h3>
        <p>Are you sure you want to submit? This cannot be undone.</p>
        <div class="modal-buttons">
          <button @click="submitExam" class="btn btn-success">Submit</button>
          <button @click="showSubmitConfirm = false" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
    <div v-if="showWarning" class="modal">
      <div class="modal-content warning">
        <h3>Warning</h3>
        <p>Tab switch {{ warningCount }}/3. Exceeding 3 ends the exam.</p>
        <button @click="showWarning = false" class="btn btn-primary">OK</button>
      </div>
    </div>
    <div v-if="examEnded" class="modal">
      <div class="modal-content ended">
        <h3>Exam Ended</h3>
        <button @click="exitExam" class="btn btn-primary">Exit</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

export default {
  name: 'ExamInterface',
  props: {
    quizId: {
      type: [Number, String],
      required: true
    },
    attemptId: {
      type: [Number, String],
      required: true
    }
  },
  data() {
    return {
      questions: [],
      currentQuestionIndex: 0,
      selectedOption: null,
      answeredQuestions: [],
      reviewQuestions: [],
      timeRemaining: '',
      duration: Number(this.$route.query.duration) || 0,
      startTime: null,
      timer: null,
      warningCount: 0,
      showSubmitConfirm: false,
      showWarning: false,
      examEnded: false,
      endReason: '',
      accessToken: this.$route.query.access_token || '',
      examResults: {},
      totalScorePossible: 0
    };
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentQuestionIndex] || {};
    }
  },
  mounted() {
    this.initializeExam();
    this.setupTabMonitoring();
  },
  beforeDestroy() {
    clearInterval(this.timer);
    window.removeEventListener('blur', this.handleTabSwitch);
  },
  methods: {
    async initializeExam() {
      try {
        await this.fetchQuestions();
        this.startTimer();
      } catch (error) {
        this.endExam('Failed to initialize exam');
      }
    },
    async fetchQuestions() {
      try {
        const response = await axios.get(
          `${BASE_URL}/dashboard/user/quiz/${this.quizId}/questions`,
          { headers: { Authorization: `Bearer ${this.$store.state.access_token}` } }
        );
        this.questions = response.data;
        this.totalScorePossible = this.questions.reduce((sum, q) => sum + q.score_value, 0);
        this.startTime = new Date();
      } catch (error) {
        throw new Error('Failed to fetch questions: ' + error.message);
      }
    },
    startTimer() {
      const endTime = new Date(this.startTime.getTime() + this.duration * 60000);
      this.timer = setInterval(() => {
        const now = new Date();
        const timeLeft = endTime - now;
        if (timeLeft <= 0) {
          this.endExam('Time expired');
        } else {
          const minutes = Math.floor(timeLeft / 60000);
          const seconds = Math.floor((timeLeft % 60000) / 1000);
          this.timeRemaining = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        }
      }, 1000);
    },
    async saveAndNext() {
      if (!this.selectedOption) return;
      try {
        await axios.post(
          `${BASE_URL}/dashboard/user/quiz/${this.quizId}/attempt/${this.attemptId}/question/${this.currentQuestion.id}`,
          { selected_option: this.selectedOption, access_token: this.accessToken },
          { headers: { Authorization: `Bearer ${this.$store.state.access_token}` } }
        );
        if (!this.answeredQuestions.includes(this.currentQuestion.id)) {
          this.answeredQuestions.push(this.currentQuestion.id);
        }
        this.nextQuestion();
      } catch (error) {
        console.error('Save failed:', error);
      }
    },
    async markForReview() {
      try {
        await axios.post(
          `${BASE_URL}/dashboard/user/quiz/${this.quizId}/attempt/${this.attemptId}/mark-for-review/${this.currentQuestion.id}`,
          { access_token: this.accessToken },
          { headers: { Authorization: `Bearer ${this.$store.state.access_token}` } }
        );
        if (!this.reviewQuestions.includes(this.currentQuestion.id)) {
          this.reviewQuestions.push(this.currentQuestion.id);
        }
        this.nextQuestion();
      } catch (error) {
        console.error('Mark for review failed:', error);
      }
    },
    async clearResponse() {
      try {
        await axios.post(
          `${BASE_URL}/dashboard/user/quiz/${this.quizId}/attempt/${this.attemptId}/clear-response/${this.currentQuestion.id}`,
          { access_token: this.accessToken },
          { headers: { Authorization: `Bearer ${this.$store.state.access_token}` } }
        );
        this.selectedOption = null;
      } catch (error) {
        console.error('Clear response failed:', error);
      }
    },
    async deleteAnswer() {
      try {
        await axios.post(
          `${BASE_URL}/dashboard/user/quiz/${this.quizId}/attempt/${this.attemptId}/delete-answer/${this.currentQuestion.id}`,
          { access_token: this.accessToken },
          { headers: { Authorization: `Bearer ${this.$store.state.access_token}` } }
        );
        this.selectedOption = null;
        this.answeredQuestions = this.answeredQuestions.filter(
          id => id !== this.currentQuestion.id
        );
      } catch (error) {
        console.error('Delete answer failed:', error);
      }
    },
    async navigateToQuestion(index) {
      try {
        await axios.post(
          `${BASE_URL}/dashboard/user/quiz/${this.quizId}/attempt/${this.attemptId}/navigate/${this.questions[index].id}`,
          { access_token: this.accessToken },
          { headers: { Authorization: `Bearer ${this.$store.state.access_token}` } }
        );
        this.currentQuestionIndex = index;
        this.selectedOption = null;
      } catch (error) {
        console.error('Navigation failed:', error);
      }
    },
    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++;
        this.selectedOption = null;
      }
    },
    confirmSubmit() {
      this.showSubmitConfirm = true;
    },
    async submitExam() {
      clearInterval(this.timer);
      try {
        const response = await axios.post(
          `${BASE_URL}/dashboard/user/quiz/${this.quizId}/attempt/${this.attemptId}/submit`,
          { access_token: this.accessToken },
          { headers: { Authorization: `Bearer ${this.$store.state.access_token}` } }
        );
        this.examEnded = true;
        this.endReason = 'Manual submission';
        this.examResults = response.data;
        this.showSubmitConfirm = false;
      } catch (error) {
        console.error('Submit exam failed:', error);
        this.endExam('Submission failed');
      }
    },
    async endExam(reason) {
      clearInterval(this.timer);
      if (this.examEnded) return;
      try {
        const response = await axios.post(
          `${BASE_URL}/dashboard/user/quiz/${this.quizId}/attempt/${this.attemptId}/end`,
          { reason, access_token: this.accessToken },
          { headers: { Authorization: `Bearer ${this.$store.state.access_token}` } }
        );
        this.examEnded = true;
        this.endReason = reason;
        this.examResults = response.data;
        this.showSubmitConfirm = false;
      } catch (error) {
        console.error('End exam failed:', error);
        this.examEnded = true;
        this.endReason = 'System error';
      }
    },
    setupTabMonitoring() {
  this.handleTabSwitch = async () => {
    if (this.examEnded) return;

    try {
      const response = await axios.post(
        `${BASE_URL}/dashboard/user/quiz/${this.quizId}/attempt/${this.attemptId}/tab-switch`,
        { access_token: this.accessToken },
        { headers: { Authorization: `Bearer ${this.$store.state.access_token}` } }
      );
      // Update local warning count from backend response
      this.warningCount = response.data.warning_count;

      // Show warning modal if the exam hasn't ended
      if (this.warningCount <= 3) {
        this.showWarning = true;
      }
    } catch (error) {
      // Handle 403 error when exam ends due to tab switches
      if (error.response && error.response.status === 403) {
        if (error.response.data.msg === 'Exam ended due to multiple tab switches') {
          await this.endExam('Tab switch limit exceeded');
        } else if (error.response.data.msg === 'Valid access token required') {
          await this.endExam('Invalid access token');
        } else {
          console.error('Unexpected 403 error:', error.response.data);
          await this.endExam('Unauthorized access');
        }
      } else {
        console.error('Tab switch logging failed:', error);
      }
    }
  };
  window.addEventListener('blur', this.handleTabSwitch);
},
    exitExam() {
      this.$router.push('/user-dashboard');
    }
  }
};
</script>

<style scoped>
.exam-container {
  display: flex;
  min-height: 100vh;
  background: #f4f7fa;
  font-family: 'Arial', sans-serif;
}

.question-section {
  flex: 3;
  padding: 20px;
  background: #ffffff;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  border-radius: 8px;
  margin: 10px;
}

.question-title {
  color: #2c3e50;
  font-size: 1.5rem;
  margin-bottom: 15px;
}

.question-text {
  color: #34495e;
  font-size: 1.2rem;
  margin-bottom: 20px;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option {
  display: flex;
  align-items: center;
  padding: 10px;
  background: #ecf0f1;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.option:hover {
  background: #dfe6e9;
}

.option-input {
  margin-right: 10px;
  cursor: pointer;
}

.option-text {
  color: #2c3e50;
  flex: 1;
}

.sidebar {
  flex: 1;
  padding: 20px;
  background: #34495e;
  color: #ffffff;
  border-radius: 8px;
  margin: 10px;
}

.timer {
  font-size: 1.2rem;
  margin-bottom: 20px;
  font-weight: 500;
}

.time {
  color: #e74c3c;
  font-weight: bold;
}

.buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn {
  padding: 10px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s ease;
}

.btn-primary { background: #3498db; color: #fff; }
.btn-primary:hover { background: #2980b9; }
.btn-warning { background: #f1c40f; color: #fff; }
.btn-warning:hover { background: #d4ac0d; }
.btn-secondary { background: #95a5a6; color: #fff; }
.btn-secondary:hover { background: #7f8c8d; }
.btn-danger { background: #e74c3c; color: #fff; }
.btn-danger:hover { background: #c0392b; }
.btn-success { background: #2ecc71; color: #fff; }
.btn-success:hover { background: #27ae60; }

.question-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 20px;
}

.tab {
  width: 30px;
  height: 30px;
  background: #ecf0f1;
  color: #2c3e50;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.3s ease;
}

.tab.answered { background: #2ecc71; color: #fff; }
.tab.review { background: #f1c40f; color: #fff; }
.tab.active { background: #3498db; color: #fff; }
.tab:hover { background: #bdc3c7; }

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.modal-content h3 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.modal-content p {
  color: #34495e;
  margin-bottom: 20px;
}

.modal-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.warning { background: #fef5e7; }
.warning h3 { color: #e67e22; }
.ended { background: #f9ebeb; }
.ended h3 { color: #e74c3c; }

@media (max-width: 768px) {
  .exam-container {
    flex-direction: column;
  }
  
  .question-section, .sidebar {
    width: 100%;
    margin: 0;
    border-radius: 0;
  }
  
  .question-title { font-size: 1.2rem; }
  .question-text { font-size: 1rem; }
  .btn { font-size: 0.9rem; }
  .timer { font-size: 1rem; }
  .question-tabs { justify-content: center; }
  .tab { width: 25px; height: 25px; font-size: 0.9rem; }
}
</style>