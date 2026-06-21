<template>
  <div id="map" style="width:100%; height:500px;"></div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const map = ref(null)

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

onMounted(async () => {
  await loadKakaoMapScript()
  const container = document.getElementById('map')
  const options = {
    center: new window.kakao.maps.LatLng(37.5665, 126.9780), // 서울 시청
    level: 5
  }
  map.value = new window.kakao.maps.Map(container, options)
})
</script>