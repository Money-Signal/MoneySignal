import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/home/HomeView.vue'
import MapView from '@/views/map/MapView.vue'
import SignupView from '@/views/accounts/SignupView.vue'
import LoginView from '@/views/accounts/LoginView.vue'
import KakaoCallbackView from '@/views/accounts/KakaoCallbackView.vue'
import MyPageView from '@/views/accounts/MyPageView.vue'
import ProfileSetupView from '@/views/accounts/ProfileSetupView.vue'
import AssetView from '@/views/exchange/AssetView.vue'
import VideoDetailView from '@/views/video/VideoDetailView.vue'
import CurrencyView from '@/views/currency/CurrencyView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    { path: '/',               name: 'home',          component: HomeView          },
    { path: '/map',            name: 'map',            component: MapView           },
    { path: '/map/directions', name: 'directions', component: () => import('@/views/map/DirectionsView.vue')},
    { path: '/signup',         name: 'signup',         component: SignupView        },
    { path: '/login',          name: 'login',          component: LoginView         },
    { path: '/oauth/callback', name: 'kakaoCallback',  component: KakaoCallbackView }, // 카카오 로그인 콜백
    { path: '/mypage',         name: 'mypage',         component: MyPageView         },
    { path: '/profile/setup',  name: 'profileSetup',   component: ProfileSetupView   }, // 카카오 첫 로그인 프로필 설정
    { path: '/exchange', name: 'exchange', component: AssetView},
    { path: '/video', name: 'VideoSearch', component: () => import('@/views/video/VideoSearchView.vue')},
    { path: '/video/:videoId', name: 'VideoDetail', component: VideoDetailView},
    { path: '/products', name: 'productList', component: () => import('@/views/products/ProductListView.vue') },
    { path: '/products/:id', name: 'productDetail', component: () => import('@/views/products/ProductDetailView.vue') },
    { path: '/currency', name: 'currency', component: CurrencyView},
    { path: '/community',        name: 'communityList',   component: () => import('@/views/community/CommunityListView.vue')   },
    { path: '/community/write',  name: 'communityWrite',  component: () => import('@/views/community/CommunityWriteView.vue')  },
    { path: '/community/:id',    name: 'communityDetail', component: () => import('@/views/community/CommunityDetailView.vue') },
  ],
})

export default router
