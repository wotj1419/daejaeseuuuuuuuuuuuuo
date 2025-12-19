import { defineStore } from 'pinia'

const LS_KEY = 'moviemate_user_signals_v1'

function loadSignals() {
  try {
    return (
      JSON.parse(localStorage.getItem(LS_KEY)) ?? {
        events: [],
        genreScore: {},
        seenCount: {},
      }
    )
  } catch {
    return { events: [], genreScore: {}, seenCount: {} }
  }
}

function saveSignals(signals) {
  localStorage.setItem(LS_KEY, JSON.stringify(signals))
}

function recencyWeight(ts) {
  const days = (Date.now() - ts) / (1000 * 60 * 60 * 24)
  return Math.exp(-days / 7)
}

export const useRecommendationStore = defineStore('recommendation', {
  state: () => ({ signals: loadSignals() }),

  actions: {
    trackEvent({ type, movie, dwellSeconds = 0 }) {
      const ts = Date.now()

      this.signals.events.unshift({
        type,
        movieId: movie?.id ?? null,
        genres: movie?.genres ?? [],
        ts,
        dwellSeconds,
      })
      this.signals.events = this.signals.events.slice(0, 300)

      if (movie?.id) {
        this.signals.seenCount[movie.id] = (this.signals.seenCount[movie.id] ?? 0) + 1
      }

      const base = type === 'like' ? 5 : type === 'view' ? 2 : 0
      const dwellBonus = dwellSeconds >= 30 ? 1 : 0
      const w = base + dwellBonus

      const genres = movie?.genres ?? []
      for (const g of genres) {
        const gid = typeof g === 'object' ? g.id : g
        this.signals.genreScore[gid] = (this.signals.genreScore[gid] ?? 0) + w
      }

      saveSignals(this.signals)
    },

    recommend(movies, { limit = 20, exploreRate = 0.2 } = {}) {
      const genreScore = this.signals.genreScore
      const seenCount = this.signals.seenCount
      const totalPref = Object.values(genreScore).reduce((a, b) => a + b, 0) || 1

      // 최근 이벤트 기반 부스트
      const recentBoost = {}
      for (const ev of this.signals.events.slice(0, 80)) {
        if (!ev.genres?.length) continue
        const rw = recencyWeight(ev.ts)
        const mult = ev.type === 'like' ? 2.0 : 1.0
        for (const g of ev.genres) {
          const gid = typeof g === 'object' ? g.id : g
          recentBoost[gid] = (recentBoost[gid] ?? 0) + rw * mult
        }
      }

      const popularityScore = (m) => {
        const rating = Number(m.vote_average ?? m.rating ?? 0) // 0~10
        const votes = Number(m.vote_count ?? 0)
        const pop = Number(m.popularity ?? 0)
        return (rating / 10) * 2 + Math.log10(votes + 1) * 0.8 + Math.log10(pop + 1) * 0.8
      }

      const contentScore = (m) => {
        const genres = m.genres ?? []
        if (!genres.length) return 0
        let s = 0
        for (const g of genres) {
          const gid = typeof g === 'object' ? g.id : g
          const base = (genreScore[gid] ?? 0) / totalPref
          const recent = recentBoost[gid] ?? 0
          s += base * 3 + recent * 1.2
        }
        return s / genres.length
      }

      const seenPenalty = (m) => Math.min(2.5, (seenCount[m.id] ?? 0) * 0.6)

      const scored = movies.map((m) => ({
        movie: m,
        score: contentScore(m) + popularityScore(m) + Math.random() * 0.2 - seenPenalty(m),
      }))

      scored.sort((a, b) => b.score - a.score)

      const topCount = Math.floor(limit * (1 - exploreRate))
      const exploreCount = limit - topCount

      const top = scored.slice(0, topCount).map((x) => x.movie)

      // 탐색: 중간 이하에서 랜덤 섞기
      const pool = scored.slice(Math.min(80, scored.length)).filter((x) => x.score > -1)
      const explore = []
      for (let i = 0; i < exploreCount && pool.length; i++) {
        const idx = Math.floor(Math.random() * pool.length)
        explore.push(pool.splice(idx, 1)[0].movie)
      }

      return [...top, ...explore]
    },
  },
})
