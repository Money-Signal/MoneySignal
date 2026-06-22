<template>
  <div id="map" style="width:100%; height:500px;"></div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'

const props = defineProps({
  banks: { type: Array, default: () => [] } // 검색 결과 (BankList에서 넘어옴)
})

const emit = defineEmits(['mapReady'])

const map = ref(null)
const markers = ref([])
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
}

// 🚀 지도를 자동으로 움직여 마커들을 한눈에 보여주는 로직 추가
const renderBankMarkers = (banks) => {
  clearBankMarkers()

  // 검색 결과가 없으면 지도를 움직이지 않고 종료합니다.
  if (!banks || banks.length === 0) return

  let openedInfowindow = null 
  
  // 1. 모든 마커를 포함할 '좌표 영역(Bounds)' 객체를 생성합니다.
  const bounds = new window.kakao.maps.LatLngBounds()

  banks.forEach(bank => {
    const position = new window.kakao.maps.LatLng(bank.y, bank.x)
    const marker = new window.kakao.maps.Marker({
      position,
      map: map.value
    })

    // 2. 생성된 마커의 좌표를 Bounds 영역에 계속 추가(확장)합니다.
    bounds.extend(position)

    const infowindow = new window.kakao.maps.InfoWindow({
      content: `
        <div style="padding:8px; font-size:13px; min-width:150px;">
          <strong>${bank.place_name}</strong><br/>
          ${bank.road_address_name || bank.address_name}<br/>
          ${bank.phone ? bank.phone : ''}
        </div>
      `
    })

    window.kakao.maps.event.addListener(marker, 'click', () => {
      if (openedInfowindow) {
        openedInfowindow.close()
      }
      infowindow.open(map.value, marker)
      openedInfowindow = infowindow
    })

    markers.value.push(marker)
  })

  // 3. 계산된 마커들의 영역이 지도의 화면 안에 꽉 차게 들어오도록 시점을 부드럽게 이동시킵니다.
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
</script>