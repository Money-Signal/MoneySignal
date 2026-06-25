<template>
  <div class="page-outer">
    <div class="page-container">
      <PageHeader title="길찾기" description="출발지와 목적지를 확인하고 경로를 선택하세요." />

      <div class="directions-wrapper">
        <!-- 왼쪽: 설정 패널 -->
        <div class="side-panel">

          <!-- 이동수단 선택 (최상단) -->
          <div class="panel-section mode-section">
            <div class="section-label">이동 수단 선택</div>
            <div class="mode-btns">
              <button
                class="mode-btn"
                :class="{ active: travelMode === 'car', loading: routeLoading && travelMode === 'car' }"
                @click="selectMode('car')"
                :disabled="routeLoading"
              >
                <img v-if="routeLoading && travelMode === 'car'" :src="spinnerSvg" class="spinner-img btn-spinner" />
                <i v-else class="bi bi-car-front-fill"></i>
                자동차
              </button>
              <button
                class="mode-btn"
                :class="{ active: travelMode === 'walk' }"
                @click="selectMode('walk')"
              >
                <i class="bi bi-person-walking"></i>
                도보 <span class="kakaomap-badge">카카오맵</span>
              </button>
            </div>
            <!-- 출발지 미설정 안내 -->
            <p v-if="!originCoords" class="mode-hint">
              <i class="bi bi-info-circle"></i> 출발지를 먼저 설정해 주세요
            </p>
          </div>

          <!-- 경로 요약 -->
          <div v-if="routeSummary" class="route-summary">
            <div class="summary-row">
              <div class="summary-item">
                <span class="summary-label">거리</span>
                <span class="summary-value">{{ formatDistance(routeSummary.distance) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">예상 시간</span>
                <span class="summary-value">{{ formatDuration(routeSummary.duration) }}</span>
              </div>
            </div>
            <button class="clear-btn" @click="clearRoute">
              <i class="bi bi-x-circle"></i> 경로 지우기
            </button>
          </div>

          <!-- 출발지 -->
          <div class="panel-section">
            <div class="section-label">
              <span class="dot origin-dot"></span>
              출발지
            </div>

            <div v-if="originMode === 'gps'" class="location-status">
              <div v-if="originLoading" class="status-row loading">
                <img :src="spinnerSvg" class="spinner-img" /> 현재 위치 확인 중...
              </div>
              <div v-else-if="originCoords" class="status-row success">
                <i class="bi bi-geo-alt-fill"></i> 현재 위치 사용 중
                <button class="text-btn" @click="switchToManual">직접 입력</button>
              </div>
              <div v-else class="status-row warn">
                <i class="bi bi-exclamation-circle"></i> 위치 권한이 거부되었어요
                <button class="text-btn" @click="retryGps">다시 시도</button>
              </div>
            </div>

            <div v-if="originMode === 'manual'" class="manual-input-area">
              <!-- 선택된 출발지 확인 표시 -->
              <div v-if="originCoords && selectedOriginName" class="origin-confirmed">
                <i class="bi bi-check-circle-fill"></i>
                <div>
                  <p class="confirmed-name">{{ selectedOriginName }}</p>
                  <p class="confirmed-addr">{{ selectedOriginAddr }}</p>
                </div>
                <button class="text-btn reset-btn" @click="resetOrigin">변경</button>
              </div>

              <!-- 입력 폼 (출발지 미선택 상태에서만 표시) -->
              <template v-else>
                <div class="input-row">
                  <input
                    v-model="originQuery"
                    placeholder="출발지 주소 또는 장소명 입력"
                    @keyup.enter="searchOrigin"
                    class="addr-input"
                  />
                  <button class="search-mini-btn" @click="searchOrigin">검색</button>
                </div>
                <ul v-if="originResults.length" class="addr-results">
                  <li
                    v-for="(r, i) in originResults"
                    :key="i"
                    @click="selectOrigin(r)"
                  >
                    <strong>{{ r.place_name || r.address_name }}</strong>
                    <span>{{ r.road_address_name || r.address_name }}</span>
                  </li>
                </ul>
                <button class="text-btn mt-4" @click="retryGps">
                  <i class="bi bi-crosshair"></i> GPS로 현재 위치 사용
                </button>
              </template>
            </div>
          </div>

          <!-- 구분선 -->
          <div class="route-divider">
            <div class="divider-line"></div>
            <div class="swap-area"><i class="bi bi-arrow-down"></i></div>
          </div>

          <!-- 목적지 -->
          <div class="panel-section">
            <div class="section-label">
              <span class="dot dest-dot"></span>
              목적지
            </div>

            <!-- 목적지 확인 카드 -->
            <div v-if="destCoords && !editingDest" class="origin-confirmed dest-confirmed">
              <i class="bi bi-bank2"></i>
              <div>
                <p class="confirmed-name">{{ destName }}</p>
                <p class="confirmed-addr">{{ destAddress }}</p>
              </div>
              <button class="text-btn reset-btn" @click="startEditDest">변경</button>
            </div>

            <!-- 목적지 수동 입력 폼 -->
            <div v-if="editingDest" class="manual-input-area">
              <div class="input-row">
                <input
                  v-model="destQuery"
                  placeholder="목적지 주소 또는 장소명 입력"
                  @keyup.enter="searchDest"
                  class="addr-input"
                />
                <button class="search-mini-btn" @click="searchDest">검색</button>
              </div>
              <ul v-if="destResults.length" class="addr-results">
                <li
                  v-for="(r, i) in destResults"
                  :key="i"
                  @click="selectDest(r)"
                >
                  <strong>{{ r.place_name || r.address_name }}</strong>
                  <span>{{ r.road_address_name || r.address_name }}</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- 뒤로가기 -->
          <button class="back-btn" @click="$router.back()">
            <i class="bi bi-arrow-left"></i> 지도로 돌아가기
          </button>
        </div>

        <!-- 오른쪽: 지도 -->
        <div class="map-panel">
          <div id="directions-map" ref="mapContainer"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import PageHeader from '@/components/common/PageHeader.vue'
import { useAlert } from '@/composables/useAlert'
import bankMarkerImg from '@/assets/bank-marker.png'
import spinnerSvg from '@/assets/spinner.svg'
import originMarkerImg from '@/assets/origin-marker.png'

const route = useRoute()
const { alert } = useAlert()

// 지도
const mapContainer = ref(null)
const map = ref(null)

// 출발지
const originMode = ref('gps')   // 'gps' | 'manual'
const originLoading = ref(false)
const originCoords = ref(null)  // { lat, lng }
const originQuery = ref('')
const originResults = ref([])
const originMarker = ref(null)
const selectedOriginName = ref('')  // 수동 선택 확인용
const selectedOriginAddr = ref('')

// 목적지
const destName = ref(route.query.name || '')
const destAddress = ref(route.query.address || '')
const destCoords = ref(
  route.query.lat ? { lat: parseFloat(route.query.lat), lng: parseFloat(route.query.lng) } : null
)
const destMarker = ref(null)
const destOverlay = ref(null)
const editingDest = ref(false)
const destQuery = ref('')
const destResults = ref([])

// 이동 수단 및 경로
const travelMode = ref('car')
const routeLoading = ref(false)
const routeSummary = ref(null)
const polyline = ref(null)

const REST_KEY = import.meta.env.VITE_KAKAO_REST_KEY

const canSearch = computed(() => originCoords.value !== null)

// ───────────────────────────────────────────
// 카카오맵 로드
// ───────────────────────────────────────────
const loadKakaoMapScript = () => {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps) { resolve(); return }
    const script = document.createElement('script')
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_MAP_KEY}&autoload=false&libraries=services`
    script.onload = () => window.kakao.maps.load(resolve)
    script.onerror = reject
    document.head.appendChild(script)
  })
}

const initMap = () => {
  const options = {
    center: new window.kakao.maps.LatLng(destCoords.value.lat, destCoords.value.lng),
    level: 5
  }
  map.value = new window.kakao.maps.Map(mapContainer.value, options)
  placeDestMarker()
}

// ───────────────────────────────────────────
// 마커
// ───────────────────────────────────────────
const createMarkerImage = () => {
  const imageSize = new window.kakao.maps.Size(38, 42)
  const imageOption = { offset: new window.kakao.maps.Point(19, 42) }
  return new window.kakao.maps.MarkerImage(bankMarkerImg, imageSize, imageOption)
}

const placeDestMarker = () => {
  if (!map.value || !destCoords.value) return
  if (destMarker.value) destMarker.value.setMap(null)
  if (destOverlay.value) destOverlay.value.setMap(null)
  const pos = new window.kakao.maps.LatLng(destCoords.value.lat, destCoords.value.lng)
  destMarker.value = new window.kakao.maps.Marker({
    position: pos,
    map: map.value,
    image: createMarkerImage()
  })

  const overlayEl = document.createElement('div')
  overlayEl.className = 'dir-dest-label'
  overlayEl.innerHTML = `<span>${destName.value}</span>`
  destOverlay.value = new window.kakao.maps.CustomOverlay({
    content: overlayEl,
    map: map.value,
    position: pos,
    xAnchor: 0.5,
    yAnchor: 2.6
  })
}

const placeOriginMarker = (lat, lng) => {
  if (!map.value) return
  if (originMarker.value) originMarker.value.setMap(null)
  const pos = new window.kakao.maps.LatLng(lat, lng)
  const imageSize = new window.kakao.maps.Size(38, 42)
  const imageOption = { offset: new window.kakao.maps.Point(19, 42) }
  const markerImage = new window.kakao.maps.MarkerImage(originMarkerImg, imageSize, imageOption)
  originMarker.value = new window.kakao.maps.Marker({ position: pos, map: map.value, image: markerImage })
}



// ───────────────────────────────────────────
// GPS
// ───────────────────────────────────────────
const tryGps = () => {
  if (!navigator.geolocation) { originMode.value = 'manual'; return }
  originLoading.value = true
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      originLoading.value = false
      originCoords.value = { lat: pos.coords.latitude, lng: pos.coords.longitude }
      placeOriginMarker(originCoords.value.lat, originCoords.value.lng)
      // GPS 성공 시 자동차 경로 자동 탐색
      getRoute()
    },
    () => {
      originLoading.value = false
      originMode.value = 'manual'
    }
  )
}

const retryGps = () => {
  originMode.value = 'gps'
  originCoords.value = null
  tryGps()
}

const switchToManual = () => {
  originMode.value = 'manual'
}

// ───────────────────────────────────────────
// 출발지 수동 검색
// ───────────────────────────────────────────
const searchOrigin = () => {
  if (!originQuery.value.trim()) return
  const ps = new window.kakao.maps.services.Places()
  ps.keywordSearch(originQuery.value, (data, status) => {
    if (status === window.kakao.maps.services.Status.OK) {
      originResults.value = data.slice(0, 5)
    } else {
      originResults.value = []
    }
  })
}

const selectOrigin = (r) => {
  originCoords.value = { lat: parseFloat(r.y), lng: parseFloat(r.x) }
  selectedOriginName.value = r.place_name || r.address_name
  selectedOriginAddr.value = r.road_address_name || r.address_name
  originQuery.value = r.place_name || r.address_name
  originResults.value = []
  placeOriginMarker(originCoords.value.lat, originCoords.value.lng)
  // 출발지 선택 즉시 경로 탐색 (이동수단이 이미 선택된 경우)
  if (travelMode.value) getRoute()
}

const resetOrigin = () => {
  originCoords.value = null
  selectedOriginName.value = ''
  selectedOriginAddr.value = ''
  originQuery.value = ''
  originResults.value = []
  if (originMarker.value) { originMarker.value.setMap(null); originMarker.value = null }
  clearRoute()
}

// ───────────────────────────────────────────
// 목적지 수동 검색
// ───────────────────────────────────────────
const startEditDest = () => {
  editingDest.value = true
  destQuery.value = ''
  destResults.value = []
  clearRoute()
}

const searchDest = () => {
  if (!destQuery.value.trim()) return
  const ps = new window.kakao.maps.services.Places()
  // 현재 위치(출발지) 기준으로 가까운 순 정렬
  const options = originCoords.value
    ? { location: new window.kakao.maps.LatLng(originCoords.value.lat, originCoords.value.lng), sort: window.kakao.maps.services.SortBy.DISTANCE }
    : {}
  ps.keywordSearch(destQuery.value, (data, status) => {
    if (status === window.kakao.maps.services.Status.OK) {
      destResults.value = data.slice(0, 5)
    } else {
      destResults.value = []
    }
  }, options)
}

const selectDest = (r) => {
  destCoords.value = { lat: parseFloat(r.y), lng: parseFloat(r.x) }
  destName.value = r.place_name || r.address_name
  destAddress.value = r.road_address_name || r.address_name
  destQuery.value = ''
  destResults.value = []
  editingDest.value = false
  placeDestMarker()
  if (originCoords.value) getRoute()
}

// 이동수단 선택 시 즉시 경로 탐색
const selectMode = (mode) => {
  travelMode.value = mode
  if (originCoords.value) getRoute()
}

// ───────────────────────────────────────────
// 경로 탐색
// ───────────────────────────────────────────
const getRoute = async () => {
  if (!originCoords.value) return
  routeLoading.value = true
  clearPolyline()

  const origin = `${originCoords.value.lng},${originCoords.value.lat}`
  const dest = `${destCoords.value.lng},${destCoords.value.lat}`

  try {
    if (travelMode.value === 'walk') {
      // 도보: 카카오맵 웹으로 연결
      openKakaoMapWalk()
      routeLoading.value = false
      return
    }

    const url = `https://apis-navi.kakaomobility.com/v1/directions?origin=${origin}&destination=${dest}&summary=false`
    const headers = { 'Authorization': `KakaoAK ${REST_KEY}`, 'Content-Type': 'application/json' }

    const res = await fetch(url, { headers })
    const data = await res.json()
    await drawCarRoute(data)
  } catch (e) {
    console.error('경로 탐색 오류:', e)
    await alert('경로를 불러오는 데 실패했어요. 잠시 후 다시 시도해 주세요.', '경로 오류')
  } finally {
    routeLoading.value = false
  }
}

const drawCarRoute = async (data) => {
  if (!data.routes || data.routes[0]?.result_code !== 0) {
    await alert('자동차 경로를 찾을 수 없어요.', '경로 없음')
    return
  }
  const route = data.routes[0]
  routeSummary.value = {
    distance: route.summary.distance,
    duration: route.summary.duration
  }

  const linePath = []
  route.sections.forEach(section => {
    section.roads.forEach(road => {
      for (let i = 0; i < road.vertexes.length; i += 2) {
        linePath.push(new window.kakao.maps.LatLng(road.vertexes[i + 1], road.vertexes[i]))
      }
    })
  })

  polyline.value = new window.kakao.maps.Polyline({
    path: linePath,
    strokeWeight: 5,
    strokeColor: '#86A78A',
    strokeOpacity: 0.9,
    strokeStyle: 'solid'
  })
  polyline.value.setMap(map.value)
  fitBounds(linePath)
}

// 도보: 카카오맵 웹으로 연결
const openKakaoMapWalk = () => {
  const oLat = originCoords.value.lat
  const oLng = originCoords.value.lng
  const dLat = destCoords.value.lat
  const dLng = destCoords.value.lng
  // 카카오맵 웹 길찾기 URL: /link/from/출발지명,위도,경도/to/목적지명,위도,경도
  const url = `https://map.kakao.com/link/from/${encodeURIComponent('출발지')},${oLat},${oLng}/to/${encodeURIComponent(destName.value)},${dLat},${dLng}`
  window.open(url, '_blank')
  // 카카오맵 이동 후 자동차 모드로 복귀
  travelMode.value = 'car'
}

const fitBounds = (linePath) => {
  const bounds = new window.kakao.maps.LatLngBounds()
  linePath.forEach(p => bounds.extend(p))
  map.value.setBounds(bounds)
}

const clearPolyline = () => {
  if (polyline.value) { polyline.value.setMap(null); polyline.value = null }
}

const clearRoute = () => {
  clearPolyline()
  routeSummary.value = null
}

// ───────────────────────────────────────────
// 포맷 유틸
// ───────────────────────────────────────────
const formatDistance = (meters) => {
  if (meters >= 1000) return `${(meters / 1000).toFixed(1)} km`
  return `${meters} m`
}

const formatDuration = (seconds) => {
  const min = Math.floor(seconds / 60)
  if (min >= 60) return `${Math.floor(min / 60)}시간 ${min % 60}분`
  return `${min}분`
}

// ───────────────────────────────────────────
// 마운트
// ───────────────────────────────────────────
onMounted(async () => {
  await loadKakaoMapScript()
  initMap()
  tryGps()
})
</script>

<style scoped>
.page-outer { background-color: #f9f8f5; min-height: 100vh; }
.page-container { max-width: 1200px; margin: 0 auto; padding: 0 24px 40px; }

.directions-wrapper {
  display: flex;
  gap: 16px;
  height: calc(100vh - 220px);
  min-height: 560px;
}

/* 사이드 패널 */
.side-panel {
  width: 340px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
  background: #ffffff;
  border: 1px solid #e1e6e2;
  border-radius: 12px;
  overflow-y: auto;
  padding: 20px;
}

.panel-section {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0ea;
}
.panel-section:last-of-type { border-bottom: none; }

.section-label {
  font-size: 11px;
  font-weight: 700;
  color: #86A78A;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.origin-dot { background: #4A90D9; border: 2px solid #fff; box-shadow: 0 0 0 2px #4A90D9; }
.dest-dot   { background: #86A78A; border: 2px solid #fff; box-shadow: 0 0 0 2px #86A78A; }

/* 출발지 상태 */
.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  padding: 8px 10px;
  border-radius: 8px;
}
.status-row.loading { background: #f0f4f0; color: #556256; }
.status-row.success { background: #edf5ee; color: #2D6A4F; }
.status-row.warn    { background: #fff8e6; color: #8a6200; }

.spinner-img {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  display: inline-block;
}

.text-btn {
  background: none; border: none; cursor: pointer;
  font-size: 12px; color: #86A78A; font-weight: 600;
  padding: 0; text-decoration: underline; margin-left: auto;
}
.mt-4 { margin-top: 8px; }

/* 수동 입력 */
.manual-input-area { display: flex; flex-direction: column; gap: 6px; }
.input-row { display: flex; gap: 6px; }
.addr-input {
  flex: 1; padding: 8px 12px; font-size: 13px;
  border: 1.5px solid #A0BAA3; border-radius: 6px;
  outline: none; background: #fff;
}
.addr-input:focus { border-color: #86A78A; box-shadow: 0 0 0 2px rgba(134,167,138,0.2); }
.search-mini-btn {
  padding: 8px 12px; font-size: 13px; font-weight: 600;
  background: #86A78A; color: #fff; border: none;
  border-radius: 6px; cursor: pointer; white-space: nowrap;
}

.addr-results {
  list-style: none; margin: 0; padding: 4px 0;
  border: 1.5px solid #A0BAA3; border-radius: 6px;
  background: #fff; max-height: 180px; overflow-y: auto;
}
.addr-results li {
  padding: 8px 12px; cursor: pointer;
  display: flex; flex-direction: column; gap: 2px;
  border-bottom: 1px solid #f0f0ea;
}
.addr-results li:last-child { border-bottom: none; }
.addr-results li:hover { background: #f0f4f0; }
.addr-results li strong { font-size: 13px; color: #222; }
.addr-results li span  { font-size: 11px; color: #888; }

/* 구분선 */
.route-divider {
  display: flex; align-items: center; gap: 8px;
  padding: 4px 0;
}
.divider-line { flex: 1; height: 1px; background: #f0f0ea; }
.swap-area {
  width: 28px; height: 28px;
  border: 1.5px solid #e1e6e2; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #A0BAA3; font-size: 12px;
}

/* 목적지 */
.dest-info {
  display: flex; gap: 10px; align-items: flex-start;
  background: #f0f4f0; border-radius: 8px; padding: 10px 12px;
}
.dest-info i { color: #86A78A; font-size: 16px; flex-shrink: 0; margin-top: 2px; }
.dest-name { font-size: 13px; font-weight: 700; color: #222; margin: 0 0 2px; }
.dest-addr { font-size: 11px; color: #666; margin: 0; }

/* 이동 수단 */
.mode-section { border-bottom: 2px solid #e1e6e2; }
.mode-btns { display: flex; gap: 8px; }
.mode-btn {
  flex: 1; padding: 12px 10px; font-size: 14px; font-weight: 700;
  border: 1.5px solid #e1e6e2; border-radius: 10px;
  background: #fff; color: #666; cursor: pointer;
  transition: all 0.15s ease;
  display: flex; align-items: center; justify-content: center; gap: 6px;
}
.mode-btn.active {
  border-color: #86A78A; background: #edf5ee; color: #2D6A4F;
  box-shadow: 0 2px 8px rgba(134,167,138,0.25);
}
.mode-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-spinner { width: 18px; height: 18px; }
.mode-hint {
  margin: 8px 0 0; font-size: 11px; color: #aaa;
  display: flex; align-items: center; gap: 4px;
}

/* 경로 요약 */
.route-summary {
  background: #f9f8f5; border: 1px solid #e1e6e2;
  border-radius: 10px; padding: 12px 14px;
  display: flex; flex-direction: column; gap: 8px;
}
.summary-row { display: flex; gap: 12px; }
.summary-item { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.summary-label { font-size: 11px; color: #888; }
.summary-value { font-size: 16px; font-weight: 700; color: #333d29; }
.clear-btn {
  background: none; border: 1px solid #e1e6e2; border-radius: 6px;
  padding: 5px 10px; font-size: 12px; color: #888; cursor: pointer;
  display: flex; align-items: center; gap: 4px; align-self: flex-start;
}
.clear-btn:hover { border-color: #86A78A; color: #86A78A; }

/* 출발지 확인 표시 */
.origin-confirmed {
  display: flex; align-items: flex-start; gap: 8px;
  background: #edf5ee; border: 1px solid #A0BAA3;
  border-radius: 8px; padding: 10px 12px;
}
.origin-confirmed > i { color: #2D6A4F; font-size: 15px; flex-shrink: 0; margin-top: 2px; }
.confirmed-name { font-size: 13px; font-weight: 700; color: #222; margin: 0 0 2px; }
.confirmed-addr { font-size: 11px; color: #556256; margin: 0; }
.reset-btn { margin-left: auto; white-space: nowrap; }

/* 뒤로가기 */
.back-btn {
  background: none; border: none; cursor: pointer;
  font-size: 13px; color: #86A78A; font-weight: 600;
  display: flex; align-items: center; gap: 4px;
  padding: 8px 0; margin-top: auto;
}

/* 지도 */
.map-panel { flex: 1; border-radius: 12px; overflow: hidden; border: 1px solid #e1e6e2; }
#directions-map { width: 100%; height: 100%; }

/* 오버레이 */
:global(.dir-dest-label) {
  background: #f9f8f5;
  border: 2px solid #A0BAA3;
  border-radius: 16px;
  padding: 5px 12px;
  font-family: 'Pretendard', -apple-system, sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: #2D3E2E;
  white-space: nowrap;
  box-shadow: 0 6px 16px rgba(134, 167, 138, 0.3);
  pointer-events: none;
}

@media (max-width: 1024px) {
  .directions-wrapper { flex-direction: column; height: auto; }
  .side-panel { width: 100%; }
  .map-panel { height: 400px; }
}
</style>

<style>
/* dest-confirmed: 목적지는 초록 계열로 구분 */
.dest-confirmed {
  background: #f0f4f0 !important;
  border-color: #86A78A !important;
}
.dest-confirmed > i { color: #86A78A !important; }
</style>

<style>
.kakaomap-badge {
  font-size: 9px;
  font-weight: 700;
  background: #FEE500;
  color: #3C1E1E;
  border-radius: 4px;
  padding: 1px 5px;
  margin-left: 3px;
  vertical-align: middle;
  white-space: nowrap;
}
</style>