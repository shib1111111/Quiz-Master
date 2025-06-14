<template>
  <div class="container-fluid">
    <Navbar :cart-count="cartCount" @search="handleSearch" />
    <Alert v-if="alertMessage" :message="alertMessage" :type="alertType" @close="alertMessage = ''" />

    <!-- Loading Spinner -->
    <div v-show="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Cart Content -->
    <div v-show="!loading" class="cart-content">
      <h2 class="cart-title">Your Shopping Cart</h2>
      <div v-if="cartItems.length === 0" class="empty-cart">
        <i class="bi bi-cart-x" style="font-size: 3rem;"></i>
        <p>Your cart is empty. <router-link to="/user-dashboard">Explore quizzes now!</router-link></p>
      </div>
      
      <div v-else class="cart-wrapper">
        <div class="list-group cart-list">
          <div v-for="(item, index) in cartItems" :key="item.quiz_id" class="list-group-item quiz-item">
            <div class="quiz-row">
              <button class="btn btn-view" @click="viewMetadata(item.quiz_id)" title="View Details">
                <i class="bi bi-info-circle"></i>
              </button>
              <div class="quiz-number">{{ index + 1 }}</div>
              <div class="quiz-details">
                <h5 class="quiz-title">Quiz #{{ item.quiz_id }}</h5>
                <div class="quiz-meta">
                  <span class="subject"><i class="bi bi-book"></i> {{ item.subject }}</span>
                  <span class="chapter"><i class="bi bi-journal-text"></i> {{ item.chapter }}</span>
                  <span class="date"><i class="bi bi-calendar"></i> {{ item.date }}</span>
                </div>
              </div>
              <div class="quiz-actions">
                <span class="price">₹ {{ item.pay_amount }}</span>
                <button class="btn btn-remove" @click="confirmRemove(item.quiz_id)">
                  <i class="bi bi-trash"></i> Remove
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="cart-footer">
          <div class="total-row">
            <span class="total-label">Total Amount:</span>
            <span class="total-price">₹ {{ totalCost }}</span>
          </div>
          <button class="btn btn-purchase" @click="confirmCheckout" :disabled="loading || cartItems.length === 0">
            <i class="bi bi-cart-check"></i> Proceed to Checkout (₹ {{ totalCost }})
          </button>
        </div>
      </div>
    </div>

    <!-- Quiz Metadata Modal -->
    <div class="modal fade" :class="{ 'show d-block': showModal }" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content subject-card">
          <div class="modal-header bg-gradient-primary text-white">
            <h5 class="modal-title">Quiz Details</h5>
            <button type="button" class="btn-close" @click="showModal = false"></button>
          </div>
          <div class="modal-body">
            <p><strong>ID:</strong> {{ metadata.quiz_id }}</p>
            <p><strong>Subject:</strong> {{ metadata.subject }}</p>
            <p><strong>Chapter:</strong> {{ metadata.chapter }}</p>
            <p><strong>Date:</strong> {{ metadata.date }}</p>
            <p><strong>Cost:</strong> ₹ {{ metadata.pay_amount || 'N/A' }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showModal = false">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Checkout Confirmation Modal -->
    <div class="modal fade" :class="{ 'show d-block': showCheckoutModal }" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header bg-gradient-primary text-white">
            <h5 class="modal-title">Confirm Checkout</h5>
            <button type="button" class="btn-close" @click="showCheckoutModal = false"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to proceed to payment for ₹ {{ totalCost }}?</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showCheckoutModal = false">Cancel</button>
            <button class="btn btn-primary" @click="initiateCheckout">Proceed</button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade" :class="{ 'show': showModal || showCheckoutModal }" v-if="showModal || showCheckoutModal" @click="closeModals"></div>
  </div>
</template>

<script>
import axios from 'axios';
import { loadStripe } from '@stripe/stripe-js';
import Alert from '@/components/Alert.vue';
import Navbar from '@/components/Navbar.vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

export default {
  components: { Alert, Navbar },
  setup() {
    const store = useStore();
    const router = useRouter();
    return { store, router };
  },
  data() {
    return {
      alertMessage: '',
      alertType: 'info',
      loading: true,
      cartItems: [],
      cartCount: 0,
      showModal: false,
      showCheckoutModal: false, // New state for checkout confirmation
      metadata: {},
      stripe: null,
    };
  },
  computed: {
    totalCost() {
      return this.cartItems.reduce((sum, item) => sum + (item.pay_amount || 0), 0);
    },
  },
  async created() {
    const access_token = this.store.state.access_token;
    const role = this.store.state.role;

    if (!access_token || role !== 'user') {
      this.router.push('/login');
      return;
    }

    await this.fetchCart(access_token);

    if (!this.store.state.stripePublicKey) {
      await this.store.dispatch('fetchStripePublicKey');
    }

    if (this.store.state.stripePublicKey) {
      this.stripe = await loadStripe(this.store.state.stripePublicKey);
    } else {
      this.alertMessage = 'Payment system initialization failed. Please try again later.';
      this.alertType = 'error';
      this.loading = false;
    }
  },
  methods: {
    async fetchCart(access_token) {
      try {
        const response = await axios.get(`${BASE_URL}/dashboard/user/cart`, {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        this.cartItems = response.data.cart_items || [];
        this.cartCount = response.data.cart_count || 0;
        this.store.commit('updateCartCount', this.cartCount);
        if (response.data.stripe_public_key && !this.store.state.stripePublicKey) {
          this.store.commit('setStripePublicKey', response.data.stripe_public_key);
        }
      } catch (error) {
        if (error.response?.status === 401) {
          await this.handleTokenRefresh();
          await this.fetchCart(this.store.state.access_token);
        } else {
          this.alertMessage = error.response?.data.msg || 'Failed to load cart.';
          this.alertType = 'error';
          this.cartItems = [];
        }
      } finally {
        this.loading = false;
      }
    },
    async removeFromCart(quizId) {
      this.loading = true;
      try {
        const access_token = this.store.state.access_token;
        const cartItem = this.cartItems.find(item => item.quiz_id === quizId);
        const response = await axios.delete(`${BASE_URL}/dashboard/user/cart/${cartItem.cart_id}/remove`, {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        this.alertMessage = response.data.msg || 'Quiz removed from cart.';
        this.alertType = 'success';
        await this.fetchCart(access_token);
      } catch (error) {
        if (error.response?.status === 401) {
          await this.handleTokenRefresh();
          await this.removeFromCart(quizId);
        } else {
          this.alertMessage = error.response?.data.msg || 'Failed to remove quiz from cart.';
          this.alertType = 'error';
        }
      } finally {
        this.loading = false;
      }
    },
    confirmRemove(quizId) {
      if (confirm('Are you sure you want to remove this quiz from your cart?')) {
        this.removeFromCart(quizId);
      }
    },
    confirmCheckout() {
      this.showCheckoutModal = true; // Show confirmation modal
    },
    async initiateCheckout() {
      if (!this.stripe) {
        this.alertMessage = 'Payment system not initialized. Please refresh the page.';
        this.alertType = 'error';
        return;
      }
      this.showCheckoutModal = false; // Close modal
      this.loading = true;
      try {
        const access_token = this.store.state.access_token;
        const response = await axios.post(`${BASE_URL}/dashboard/user/cart/purchase`, {}, {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        
        if (response.data.session_id) {
          const { error } = await this.stripe.redirectToCheckout({
            sessionId: response.data.session_id
          });
          if (error) {
            throw new Error(error.message);
          }
        }
      } catch (error) {
        if (error.response?.status === 401) {
          await this.handleTokenRefresh();
          await this.initiateCheckout();
        } else {
          this.alertMessage = error.response?.data.msg || 'Checkout initiation failed: ' + error.message;
          this.alertType = 'error';
          this.loading = false;
        }
      }
    },
    async viewMetadata(quizId) {
      try {
        const access_token = this.store.state.access_token;
        const response = await axios.get(`${BASE_URL}/dashboard/user/quiz/${quizId}/metadata`, {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        this.metadata = response.data.quiz_metadata;
        this.showModal = true;
      } catch (error) {
        if (error.response?.status === 401) {
          await this.handleTokenRefresh();
          await this.viewMetadata(quizId);
        } else {
          this.alertMessage = error.response?.data.msg || 'Failed to load quiz metadata.';
          this.alertType = 'error';
        }
      }
    },
    async handleTokenRefresh() {
      try {
        await this.store.dispatch('refreshToken');
      } catch (error) {
        this.store.commit('clearAuth');
        this.router.push('/login');
      }
    },
    handleSearch(query) {
      this.searchQuery = query;
    },
    closeModals() {
      this.showModal = false;
      this.showCheckoutModal = false;
    },
  },
};
</script>

<style scoped>
.container-fluid {
  padding: 0;
  width: 100%;
  max-width: 100%;
}

.cart-content {
  padding: 40px 20px;
  min-height: calc(100vh - 70px);
}

.cart-title {
  text-align: center;
  color: #1a3c34;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 30px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.cart-wrapper {
  width: 100%;
  padding: 0 15px;
}

.cart-list {
  margin-bottom: 30px;
}

.quiz-item {
  border: none;
  border-radius: 12px;
  margin-bottom: 15px;
  background: rgba(255, 255, 255, 0.9); /* Slight transparency to blend with tiled background */
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.quiz-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  background: rgba(255, 245, 245, 0.9);
}

.quiz-row {
  display: flex;
  align-items: center;
  padding: 15px;
  gap: 15px; /* Improved spacing between elements */
}

.btn-view {
  background: linear-gradient(135deg, #4ea8de, #f7eef4);
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: all 0.3s ease;
}

.btn-view:hover {
  background: linear-gradient(135deg, #1d3557, #14213d);
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(29, 53, 87, 0.2);
}

.quiz-number {
  width: 40px;
  height: 40px;
  background: #0077b6;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  transition: all 0.3s ease;
}

.quiz-item:hover .quiz-number {
  background: #023e8a;
  transform: scale(1.1);
}

.quiz-details {
  flex: 1;
}

.quiz-title {
  color: #2d6a4f;
  font-size: 1.4rem;
  margin-bottom: 8px;
}

.quiz-meta span {
  margin-right: 15px;
  font-size: 0.95rem;
}

.subject {
  color: #7209b7;
  font-weight: 600;
}

.chapter {
  color: #f48c06;
  font-weight: 500;
}

.date {
  color: #495057;
}

.quiz-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.price {
  color: #2d6a4f;
  font-weight: bold;
  font-size: 1.1rem;
  padding: 5px 10px;
  background: rgba(216, 243, 220, 0.9);
  border-radius: 5px;
}

.btn-remove {
  background: linear-gradient(135deg, #ff6b6b, #d00000);
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  color: white;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-remove:hover {
  background: linear-gradient(135deg, #d00000, #9d0208);
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(208, 0, 0, 0.2);
}

.cart-footer {
  padding: 20px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  margin: 0 15px;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.total-label {
  font-size: 1.3rem;
  color: #1a3c34;
}

.total-price {
  font-size: 1.5rem;
  color: #2d6a4f;
  font-weight: bold;
}

.btn-purchase {
  width: 100%;
  padding: 12px;
  font-size: 1.2rem;
  background: linear-gradient(135deg, #52b788, #2d6a4f);
  border: none;
  color: white;
  transition: all 0.3s ease;
}

.btn-purchase:hover {
  background: linear-gradient(135deg, #2d6a4f, #1a3c34);
  transform: scale(1.02);
  box-shadow: 0 4px 8px rgba(45, 106, 79, 0.2);
}

.empty-cart {
  text-align: center;
  padding: 60px;
  border-radius: 12px;
  margin: 0 15px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.empty-cart a {
  color: #0077b6;
  text-decoration: none;
  font-weight: 500;
}

.empty-cart a:hover {
  text-decoration: underline;
  color: #023e8a;
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #0077b6, #023e8a);
}

@media (max-width: 767px) {
  .quiz-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .quiz-actions {
    margin-top: 15px;
    width: 100%;
    justify-content: flex-end;
    gap: 8px;
  }

  .quiz-number,
  .btn-view {
    margin-bottom: 10px;
  }

  .cart-footer {
    margin: 0;
  }

  .btn-remove {
    padding: 6px 12px;
  }
}
</style>