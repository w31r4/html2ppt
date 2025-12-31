<template>
  <header class="top-header">
    <div class="brand">
      <div class="brand-mark"></div>
      <div class="brand-copy">
        <h1>HTML2PPT Agent</h1>
        <p>Conversational workspace for Slidev generation</p>
      </div>
      <div class="status-pill" v-if="statusLabel">
        <span class="status-dot"></span>
        <span>{{ statusLabel }}</span>
      </div>
    </div>
    <div class="header-actions">
      <select
        v-if="sessions.length"
        class="chip"
        :value="activeSession"
        @change="onSelect"
      >
        <option value="">Recent sessions</option>
        <option v-for="session in sessions" :key="session.id" :value="session.id">
          {{ session.title }}
        </option>
      </select>
      <button class="btn-ghost" type="button" @click="$emit('open-streamlit')">
        Open Streamlit
      </button>
      <button class="btn-ghost" type="button" @click="$emit('new-session')">
        New session
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import type { SessionHistoryEntry, SessionStatus } from '@/stores/session';

const props = defineProps<{
  status: SessionStatus;
  sessions: SessionHistoryEntry[];
  activeSession: string;
}>();

const emit = defineEmits<{
  (e: 'select-session', id: string): void;
  (e: 'new-session'): void;
  (e: 'open-streamlit'): void;
}>();

const statusLabel = computed(() => {
  if (!props.status || props.status === 'idle') return '';
  const labels: Record<string, string> = {
    pending: 'Preparing',
    outline_ready: 'Outline Ready',
    draft: 'Outline Draft',
    confirmed: 'Confirmed',
    generating: 'Generating',
    assembling: 'Assembling',
    completed: 'Ready',
    error: 'Error'
  };
  return labels[props.status] || props.status;
});

const onSelect = (event: Event) => {
  const target = event.target as HTMLSelectElement;
  emit('select-session', target.value);
};
</script>
