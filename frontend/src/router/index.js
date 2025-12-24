import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/home/HomeView.vue') },

    // 로그인이 된 영화 목록(메인)
    { path: '/movies', name: 'movies', component: () => import('@/views/movies/MoviesView.vue') },

    // movieId 중심으로 동작하는 구조 (현재 백엔드 movie list/detail API가 없음)
    {
      path: '/movies/:movieId',
      name: 'movieDetail',
      component: () => import('@/views/movies/MovieDetailView.vue'),
      props: true,
    },

    // 커뮤니티(리뷰 목록)도 movieId 기반
    {
      path: '/movies/:movieId/community',
      name: 'community',
      component: () => import('@/views/movies/CommunityView.vue'),
      props: true,
    },
    {
      path: '/person/:personId',
      name: 'personDetail',
      component: () => import('@/views/movies/PersonDetailView.vue'),
      props: true,
    },

    // 리뷰 작성도 movieId 기반
    {
      path: '/movies/:movieId/posts/new',
      name: 'postCreate',
      component: () => import('@/views/movies/posts/PostCreateView.vue'),
      props: true,
    },

    // 리뷰 상세(리뷰 id 기반)
    {
      path: '/posts/:id',
      name: 'postDetail',
      component: () => import('@/views/movies/posts/PostDetailView.vue'),
      props: true,
    },

    { path: '/me', name: 'myHub', component: () => import('@/views/user/UserHubView.vue') },
    { path: '/profile', name: 'profile', component: () => import('@/views/user/ProfileView.vue') },
    { path: '/movie-share', name: 'movieShare', component: () => import('@/views/movies/MovieShareView.vue') },

    // 보관 / 글
    { path: '/my-movies', name: 'myMovies', component: () => import('@/views/user/library/MyMoviesView.vue') },
    { path: '/my-reviews', name: 'myReviews', component: () => import('@/views/user/library/MyReviewsView.vue') },
    { path: '/my-friends', name: 'myFriends', component: () => import('@/views/user/MyFriendsView.vue') },
    { path: '/boards', redirect: { name: 'freeBoard' } },
    { path: '/boards/free', name: 'freeBoard', component: () => import('@/views/boards/FreeBoardView.vue') },
    {
      path: '/boards/free/new',
      name: 'freeBoardCreate',
      component: () => import('@/views/boards/FreeBoardCreateView.vue'),
    },
    {
      path: '/boards/free/:id',
      name: 'freeBoardDetail',
      component: () => import('@/views/boards/FreeBoardDetailView.vue'),
      props: true,
    },
    { path: '/boards/friend', name: 'friendBoard', component: () => import('@/views/boards/FriendBoardView.vue') },
    { path: '/boards/nearby', name: 'nearbyBoard', component: () => import('@/views/boards/NearbyFriendsView.vue') },

    // Auth
    { path: '/login', name: 'login', component: () => import('@/views/auth/LoginView.vue') },
    { path: '/signup', name: 'signup', component: () => import('@/views/auth/SignUpView.vue') },

    { path: '/:pathMatch(.*)*', name: 'notFound', component: () => import('@/views/NotFoundView.vue') },
  ],
})

export default router
