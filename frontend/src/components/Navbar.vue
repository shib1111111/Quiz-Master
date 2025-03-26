<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top mb-1 shadow-sm">
    <div class="container-fluid px-4">
      <!-- Brand/Logo -->
      <router-link class="navbar-brand fw-bold" :to="dashboardRoute">
        <img src="@/assets/logo.svg" alt="MyApp Logo" class="favicon">
      </router-link>

      <!-- Toggle button for mobile -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarContent"
        aria-controls="navbarContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Navbar content -->
      <div class="collapse navbar-collapse" id="navbarContent">
        <!-- Admin Navbar Links -->
        <ul class="navbar-nav me-auto mb-2 mb-lg-0" v-if="role === 'admin' && isAuthenticated">
          <li class="nav-item">
            <router-link class="nav-link nav-btn home-link" :to="dashboardRoute" active-class="active">
              Home
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link nav-btn admin-link" to="/admin/quiz" active-class="active">
              Quiz
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link nav-btn admin-link" to="/admin/summary" active-class="active">
              Summary
            </router-link>
          </li>
        </ul>

        <!-- User Navbar Links -->
        <ul class="navbar-nav me-auto mb-2 mb-lg-0" v-if="role === 'user' && isAuthenticated">
          <li class="nav-item">
            <router-link class="nav-link nav-btn home-link" :to="dashboardRoute" active-class="active">
              Home
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link nav-btn user-link" to="/user/scores" active-class="active">
              Scores
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link nav-btn user-link" to="/user/summary" active-class="active">
              Summary
            </router-link>
          </li>
        </ul>

        <!-- Right-side elements (Search + Cart + Logout) -->
        <div class="d-flex align-items-center flex-column flex-lg-row">
          <!-- Search Bar -->
          <form class="d-flex mb-2 mb-lg-0 me-lg-3" @submit.prevent="emitSearch">
            <input
              v-model="searchQuery"
              class="form-control me-2 search-input"
              type="search"
              placeholder="Type to search..."
              aria-label="Search" 
            >
            <button class="btn btn-outline-primary" type="submit">Search</button>
          </form>

              <!-- Cart Button (Visible only for users) -->
              <button
              v-if="role === 'user' && isAuthenticated && cartCount > 0"
              class="btn btn-success cart-btn me-3"
              @click="$router.push('/cart')"
              >
              Cart ({{ cartCount }})
              </button>
          <!-- Logout Button -->
          <button v-if="isAuthenticated" class="btn btn-danger logout-btn" @click="handleLogout">
            Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import axios from 'axios';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

export default {
  name: 'Navbar',
  setup() {
    const store = useStore();
    const router = useRouter();
    return { store, router };
  },
  data() {
    return {
      searchQuery: '',
      cartCount: 0, // Managed locally or via Vuex; fetch if needed
    };
  },
  computed: {
    isAuthenticated() {
      return !!this.store.state.access_token;
    },
    role() {
      return this.store.state.role;
    },
    dashboardRoute() {
      return this.role === 'admin' ? '/admin-dashboard' : '/user-dashboard';
    },
  },
  async created() {
    if (this.role === 'user' && this.isAuthenticated) {
      await this.fetchCartCount();
    }
  },
  methods: {
    async fetchCartCount() {
      try {
        const response = await axios.get(`${BASE_URL}/dashboard/user/cart`, {
          headers: { Authorization: `Bearer ${this.store.state.access_token}` },
        });
        this.cartCount = (response.data.cart_items || []).length;
      } catch (error) {
        console.error('Failed to fetch cart count:', error.response?.data || error.message);
        this.cartCount = 0; // Default to 0 on error
      }
    },
    async handleLogout() {
      try {
        const endpoint = this.role === 'admin' ? '/logout/admin' : '/logout/user';
        await axios.post(`${BASE_URL}${endpoint}`, {}, {
          headers: { Authorization: `Bearer ${this.store.state.access_token}` },
        });
        this.store.commit('clearAuth');
        this.router.push('/login');
      } catch (error) {
        console.error('Logout failed:', error.response?.data || error.message);
        this.store.commit('clearAuth');
        this.router.push('/login');
        this.$emit('alert', { message: 'Logout failed.', type: 'error' });
      }
    },
    emitSearch() {
      this.$emit('search', this.searchQuery);
    },
  },
};
</script>

<style scoped>
.navbar {
  padding: 0.5rem 0;
  z-index: 100;
}

.favicon {
  height: 30px;
}

.nav-btn {
  min-width: 120px;
  text-align: center;
  transition: all 0.3s ease;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 1rem;
}

.nav-btn:hover {
  filter: brightness(0.9);
}

.active {
  background-color: #007bff;
  color: #fff !important;
}

.home-link:hover {
  background-color: #e3f2fd;
  color: #1976d2;
}

.admin-link:hover {
  background-color: #fce4ec;
  color: #ad1457;
}

.user-link:hover {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.search-input {
  min-width: 150px;
  width: 100%;
  transition: all 0.3s ease;
  border-color: #ced4da;
}

.search-input:focus {
  border-color: #007bff;
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}

.btn-outline-primary {
  transition: background-color 0.3s ease, color 0.3s ease;
}

.btn-outline-primary:hover {
  background-color: #007bff;
  color: white;
}

.logout-btn {
  transition: background-color 0.3s ease;
}

.logout-btn:hover {
  background-color: #c82333;
}

.cart-icon {
  cursor: pointer;
  font-size: 1.5rem;
  position: relative;
}

.cart-icon .badge {
  position: absolute;
  top: -5px;
  right: -5px;
  font-size: 0.7rem;
  padding: 3px 6px;
}

@media (min-width: 992px) {
  .navbar-nav .nav-item {
    margin-right: 0.5rem;
  }
  .search-input {
    min-width: 200px;
  }
  .logout-btn {
    padding: 0.5rem 1.5rem;
  }
}

@media (max-width: 991px) {
  .navbar-nav {
    margin-top: 1rem;
    text-align: center;
  }
  .nav-item {
    margin-bottom: 0.5rem;
  }
  .search-input {
    width: 100%;
    margin-bottom: 1rem;
  }
  .logout-btn {
    padding: 0.5rem;
    margin-top: 1rem;
  }
  .navbar-collapse {
    padding-bottom: 1rem;
  }
}

@media (max-width: 576px) {
  .container-fluid {
    padding-left: 15px;
    padding-right: 15px;
  }
  .nav-btn {
    font-size: 0.9rem;
  }
  .search-input {
    min-width: 100px;
  }
}
</style>