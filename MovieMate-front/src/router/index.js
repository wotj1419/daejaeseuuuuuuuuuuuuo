import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import MoviesView from '@/views/MoviesView.vue'   // ✅ 추가
import MovieDetailView from '@/views/MovieDetailView.vue'
import CommunityView from '@/views/CommunityView.vue'
import PostCreateView from '@/views/PostCreateView.vue'
import PostDetailView from '@/views/PostDetailView.vue'
import ProfileView from '@/views/ProfileView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },

    // ✅ 로그인 없이 영화 목록(내 데이터)
    { path: '/movies', name: 'movies', component: MoviesView },

    // movieId 중심으로 동작하는 구조 (현재 백엔드가 movie list/detail API가 없으므로)
    { path: '/movies/:movieId', name: 'movieDetail', component: MovieDetailView, props: true },

    // 커뮤니티(리뷰 목록)도 movieId 기반
    { path: '/movies/:movieId/community', name: 'community', component: CommunityView, props: true },

    // 리뷰 작성도 movieId 기반
    { path: '/movies/:movieId/posts/new', name: 'postCreate', component: PostCreateView, props: true },

    // 리뷰 상세(리뷰 id 기반)
    { path: '/posts/:id', name: 'postDetail', component: PostDetailView, props: true },

    { path: '/profile', name: 'profile', component: ProfileView },

    { path: '/:pathMatch(.*)*', name: 'notFound', component: NotFoundView },
  ],
})

export default router
