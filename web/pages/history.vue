<template>
  <div class="max-w-3xl mx-auto animate-fade-in">
    <header class="mb-8">
      <h1 class="text-3xl font-semibold text-text-light dark:text-text-dark mb-2">History</h1>
      <p class="text-gray-500 dark:text-gray-400">View and resume your past generation sessions.</p>
    </header>

    <div class="flex flex-col gap-4" v-if="store.history.length">
      <div
        v-for="session in store.history"
        :key="session.id"
        class="card p-5 flex items-center justify-between cursor-pointer hover:border-primary hover:-translate-y-0.5 transition-all duration-200"
        @click="resumeSession(session.id)"
      >
        <div class="flex-1">
          <h3 class="text-lg font-semibold text-text-light dark:text-text-dark mb-2">
            {{ session.title || 'Untitled Session' }}
          </h3>
          <div class="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
            <span>{{ formatDate(session.createdAt) }}</span>
            <span
              class="text-xs uppercase tracking-wide px-2 py-0.5 rounded-full border"
              :class="getStatusClass(session.status)"
            >
              {{ session.status }}
            </span>
          </div>
        </div>
        <button
          class="w-9 h-9 rounded-full border border-border-light dark:border-border-dark flex items-center justify-center text-gray-400 hover:bg-primary hover:text-white hover:border-primary transition-all"
          aria-label="Resume session"
        >
          <span class="material-symbols-rounded text-lg">arrow_forward</span>
        </button>
      </div>
    </div>

    <div v-else class="text-center py-16 card border-dashed">
      <span class="material-symbols-rounded text-5xl text-gray-300 dark:text-gray-600 mb-4">history</span>
      <h3 class="text-xl font-semibold text-text-light dark:text-text-dark mb-2">No history yet</h3>
      <p class="text-gray-500 dark:text-gray-400 mb-6">Start a new session to see it here.</p>
      <NuxtLink to="/" class="btn btn-primary">Start New Session</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';

import { useSessionStore } from '@/stores/session';

const store = useSessionStore();
const router = useRouter();

onMounted(() => {
  store.initHistory();
});

const resumeSession = (id: string) => {
  store.loadSession(id);
  router.push('/');
};

const formatDate = (timestamp: number) => {
  return new Date(timestamp).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getStatusClass = (status: string) => {
  switch (status) {
    case 'completed':
      return 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-200 dark:border-green-800';
    case 'error':
      return 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-200 dark:border-red-800';
    default:
      return 'bg-gray-50 dark:bg-gray-800 text-gray-500 dark:text-gray-400 border-gray-200 dark:border-gray-700';
  }
};
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
