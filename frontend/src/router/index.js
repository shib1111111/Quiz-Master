import { createRouter, createWebHistory } from 'vue-router';
import Signup from '@/components/Signup.vue';
import Login from '@/components/Login.vue';
import ForgotPassword from '@/components/ForgotPassword.vue';
import ResetPassword from '@/components/ResetPassword.vue';
import AdminDashboard from '@/components/AdminDashboard.vue';
import UserDashboard from '@/components/UserDashboard.vue';
import Error from '@/components/Error.vue';
import AdminQuiz from '@/components/AdminQuiz.vue';
import AdminSummary from '@/components/AdminSummary.vue';
import QuizCart from '../components/QuizCart.vue';
import ViewInstructions from '../components/ViewInstructions.vue';
import ExamInterface from '../components/ExamInterface.vue';
import Success from '../components/Success.vue';
import UserScore from '../components/UserScore.vue';
import UserSummary from '../components/UserSummary.vue';
import store from '@/store';



const routes = [
  { path: '/', redirect: '/login' },
  { path: '/:pathMatch(.*)*', name: 'Error', component: Error },
  { path: '/signup', component: Signup },
  { path: '/login', component: Login },
  { path: '/forgot-password', component: ForgotPassword },
  { path: '/reset-password', component: ResetPassword },
  { path: '/admin-dashboard',component: AdminDashboard,beforeEnter: (to, from, next) => {if (store.state.role !== 'admin') next('/login'); else next();}},
  { path: '/admin/quiz', component: AdminQuiz, meta: { requiresAuth: true, adminOnly: true },beforeEnter: (to, from, next) => {if (store.state.role !== 'admin') next('/login'); else next();}},
  { path: '/admin/summary', component: AdminSummary, meta: { requiresAuth: true, adminOnly: true } ,beforeEnter: (to, from, next) => {if (store.state.role !== 'admin') next('/login'); else next();}},
  { path: '/user-dashboard',component: UserDashboard,beforeEnter: (to, from, next) => {if (store.state.role !== 'user') next('/login');else next();}},
  { path: '/cart',component: QuizCart,beforeEnter: (to, from, next) => {if (store.state.role !== 'user') next('/login');else next();}},
  {path: '/cart/success',component: Success,beforeEnter: (to, from, next) => {if (store.state.role !== 'user' || !store.state.access_token) next('/login');else next();},},
  {path: '/quiz/:quizId/attempt/:attemptId/instructions',component: ViewInstructions,props: true,beforeEnter: (to, from, next) => {if (store.state.role !== 'user') next('/login');else next();}},
  {path:'/user-score',component:UserScore,beforeEnter: (to, from, next) => {if (store.state.role !== 'user') next('/login');else next();}},
  { path: '/quiz/:quizId/attempt/:attemptId/exam', component: ExamInterface, props: true,beforeEnter: (to, from, next) => { if (!store.state.access_token) next('/login'); else next();}},
  {path: '/user-summary',component: UserSummary,beforeEnter: (to, from, next) => {if (store.state.role !== 'user') next('/login');else next();}},
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!store.state.access_token;
  const userRole = store.state.role;

  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      next('/login');
    } else if (to.meta.role && to.meta.role !== userRole) {
      next(userRole === 'admin' ? '/admin-dashboard' : '/user-dashboard');
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;