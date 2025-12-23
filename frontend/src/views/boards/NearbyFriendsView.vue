<script setup>
import { onMounted, ref } from 'vue'
import { boardsApi } from '@/api/boards'
import { accountsApi } from '@/api/accounts'
import { useRouter } from 'vue-router'

const mapContainer = ref(null)
const mapInstance = ref(null)
const posts = ref([])
const theaters = ref([])
const loading = ref(true)
const error = ref('')
const location = ref({ lat: null, lng: null })
const radiusKm = 20
const mapMarkers = []
const theaterMarkers = []
const theaterMarkerMap = new Map()
const brandSearches = [
  { label: 'CGV', query: 'CGV 영화관' },
  { label: '롯데시네마', query: '롯데시네마 영화관' },
  { label: '메가박스', query: '메가박스 영화관' },
]
const formatMetersToKm = (meters) => (meters == null ? null : (meters / 1000).toFixed(1))
const kakaoAppKey = ref(import.meta.env.VITE_KAKAO_MAP_APP_KEY || '')
const mapKeyLoading = ref(false)
const mapKeyError = ref('')
let circle = null
let infoWindow = null
const router = useRouter()

async function ensureKakaoKey() {
  if (kakaoAppKey.value) {
    return kakaoAppKey.value
  }
  if (mapKeyLoading.value) {
    return kakaoAppKey.value
  }
  mapKeyLoading.value = true
  try {
    const { data } = await boardsApi.getMapConfig()
    kakaoAppKey.value = data?.kakao_map_app_key || ''
    if (!kakaoAppKey.value) {
      mapKeyError.value = '카카오맵 앱 키가 설정되어 있지 않습니다.'
      throw new Error(mapKeyError.value)
    }
    mapKeyError.value = ''
    return kakaoAppKey.value
  } catch (err) {
    console.error('Failed to load Kakao map key', err)
    if (!mapKeyError.value) {
      mapKeyError.value = '카카오맵 앱 키를 불러올 수 없습니다.'
    }
    throw err
  } finally {
    mapKeyLoading.value = false
  }
}

async function loadKakaoScript() {
  const key = await ensureKakaoKey()
  if (!key) {
    throw new Error(mapKeyError.value || '카카오맵 앱 키가 없습니다.')
  }
  if (window.kakao?.maps) {
    return window.kakao.maps
  }
  return new Promise((resolve, reject) => {
    const existingScript = document.getElementById('kakao-map-script')
    if (existingScript) {
      existingScript.addEventListener('load', () => resolve(window.kakao.maps))
      existingScript.addEventListener('error', reject)
      return
    }
    const script = document.createElement('script')
    script.id = 'kakao-map-script'
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${key}&libraries=services,clusterer`
    script.onload = () => resolve(window.kakao.maps)
    script.onerror = reject
    document.head.appendChild(script)
  })
}

async function initMap() {
  if (!mapContainer.value) return
  try {
    await loadKakaoScript()
    const center = new window.kakao.maps.LatLng(
      location.value.lat || 37.5665,
      location.value.lng || 126.9784
    )
    mapInstance.value = new window.kakao.maps.Map(mapContainer.value, {
      center,
      level: 5,
      mapTypeId: window.kakao.maps.MapTypeId.ROADMAP,
    })
    infoWindow = new window.kakao.maps.InfoWindow({ zIndex: 1 })
    drawRadiusCircle(center)
  } catch (err) {
    error.value = err.message || '지도를 불러오지 못했습니다.'
  }
}

function drawRadiusCircle(center) {
  if (!mapInstance.value || !window.kakao?.maps) return
  if (circle) {
    circle.setMap(null)
  }
  circle = new window.kakao.maps.Circle({
    center,
    radius: radiusKm * 1000,
    map: mapInstance.value,
    strokeWeight: 3,
    strokeColor: '#1ed760',
    strokeOpacity: 0.8,
    fillColor: 'rgba(29, 185, 84, 0.15)',
    fillOpacity: 0.4,
  })
}

function centerMap(coords) {
  if (!mapInstance.value || !coords.lat || !coords.lng) return
  const target = new window.kakao.maps.LatLng(coords.lat, coords.lng)
  mapInstance.value.setCenter(target)
  drawRadiusCircle(target)
}

function clearMarkers(list, registry) {
  list.forEach((marker) => marker.setMap(null))
  list.length = 0
  if (registry) {
    registry.clear()
  }
}

function createPostMarker(post) {
  if (!window.kakao?.maps || !mapInstance.value) return
  if (!post.latitude || !post.longitude) return
  const latLng = new window.kakao.maps.LatLng(post.latitude, post.longitude)
  const marker = new window.kakao.maps.Marker({
    position: latLng,
    map: mapInstance.value,
    title: post.title,
  })
  window.kakao.maps.event.addListener(marker, 'click', () => {
    if (!infoWindow) return
    infoWindow.setContent(`
      <div class="info-window">
        <strong>${post.title}</strong>
        <p>${post.content?.substring(0, 80) || '내용이 없습니다.'}</p>
        <small>거리 ${post.distance_km?.toFixed(1) || '0.0'} km</small>
      </div>
    `)
    infoWindow.open(mapInstance.value, marker)
  })
  mapMarkers.push(marker)
}

function createTheaterMarker(theater) {
  if (!window.kakao?.maps || !mapInstance.value) return
  if (!theater.latitude || !theater.longitude) return
  const latLng = new window.kakao.maps.LatLng(theater.latitude, theater.longitude)
  const marker = new window.kakao.maps.Marker({
    position: latLng,
    map: mapInstance.value,
  })
  window.kakao.maps.event.addListener(marker, 'click', () => {
    showTheaterInfoWindow(theater, marker)
  })
  theaterMarkers.push(marker)
  theaterMarkerMap.set(theater.title, marker)
}

function showTheaterInfoWindow(theater, marker) {
  if (!infoWindow || !marker) return
  const distanceLabel = formatMetersToKm(theater.distance)
    ? `<small>${formatMetersToKm(theater.distance)} km 이내</small>`
    : ''
  const contact = theater.telephone || '전화번호 정보 없음'
  const link = theater.place_url
    ? `<a href="${theater.place_url}" target="_blank" rel="noreferrer">카카오맵에서 상영시간 보기</a>`
    : ''
  infoWindow.setContent(`
    <div class="info-window">
      <strong>${theater.title}</strong>
      <p>${theater.address}</p>
      ${distanceLabel}
      <small>${contact}</small>
      ${link}
    </div>
  `)
  infoWindow.open(mapInstance.value, marker)
  centerMap({ lat: theater.latitude, lng: theater.longitude })
}

function focusTheater(theater) {
  if (!theater || !mapInstance.value) return
  const marker = theaterMarkerMap.get(theater.title)
  if (marker) {
    showTheaterInfoWindow(theater, marker)
    return
  }
  const target = new window.kakao.maps.LatLng(theater.latitude, theater.longitude)
  mapInstance.value.setCenter(target)
  drawRadiusCircle(target)
}

function focusBrand(brand) {
  if (!brand) return
  const match = theaters.value.find((theater) =>
    theater.title?.toLowerCase().includes(brand.label.toLowerCase())
  )
  if (match) {
    focusTheater(match)
  } else if (theaters.value.length) {
    focusTheater(theaters.value[0])
  }
}

async function refreshNearby() {
  if (!location.value.lat || !location.value.lng) {
    loading.value = false
    return
  }
  loading.value = true
  try {
    const [postResp, theaterResp] = await Promise.all([
      boardsApi.getNearbyPosts({
        lat: location.value.lat,
        lng: location.value.lng,
        radius: radiusKm,
      }),
      boardsApi.getNearbyTheaters({
        lat: location.value.lat,
        lng: location.value.lng,
        radius: radiusKm * 1000,
      }),
    ])
    posts.value = postResp.data.results || []
    theaters.value = theaterResp.data.results || []
    clearMarkers(mapMarkers)
    clearMarkers(theaterMarkers, theaterMarkerMap)
    posts.value.forEach(createPostMarker)
    theaters.value.forEach(createTheaterMarker)
  } catch (err) {
    console.error(err)
    error.value = '주변 정보를 불러오는 중 문제가 발생했습니다.'
  } finally {
    loading.value = false
  }
}

async function useBrowserLocation() {
  if (!navigator.geolocation) {
    error.value = '위치 정보를 사용할 수 없습니다.'
    return
  }
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      location.value.lat = position.coords.latitude
      location.value.lng = position.coords.longitude
      centerMap(location.value)
      try {
        await accountsApi.updateLocation({
          latitude: location.value.lat,
          longitude: location.value.lng,
        })
      } catch {
        // ignore
      }
      await refreshNearby()
    },
    (err) => {
      error.value = '위치 접근을 허용해주세요.'
      console.error(err)
    }
  )
}

async function loadStoredLocation() {
  try {
    const { data } = await accountsApi.getLocation()
    if (data.latitude && data.longitude) {
      location.value.lat = data.latitude
      location.value.lng = data.longitude
    }
  } catch (err) {
    console.warn('위치 로드 실패', err)
  }
}

async function initNearbyExperience() {
  await loadStoredLocation()
  await initMap()
  if (!location.value.lat || !location.value.lng) {
    useBrowserLocation()
  } else {
    centerMap(location.value)
    await refreshNearby()
  }
}

onMounted(() => {
  initNearbyExperience()
})
</script>

<template>
  <div class="nearby-page">
    <section class="page-header">
      <div>
        <p class="hero-label">Nearby</p>
        <h1>?? ?? ?? ??</h1>
        <p>?????? ? ???? 20km ?? ?? ?? ???? ?? ?? ?? ??? ????? ??? ??????.</p>
      </div>
      <div class="page-actions">
        <button type="button" class="primary-btn" @click="useBrowserLocation">
          ?? ?? ?? ????
        </button>
        <router-link class="ghost-btn" :to="{ name: 'friendBoard' }">?? ?? ???</router-link>
      </div>
    </section>

    <section class="map-panel">
      <div ref="mapContainer" class="map-container">
        <span v-if="mapKeyError" class="map-placeholder">{{ mapKeyError }}</span>
        <span v-else-if="!kakaoAppKey && mapKeyLoading" class="map-placeholder">
          카카오맵 키를 불러오는 중입니다...
        </span>
        <span v-else-if="!kakaoAppKey" class="map-placeholder">
          카카오맵 키가 설정되어 있지 않습니다. 관리자에게 문의해주세요.
        </span>
      </div>
      <aside class="map-details">
        <div class="brand-links">
          <button
            v-for="brand in brandSearches"
            :key="brand.label"
            type="button"
            class="brand-link"
            @click="focusBrand(brand)"
          >
            {{ brand.label }} 상영정보
          </button>
        </div>
        <h3>?? ?? ??</h3>
        <p class="subtitle">{{ radiusKm }}km ?? ??? ??? ?? ??? ???? ?? ?????.</p>
        <div v-if="loading" class="loader">??? ???? ????...</div>
        <div v-else>
          <article
            v-for="post in posts"
            :key="post.id"
            class="post-card"
            @click="router.push({ name: 'friendBoard' })"
          >
            <header>
              <strong>{{ post.title }}</strong>
              <span>{{ post.distance_km?.toFixed(1) || '0.0' }} km</span>
            </header>
            <p>{{ post.content || '?? ??? ?????.' }}</p>
            <div class="meta">
              <span>??? {{ post.author_username }}</span>
              <span>{{ new Date(post.created_at).toLocaleString('ko-KR') }}</span>
            </div>
          </article>
          <p v-if="!posts.length" class="empty-state">?? {{ radiusKm }}km ?? ?? ?? ????.</p>
        </div>
        <div class="divider" />
        <h3>?? ???</h3>
        <p class="subtitle">CGV, ?????, ????? ?????? ?? ??? ? ????.</p>
        <div v-if="theaters.length" class="theater-list">
          <article
            v-for="theater in theaters"
            :key="theater.place_url || theater.title"
            class="theater-card"
          >
            <header>
              <strong>{{ theater.title }}</strong>
              <span v-if="formatMetersToKm(theater.distance)">
                {{ formatMetersToKm(theater.distance) }} km
              </span>
            </header>
            <p>{{ theater.category }}</p>
            <p class="meta">{{ theater.address }}</p>
            <p class="meta">{{ theater.telephone || '???? ?? ??' }}</p>
            <a
              v-if="theater.place_url"
              class="theater-link"
              :href="theater.place_url"
              target="_blank"
              rel="noreferrer"
            >
              ?????? ???? ??
            </a>
          </article>
        </div>
        <p v-else class="empty-state">?? {{ radiusKm }}km ??? ??? ??? ??? ? ????.</p>
      </aside>
    </section>
    <p v-if="error" class="error">{{ error }}</p>
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
  padding: 60px 50px 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.page-header h1 {
  margin: 6px 0;
  font-size: 36px;
}

.hero-label {
  font-size: 12px;
  letter-spacing: 0.6em;
  text-transform: uppercase;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.6);
}

.page-actions {
  display: flex;
  gap: 12px;
}

.primary-btn,
.ghost-btn {
  border-radius: 999px;
  padding: 12px 20px;
  border: none;
  font-weight: 700;
  cursor: pointer;
}

.primary-btn {
  background: linear-gradient(135deg, #1db954, #1ed760);
  color: #000;
}

.ghost-btn {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.map-panel {
  display: flex;
  gap: 24px;
  padding: 0 50px;
}

.map-container {
  flex: 1;
  min-height: 480px;
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
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 20px;
}

.brand-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.brand-link {
  flex: 1;
  text-align: center;
  border-radius: 999px;
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(29, 185, 84, 0.15);
  color: #dff5e5;
  font-size: 0.85rem;
  text-decoration: none;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.brand-link:hover {
  border-color: #1db954;
  transform: translateY(-1px);
}

.subtitle {
  margin: 0;
  color: #9fb9ac;
  font-size: 0.9rem;
}

.loader {
  padding: 32px;
  text-align: center;
  color: #bbb;
}

.post-card,
.theater-card {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.02);
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.post-card:hover,
.theater-card:hover {
  border-color: #1db954;
  transform: translateY(-2px);
}

.post-card header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.theater-card header span {
  font-size: 0.8rem;
  color: #9fb9ac;
}

.post-card p {
  margin: 4px 0 0;
  color: #dbece0;
  font-size: 0.95rem;
}

.meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #8da99b;
  margin-top: 6px;
}

.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
  margin: 10px 0;
}

.theater-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.theater-link {
  margin-top: 6px;
  display: inline-flex;
  color: #1ed760;
  font-weight: 600;
  font-size: 0.85rem;
  text-decoration: none;
}

.empty-state {
  color: #8da99b;
  font-size: 0.9rem;
}

.error {
  padding: 20px 50px;
  color: #ff6b6b;
}

.naver-pin {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.45);
}
.naver-pin.post-pin {
  background: #1ed760;
}
.naver-pin.theater-pin {
  background: #326cd6;
}

.info-window {
  color: #000;
  line-height: 1.3;
}
</style>
