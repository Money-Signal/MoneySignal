import { createRouter, createWebHistory } from 'vue-router'
import SignupView from '@/views/accounts/SignupView.vue'
import LoginView from '@/views/accounts/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/signup', name: 'signup', component: SignupView },
    { path: '/login',  name: 'login',  component: LoginView  },
  ],
})

export default router
