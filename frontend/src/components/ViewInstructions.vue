<template>
  <div class="instructions-container">
    <h1 class="title">Welcome to Your Quiz</h1>
    <ul class="instructions-list">
      <li>Grant permissions for camera and audio access</li>
      <li>Limit tab switches to a maximum of 3</li>
      <li>Time Limit: {{ duration }} minutes</li>
      <li>Press "Begin Quiz" when you're prepared</li>
    </ul>
    <div class="status-panel">
      <p>Camera: <span :class="{ 'active': cameraOn }">{{ cameraOn ? 'Enabled' : 'Disabled' }}</span></p>
      <p>Audio: <span :class="{ 'active': audioOn }">{{ audioOn ? 'Enabled' : 'Disabled' }}</span></p>
      <p>Tab Focus: <span :class="{ 'active': singleTab }">{{ singleTab ? 'Active' : 'Inactive' }}</span></p>
    </div>
    <button 
      :disabled="!isReady" 
      @click="startExam" 
      class="btn btn-start"
      :class="{ 'disabled': !isReady }"
    >
      Begin Quiz
    </button>
    <div v-if="alertMessage" :class="['alert', alertType]">{{ alertMessage }}</div>
  </div>
</template>

<script>
import axios from 'axios';

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

export default {
  name: 'ViewInstructions',
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
      duration: Number(this.$route.query.duration) || 0,
      accessToken: this.$route.query.access_token || '',
      cameraOn: false,
      audioOn: false,
      singleTab: true,
      alertMessage: '',
      alertType: '',
      isLoading: false
    };
  },
  computed: {
    isReady() {
      return this.cameraOn && this.audioOn && this.singleTab && !this.isLoading;
    }
  },
  mounted() {
    this.initializeMedia();
    this.setupTabMonitoring();
  },
  beforeDestroy() {
    window.removeEventListener('blur', this.handleTabBlur);
    window.removeEventListener('focus', this.handleTabFocus);
  },
  methods: {
    async initializeMedia() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true
        });
        this.cameraOn = true;
        this.audioOn = true;
        stream.getTracks().forEach(track => track.stop());
      } catch (error) {
        this.showAlert('Please allow camera and audio access to proceed', 'error');
        console.error('Media initialization failed:', error);
      }
    },
    setupTabMonitoring() {
      this.handleTabBlur = () => { this.singleTab = false; };
      this.handleTabFocus = () => { this.singleTab = true; };
      window.addEventListener('blur', this.handleTabBlur);
      window.addEventListener('focus', this.handleTabFocus);
    },
    async startExam() {
      if (!this.isReady) {
        this.showAlert('Ensure all conditions are met before starting', 'error');
        return;
      }

      this.isLoading = true;
      try {
        const response = await axios.post(
          `${BASE_URL}/dashboard/user/quiz/${this.quizId}/attempt/${this.attemptId}/start`,
          { access_token: this.accessToken },
          { headers: { Authorization: `Bearer ${this.$store.state.access_token}` } }
        );

        if (response.data.msg === 'Exam started successfully') {
          await this.$router.push({
            path: `/quiz/${this.quizId}/attempt/${this.attemptId}/exam`,
            query: {
              access_token: this.accessToken,
              duration: this.duration
            }
          });
        }
      } catch (error) {
        const errorMsg = error.response?.data?.msg || 'Unable to start the quiz';
        this.showAlert(errorMsg, 'error');
        console.error('Start exam failed:', error);
      } finally {
        this.isLoading = false;
      }
    },
    showAlert(message, type) {
      this.alertMessage = message;
      this.alertType = type;
      setTimeout(() => {
        this.alertMessage = '';
        this.alertType = '';
      }, 3000);
    }
  }
};
</script>

<style scoped>
.instructions-container {
  max-width: 700px; 
  margin: 0 auto;
  padding: 30px; 
  background: #ffffff;
  border-radius: 12px; 
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); 
  min-height: 100vh;
  font-family: 'Inter', sans-serif; 
}


.title {
  color: #1a2a44; 
  font-size: 2.5rem; 
  text-align: center;
  margin-bottom: 30px;
  position: relative;
  font-weight: 700;
}

.title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 4px;
  background: linear-gradient(90deg, #4a90e2, #87ceeb); 
  border-radius: 2px;
}


.instructions-list {
  list-style: none;
  padding: 0;
  color: #2c3e50; 
  font-size: 1.2rem; 
}

.instructions-list li {
  margin: 15px 0; 
  position: relative;
  padding-left: 30px; 
  transition: color 0.3s ease; 
}

.instructions-list li:hover {
  color: #4a90e2; 
}

.instructions-list li::before {
  content: "➤"; 
  color: #4a90e2; 
  position: absolute;
  left: 0;
  font-size: 1.3rem;
}
.status-panel {
  margin: 30px 0;
  padding: 20px;
  background: #f9fafb; 
  border-radius: 8px;
  border: 1px solid #e5e7eb; 
  font-size: 1.1rem;
}

.status-panel p {
  margin: 10px 0;
  color: #374151; 
}

.status-panel span {
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.3s ease; 
}

.status-panel span.active {
  color: #16a34a; 
  background: #dcfce7; 
}

.status-panel span:not(.active) {
  color: #dc2626; 
  background: #fee2e2; 
}

.status-panel p:hover span {
  background: #e5e7eb; 
}


.btn-start {
  display: block;
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #4a90e2, #357abd); 
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease; 
  box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3); 
}

.btn-start:hover:not(.disabled) {
  transform: translateY(-2px); 
  box-shadow: 0 6px 20px rgba(74, 144, 226, 0.5); 
}

.btn-start.disabled {
  background: #9ca3af; 
  cursor: not-allowed;
  box-shadow: none;
}


.alert {
  margin-top: 25px;
  padding: 12px 20px;
  border-radius: 6px;
  text-align: center;
  font-weight: 500;
  animation: fadeIn 0.3s ease-in;
}

.alert.error {
  background: #fef2f2; 
  color: #b91c1c; 
  border: 1px solid #fecaca;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@media (max-width: 768px) {
  .instructions-container {
    padding: 20px;
    margin: 15px;
  }

  .title {
    font-size: 2rem;
  }

  .instructions-list {
    font-size: 1.1rem;
  }

  .btn-start {
    font-size: 1.1rem;
    padding: 12px;
  }

  .status-panel {
    font-size: 1rem;
  }
}
</style>