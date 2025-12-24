<script setup>
import { computed, onMounted, ref } from 'vue'
import { boardsApi } from '@/api/boards'

const mapContainer = ref(null)
const kakaoMaps = ref(null)
const mapInstance = ref(null)
const infoWindow = ref(null)
const markers = []
const theaters = ref([])
const loading = ref(false)
const error = ref('')
const mapKeyLoading = ref(false)
const mapKeyError = ref('')
const kakaoAppKey = ref(
  import.meta.env.VITE_KAKAO_API_KEY || import.meta.env.VITE_KAKAO_MAP_APP_KEY || ''
)
const center = ref({ lat: 37.5665, lng: 126.9784 })
const selectedBrand = ref('전체')
const searchRadius = 10000 // meters
const page = ref(1)
const pageSize = 5

const brands = [
  { label: '전체', query: '영화관' },
  { label: 'CGV', query: 'CGV 영화관' },
  { label: '롯데시네마', query: '롯데시네마' },
  { label: '메가박스', query: '메가박스' },
]

const totalPages = computed(() => Math.max(1, Math.ceil(theaters.value.length / pageSize)))
const pagedTheaters = computed(() => {
  const start = (page.value - 1) * pageSize
  return theaters.value.slice(start, start + pageSize)
})

async function ensureKakaoKey() {
  if (kakaoAppKey.value) return kakaoAppKey.value
  if (mapKeyLoading.value) return kakaoAppKey.value
  mapKeyLoading.value = true
  try {
    const { data } = await boardsApi.getMapConfig()
    kakaoAppKey.value = data?.kakao_api_key || data?.kakao_map_app_key || ''
    if (!kakaoAppKey.value) {
      mapKeyError.value = '카카오 지도 키를 불러오지 못했습니다.'
      throw new Error(mapKeyError.value)
    }
    return kakaoAppKey.value
  } catch (err) {
    console.error('Failed to load Kakao map key', err)
    if (!mapKeyError.value) {
      mapKeyError.value = '지도 키를 불러오는 중 문제가 발생했습니다.'
    }
    throw err
  } finally {
    mapKeyLoading.value = false
  }
}

async function loadKakaoScript() {
  const key = await ensureKakaoKey()
  if (!key) throw new Error(mapKeyError.value || '지도 키가 없습니다.')

  if (window.kakao?.maps) {
    kakaoMaps.value = window.kakao.maps
    return kakaoMaps.value
  }

  return new Promise((resolve, reject) => {
    const existing = document.getElementById('kakao-map-script')
    if (existing) {
      existing.addEventListener('load', () => {
        window.kakao.maps.load(() => {
          kakaoMaps.value = window.kakao.maps
          resolve(window.kakao.maps)
        })
      })
      existing.addEventListener('error', () => {
        mapKeyError.value = '카카오 지도 스크립트를 불러오지 못했습니다.'
        reject(new Error(mapKeyError.value))
      })
      return
    }
    const script = document.createElement('script')
    script.id = 'kakao-map-script'
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?autoload=false&appkey=${key}&libraries=services`
    script.onload = () => {
      window.kakao.maps.load(() => {
        kakaoMaps.value = window.kakao.maps
        resolve(window.kakao.maps)
      })
    }
    script.onerror = () => {
      mapKeyError.value = '카카오 지도 스크립트를 불러오지 못했습니다.'
      reject(new Error(mapKeyError.value))
    }
    document.head.appendChild(script)
  })
}

function clearMarkers() {
  markers.forEach((marker) => marker.setMap(null))
  markers.length = 0
}

function placeMarkers(items) {
  clearMarkers()
  if (!kakaoMaps.value || !mapInstance.value) return
  const bounds = new kakaoMaps.value.LatLngBounds()
  items.forEach((item) => {
    const position = new kakaoMaps.value.LatLng(Number(item.y), Number(item.x))
    const marker = new kakaoMaps.value.Marker({ position, map: mapInstance.value })
    kakaoMaps.value.event.addListener(marker, 'click', () => {
      const distanceLabel = item.distance ? `${(item.distance / 1000).toFixed(1)} km` : ''
      infoWindow.value.setContent(`
        <div class="info-window">
          <strong>${item.place_name}</strong>
          <p>${item.road_address_name || item.address_name || ''}</p>
          <small>${item.phone || '연락처 없음'} ${distanceLabel}</small>
        </div>
      `)
      infoWindow.value.open(mapInstance.value, marker)
    })
    markers.push(marker)
    bounds.extend(position)
  })
  if (!bounds.isEmpty()) {
    mapInstance.value.setBounds(bounds)
  }
}

function syncCenterFromMap() {
  if (!mapInstance.value || !kakaoMaps.value) return
  const c = mapInstance.value.getCenter()
  center.value = { lat: c.getLat(), lng: c.getLng() }
}

function goToPage(newPage) {
  page.value = Math.min(totalPages.value, Math.max(1, newPage))
}

function searchTheaters(brand) {
  if (!kakaoMaps.value || !mapInstance.value) return
  selectedBrand.value = brand.label
  loading.value = true
  theaters.value = []
  page.value = 1
  const places = new kakaoMaps.value.services.Places()
  const location = new kakaoMaps.value.LatLng(center.value.lat, center.value.lng)
  places.keywordSearch(
    brand.query,
    (data, status) => {
      loading.value = false
      if (status === kakaoMaps.value.services.Status.OK) {
        theaters.value = data
        page.value = 1
        placeMarkers(data)
        error.value = ''
      } else if (status === kakaoMaps.value.services.Status.ZERO_RESULT) {
        theaters.value = []
        clearMarkers()
        page.value = 1
        error.value = '주변에 해당 브랜드 영화관이 없습니다.'
      } else {
        theaters.value = []
        clearMarkers()
        page.value = 1
        error.value = '영화관을 불러오지 못했습니다.'
      }
    },
    {
      location,
      radius: searchRadius,
      size: 15,
    }
  )
}

function searchAtCurrentCenter() {
  if (!mapInstance.value || !kakaoMaps.value) return
  syncCenterFromMap()
  const targetBrand = brands.find((b) => b.label === selectedBrand.value) || brands[0]
  searchTheaters(targetBrand)
}

async function initMap() {
  try {
    await loadKakaoScript()
    if (!mapContainer.value || !kakaoMaps.value) return
    const initial = new kakaoMaps.value.LatLng(center.value.lat, center.value.lng)
    mapInstance.value = new kakaoMaps.value.Map(mapContainer.value, {
      center: initial,
      level: 4,
      draggable: true,
    })
    infoWindow.value = new kakaoMaps.value.InfoWindow({ zIndex: 1 })
    kakaoMaps.value.event.addListener(mapInstance.value, 'idle', syncCenterFromMap)
    searchTheaters(brands[0])
  } catch (err) {
    console.error(err)
    error.value = err.message || '지도를 불러오지 못했습니다.'
  }
}

function useMyLocation() {
  if (!navigator.geolocation) {
    error.value = '브라우저에서 위치 정보를 지원하지 않습니다.'
    return
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      center.value = { lat: pos.coords.latitude, lng: pos.coords.longitude }
      if (mapInstance.value && kakaoMaps.value) {
        const target = new kakaoMaps.value.LatLng(center.value.lat, center.value.lng)
        mapInstance.value.setCenter(target)
      }
      searchTheaters(brands.find((b) => b.label === selectedBrand.value) || brands[0])
    },
    () => {
      error.value = '위치 권한을 허용해야 주변 영화관을 찾을 수 있습니다.'
    }
  )
}

onMounted(() => {
  initMap()
})
</script>

<template>
  <div class="nearby-page">
    <section class="page-header">
      <div>
        <p class="hero-label">Friends</p>
        <h1>주변 영화관에서 찾기</h1>
        <p class="subtitle">
          
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="primary-btn" @click="useMyLocation">내 위치로 찾기</button>
      </div>
    </section>

    <section class="map-panel">
      <div ref="mapContainer" class="map-container">
        <span v-if="mapKeyError" class="map-placeholder">{{ mapKeyError }}</span>
        <span v-else-if="!kakaoAppKey && mapKeyLoading" class="map-placeholder">
          카카오 지도 키를 불러오는 중입니다...
        </span>
        <span v-else-if="!kakaoAppKey" class="map-placeholder">
          카카오 지도 키가 없습니다. 백엔드 .env에 KAKAO_API_KEY, 프런트 .env에 VITE_KAKAO_API_KEY를
          설정해주세요.
        </span>
      </div>
      <aside class="map-details">
        <div class="brand-links">
          <button
            v-for="brand in brands"
            :key="brand.label"
            type="button"
            class="brand-link"
            :class="{ active: selectedBrand === brand.label }"
            @click="searchTheaters(brand)"
          >
            {{ brand.label }}
          </button>
        </div>
        <button type="button" class="secondary-btn" @click="searchAtCurrentCenter">
          현재 위치로 다시 검색
        </button>
        <p class="subtitle">
          지도 중심 기준 {{ searchRadius / 1000 }}km 반경의 영화관을 보여줍니다.
        </p>
        <div v-if="loading" class="loader">주변 영화관을 불러오는 중...</div>
        <div v-else-if="theaters.length">
          <article v-for="theater in pagedTheaters" :key="theater.id" class="theater-card">
            <header>
              <strong>{{ theater.place_name }}</strong>
              <span v-if="theater.distance">{{ (theater.distance / 1000).toFixed(1) }} km</span>
            </header>
            <p>{{ theater.category_name }}</p>
            <p class="meta">{{ theater.road_address_name || theater.address_name }}</p>
            <p class="meta">{{ theater.phone || '전화번호 없음' }}</p>
            <a
              v-if="theater.place_url"
              class="theater-link"
              :href="theater.place_url"
              target="_blank"
              rel="noreferrer"
            >
              자세히 보기
            </a>
          </article>
          <div v-if="totalPages > 1" class="pagination">
            <button type="button" @click="goToPage(page - 1)" :disabled="page === 1">이전</button>
            <span>{{ page }} / {{ totalPages }}</span>
            <button type="button" @click="goToPage(page + 1)" :disabled="page === totalPages">
              다음
            </button>
          </div>
        </div>
        <p v-else class="empty-state">
          {{ error || '이 주변에 영화관을 찾지 못했습니다.' }}
        </p>
      </aside>
    </section>
  </div>
</template>

<style scoped>
.nearby-page {
  min-height: 100vh;
  background: #030303;
  color: #fff;
  padding-bottom: 60px;
}

.page-header {
  padding: 50px 50px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.page-header h1 {
  margin: 6px 0;
  font-size: 34px;
}

.hero-label {
  font-size: 12px;
  letter-spacing: 0.6em;
  text-transform: uppercase;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.6);
}

.subtitle {
  color: #9fb9ac;
  font-size: 0.95rem;
  margin: 0;
}

.page-actions {
  display: flex;
  gap: 12px;
}

.primary-btn {
  border-radius: 999px;
  padding: 12px 20px;
  border: none;
  font-weight: 700;
  cursor: pointer;
  background: linear-gradient(135deg, #1db954, #1ed760);
  color: #000;
}

.map-panel {
  display: flex;
  gap: 24px;
  padding: 0 50px;
  flex-wrap: wrap;
}

.map-container {
  flex: 1 1 520px;
  min-height: 520px;
  border-radius: 24px;
  background: #0c0c0c;
  border: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
  overflow: hidden;
}

.map-container .map-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bbb;
  padding: 24px;
  text-align: center;
}

.map-details {
  width: 340px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 16px;
  max-height: 560px;
  overflow: auto;
}

.brand-links {
  display: flex;
  gap: 8px;
}

.brand-link {
  flex: 1;
  text-align: center;
  border-radius: 999px;
  padding: 9px 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(29, 185, 84, 0.12);
  color: #dff5e5;
  font-size: 0.9rem;
  text-decoration: none;
  transition: border-color 0.2s ease, transform 0.2s ease, background 0.2s ease;
}

.brand-link.active {
  background: linear-gradient(135deg, #1db954, #1ed760);
  color: #000;
  border-color: #1ed760;
}

.brand-link:hover {
  border-color: #1db954;
  transform: translateY(-1px);
}

.secondary-btn {
  width: 100%;
  margin-top: 4px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.loader {
  padding: 20px;
  text-align: center;
  color: #bbb;
}

.theater-card {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.02);
}

.theater-card header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.theater-card strong {
  font-size: 0.98rem;
}

.theater-card header span {
  font-size: 0.78rem;
  color: #9fb9ac;
}

.theater-card p {
  margin: 3px 0;
  color: #dbece0;
  font-size: 0.9rem;
}

.meta {
  font-size: 0.82rem;
  color: #8da99b;
}

.theater-link {
  margin-top: 4px;
  display: inline-flex;
  color: #1ed760;
  font-weight: 600;
  font-size: 0.86rem;
  text-decoration: none;
}

.pagination {
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 0.9rem;
}

.pagination button {
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-state {
  color: #8da99b;
  font-size: 0.9rem;
}

.info-window {
  color: #000;
  line-height: 1.3;
}

@media (max-width: 1024px) {
  .map-panel {
    flex-direction: column;
  }

  .map-details {
    width: 100%;
    max-height: none;
  }
}
</style>
