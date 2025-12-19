import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import MovieDetailView from '@/views/MovieDetailView.vue'

import CommunityView from '@/views/CommunityView.vue'
import PostDetailView from '@/views/PostDetailView.vue'
import PostCreateView from '@/views/PostCreateView.vue'
import ProfileView from '@/views/ProfileView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },

    { path: '/movies/:id', name: 'movieDetail', component: MovieDetailView },

    { path: '/community', name: 'community', component: CommunityView },
    { path: '/community/posts/new', name: 'postCreate', component: PostCreateView },
    { path: '/community/posts/:id', name: 'postDetail', component: PostDetailView },

    { path: '/profile', name: 'profile', component: ProfileView },

    { path: '/:pathMatch(.*)*', name: 'notFound', component: NotFoundView },
  ],
})

export default router``
