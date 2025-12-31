<template>
  <div class="chat-thread">
    <div v-for="message in messages" :key="message.id" :class="['message', message.role]">
      <div class="avatar" v-if="message.role !== 'meta'">
        {{ message.role === 'user' ? 'YOU' : 'AGT' }}
      </div>
      <div class="bubble">
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
