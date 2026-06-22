<template>
  <div class="bank-list-container">
    <div class="search-section">
      <h2 class="search-title">
        <i class="bi bi-bank me-1"></i> 주변 은행 찾기
      </h2>
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
        <i class="bi bi-folder-fill me-1"></i> 검색 결과 ({{ localBanks.length }})
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'favorites' }" 
        @click="activeTab = 'favorites'"
      >
        <i class="bi bi-star-fill me-1"></i> 즐겨찾기 ({{ favoriteBanks.length }})
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
                    <i :class="isFavorite(bank) ? 'bi bi-star-fill' : 'bi bi-star'"></i>
                  </button>
                </div>
                <p class="bank-address">
                  <i class="bi bi-geo-alt-fill me-1"></i> {{ bank.road_address_name || bank.address_name }}
                </p>
                <p v-if="bank.phone" class="bank-phone">
                  <i class="bi bi-telephone-fill me-1"></i> {{ bank.phone }}
                </p>
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
          
          <div 
            v-for="(bank, index) in favoriteBanks" 
            :key="index" 
            class="bank-item"
            @click="clickBankItem(bank)"
            style="cursor: pointer;"
          >
            <div class="bank-info">
              <span class="bank-badge fav-badge">
                <i class="bi bi-star-fill"></i>
              </span>
              <div class="bank-details">
                <div class="bank-header-row">
                  <h4 class="bank-name">{{ bank.place_name }}</h4>
                  <button 
                    class="fav-toggle-btn is-favorite" 
                    @click.stop="toggleFavorite(bank)"
                  >
                    <i class="bi bi-star-fill"></i>
                  </button>
                </div>
                <p class="bank-address">
                  <i class="bi bi-geo-alt-fill me-1"></i> {{ bank.road_address_name || bank.address_name }}
                </p>
                <p v-if="bank.phone" class="bank-phone">
                  <i class="bi bi-telephone-fill me-1"></i> {{ bank.phone }}
                </p>
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
const favoriteBanks = ref([]) 

const clickBankItem = (bank) => {
  emit('selectBank', bank)
}

const fetchFavorites = async () => {
  try {
    const token = localStorage.getItem('access_token') 
    if (!token) return

    const response = await axios.get('http://127.0.0.1:8000/api/v1/map/favorites/', {
      headers: { Authorization: `Bearer ${token}` } 
    })
    
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

onMounted(() => {
  fetchFavorites()
})

const isFavorite = (bank) => {
  return favoriteBanks.value.some(b => b.id === String(bank.id))
}

const toggleFavorite = async (bank) => {
  try {
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
      headers: { Authorization: `Bearer ${token}` }
    })

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
  display: flex;
  align-items: center;
}
/* 🎯 제목 아이콘 포인트 컬러 */
.search-title i {
  color: #606c38; 
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
  display: flex;
  justify-content: center;
  align-items: center;
}

.tab-btn.active {
  color: #86A78A;
  border-bottom-color: #86A78A;
  background-color: #fcfbfa;
}

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
  transition: border-color 0.15s ease;
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

/* 🎯 즐겨찾기 배지 내부 아이콘 센터 정렬 보정 */
.bank-badge.fav-badge {
  background-color: #ffcc00;
  font-size: 10px;
}

.bank-details { flex: 1; display: flex; flex-direction: column; gap: 4px; }

.bank-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bank-name { font-size: 13px; font-weight: 600; color: #222; margin: 0; }

.fav-toggle-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #ccc; 
  padding: 0 4px;
  transition: transform 0.1s ease, color 0.1s ease;
  outline: none;
  display: flex;
  align-items: center;
}

.fav-toggle-btn:hover {
  transform: scale(1.2);
}

.fav-toggle-btn.is-favorite {
  color: #ffcc00;
  filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.1));
}

/* 🎯 아이콘들이 글자와 수평이 잘 맞도록 정렬 보정 */
.bank-address, .bank-phone {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 0;
}
.bank-address { font-size: 12px; color: #666; }
.bank-address i { color: #A0BAA3; } /* 주소 핀 컬러 단장 */

.bank-phone { font-size: 11px; color: #86A78A; }

.no-result {
  text-align: center;
  padding: 40px 10px;
  border: 1px dashed #d1d0c5;
  border-radius: 8px;
}
.no-result p { 
  font-size: 13px; 
  font-weight: 600; 
  color: #333d29; 
  margin: 0 0 4px 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.no-result span { font-size: 11px; color: #86A78A; }
</style>