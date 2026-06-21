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

  // 현재 위치 마커 (다른 마커와 구분되게 별도 이미지 써도 됨)
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

const renderBankMarkers = (banks) => {
  clearBankMarkers()

  let openedInfowindow = null // 현재 열려있는 인포윈도우 추적

  banks.forEach(bank => {
    const position = new window.kakao.maps.LatLng(bank.y, bank.x)
    const marker = new window.kakao.maps.Marker({
      position,
      map: map.value
    })

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
}

onMounted(async () => {
  await loadKakaoMapScript()
  const container = document.getElementById('map')
  const options = {
    center: new window.kakao.maps.LatLng(37.5665, 126.9780),
    level: 5
  }
  map.value = new window.kakao.maps.Map(container, options)

  // 현재 위치 가져오기
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords
        setCurrentLocationMarker(latitude, longitude)
      },
      (err) => {
        console.warn('위치 정보를 가져올 수 없습니다:', err)
        // 위치 거부 시 기본 좌표(서울시청) 유지
      }
    )
  }

  emit('mapReady', map.value)
})

// 부모에서 검색 결과(banks)가 바뀌면 마커 다시 그림
watch(() => props.banks, (newBanks) => {
  renderBankMarkers(newBanks)
})
</script>