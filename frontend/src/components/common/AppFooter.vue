<template>
  <footer class="app-footer">
    <div class="footer-inner">

      <!-- 상단: 3컬럼 -->
      <div class="footer-grid">

        <!-- 서비스 -->
        <div class="footer-col">
          <p class="footer-col-title">서비스</p>
          <ul>
            <li><RouterLink to="/products">예·적금 상품</RouterLink></li>
            <li><RouterLink to="/currency">환율 조회</RouterLink></li>
            <li><RouterLink to="/video">영상 검색</RouterLink></li>
            <li><RouterLink to="/map">주변 은행 찾기</RouterLink></li>
            <li><RouterLink to="/exchange">금·은 시세</RouterLink></li>
            <li><RouterLink to="/community">커뮤니티</RouterLink></li>
          </ul>
        </div>

        <!-- 팀 정보 -->
        <div class="footer-col">
          <p class="footer-col-title">팀 정보</p>
          <ul>
            <li>삼성 청년 SW 아카데미 15기</li>
            <li>관통 프로젝트 · 1학기</li>
            <li class="team-stack">Django · Vue.js</li>
          </ul>
        </div>

        <!-- 데이터 출처 -->
        <div class="footer-col">
          <p class="footer-col-title">데이터 출처</p>
          <ul>
            <li>환율: 한국은행 API</li>
            <li>금융 상품: 금융감독원 API</li>
            <li>영상: YouTube Data API v3</li>
            <li>지도: Kakao Maps API</li>
          </ul>
        </div>

      </div>

      <!-- 하단: 카피라이트 -->
      <div class="footer-bottom">
        <span class="footer-logo">MoneySignal</span>
        <span class="footer-copy">© 2025 MoneySignal. SSAFY 15기 관통 프로젝트.</span>
      </div>

    </div>
  </footer>
</template>

<script setup>
</script>

<style scoped>
.app-footer {
  background: #f9f8f5;
  border-top: 0.5px solid #e8e6e0;
  padding: 44px 0 28px;
  margin-top: auto;
}

.footer-inner {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 30px;
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
  margin-bottom: 36px;
}

.footer-col-title {
  font-size: 13px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 14px;
  letter-spacing: 0.02em;
}

.footer-col ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.footer-col ul li {
  font-size: 13px;
  color: #888;
  line-height: 1.5;
}

.footer-col ul li a {
  font-size: 13px;
  color: #888;
  text-decoration: none;
  transition: color 0.15s;
}

.footer-col ul li a:hover {
  color: #6A7F5A;
}

.team-stack {
  color: #6A7F5A !important;
  font-weight: 600;
}

.footer-bottom {
  border-top: 0.5px solid #e8e6e0;
  padding-top: 22px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.footer-logo {
  font-size: 15px;
  font-weight: 800;
  color: #6A7F5A;
  letter-spacing: -0.3px;
}

.footer-copy {
  font-size: 12px;
  color: #bbb;
}
</style>