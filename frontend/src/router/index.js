import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import MoviesView from '@/views/MoviesView.vue'   // ✅ 추가
import MovieDetailView from '@/views/MovieDetailView.vue'
import CommunityView from '@/views/CommunityView.vue'
import PostCreateView from '@/views/PostCreateView.vue'
import PostDetailView from '@/views/PostDetailView.vue'
import ProfileView from '@/views/ProfileView.vue'
import MyMoviesView from '@/views/MyMoviesView.vue'
import MyReviewsView from '@/views/MyReviewsView.vue'
import MyFriendsView from '@/views/MyFriendsView.vue'
import MovieShareView from '@/views/MovieShareView.vue'
import FreeBoardView from '@/views/FreeBoardView.vue'
import FriendBoardView from '@/views/FriendBoardView.vue'
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
    { path: '/movie-share', name: 'movieShare', component: MovieShareView },

    // 내 영화 / 내 글
    { path: '/my-movies', name: 'myMovies', component: MyMoviesView },
    { path: '/my-reviews', name: 'myReviews', component: MyReviewsView },
    { path: '/my-friends', name: 'myFriends', component: MyFriendsView },
    { path: '/boards', redirect: { name: 'freeBoard' } },
    { path: '/boards/free', name: 'freeBoard', component: FreeBoardView },
    { path: '/boards/friend', name: 'friendBoard', component: FriendBoardView },

    // Auth
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
    { path: '/signup', name: 'signup', component: () => import('@/views/SignUpView.vue') },

    { path: '/:pathMatch(.*)*', name: 'notFound', component: NotFoundView },
  ],
})

export default router
