<template>
  <div class="bank-list-container">
    <div class="search-section">
      <h2 class="search-title">🏦 주변 은행 찾기</h2>
      <p class="search-subtitle">원하시는 지역과 은행명을 입력해 주세요.</p>
      
      <div class="search-form">
        <div class="form-group">
          <select v-model="selectedSido" @change="onSidoChange" @keyup.enter="searchBanks">
            <option value="">광역시도 선택</option>
            <option v-for="sido in sidoList" :key="sido" :value="sido">{{ sido }}</option>
          </select>
        </div>

        <div class="form-group">
          <select v-model="selectedGugun" :disabled="!selectedSido || gugunList.length <= 1" @keyup.enter="searchBanks">
            <option value="">시군구 선택</option>
            <option v-for="gugun in gugunList" :key="gugun" :value="gugun">{{ gugun }}</option>
          </select>
        </div>

        <div class="form-group input-wrapper">
          <input 
            v-model="bankName" 
            placeholder="은행명 (예: 국민은행)" 
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
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'list' }" 
        @click="activeTab = 'list'"
      >
        📂 검색 결과 ({{ localBanks.length }})
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'favorites' }" 
        @click="activeTab = 'favorites'"
      >
        ⭐ 즐겨찾기 ({{ favoriteBanks.length }})
      </button>
    </div>

    <div class="results-section">
      
      <div v-if="activeTab === 'list'" class="tab-content-wrapper">
        <div v-if="localBanks.length > 0" class="bank-items-list">
          <p class="result-count">검색 결과 총 <strong>{{ localBanks.length }}</strong>건</p>
          
          <div 
            v-for="(bank, index) in localBanks" 
            :key="index" 
            class="bank-item"
            @click="clickBankItem(bank)"
            style="cursor: pointer;"
          >
            <div class="bank-info">
              <span class="bank-badge">{{ index + 1 }}</span>
              <div class="bank-details">
                <div class="bank-header-row">
                  <h4 class="bank-name">{{ bank.place_name }}</h4>
                  <button 
                    class="fav-toggle-btn" 
                    :class="{ 'is-favorite': isFavorite(bank) }" 
                    @click.stop="toggleFavorite(bank)"
                  >
                    {{ isFavorite(bank) ? '★' : '☆' }}
                  </button>
                </div>
                <p class="bank-address">{{ bank.road_address_name || bank.address_name }}</p>
                <p v-if="bank.phone" class="bank-phone">📞 {{ bank.phone }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="no-result">
          <p>🔍 검색된 은행 결과가 없습니다.</p>
          <span>지역을 선택하고 검색 버튼을 누르거나 엔터를 쳐보세요!</span>
        </div>
      </div>

      <div v-if="activeTab === 'favorites'" class="tab-content-wrapper">
        <div v-if="favoriteBanks.length > 0" class="bank-items-list">
          <p class="result-count">내가 저장한 은행 <strong>{{ favoriteBanks.length }}</strong>곳</p>
          
          <div 
            v-for="(bank, index) in favoriteBanks" 
            :key="index" 
            class="bank-item"
            @click="clickBankItem(bank)"
            style="cursor: pointer;"
          >
            <div class="bank-info">
              <span class="bank-badge fav-badge">⭐</span>
              <div class="bank-details">
                <div class="bank-header-row">
                  <h4 class="bank-name">{{ bank.place_name }}</h4>
                  <button 
                    class="fav-toggle-btn is-favorite" 
                    @click.stop="toggleFavorite(bank)"
                  >
                    ★
                  </button>
                </div>
                <p class="bank-address">{{ bank.road_address_name || bank.address_name }}</p>
                <p v-if="bank.phone" class="bank-phone">📞 {{ bank.phone }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="no-result">
          <p>⭐ 아직 즐겨찾기한 은행이 없습니다.</p>
          <span>자주 방문하는 은행 옆의 별을 클릭해 저장해 보세요!</span>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'
import { regionData } from '@/utils/regionData'

const props = defineProps({
  banks: { type: Array, default: () => [] }
})

const emit = defineEmits(['searchResult', 'selectBank'])

const activeTab = ref('list')
const selectedSido = ref('')
const selectedGugun = ref('')
const bankName = ref('')
const gugunList = ref([])

const localBanks = ref([...props.banks])
const favoriteBanks = ref([]) // DB에서 가져온 진짜 즐겨찾기 리스트

const clickBankItem = (bank) => {
  emit('selectBank', bank)
}

// 🚀 1. 백엔드에서 현재 유저의 즐겨찾기 목록 받아오기
const fetchFavorites = async () => {
  try {
    // 🔍 확인된 로컬 스토리지의 키 'access_token'으로 토큰을 가져옵니다.
    const token = localStorage.getItem('access_token') 
    if (!token) return

    const response = await axios.get('http://127.0.0.1:8000/api/v1/map/favorites/', {
      // 🔍 JWT 방식에 맞추어 접두사를 'Bearer'로 변경합니다.
      headers: { Authorization: `Bearer ${token}` } 
    })
    
    // 카카오맵 템플릿 포맷에 맞춰 데이터 매핑
    favoriteBanks.value = response.data.map(fav => ({
      id: fav.kakao_id,
      place_name: fav.place_name,
      road_address_name: fav.road_address_name,
      address_name: fav.address_name,
      phone: fav.phone
    }))
  } catch (error) {
    console.error('즐겨찾기 목록 로드 실패:', error)
  }
}

// 화면이 켜지자마자 유저의 즐겨찾기를 불러옵니다.
onMounted(() => {
  fetchFavorites()
})

// 카카오 API의 id는 숫자형일 수 있으므로 안전하게 String으로 변환 후 매칭 검사
const isFavorite = (bank) => {
  return favoriteBanks.value.some(b => b.id === String(bank.id))
}

// 🚀 2. 별을 클릭했을 때 백엔드로 저장/삭제 요청을 보내는 함수
const toggleFavorite = async (bank) => {
  try {
    // 🔍 똑같이 'access_token'에서 토큰을 땡겨옵니다.
    const token = localStorage.getItem('access_token')
    if (!token) {
      alert('로그인이 필요한 서비스입니다.')
      return
    }

    await axios.post('http://127.0.0.1:8000/api/v1/map/favorites/', {
      id: String(bank.id),
      place_name: bank.place_name,
      road_address_name: bank.road_address_name,
      address_name: bank.address_name,
      phone: bank.phone
    }, {
      // 🔍 접두사를 'Bearer'로 세팅하여 전송합니다.
      headers: { Authorization: `Bearer ${token}` }
    })

    // 변경이 끝나면 서버의 최신 상태를 받아와 화면을 동기화합니다.
    await fetchFavorites()
  } catch (error) {
    console.error('즐겨찾기 토글 실패:', error)
    alert('요청 처리 중 오류가 발생했습니다.')
  }
}

watch(() => props.banks, (newBanks) => {
  localBanks.value = newBanks || []
  if (newBanks && newBanks.length > 0) {
    activeTab.value = 'list'
  }
}, { immediate: true })

const sidoList = Object.keys(regionData)

const onSidoChange = () => {
  selectedGugun.value = ''
  gugunList.value = regionData[selectedSido.value] || []
}

const searchBanks = () => {
  if (!window.kakao || !window.kakao.maps) {
    console.error('카카오맵 SDK가 로드되지 않았습니다.')
    return
  }
  const ps = new window.kakao.maps.services.Places()
  const query = [selectedSido.value, selectedGugun.value, bankName.value || '은행'].filter(Boolean).join(' ')

  ps.keywordSearch(query, (data, status) => {
    if (status === window.kakao.maps.services.Status.OK) {
      localBanks.value = data
      emit('searchResult', data)
    } else {
      localBanks.value = []
      emit('searchResult', [])
    }
  }, { category_group_code: 'BK9' })
}
</script>

<style scoped>
/* 세로 스페이스를 꽉 채우기 위해 flex 레이아웃 세팅 */
.bank-list-container {
  font-family: 'Pretendard', -apple-system, sans-serif;
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
}

.search-section {
  background-color: #EBEADD;
  padding: 16px 20px;
  flex-shrink: 0;
}

.search-title {
  font-size: 16px;
  font-weight: 700;
  color: #333d29;
  margin: 0 0 2px 0;
}

.search-subtitle {
  font-size: 12px;
  color: #606c38;
  margin: 0 0 12px 0;
}

.search-form {
  display: flex;
  gap: 8px;
}

.form-group {
  flex: 1;
}

select, input {
  width: 100%;
  padding: 8px 12px;
  font-size: 13px;
  border: 1.5px solid #A0BAA3;
  border-radius: 6px;
  background-color: #ffffff;
  outline: none;
  box-sizing: border-box;
}

select:focus, input:focus {
  border-color: #86A78A;
}

.search-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #ffffff;
  background-color: #86A78A;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
}

/* 🚀 탭 네비게이션 스타일 */
.tab-navigation {
  display: flex;
  background-color: #ffffff;
  border-bottom: 1px solid #e6e5da;
  flex-shrink: 0;
}

.tab-btn {
  flex: 1;
  padding: 12px;
  font-size: 13px;
  font-weight: 600;
  background: none;
  border: none;
  color: #888;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 3px solid transparent;
}

.tab-btn.active {
  color: #86A78A;
  border-bottom-color: #86A78A;
  background-color: #fcfbfa;
}

/* 📜 결과 리스트 본문 영역 */
.results-section {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #ffffff;
}

.results-section::-webkit-scrollbar {
  width: 5px;
}
.results-section::-webkit-scrollbar-thumb {
  background-color: #c4c3b7;
  border-radius: 4px;
}

.result-count {
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
}
.result-count strong { color: #86A78A; }

.bank-item {
  background-color: #ffffff;
  border: 1px solid #e6e5da;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
}
.bank-item:hover { border-color: #86A78A; }

.bank-info { display: flex; gap: 10px; }

.bank-badge {
  background-color: #A0BAA3;
  color: white;
  font-size: 10px;
  font-weight: 700;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* 즐겨찾기 탭 배지 스타일 */
.bank-badge.fav-badge {
  background-color: #ffcc00;
  font-size: 9px;
}

.bank-details { flex: 1; display: flex; flex-direction: column; gap: 2px; }

.bank-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bank-name { font-size: 13px; font-weight: 600; color: #222; margin: 0; }

/* 🚀 즐겨찾기 별 토글 버튼 스타일 커스텀 */
.fav-toggle-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #ccc; /* 비어있는 별 기본 회색 */
  padding: 0 4px;
  transition: transform 0.1s ease, color 0.1s ease;
  outline: none;
}

.fav-toggle-btn:hover {
  transform: scale(1.2);
}

/* 🚀 즐겨찾기가 활성화(is-favorite) 되었을 때 노란색 채우기 */
.fav-toggle-btn.is-favorite {
  color: #ffcc00;
  filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.1));
}

.bank-address { font-size: 12px; color: #666; margin: 0; }
.bank-phone { font-size: 11px; color: #86A78A; margin: 0; }

.no-result {
  text-align: center;
  padding: 40px 10px;
  border: 1px dashed #d1d0c5;
  border-radius: 8px;
}
.no-result p { font-size: 13px; font-weight: 600; color: #333d29; margin: 0 0 4px 0; }
.no-result span { font-size: 11px; color: #86A78A; }
</style>