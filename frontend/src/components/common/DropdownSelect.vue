<template>
  <div class="ds-wrap" ref="wrapRef">
    <button type="button" class="ds-trigger" @click.stop="toggle">
      <span class="ds-text" :class="{ 'ds-placeholder': !hasValue }">{{ displayText }}</span>
      <i class="bi bi-chevron-down ds-chevron" :class="{ 'ds-open': isOpen }"></i>
    </button>

    <div v-if="isOpen" class="ds-panel" @click.stop>
      <label
        v-for="opt in options"
        :key="opt.value"
        class="ds-item"
        :class="{ 'ds-item--active': isSelected(opt.value) }"
        @click="handleSelect(opt.value)"
      >
        <span v-if="opt.emoji" class="ds-emoji">{{ opt.emoji }}</span>
        <span class="ds-label">{{ opt.label }}</span>
        <i v-if="isSelected(opt.value)" class="bi bi-check2 ds-check"></i>
      </label>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  options:      { type: Array,   required: true },
  modelValue:   { default: null },
  multiple:     { type: Boolean, default: false },
  placeholder:  { type: String,  default: '선택하세요' },
})

const emit = defineEmits(['update:modelValue'])

const isOpen  = ref(false)
const wrapRef = ref(null)

const hasValue = computed(() =>
  props.multiple ? props.modelValue?.length > 0 : !!props.modelValue
)

const displayText = computed(() => {
  if (props.multiple) {
    if (!props.modelValue?.length) return props.placeholder
    return props.modelValue
      .map(v => props.options.find(o => o.value === v)?.label)
      .filter(Boolean)
      .join(', ')
  }
  return props.options.find(o => o.value === props.modelValue)?.label || props.placeholder
})

function isSelected(value) {
  return props.multiple
    ? Array.isArray(props.modelValue) && props.modelValue.includes(value)
    : props.modelValue === value
}

function toggle() {
  isOpen.value = !isOpen.value
}

function handleSelect(value) {
  if (props.multiple) {
    const current = Array.isArray(props.modelValue) ? [...props.modelValue] : []
    const idx = current.indexOf(value)
    if (idx >= 0) current.splice(idx, 1)
    else current.push(value)
    emit('update:modelValue', current)
  } else {
    emit('update:modelValue', value)
    isOpen.value = false
  }
}

function onOutsideClick() {
  isOpen.value = false
}

onMounted(() => document.addEventListener('click', onOutsideClick))
onUnmounted(() => document.removeEventListener('click', onOutsideClick))
</script>

<style scoped>
.ds-wrap {
  position: relative;
  width: 100%;
}

.ds-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 0.9rem;
  background: white;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #333;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
  text-align: left;
}
.ds-trigger:focus,
.ds-wrap:focus-within .ds-trigger {
  border-color: #A0BAA3;
  box-shadow: 0 0 0 3px rgba(160, 186, 163, 0.2);
  outline: none;
}

.ds-placeholder {
  color: #aaa;
}

.ds-chevron {
  font-size: 0.8rem;
  color: #aaa;
  transition: transform 0.2s;
  flex-shrink: 0;
  margin-left: 0.5rem;
}
.ds-open {
  transform: rotate(180deg);
  color: #86A78A;
}

.ds-panel {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: white;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  z-index: 100;
  overflow: hidden;
  max-height: 260px;
  overflow-y: auto;
}

.ds-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.65rem 1rem;
  cursor: pointer;
  font-size: 0.88rem;
  color: #444;
  transition: background 0.15s;
}
.ds-item:hover {
  background: #f5faf5;
}
.ds-item--active {
  background: #eaf4eb;
  color: #4a8a50;
  font-weight: 600;
}

.ds-emoji {
  font-size: 1rem;
  width: 1.4rem;
  text-align: center;
}
.ds-label {
  flex: 1;
}
.ds-check {
  color: #86A78A;
  font-size: 1rem;
  font-weight: 700;
}
</style>
