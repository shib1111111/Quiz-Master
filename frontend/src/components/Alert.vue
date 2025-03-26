<template>
  <transition name="slide">
    <div v-if="visible" :class="['alert', alertTypeClass]" role="alert">
      <slot>{{ message }}</slot>
      <button v-if="dismissible" type="button" class="btn-close" @click="closeAlert"></button>
    </div>
  </transition>
</template>

<script>
import { ref, computed, onMounted } from 'vue';

export default {
  props: {
    message: { type: String, default: '' },
    type: { type: String, default: 'info' }, // 'error', 'success', 'warning', 'info'
    duration: { type: Number, default: 3000 }, // ms, 0 to disable auto-dismiss
    dismissible: { type: Boolean, default: true }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const visible = ref(true);

    const alertTypeClass = computed(() => ({
      'alert-danger': props.type === 'error',
      'alert-success': props.type === 'success',
      'alert-warning': props.type === 'warning',
      'alert-info': props.type === 'info'
    }));

    function closeAlert() {
      visible.value = false;
      emit('close');
    }

    onMounted(() => {
      if (props.duration > 0) {
        setTimeout(closeAlert, props.duration);
      }
    });

    return { visible, alertTypeClass, closeAlert };
  }
};
</script>

<style scoped>
.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease;
}
.slide-enter-from, .slide-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>



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
