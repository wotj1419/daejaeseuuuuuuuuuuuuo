import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import HomeView from '@/views/HomeView.vue'
import MoviesView from '@/views/MoviesView.vue'
import MovieDetailView from '@/views/MovieDetailView.vue'
import CommunityView from '@/views/CommunityView.vue'
import PostCreateView from '@/views/PostCreateView.vue'
import PostDetailView from '@/views/PostDetailView.vue'
import ProfileView from '@/views/ProfileView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },

    // 인증
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },

    // ✅ 로그인 없이 영화 목록(내 데이터)
    { path: '/movies', name: 'movies', component: MoviesView },

    // movieId 중심으로 동작하는 구조
    { path: '/movies/:movieId', name: 'movieDetail', component: MovieDetailView, props: true },

    // 커뮤니티(리뷰 목록)도 movieId 기반
    { path: '/movies/:movieId/community', name: 'community', component: CommunityView, props: true },

    // 리뷰 작성도 movieId 기반 (인증 필요)
    { 
      path: '/movies/:movieId/posts/new', 
      name: 'postCreate', 
      component: PostCreateView, 
      props: true,
      meta: { requiresAuth: true }
    },

    // 리뷰 상세(리뷰 id 기반)
    { path: '/posts/:id', name: 'postDetail', component: PostDetailView, props: true },

    // 프로필 (인증 필요)
    { 
      path: '/profile', 
      name: 'profile', 
      component: ProfileView,
      meta: { requiresAuth: true }
    },

    { path: '/:pathMatch(.*)*', name: 'notFound', component: NotFoundView },
  ],
})

// 네비게이션 가드
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
