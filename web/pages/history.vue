<template>
  <div class="max-w-3xl mx-auto animate-fade-in px-4 md:px-0 py-6 md:py-0">
    <header class="mb-6 md:mb-8">
      <h1 class="text-2xl md:text-3xl font-semibold text-text-light dark:text-text-dark mb-2">History</h1>
      <p class="text-sm md:text-base text-gray-500 dark:text-gray-400">View and resume your past generation sessions.</p>
    </header>

    <!-- Loading Skeleton -->
    <div v-if="isLoading" class="flex flex-col gap-4">
      <div v-for="i in 3" :key="i" class="card p-5 animate-pulse">
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-48 mb-3"></div>
            <div class="flex items-center gap-3">
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
            </div>
          </div>
          <div class="w-9 h-9 rounded-full bg-gray-200 dark:bg-gray-700"></div>
        </div>
      </div>
    </div>

    <!-- History List -->
    <div v-else-if="store.history.length" class="flex flex-col gap-3 md:gap-4">
      <button
        v-for="session in store.history"
        :key="session.id"
        class="card p-4 md:p-5 flex items-center justify-between cursor-pointer hover:border-primary hover:-translate-y-0.5 transition-all duration-200 text-left w-full focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
        @click="resumeSession(session.id)"
      >
        <div class="flex-1 min-w-0">
          <h3 class="text-base md:text-lg font-semibold text-text-light dark:text-text-dark mb-1 md:mb-2 truncate">
            {{ session.title || 'Untitled Session' }}
          </h3>
          <div class="flex flex-wrap items-center gap-2 md:gap-3 text-xs md:text-sm text-gray-500 dark:text-gray-400">
            <span>{{ formatDate(session.createdAt) }}</span>
            <span
              class="text-xs uppercase tracking-wide px-2 py-0.5 rounded-full border"
              :class="getStatusClass(session.status)"
            >
              {{ session.status }}
            </span>
          </div>
        </div>
        <div
          class="w-8 h-8 md:w-9 md:h-9 rounded-full border border-border-light dark:border-border-dark flex items-center justify-center text-gray-400 hover:bg-primary hover:text-white hover:border-primary transition-all shrink-0 ml-3"
          aria-hidden="true"
        >
          <span class="material-symbols-rounded text-base md:text-lg">arrow_forward</span>
        </div>
      </button>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12 md:py-16 card border-dashed">
      <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
        <span class="material-symbols-rounded text-3xl text-gray-400 dark:text-gray-500">history</span>
      </div>
      <h3 class="text-lg md:text-xl font-semibold text-text-light dark:text-text-dark mb-2">No history yet</h3>
      <p class="text-sm md:text-base text-gray-500 dark:text-gray-400 mb-6">Start a new session to see it here.</p>
      <NuxtLink to="/" class="btn btn-primary inline-flex items-center gap-2">
        <span class="material-symbols-rounded text-lg">add</span>
        Start New Session
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

import { useSessionStore } from '@/stores/session';

const store = useSessionStore();
const router = useRouter();
const isLoading = ref(true);

onMounted(async () => {
  await store.initHistory();
  isLoading.value = false;
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

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
