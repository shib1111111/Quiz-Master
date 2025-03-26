<template>
  <div class="instructions-container">
    <h1 class="title">Quiz Instructions</h1>
    <ul class="instructions-list">
      <li>Enable your camera and audio permissions</li>
      <li>Maximum 3 tab switches allowed</li>
      <li>Duration: {{ duration }} minutes</li>
      <li>Click "Start Exam" when ready</li>
    </ul>
    <div class="status">
      <p>Camera: <span :class="{ 'active': cameraOn }">{{ cameraOn ? 'On' : 'Off' }}</span></p>
      <p>Audio: <span :class="{ 'active': audioOn }">{{ audioOn ? 'On' : 'Off' }}</span></p>
      <p>Single Tab: <span :class="{ 'active': singleTab }">{{ singleTab ? 'Yes' : 'No' }}</span></p>
    </div>
    <button 
      :disabled="!isReady" 
      @click="startExam" 
      class="btn btn-start"
      :class="{ 'disabled': !isReady }"
    >
      Start Exam
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
        this.showAlert('Please enable camera and audio permissions', 'error');
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
        this.showAlert('Please ensure all requirements are met', 'error');
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
        const errorMsg = error.response?.data?.msg || 'Failed to start exam';
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
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  min-height: 100vh;
  font-family: 'Arial', sans-serif;
}

.title {
  color: #2c3e50;
  font-size: 2rem;
  text-align: center;
  margin-bottom: 20px;
}

.instructions-list {
  list-style: none;
  padding: 0;
  color: #34495e;
  font-size: 1.1rem;
}

.instructions-list li {
  margin: 10px 0;
  position: relative;
  padding-left: 20px;
}

.instructions-list li:before {
  content: "•";
  color: #3498db;
  position: absolute;
  left: 0;
}

.status {
  margin: 20px 0;
  font-size: 1rem;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 5px;
}

.status p {
  margin: 5px 0;
  color: #34495e;
}

.status span {
  font-weight: bold;
}

.status .active {
  color: #2ecc71;
}

.btn-start {
  display: block;
  width: 100%;
  padding: 12px;
  background: #3498db;
  color: #fff;
  border: none;
  border-radius: 5px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.3s ease;
}

.btn-start:hover:not(.disabled) {
  background: #2980b9;
}

.btn-start.disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.alert {
  margin-top: 20px;
  padding: 10px;
  border-radius: 5px;
  text-align: center;
  font-weight: 500;
}

.alert.error {
  background: #f9ebeb;
  color: #e74c3c;
}


@media (max-width: 768px) {
  .instructions-container {
    padding: 15px;
    margin: 10px;
  }
  
  .title {
    font-size: 1.5rem;
  }
  
  .instructions-list {
    font-size: 1rem;
  }
  
  .btn-start {
    font-size: 1rem;
  }
}
</style>