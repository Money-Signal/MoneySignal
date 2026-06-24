<template>
  <div class="map-container">
    <div id="map" ref="mapContainer"></div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import bankMarkerImg from '@/assets/bank-marker.png' 
import originMarkerImg from '@/assets/origin-marker.png'

const props = defineProps({
  banks: { type: Array, default: () => [] }
})

const emit = defineEmits(['mapReady'])
const router = useRouter()

const map = ref(null)
const markers = ref([])
const overlays = ref([]) 
const currentMarker = ref(null)

const loadKakaoMapScript = () => {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps) {
      resolve()
      return
    }
    const script = document.createElement('script')
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_MAP_KEY}&autoload=false&libraries=services`
    script.onload = () => window.kakao.maps.load(resolve)
    script.onerror = reject
    document.head.appendChild(script)
  })
}

const setCurrentLocationMarker = (lat, lng) => {
  const position = new window.kakao.maps.LatLng(lat, lng)
  const imageSize = new window.kakao.maps.Size(38, 42)
  const imageOption = { offset: new window.kakao.maps.Point(19, 42) }
  const markerImage = new window.kakao.maps.MarkerImage(originMarkerImg, imageSize, imageOption)
  currentMarker.value = new window.kakao.maps.Marker({
    position,
    map: map.value,
    image: markerImage
  })
  map.value.setCenter(position)
}

const clearBankMarkers = () => {
  markers.value.forEach(m => m.setMap(null))
  markers.value = []
  overlays.value.forEach(o => { if (o) o.setMap(null) })
  overlays.value = []
}

const createCustomMarkerImage = () => {
  if (!window.kakao || !window.kakao.maps) return null
  const imageSize = new window.kakao.maps.Size(38, 42) 
  const imageOption = { offset: new window.kakao.maps.Point(19, 42) } 
  return new window.kakao.maps.MarkerImage(bankMarkerImg, imageSize, imageOption)
}

// 길찾기 버튼 클릭 핸들러 (오버레이 내부 버튼용)
const goToDirections = (bank, lat, lng) => {
  router.push({
    name: 'directions',
    query: {
      lat,
      lng,
      name: bank.place_name,
      address: bank.road_address_name || bank.address_name
    }
  })
}

// 오버레이 카드 HTML 생성 (검색결과 / moveToBank 공용)
const createOverlayContent = (bank, lat, lng) => {
  const content = document.createElement('div')
  content.className = 'custom-bank-overlay'
  content.innerHTML = `
    <div class="overlay-hover-zone">
      <div class="overlay-card">
        <span class="title">${bank.place_name}</span>
        <div class="detail-info">
          <p class="address">${bank.road_address_name || bank.address_name}</p>
          ${bank.phone ? `<p class="phone">📞 ${bank.phone}</p>` : ''}
          <button class="directions-btn-overlay" data-lat="${lat}" data-lng="${lng}">길찾기</button>
        </div>
      </div>
    </div>
  `
  // 길찾기 버튼 이벤트 (innerHTML로 생성된 버튼은 직접 addEventListener)
  const btn = content.querySelector('.directions-btn-overlay')
  btn.addEventListener('click', (e) => {
    e.stopPropagation()
    goToDirections(bank, lat, lng)
  })
  return content
}

// 검색 결과 마커 및 오버레이 렌더링
const renderBankMarkers = (banks) => {
  clearBankMarkers()
  if (!banks || banks.length === 0) return

  const bounds = new window.kakao.maps.LatLngBounds()
  const markerImage = createCustomMarkerImage()

  banks.forEach(bank => {
    const position = new window.kakao.maps.LatLng(bank.y, bank.x)
    const marker = new window.kakao.maps.Marker({
      position,
      map: map.value,
      image: markerImage
    })
    bounds.extend(position)

    const content = createOverlayContent(bank, bank.y, bank.x)

    const overlay = new window.kakao.maps.CustomOverlay({
      content: content,
      map: map.value, 
      position: position,
      xAnchor: 0.5,
      yAnchor: 1.0
    })

    content.addEventListener('mouseenter', () => { if (overlay) overlay.setZIndex(999) })
    content.addEventListener('mouseleave', () => { if (overlay) overlay.setZIndex(50) })

    markers.value.push(marker)
    overlays.value.push(overlay)
  })

  map.value.setBounds(bounds)
}

onMounted(async () => {
  await loadKakaoMapScript()
  const container = document.getElementById('map')
  const options = {
    center: new window.kakao.maps.LatLng(37.5665, 126.9780),
    level: 5
  }
  map.value = new window.kakao.maps.Map(container, options)

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords
        setCurrentLocationMarker(latitude, longitude)
      },
      (err) => {
        console.warn('위치 정보를 가져올 수 없습니다:', err)
      }
    )
  }

  emit('mapReady', map.value)
})

watch(() => props.banks, (newBanks) => {
  renderBankMarkers(newBanks)
})

// 즐겨찾기 목록에서 은행 클릭 시 단독 이동 함수
const moveToBank = (bank) => {
  if (!window.kakao || !window.kakao.maps || !map.value) return

  const geocoder = new window.kakao.maps.services.Geocoder()
  const address = bank.road_address_name || bank.address_name
  if (!address) return

  geocoder.addressSearch(address, (result, status) => {
    if (status === window.kakao.maps.services.Status.OK) {
      const lat = result[0].y
      const lng = result[0].x
      const coords = new window.kakao.maps.LatLng(lat, lng)

      clearBankMarkers()
      const markerImage = createCustomMarkerImage()
      const marker = new window.kakao.maps.Marker({
        map: map.value,
        position: coords,
        image: markerImage
      })

      const content = createOverlayContent(bank, lat, lng)

      const overlay = new window.kakao.maps.CustomOverlay({
        content: content,
        map: map.value,
        position: coords,
        xAnchor: 0.5,
        yAnchor: 1.0
      })

      overlay.setZIndex(999)
      content.addEventListener('mouseenter', () => { if (overlay) overlay.setZIndex(999) })
      content.addEventListener('mouseleave', () => { if (overlay) overlay.setZIndex(50) })

      markers.value.push(marker)
      overlays.value.push(overlay)

      map.value.panTo(coords)
    }
  })
}

defineExpose({ moveToBank })
</script>

<style scoped>
.map-container { width: 100%; height: 100%; position: relative; }
#map { width: 100%; height: 100%; }
</style>

<style>
.custom-bank-overlay {
  position: relative;
  font-family: 'Pretendard', -apple-system, sans-serif;
  pointer-events: none; 
}

.custom-bank-overlay .overlay-hover-zone {
  position: absolute;
  bottom: 0;
  left: -19px; 
  width: 38px;
  height: 42px;
  pointer-events: auto !important; 
  cursor: pointer;
}

.custom-bank-overlay .overlay-card {
  position: absolute;
  bottom: 57px; 
  left: 50%;
  transform: translateX(-50%);
  background-color: #f9f8f5;
  border: 2px solid #A0BAA3;   
  border-radius: 16px;         
  padding: 8px 14px;
  box-shadow: 0 8px 20px rgba(134, 167, 138, 0.3);
  text-align: center;
  min-width: 180px;
  max-width: 260px;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease-in-out;
}

.custom-bank-overlay .overlay-card::after {
  content: '';
  position: absolute;
  bottom: -10px; 
  left: 50%;
  transform: translateX(-50%);
  border-width: 10px 7px 0 7px;
  border-style: solid;
  border-color: #A0BAA3 transparent transparent transparent; 
}

.custom-bank-overlay .title {
  color: #2D3E2E;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  display: block;
}

.custom-bank-overlay .detail-info {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  text-align: left;
  transition: max-height 0.25s ease-in-out, opacity 0.2s ease-in-out;
}

.custom-bank-overlay .address {
  font-size: 11px;
  color: #556256;
  margin-top: 6px;
  margin-bottom: 3px;
  line-height: 1.35;
  word-break: keep-all;
}

.custom-bank-overlay .phone {
  font-size: 11px;
  color: #ffffff;
  background-color: #86A78A;   
  padding: 1px 6px;
  border-radius: 8px;
  font-weight: 500;
  display: inline-block;
  margin: 2px 0 0 0;
}

/* 길찾기 버튼 */
.custom-bank-overlay .directions-btn-overlay {
  display: inline-block;
  margin-top: 6px;
  padding: 3px 10px;
  font-size: 11px;
  font-weight: 700;
  font-family: 'Pretendard', -apple-system, sans-serif;
  color: #2D6A4F !important;
  background: #edf5ee !important;
  border: 1.5px solid #A0BAA3 !important;
  border-radius: 8px;
  cursor: pointer;
  pointer-events: auto !important;
  white-space: nowrap;
  transition: background 0.15s, color 0.15s;
}
.custom-bank-overlay .directions-btn-overlay:hover {
  background: #86A78A !important;
  color: #fff !important;
  border-color: #86A78A !important;
}

.custom-bank-overlay .overlay-hover-zone:hover .overlay-card {
  opacity: 1;
  visibility: visible;
  background-color: #F7F6F2;   
  box-shadow: 0 12px 25px rgba(134, 167, 138, 0.5);
  padding: 10px 14px;
}

.custom-bank-overlay .overlay-hover-zone:hover .detail-info {
  max-height: 180px;           
  opacity: 1;
}
</style>