<template>
  <div class="history-page">
    <header class="page-header">
      <h1>History</h1>
      <p>View and resume your past generation sessions.</p>
    </header>

    <div class="history-list" v-if="store.history.length">
      <div 
        v-for="session in store.history" 
        :key="session.id" 
        class="history-card"
        @click="resumeSession(session.id)"
      >
        <div class="card-content">
          <h3>{{ session.title || 'Untitled Session' }}</h3>
          <div class="meta">
            <span class="date">{{ formatDate(session.createdAt) }}</span>
            <span class="status-badge" :class="session.status">{{ session.status }}</span>
          </div>
        </div>
        <div class="card-actions">
          <button class="btn-icon">
            <div class="icon i-arrow-right"></div>
          </button>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <div class="empty-icon"></div>
      <h3>No history yet</h3>
      <p>Start a new session to see it here.</p>
      <NuxtLink to="/" class="btn-primary">Start New Session</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
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
</script>

<style scoped>
.history-page {
  max-width: 800px;
  margin: 0 auto;
  animation: rise 0.6s ease both;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-family: var(--font-serif);
  font-size: 2rem;
  margin: 0 0 8px;
}

.page-header p {
  color: var(--muted);
  margin: 0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.2s ease;
}

.history-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-soft);
  border-color: var(--accent-teal);
}

.card-content h3 {
  margin: 0 0 8px;
  font-size: 1.1rem;
  font-weight: 600;
}

.meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.85rem;
  color: var(--muted);
}

.status-badge {
  text-transform: uppercase;
  font-size: 0.7rem;
  letter-spacing: 0.05em;
  padding: 2px 8px;
  border-radius: 99px;
  background: var(--surface-warm);
  border: 1px solid var(--line);
}

.status-badge.completed {
  background: rgba(154, 168, 107, 0.15);
  color: #6b7a45;
  border-color: rgba(154, 168, 107, 0.3);
}

.status-badge.error {
  background: rgba(214, 122, 58, 0.1);
  color: #d67a3a;
  border-color: rgba(214, 122, 58, 0.3);
}

.btn-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--line);
  background: transparent;
  display: grid;
  place-items: center;
  color: var(--muted);
  transition: all 0.2s;
}

.history-card:hover .btn-icon {
  background: var(--accent-teal);
  color: #fff;
  border-color: var(--accent-teal);
}

.icon {
  width: 18px;
  height: 18px;
  background-color: currentColor;
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
  -webkit-mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
}

.i-arrow-right {
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='5' y1='12' x2='19' y2='12'%3E%3C/line%3E%3Cpolyline points='12 5 19 12 12 19'%3E%3C/polyline%3E%3C/svg%3E");
  -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='5' y1='12' x2='19' y2='12'%3E%3C/line%3E%3Cpolyline points='12 5 19 12 12 19'%3E%3C/polyline%3E%3C/svg%3E");
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: var(--surface);
  border-radius: var(--radius-lg);
  border: 1px dashed var(--line);
}

.empty-state h3 {
  margin: 16px 0 8px;
  font-family: var(--font-serif);
}

.empty-state p {
  color: var(--muted);
  margin-bottom: 24px;
}

.btn-primary {
  display: inline-block;
  background: var(--accent-teal);
  color: #fff;
  padding: 10px 24px;
  border-radius: var(--radius-sm);
  font-weight: 500;
  transition: opacity 0.2s;
}

.btn-primary:hover {
  opacity: 0.9;
}
</style>