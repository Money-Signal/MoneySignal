<template>
  <div class="bank-list-container">
    <div class="search-section">
      <p class="search-subtitle">원하시는 지역과 은행명을 입력해 주세요.</p>
      <div class="search-form">
        <!-- 광역시도 커스텀 드롭다운 -->
        <div class="form-group custom-select-wrapper" ref="sidoRef">
          <div class="custom-select-box" :class="{ open: sidoOpen }" @click="sidoOpen = !sidoOpen">
            <span :class="{ 'is-placeholder': !selectedSido }">{{ selectedSido || '광역시도 선택' }}</span>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" class="arrow-icon" :class="{ rotated: sidoOpen }">
              <path fill="#606c38" d="M8 11l4-4H4z"/>
            </svg>
          </div>
          <ul v-if="sidoOpen" class="custom-options">
            <li @click="selectedSido = ''; onSidoChange(); sidoOpen = false" :class="{ selected: !selectedSido }">광역시도 선택</li>
            <li v-for="sido in sidoList" :key="sido" @click="selectedSido = sido; onSidoChange(); sidoOpen = false" :class="{ selected: selectedSido === sido }">{{ sido }}</li>
          </ul>
        </div>

        <!-- 시군구 커스텀 드롭다운 -->
        <div class="form-group custom-select-wrapper" ref="gugunRef">
          <div
            class="custom-select-box"
            :class="{ open: gugunOpen, disabled: !selectedSido || gugunList.length <= 1 }"
            @click="(!selectedSido || gugunList.length <= 1) ? null : (gugunOpen = !gugunOpen)"
          >
            <span :class="{ 'is-placeholder': !selectedGugun }">{{ selectedGugun || '시군구 선택' }}</span>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" class="arrow-icon" :class="{ rotated: gugunOpen }">
              <path fill="#606c38" d="M8 11l4-4H4z"/>
            </svg>
          </div>
          <ul v-if="gugunOpen" class="custom-options">
            <li @click="selectedGugun = ''; gugunOpen = false" :class="{ selected: !selectedGugun }">시군구 선택</li>
            <li v-for="gugun in gugunList" :key="gugun" @click="selectedGugun = gugun; gugunOpen = false" :class="{ selected: selectedGugun === gugun }">{{ gugun }}</li>
          </ul>
        </div>

        <div class="form-group input-wrapper">
          <input 
            v-model="bankName" 
            placeholder="은행명 / 위치"
            @keyup.enter="searchBanks" 
          />
        </div>

        <button class="search-btn" @click="searchBanks">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001q.044.06.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1 1 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0"/>
          </svg>
          검색
        </button>
      </div>
    </div>

    <div class="tab-navigation">
      <button class="tab-btn" :class="{ active: activeTab === 'list' }" @click="activeTab = 'list'">
        <i class="bi bi-folder-fill me-1"></i> 검색 결과 ({{ localBanks.length }})
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'favorites' }" @click="activeTab = 'favorites'">
        <i class="bi bi-star-fill me-1"></i> 즐겨찾기 ({{ favoriteBanks.length }})
      </button>
    </div>

    <div class="results-section">
      <div v-if="activeTab === 'list'" class="tab-content-wrapper">
        <div v-if="localBanks.length > 0" class="bank-items-list">
          <p class="result-count">
            검색 결과 총 <strong>{{ localBanks.length }}</strong>건
            <span v-if="userLocation" class="sort-badge"><i class="bi bi-geo-alt-fill"></i> 가까운 순</span>
          </p>
          <div v-for="(bank, index) in localBanks" :key="index" class="bank-item" @click="clickBankItem(bank)" style="cursor: pointer;">
            <div class="bank-info">
              <span class="bank-badge">{{ index + 1 }}</span>
              <div class="bank-details">
                <div class="bank-header-row">
                  <h4 class="bank-name">{{ bank.place_name }}</h4>
                  <button class="fav-toggle-btn" :class="{ 'is-favorite': isFavorite(bank) }" @click.stop="toggleFavorite(bank)">
                    <i :class="isFavorite(bank) ? 'bi bi-star-fill' : 'bi bi-star'"></i>
                  </button>
                </div>
                <p class="bank-address"><i class="bi bi-geo-alt-fill me-1"></i> {{ bank.road_address_name || bank.address_name }}</p>
                <p v-if="bank.phone" class="bank-phone"><i class="bi bi-telephone-fill me-1"></i> {{ bank.phone }}</p>
                <!-- ✅ 길찾기 버튼 추가 -->
                <button class="directions-btn" @click.stop="goToDirections(bank)">
                  <i class="bi bi-signpost-2-fill"></i> 길찾기
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="no-result">
          <p><i class="bi bi-search me-1"></i> 검색된 은행 결과가 없습니다.</p>
          <span>지역을 선택하고 검색 버튼을 누르거나 엔터를 쳐보세요!</span>
        </div>
      </div>

      <div v-if="activeTab === 'favorites'" class="tab-content-wrapper">
        <div v-if="favoriteBanks.length > 0" class="bank-items-list">
          <p class="result-count">내가 저장한 은행 <strong>{{ favoriteBanks.length }}</strong>곳</p>
          <div v-for="(bank, index) in favoriteBanks" :key="index" class="bank-item" @click="clickBankItem(bank)" style="cursor: pointer;">
            <div class="bank-info">
              <span class="bank-badge fav-badge"><i class="bi bi-star-fill"></i></span>
              <div class="bank-details">
                <div class="bank-header-row">
                  <h4 class="bank-name">{{ bank.place_name }}</h4>
                  <button class="fav-toggle-btn is-favorite" @click.stop="toggleFavorite(bank)">
                    <i class="bi bi-star-fill"></i>
                  </button>
                </div>
                <p class="bank-address"><i class="bi bi-geo-alt-fill me-1"></i> {{ bank.road_address_name || bank.address_name }}</p>
                <p v-if="bank.phone" class="bank-phone"><i class="bi bi-telephone-fill me-1"></i> {{ bank.phone }}</p>
                <!-- ✅ 즐겨찾기 탭에도 길찾기 버튼 추가 -->
                <button class="directions-btn" @click.stop="goToDirections(bank)">
                  <i class="bi bi-signpost-2-fill"></i> 길찾기
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="no-result">
          <p><i class="bi bi-star me-1"></i> 아직 즐겨찾기한 은행이 없습니다.</p>
          <span>자주 방문하는 은행 옆의 별을 클릭해 저장해 보세요!</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'  // ✅ 추가
import axios from 'axios'
import { regionData } from '@/utils/regionData'
import { useAlert } from '@/composables/useAlert'

const { alert } = useAlert()
const router = useRouter()  // ✅ 추가

// 현재 위치 (거리순 정렬용)
const userLocation = ref(null)  // { lat, lng }

const props = defineProps({
  banks: { type: Array, default: () => [] },
  initialQuery: { type: String, default: '' }
})

const emit = defineEmits(['searchResult', 'selectBank'])

const activeTab = ref('list')
const selectedSido = ref('')
const selectedGugun = ref('')
const bankName = ref('')
const gugunList = ref([])

const localBanks = ref([...props.banks])
const favoriteBanks = ref([])

const sidoOpen = ref(false)
const gugunOpen = ref(false)
const sidoRef = ref(null)
const gugunRef = ref(null)

const handleOutsideClick = (e) => {
  if (sidoRef.value && !sidoRef.value.contains(e.target)) sidoOpen.value = false
  if (gugunRef.value && !gugunRef.value.contains(e.target)) gugunOpen.value = false
}

const clickBankItem = (bank) => { emit('selectBank', bank) }

// ✅ 길찾기 페이지로 이동
const goToDirections = (bank) => {
  router.push({
    name: 'directions',
    query: {
      lat: bank.y,
      lng: bank.x,
      name: bank.place_name,
      address: bank.road_address_name || bank.address_name
    }
  })
}

const fetchFavorites = async () => {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return
    const response = await axios.get('http://127.0.0.1:8000/api/v1/map/favorites/', { headers: { Authorization: `Bearer ${token}` } })
    favoriteBanks.value = response.data.map(fav => ({ id: fav.kakao_id, place_name: fav.place_name, road_address_name: fav.road_address_name, address_name: fav.address_name, phone: fav.phone }))
  } catch (error) { console.error('즐겨찾기 목록 로드 실패:', error) }
}

// Haversine 공식으로 두 좌표 간 거리(km) 계산
const getDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

const sortByDistance = (banks) => {
  if (!userLocation.value) return banks
  const { lat, lng } = userLocation.value
  return [...banks].sort((a, b) =>
    getDistance(lat, lng, parseFloat(a.y), parseFloat(a.x)) -
    getDistance(lat, lng, parseFloat(b.y), parseFloat(b.x))
  )
}

const searchBanks = () => {
  if (!window.kakao || !window.kakao.maps) return
  const ps = new window.kakao.maps.services.Places()
  const query = [selectedSido.value, selectedGugun.value, bankName.value || '은행'].filter(Boolean).join(' ')
  ps.keywordSearch(query, (data, status) => {
    if (status === window.kakao.maps.services.Status.OK) {
      const sorted = sortByDistance(data)
      localBanks.value = sorted
      emit('searchResult', sorted)
    } else {
      localBanks.value = []
      emit('searchResult', [])
    }
  }, { category_group_code: 'BK9' })
}

onMounted(() => {
  fetchFavorites()
  document.addEventListener('click', handleOutsideClick)
  // 현재 위치 조용히 가져오기 (성공 시 이후 검색에 반영)
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        userLocation.value = { lat: pos.coords.latitude, lng: pos.coords.longitude }
      },
      () => { /* 거부 시 거리 정렬 없이 그냥 표시 */ }
    )
  }
})

watch(() => props.initialQuery, (query) => {
  if (query) {
    bankName.value = query
    const trySearch = setInterval(() => {
      if (window.kakao && window.kakao.maps) {
        clearInterval(trySearch)
        searchBanks()
      }
    }, 200)
  }
}, { immediate: true })

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
})

const isFavorite = (bank) => { return favoriteBanks.value.some(b => b.id === String(bank.id)) }

const toggleFavorite = async (bank) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    await alert('로그인이 필요한 서비스입니다.', '로그인 필요')
    return;
  }
  try {
    await axios.post('http://127.0.0.1:8000/api/v1/map/favorites/', {
      id: String(bank.id),
      place_name: bank.place_name,
      road_address_name: bank.road_address_name,
      address_name: bank.address_name,
      phone: bank.phone
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    await fetchFavorites();
  } catch (error) {
    await alert('요청 처리 중 오류가 발생했습니다.', '오류')
  }
}

watch(() => props.banks, (newBanks) => {
  localBanks.value = newBanks || []
  if (newBanks && newBanks.length > 0) activeTab.value = 'list'
}, { immediate: true })

const sidoList = Object.keys(regionData)
const onSidoChange = () => {
  selectedGugun.value = ''
  gugunList.value = regionData[selectedSido.value] || []
}
</script>

<style scoped>
.bank-list-container { font-family: 'Pretendard', -apple-system, sans-serif; display: flex; flex-direction: column; height: 100%; box-sizing: border-box; }
.search-section { background-color: #f9f8f5; padding: 16px 20px; flex-shrink: 0; }
.search-title { font-size: 16px; font-weight: 700; color: #333d29; margin: 0 0 2px 0; display: flex; align-items: center; }
.search-title i { color: #606c38; }
.search-subtitle { font-size: 12px; color: #606c38; margin: 0 0 12px 0; }
.search-form { display: flex; gap: 8px; }
.form-group { flex: 1; }

input { width: 100%; padding: 8px 12px; font-size: 13px; border: 1.5px solid #A0BAA3; border-radius: 6px; background-color: #ffffff; outline: none; box-sizing: border-box; }

.custom-select-wrapper { position: relative; flex: 1; }
.custom-select-box { display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; font-size: 13px; border: 1.5px solid #A0BAA3; border-radius: 6px; background-color: #ffffff; cursor: pointer; user-select: none; transition: border-color 0.2s, box-shadow 0.2s; white-space: nowrap; overflow: hidden; }
.custom-select-box.open { border-color: #86A78A; box-shadow: 0 0 0 2px rgba(134, 167, 138, 0.2); }
.custom-select-box.disabled { background-color: #f5f5f0; cursor: not-allowed; opacity: 0.6; }
.custom-select-box span { color: #333; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; background-color: transparent !important; opacity: 1 !important; }
.custom-select-box span.is-placeholder { color: #aaa; }
.arrow-icon { width: 16px; height: 16px; flex-shrink: 0; transition: transform 0.2s; }
.arrow-icon.rotated { transform: rotate(180deg); }
.custom-options { position: absolute; top: calc(100% + 4px); left: 0; right: 0; background: #ffffff; border: 1.5px solid #A0BAA3; border-radius: 6px; max-height: 200px; overflow-y: auto; list-style: none; margin: 0; padding: 4px 0; z-index: 1000; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.custom-options li { padding: 8px 14px; font-size: 13px; cursor: pointer; transition: background 0.15s; color: #333; }
.custom-options li:hover { background-color: #f0f4f0; }
.custom-options li.selected { color: #606c38; font-weight: 600; background-color: #edf2ed; }
.custom-options::-webkit-scrollbar { width: 4px; }
.custom-options::-webkit-scrollbar-thumb { background: #c4c3b7; border-radius: 4px; }

.search-btn { display: flex; align-items: center; gap: 4px; padding: 8px 14px; font-size: 13px; font-weight: 600; color: #ffffff; background-color: #86A78A; border: none; border-radius: 6px; cursor: pointer; white-space: nowrap; }

.tab-navigation { display: flex; background-color: #ffffff; border-bottom: 1px solid #e6e5da; flex-shrink: 0; }
.tab-btn { flex: 1; padding: 12px; font-size: 13px; font-weight: 600; background: none; border: none; color: #888; cursor: pointer; transition: all 0.2s ease; border-bottom: 3px solid transparent; display: flex; justify-content: center; align-items: center; }
.tab-btn.active { color: #86A78A; border-bottom-color: #86A78A; background-color: #fcfbfa; }

.results-section { flex: 1; overflow-y: auto; padding: 16px; background-color: #ffffff; }
.results-section::-webkit-scrollbar { width: 5px; }
.results-section::-webkit-scrollbar-thumb { background-color: #c4c3b7; border-radius: 4px; }

.result-count { font-size: 12px; color: #666; margin-bottom: 10px; }
.result-count strong { color: #86A78A; }
.sort-badge { font-size: 10px; color: #86A78A; font-weight: 600; margin-left: 6px; }

.bank-item { background-color: #ffffff; border: 1px solid #e6e5da; border-radius: 8px; padding: 12px; margin-bottom: 8px; transition: border-color 0.15s ease; }
.bank-item:hover { border-color: #86A78A; }
.bank-info { display: flex; gap: 10px; }
.bank-badge { background-color: #A0BAA3; color: white; font-size: 10px; font-weight: 700; border-radius: 50%; width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.bank-badge.fav-badge { background-color: #ffcc00; font-size: 10px; }
.bank-details { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.bank-header-row { display: flex; justify-content: space-between; align-items: center; }
.bank-name { font-size: 13px; font-weight: 600; color: #222; margin: 0; }
.fav-toggle-btn { background: none; border: none; cursor: pointer; font-size: 16px; color: #ccc; padding: 0 4px; transition: transform 0.1s ease, color 0.1s ease; outline: none; display: flex; align-items: center; }
.fav-toggle-btn:hover { transform: scale(1.2); }
.fav-toggle-btn.is-favorite { color: #ffcc00; filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.1)); }

.bank-address, .bank-phone { display: flex; align-items: center; gap: 4px; margin: 0; }
.bank-address { font-size: 12px; color: #666; }
.bank-address i { color: #A0BAA3; }
.bank-phone { font-size: 11px; color: #86A78A; }

/* ✅ 길찾기 버튼 스타일 */
.directions-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  color: #86A78A;
  background: #edf5ee;
  border: 1px solid #A0BAA3;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  align-self: flex-start;
}
.directions-btn:hover {
  background: #86A78A;
  color: #fff;
  border-color: #86A78A;
}

.no-result { text-align: center; padding: 40px 10px; border: 1px dashed #d1d0c5; border-radius: 8px; }
.no-result p { font-size: 13px; font-weight: 600; color: #333d29; margin: 0 0 4px 0; display: flex; align-items: center; justify-content: center; }
.no-result span { font-size: 11px; color: #86A78A; }
</style>