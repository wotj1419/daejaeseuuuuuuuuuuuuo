import { defineStore } from 'pinia'
import { moviesApi } from '@/api/movies'

export const useRecommendationStore = defineStore('recommendation', {
  state: () => ({
    items: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchRecommend(movieId) {
      this.loading = true
      this.error = null
      try {
        const { data } = await moviesApi.recommend(movieId)
        this.items = data
      } catch (e) {
        console.error(e)
        this.error = '추천 데이터를 불러오지 못했어요.'
        this.items = []
      } finally {
        this.loading = false
      }
    },
  },
})
