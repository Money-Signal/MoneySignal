<template>
  <div :class="['loading-spinner-wrap', { small }]">
    <img src="@/assets/loading-spinner.svg" alt="로딩 중" class="spinner-img" />
    <p class="loading-text">신호를 찾는중...</p>
  </div>
</template>

<script setup>
defineProps({
  small: { type: Boolean, default: false }
})
</script>

<style scoped>
.loading-spinner-wrap {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem 0;
  gap: 4px;
}

.loading-spinner-wrap.small {
  padding: 0.75rem 0;
}

.spinner-img {
  width: 80px;
  height: 80px;
}

.loading-spinner-wrap.small .spinner-img {
  width: 44px;
  height: 44px;
}

.loading-text {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #86A78A;
  letter-spacing: 0.3px;
}

.loading-spinner-wrap.small .loading-text {
  font-size: 11px;
}
</style>
