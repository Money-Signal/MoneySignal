import { createRouter, createWebHistory } from 'vue-router'
import SignupView from '@/views/accounts/SignupView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/signup', name: 'signup', component: SignupView },
  ],
})

export default router
