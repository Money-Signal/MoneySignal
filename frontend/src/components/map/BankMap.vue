<template>
  <div class="map-container">
    <div id="map" ref="mapContainer"></div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
// 🚀 [체크] src/assets/bank-marker.png 경로에 파일이 실제로 있어야 합니다.
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
  
  overlays.value.forEach(o => o.setMap(null))
  overlays.value = []
}

// 🚀 [수정] 카카오맵이 인식할 수 있도록 이미지 경로 문자열을 정확히 주입합니다.
const createCustomMarkerImage = () => {
  if (!window.kakao || !window.kakao.maps) return null
  
  const imageSize = new window.kakao.maps.Size(38, 42) 
  const imageOption = { offset: new window.kakao.maps.Point(19, 42) } 
  
  // ✨ bankMarkerImg 모듈 경로를 정확히 빌드하여 주입
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
      image: markerImage // ✨ 커스텀 마커 이미지 적용
    })

    bounds.extend(position)

    // 🎯 깔끔하고 트렌디한 조약돌 스타일 오버레이 구조 (기본 상태는 open 클래스 없음)
    const content = document.createElement('div')
    content.className = 'custom-bank-overlay'
    content.innerHTML = `
      <div class="overlay-card">
        <span class="title">${bank.place_name}</span>
        <div class="detail-info">
          <p class="address">${bank.road_address_name || bank.address_name}</p>
          ${bank.phone ? `<p class="phone">📞 ${bank.phone}</p>` : ''}
        </div>
      </div>
    `

    const overlay = new window.kakao.maps.CustomOverlay({
      content: content,
      map: null, // 🔥 중요: 처음에는 지도에 표시하지 않고 마우스를 올릴 때만 띄웁니다!
      position: position,
      yAnchor: 1.5 // 마커 정중앙 머리 위에 안착되도록 정밀 조절
    })

    // 🎯 [핵심 해결책] 카카오맵 마커에 직접 마우스 오버 / 아웃 이벤트를 등록하여 정보창 제어!
    window.kakao.maps.event.addListener(marker, 'mouseover', () => {
      overlay.setMap(map.value)
      content.classList.add('open') // 애니메이션 효과용 클래스 부여
    })

    window.kakao.maps.event.addListener(marker, 'mouseout', () => {
      content.classList.remove('open')
      overlay.setMap(null)
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
      content.className = 'custom-bank-overlay open' // 단독 이동 시엔 즉시 상세 정보 노출
      content.innerHTML = `
        <div class="overlay-card">
          <span class="title">${bank.place_name}</span>
          <div class="detail-info">
            <p class="address">${bank.road_address_name || bank.address_name}</p>
            ${bank.phone ? `<p class="phone">📞 ${bank.phone}</p>` : ''}
          </div>
        </div>
      `

      const overlay = new window.kakao.maps.CustomOverlay({
        content: content,
        map: map.value,
        position: coords,
        yAnchor: 1.5
      })

      // 즐겨찾기로 온 마커도 마우스 아웃 시 꺼지게 하고 싶다면 활성화 가능합니다.
      window.kakao.maps.event.addListener(marker, 'mouseover', () => {
        overlay.setMap(map.value)
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
/* 말풍선 기본 구조 */
.custom-bank-overlay {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: 'Pretendard', -apple-system, sans-serif;
  z-index: 50;
  pointer-events: none; /* 지도 드래그 및 마커 호버 방해 금지 */
}

/* 🎯 지정 컬러 매칭: 선을 없애고 면 분할 레이아웃으로 변경 */
.custom-bank-overlay .overlay-card {
  background-color: #EBEADD;     /* 🎨 지정 배경색 */
  border: 2px solid #A0BAA3;   /* 🎨 지정 포인트 컬러1 테두리 */
  border-radius: 16px;         /* 조약돌 스타일 부드러운 라운딩 */
  padding: 8px 14px;
  box-shadow: 0 8px 20px rgba(134, 167, 138, 0.3); /* 포인트2 기반 은은한 그림자 */
  text-align: center;
  max-width: 240px;
  transition: all 0.2s ease-in-out;
}

/* 은행 이름 스타일 (가독성을 위한 다크 포레스트 그린 매칭) */
.custom-bank-overlay .title {
  color: #2D3E2E;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  display: block;
}

/* 기본적으로 주소와 전화번호는 숨김 상태 */
.custom-bank-overlay .detail-info {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  transition: all 0.25s ease-in-out;
  text-align: left;
}

/* 주소 스타일 */
.custom-bank-overlay .address {
  font-size: 11px;
  color: #556256;
  margin-top: 6px;
  margin-bottom: 3px;
  line-height: 1.35;
  word-break: keep-all;
}

/* 🎯 지정 포인트 컬러2(#86A78A)를 활용한 전화번호 강조 칩 */
.custom-bank-overlay .phone {
  font-size: 11px;
  color: #ffffff;
  background-color: #86A78A;   /* 🎨 지정 포인트 컬러2 */
  padding: 1px 6px;
  border-radius: 8px;
  font-weight: 500;
  display: inline-block;
  margin: 2px 0 0 0;
}

/* 🎯 마우스가 마커 위에 올라가 활성화(.open)되었을 때 스타일 변경 */
.custom-bank-overlay.open .overlay-card {
  background-color: #F7F6F2;   /* 카드가 살짝 밝아지며 가독성 증대 */
  box-shadow: 0 12px 25px rgba(134, 167, 138, 0.5);
  padding: 10px 14px;
}

.custom-bank-overlay.open .detail-info {
  max-height: 80px;            /* 세부 주소와 전화번호 노출 */
  opacity: 1;
}
</style>