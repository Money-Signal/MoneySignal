import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/home/HomeView.vue'
import MapView from '@/views/map/MapView.vue'
import SignupView from '@/views/accounts/SignupView.vue'
import LoginView from '@/views/accounts/LoginView.vue'
import KakaoCallbackView from '@/views/accounts/KakaoCallbackView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/',               name: 'home',          component: HomeView          },
    { path: '/map',            name: 'map',            component: MapView           },
    { path: '/signup',         name: 'signup',         component: SignupView        },
    { path: '/login',          name: 'login',          component: LoginView         },
    { path: '/oauth/callback', name: 'kakaoCallback',  component: KakaoCallbackView }, // 카카오 로그인 콜백
  ],
})

export default router
