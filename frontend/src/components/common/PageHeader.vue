<template>
  <div class="page-header">
    <div class="page-header-text">
      <h2 class="page-header-title">{{ title }}</h2>
      <p v-if="description" class="page-header-desc">{{ description }}</p>
    </div>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1.5px solid #e8e6df;
}
.page-header-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: #2d2d25;
  margin-bottom: 4px;
  letter-spacing: -0.3px;
}
.page-header-desc {
  font-size: 0.86rem;
  color: #a0a090;
  margin: 0;
}
</style>
