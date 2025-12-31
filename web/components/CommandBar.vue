<template>
  <div class="command-bar">
    <button
      v-for="chip in chips"
      :key="chip"
      class="chip"
      type="button"
      @click="$emit('append', chip)"
    >
      {{ chip }}
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  chips: string[];
}>();

defineEmits<{
  (e: 'append', value: string): void;
}>();
</script>
