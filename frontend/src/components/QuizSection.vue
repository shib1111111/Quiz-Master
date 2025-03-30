<template>
    <div class="col-12">
      <div class="subject-card">
        <div :class="['card-header', 'text-white', bgClass]">
          <h3>{{ title }}</h3>
        </div>
        
        
        <div class="card-body">
          <div class="row row-cols-1 row-cols-md-3 g-3">
            <div v-for="quiz in quizzes" :key="quiz.quiz_id" class="col">
              <div class="card h-100 quiz-card" :class="{ 'border-success': quiz.in_cart }">
                <div class="card-body">
                  <h5 class="card-title text-primary">Quiz #{{ quiz.quiz_id }}</h5>
                  <div class="quiz-tile">
                    <span class="quiz-info questions">Questions: {{ quiz.number_of_questions }}</span>
                    <span class="quiz-info date">Date: {{ quiz.date }}</span>
                    <span class="quiz-info duration">Duration: {{ quiz.duration }}</span>
                    <span class="quiz-info price"><strong>Price:</strong> ₹{{ quiz.pay_amount || '0.00' }}</span> <!-- Changed from price -->
                  </div>
                </div>
                <div class="card-footer d-flex justify-content-between">
                  <button class="btn btn-primary btn-sm" @click="$emit('view-metadata', quiz.quiz_id)">View</button>
                  <button v-if="quiz.in_cart" class="btn btn-success btn-sm" @click="$router.push('/cart')">Go to Cart</button>
                  <button v-else-if="quiz.date === today && quiz.pay_required && quiz.paid" class="btn btn-success btn-sm" @click="$emit('start-quiz', quiz.quiz_id)">Start Now</button>
                  <button v-else-if="quiz.date === today && quiz.pay_required && !quiz.paid" class="btn btn-warning btn-sm" @click="$emit('add-to-cart', quiz.quiz_id)">Add to Cart</button>
                  <button v-else-if="quiz.date === today && !quiz.pay_required" class="btn btn-success btn-sm" @click="$emit('start-quiz', quiz.quiz_id)">Start Now</button>
                  <button v-else-if="quiz.date < today" class="btn btn-info btn-sm" @click="$emit('start-quiz', quiz.quiz_id)">Practice</button>
                  <button v-else-if="quiz.date > today && quiz.pay_required && !quiz.paid" class="btn btn-warning btn-sm" @click="$emit('add-to-cart', quiz.quiz_id)">Add to Cart</button>
                  <button v-else-if="quiz.date > today && !quiz.pay_required" class="btn btn-secondary btn-sm" disabled>Upcoming</button>
                  <button v-else-if="quiz.date > today && quiz.pay_required && quiz.paid" class="btn btn-secondary btn-sm" disabled>Upcoming</button>
                </div>
              </div>
            </div>
            <div v-if="quizzes.length === 0" class="col-12 no-quizzes">
              <i class="bi bi-exclamation-triangle"></i><br>No quizzes available.
            </div>
          </div>
          <!-- Pagination -->
          <nav v-if="totalItems > itemsPerPage" class="mt-3">
            <ul class="pagination justify-content-center">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button class="page-link" @click="$emit('page-change', currentPage - 1)">Previous</button>
              </li>
              <li v-for="page in totalPages" :key="page" class="page-item" :class="{ active: currentPage === page }">
                <button class="page-link" @click="$emit('page-change', page)">{{ page }}</button>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button class="page-link" @click="$emit('page-change', currentPage + 1)">Next</button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>
  </template>
  
<script>
  export default {
    props: {
      title: String,
      bgClass: String,
      quizzes: Array,
      totalItems: Number,
      currentPage: Number,
    },
    data() {
      return {
        today: new Date().toISOString().split('T')[0],
        itemsPerPage: 6,
      };
    },
    computed: {
      totalPages() {
        return Math.ceil(this.totalItems / this.itemsPerPage);
      },
    },
  };
</script>
  
  <style scoped>
  .card-body {
    padding: 15px;
  }
  
  .card-title {
    font-size: 1.1rem;
    color: #0077b6; /* Vibrant blue */
  }
  
  .quiz-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
  }
  
  .quiz-card:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
    background-color: #f8f9fa;
  }
  
  .quiz-tile {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    font-size: 0.9rem;
  }
  
  .quiz-info {
    margin: 0 5px;
  }
  
  .questions {
    color: #2d6a4f; /* Deep green */
    font-weight: 500;
  }
  
  .date {
    color: #ff6200; /* Bright orange */
    font-weight: 500;
  }
  
  .duration {
    color: #7209b7; /* Vibrant purple */
    font-weight: 500;
  }
  
  .border-success {
    border: 2px solid #52b788;
  }
  
  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .btn-primary { background: linear-gradient(135deg, #00b4d8, #0077b6); border: none; color: #fff; }
  .btn-primary:hover { background: linear-gradient(135deg, #0077b6, #005f8c); }
  .btn-success { background: linear-gradient(135deg, #52b788, #2d6a4f); border: none; color: #fff; }
  .btn-success:hover { background: linear-gradient(135deg, #2d6a4f, #1e4536); }
  .btn-warning { background: linear-gradient(135deg, #ff9f1c, #ff6200); border: none; color: #fff; }
  .btn-warning:hover { background: linear-gradient(135deg, #ff6200, #cc4e00); }
  .btn-info { background: linear-gradient(135deg, #7209b7, #480ca8); border: none; color: #fff; }
  .btn-info:hover { background: linear-gradient(135deg, #480ca8, #2f0775); }
  .btn-secondary { background: linear-gradient(135deg, #adb5bd, #6c757d); border: none; color: #fff; }
  .btn-secondary:hover { background: linear-gradient(135deg, #6c757d, #495057); }
  .btn:disabled { opacity: 0.6; cursor: not-allowed; }
  
  .pagination .page-link {
    color: #0077b6;
    transition: background-color 0.3s ease, color 0.3s ease;
  }
  
  .pagination .page-item.active .page-link {
    background-color: #0077b6;
    color: #fff;
    border-color: #0077b6;
  }
  
  .pagination .page-link:hover {
    background-color: #b8c9d9;
    color: #005f8c;
  }
  
  @media (max-width: 767px) {
    .card-body {
      padding: 10px;
    }
    .card-title {
      font-size: 1rem;
    }
    .quiz-tile {
      font-size: 0.85rem;
      flex-direction: column;
    }
    .quiz-info {
      margin: 2px 0;
    }
  }
  </style>