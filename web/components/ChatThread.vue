<template>
  <div ref="container" class="space-y-6">
    <div v-for="message in messages" :key="message.id" :class="['flex gap-3', message.role === 'user' ? 'flex-row-reverse' : '']">
      <div
        v-if="message.role !== 'meta'"
        class="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0"
        :class="message.role === 'user' ? 'bg-primary/20 text-primary' : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'"
      >
        {{ message.role === 'user' ? 'YOU' : 'AGT' }}
      </div>
      <div
        class="p-3 rounded-2xl text-sm shadow-sm max-w-[90%]"
        :class="[
          message.role === 'user'
            ? 'bg-primary/10 border border-primary/20 text-gray-900 dark:text-gray-100 rounded-tr-none'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-none'
        ]"
      >
        {{ message.content }}
      </div>
    </div>
    <!-- Loading indicator when generating -->
    <div v-if="isLoading" class="flex gap-3">
      <div class="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
        AGT
      </div>
      <div class="p-3 rounded-2xl text-sm shadow-sm bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-none">
        <div class="flex items-center gap-2">
          <span class="inline-flex gap-1">
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms;"></span>
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms;"></span>
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms;"></span>
          </span>
          <span class="text-gray-500 dark:text-gray-400 text-xs">{{ loadingText }}</span>
        </div>
      </div>
    </div>
    <!-- Scroll anchor -->
    <div ref="scrollAnchor"></div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from 'vue';

import type { Message } from '@/stores/session';

const props = defineProps<{
  messages: Message[];
  isLoading?: boolean;
  loadingText?: string;
}>();

const container = ref<HTMLElement | null>(null);
const scrollAnchor = ref<HTMLElement | null>(null);

// Auto-scroll to bottom when messages change or loading state changes
watch(
  () => [props.messages.length, props.isLoading],
  async () => {
    await nextTick();
    scrollAnchor.value?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }
);
</script>

<style scoped>
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
.animate-bounce {
  animation: bounce 0.6s infinite;
}
</style>
