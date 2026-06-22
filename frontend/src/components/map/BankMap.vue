<template>
  <div class="map-container">
    <div id="map" ref="mapContainer"></div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import bankMarkerImg from '@/assets/bank-marker.png' 

const props = defineProps({
  banks: { type: Array, default: () => [] } // 검색 결과
})

const emit = defineEmits(['mapReady'])

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
  currentMarker.value = new window.kakao.maps.Marker({
    position,
    map: map.value
  })
  map.value.setCenter(position)
}

const clearBankMarkers = () => {
  markers.value.forEach(m => m.setMap(null))
  markers.value = []
  
  overlays.value.forEach(o => {
    if (o) o.setMap(null)
  })
  overlays.value = []
}

const createCustomMarkerImage = () => {
  if (!window.kakao || !window.kakao.maps) return null
  
  const imageSize = new window.kakao.maps.Size(38, 42) 
  const imageOption = { offset: new window.kakao.maps.Point(19, 42) } 
  
  return new window.kakao.maps.MarkerImage(bankMarkerImg, imageSize, imageOption)
}

// 🚀 일반 검색 결과 마커 및 오버레이 렌더링 로직
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

    const content = document.createElement('div')
    content.className = 'custom-bank-overlay'
    content.innerHTML = `
      <div class="overlay-hover-zone">
        <div class="overlay-card">
          <span class="title">${bank.place_name}</span>
          <div class="detail-info">
            <p class="address">${bank.road_address_name || bank.address_name}</p>
            ${bank.phone ? `<p class="phone">📞 ${bank.phone}</p>` : ''}
          </div>
        </div>
      </div>
    `

    const overlay = new window.kakao.maps.CustomOverlay({
      content: content,
      map: map.value, 
      position: position,
      xAnchor: 0.5,
      yAnchor: 1.0
    })

    // 🎯 [버그 해결 핵심] 마우스를 올리는 순간, 카카오맵 자체 zIndex를 왕으로 만들어 마커를 아래로 깔아버립니다.
    content.addEventListener('mouseenter', () => {
      if (overlay) overlay.setZIndex(999)
    })

    // 마우스가 나가면 다시 평범한 서민 등급(50)으로 복귀시킵니다.
    content.addEventListener('mouseleave', () => {
      if (overlay) overlay.setZIndex(50)
    })

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

// 🚀 즐겨찾기 목록에서 은행 클릭 시 단독 이동 함수
const moveToBank = (bank) => {
  if (!window.kakao || !window.kakao.maps || !map.value) return

  const geocoder = new window.kakao.maps.services.Geocoder()
  const address = bank.road_address_name || bank.address_name

  if (!address) return

  geocoder.addressSearch(address, (result, status) => {
    if (status === window.kakao.maps.services.Status.OK) {
      const coords = new window.kakao.maps.LatLng(result[0].y, result[0].x)

      clearBankMarkers()
      const markerImage = createCustomMarkerImage()

      const marker = new window.kakao.maps.Marker({
        map: map.value,
        position: coords,
        image: markerImage
      })

      const content = document.createElement('div')
      content.className = 'custom-bank-overlay' 
      content.innerHTML = `
        <div class="overlay-hover-zone">
          <div class="overlay-card">
            <span class="title">${bank.place_name}</span>
            <div class="detail-info">
              <p class="address">${bank.road_address_name || bank.address_name}</p>
              ${bank.phone ? `<p class="phone">📞 ${bank.phone}</p>` : ''}
            </div>
          </div>
        </div>
      `

      const overlay = new window.kakao.maps.CustomOverlay({
        content: content,
        map: map.value,
        position: coords,
        xAnchor: 0.5,
        yAnchor: 1.0
      })

      // 즐겨찾기로 바로 이동했을 때는 즉시 최상단 배치
      overlay.setZIndex(999)

      content.addEventListener('mouseenter', () => {
        if (overlay) overlay.setZIndex(999)
      })
      content.addEventListener('mouseleave', () => {
        if (overlay) overlay.setZIndex(50)
      })

      markers.value.push(marker)
      overlays.value.push(overlay)

      map.value.panTo(coords)
    }
  })
}

defineExpose({
  moveToBank
})
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
  position: relative;
}
#map {
  width: 100%;
  height: 100%;
}
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
  background-color: #EBEADD;     
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
  transition: max-height 0.2s ease-in-out, opacity 0.15s ease-in-out;
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

.custom-bank-overlay .overlay-hover-zone:hover .overlay-card {
  opacity: 1;
  visibility: visible;
  background-color: #F7F6F2;   
  box-shadow: 0 12px 25px rgba(134, 167, 138, 0.5);
  padding: 10px 14px;
}

.custom-bank-overlay .overlay-hover-zone:hover .detail-info {
  max-height: 100px;            
  opacity: 1;
}
</style>