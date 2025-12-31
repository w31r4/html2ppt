<template>
  <div class="space-y-6">
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
  </div>
</template>

<script setup lang="ts">
import type { Message } from '@/stores/session';

defineProps<{
  messages: Message[];
}>();
</script>
