import { createRouter, createWebHistory } from 'vue-router'
import Books from '../components/Books.vue'
import Error from '../components/Error.vue'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {path: '/', name: 'Books',component: Books,},
    { path: '/:pathMatch(.*)*', component: Error },

  ]

})
export default router