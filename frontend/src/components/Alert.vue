<template>
  <transition name="slide">
    <div v-if="visible" :class="['alert', alertTypeClass]" role="alert">
      <slot>{{ message }}</slot>
      <button v-if="dismissible" type="button" class="close" @click="closeAlert">&times;</button>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

// Define props for message, type, duration, and dismissibility.
const props = defineProps({
  message: { type: String, default: '' },
  type: { type: String, default: 'info' }, // Options: 'error', 'success', 'warning', 'info'
  duration: { type: Number, default: 3000 }, // Duration in ms (set 0 to disable auto-dismiss)
  dismissible: { type: Boolean, default: true }
});

// Emit event to notify parent on alert close.
const emit = defineEmits(['close']);

// Local state for visibility.
const visible = ref(true);

// Compute the alert class based on type.
const alertTypeClass = computed(() => {
  const types = {
    error: 'alert-danger',
    success: 'alert-success',
    warning: 'alert-warning',
    info: 'alert-info'
  };
  return types[props.type] || types.info;
});

// Function to close the alert.
function closeAlert() {
  visible.value = false;
  emit('close');
}

// Auto-dismiss the alert after the specified duration.
onMounted(() => {
  if (props.duration > 0) {
    setTimeout(closeAlert, props.duration);
  }
});
</script>

<style scoped>
/* Slide transition: the alert starts 2 inches to the right */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.5s ease, opacity 0.5s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(2in);
  opacity: 0;
}
.slide-enter-to,
.slide-leave-from {
  transform: translateX(0);
  opacity: 1;
}

/* Basic alert styling */
.alert {
  position: relative;
  padding-right: 3rem; /* Reserve space for the close button */
}

/* Styling for the close ("X") button */
.close {
  position: absolute;
  top: 0;
  right: 0;
  padding: 0.75rem;
  border: none;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
}
</style>
