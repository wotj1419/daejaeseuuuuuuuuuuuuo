import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/home/HomeView.vue'
import MoviesView from '@/views/movies/MoviesView.vue'   // ??ì¶”ê?
import MovieDetailView from '@/views/movies/MovieDetailView.vue'
import CommunityView from '@/views/movies/CommunityView.vue'
import PostCreateView from '@/views/movies/posts/PostCreateView.vue'
import PostDetailView from '@/views/movies/posts/PostDetailView.vue'
import UserHubView from '@/views/user/UserHubView.vue'
import ProfileView from '@/views/user/ProfileView.vue'
import MyMoviesView from '@/views/user/library/MyMoviesView.vue'
import MyReviewsView from '@/views/user/library/MyReviewsView.vue'
import MyFriendsView from '@/views/user/MyFriendsView.vue'
import MovieShareView from '@/views/movies/MovieShareView.vue'
import FreeBoardView from '@/views/boards/FreeBoardView.vue'
import FreeBoardCreateView from '@/views/boards/FreeBoardCreateView.vue'
import FreeBoardDetailView from '@/views/boards/FreeBoardDetailView.vue'
import FriendBoardView from '@/views/boards/FriendBoardView.vue'
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

    { path: '/me', name: 'myHub', component: UserHubView },
    { path: '/profile', name: 'profile', component: ProfileView },
    { path: '/movie-share', name: 'movieShare', component: MovieShareView },

    // 내 영화 / 내 글
    { path: '/my-movies', name: 'myMovies', component: MyMoviesView },
    { path: '/my-reviews', name: 'myReviews', component: MyReviewsView },
    { path: '/my-friends', name: 'myFriends', component: MyFriendsView },
    { path: '/boards', redirect: { name: 'freeBoard' } },
    { path: '/boards/free', name: 'freeBoard', component: FreeBoardView },
    { path: '/boards/free/new', name: 'freeBoardCreate', component: FreeBoardCreateView },
    { path: '/boards/free/:id', name: 'freeBoardDetail', component: FreeBoardDetailView, props: true },
    { path: '/boards/friend', name: 'friendBoard', component: FriendBoardView },

    // Auth
    { path: '/login', name: 'login', component: () => import('@/views/auth/LoginView.vue') },
    { path: '/signup', name: 'signup', component: () => import('@/views/auth/SignUpView.vue') },

    { path: '/:pathMatch(.*)*', name: 'notFound', component: NotFoundView },
  ],
})

export default router
