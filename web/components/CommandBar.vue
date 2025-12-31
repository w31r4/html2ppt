<template>
  <div class="flex flex-wrap gap-2 pt-2">
    <button
      v-for="chip in chips"
      :key="chip"
      class="px-3 py-1.5 rounded-full border border-gray-200 dark:border-gray-700 hover:border-primary/50 text-xs text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-800 transition-colors"
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
