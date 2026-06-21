import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/home/HomeView.vue'
import MapView from '@/views/map/MapView.vue'
import SignupView from '@/views/accounts/SignupView.vue'
import LoginView from '@/views/accounts/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/',       name: 'home',   component: HomeView   },
    { path: '/map',    name: 'map',    component: MapView    },
    { path: '/signup', name: 'signup', component: SignupView },
    { path: '/login',  name: 'login',  component: LoginView  },
  ],
})

export default router
